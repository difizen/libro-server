
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd


class DatabaseConfig(BaseModel):
    db_type: str
    username: str
    password: str
    host: str
    port: int
    database: str


class Database:
    config: DatabaseConfig

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine = self._create_engine()

    def _create_engine(self):
        """Create the SQLAlchemy engine based on the database type."""
        config = self.config
        try:
            if config.db_type == 'postgresql':
                engine = create_engine(
                    f'postgresql+psycopg2://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}')
            elif config.db_type == 'mysql':
                engine = create_engine(
                    f'mysql+pymysql://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}')
            elif config.db_type == 'sqlite':
                engine = create_engine(f'sqlite:///{config.database}')
            else:
                raise ValueError(
                    f"Unsupported database type: {config.db_type}")
            return engine
        except Exception as e:
            print(f"Error creating engine: {e}")
            raise

    def execute(self, query):
        """Execute a SQL query or non-query and return the result.

        If the query is a SELECT statement, return the result as a DataFrame.
        For other statements (INSERT, UPDATE, DELETE), execute the statement and return the number of affected rows.
        """
        with self.engine.connect() as connection:
            try:
                result = connection.execute(text(query))
                if result.returns_rows:
                    # Fetch all rows and construct DataFrame with column names
                    rows = result.fetchall()
                    if rows:
                        # Debug: Print fetched rows
                        df = pd.DataFrame(rows, columns=result.keys())
                    else:
                        df = pd.DataFrame()  # Return empty DataFrame if no rows
                    return df
                else:
                    if result.rowcount is not None:
                        connection.commit()
                        return result.rowcount
                    else:
                        return result
            except SQLAlchemyError as e:
                print(f"Error executing query: {e}")
                raise


class DatabaseManager():
    db: Optional[Database] = None

    def config(self, c: dict):
        config = DatabaseConfig.model_validate(c)
        self.db = Database(config)

    def execute(self, query):
        """Execute a SQL query or non-query and return the result.

        If the query is a SELECT statement, return the result as a DataFrame.
        For other statements (INSERT, UPDATE, DELETE), execute the statement and return the number of affected rows.
        """
        if self.db is not None:
            return self.db.execute(query)
        else:
            raise Exception(
                'Can not execute sql before database config set')
        
    def get_db_config(self):
        if self.db is None:
            return None
        else:
            return self.db.config

db = DatabaseManager()
