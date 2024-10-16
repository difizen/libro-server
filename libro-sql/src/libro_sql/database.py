
from typing import Dict
from pydantic import BaseModel, field_validator
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from libro_core.config import libro_config

class DatabaseConfig(BaseModel):
    db_type: str
    username: str | None = None  # 可选字段
    password: str | None = None  # 可选字段
    host: str | None = None  # 可选字段
    port: int | None = None  # 可选字段
    database: str
    
    @field_validator('database', mode='before')
    def validate_database(cls, v, values):
        db_type = values.get('db_type')
        if db_type in ['postgresql', 'mysql','sqlite'] and not v:
            raise ValueError('database must be provided.')
        return v

    @field_validator('username', 'password', 'host', 'port', mode='before')
    def validate_fields(cls, v, values, field):
        db_type = values.get('db_type')
        if db_type in ['postgresql', 'mysql']:
            if v is None:
                raise ValueError(f'{field.name} must be provided when db_type is {db_type}')
            # 对于sqlite，不需要验证其他字段
        return v

class Database:
    config: DatabaseConfig
    id: str

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.id = config.db_type + ': ' + config.database
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
    # 添加一个方法用于将对象转换为字典
    def to_dict(self):
        return {
            "db_type": self.config.db_type,
            "id": self.id,
            "password": self.config.password,
            "host": self.config.host,
            "port": self.config.port,
            "database": self.config.database
        }

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
    dbs: Dict[str, Database] = {}

    def __init__(self) -> None:
        libro_sql_config = libro_config.get_config().get("db")
        for db in libro_sql_config:
            self.config(db)

    def config(self, c: dict):
        config = DatabaseConfig.model_validate(c)
        database = Database(config)
        self.dbs[database.id] = database

    def execute(self, query,id):
        """Execute a SQL query or non-query and return the result.

        If the query is a SELECT statement, return the result as a DataFrame.
        For other statements (INSERT, UPDATE, DELETE), execute the statement and return the number of affected rows.
        """
        execute_db = self.dbs.get(id)
        if execute_db is not None:
            return execute_db.execute(query)
        else:
            raise Exception(
                'Can not execute sql before database config set')
        
    def to_dbs_array(self):
        return [db.to_dict() for db in self.dbs.values()]

db = DatabaseManager()
