from typing import Dict, Optional
from langchain_core.messages import BaseMessage

# langchain is cuurently using pydantic v1
from pydantic.v1 import BaseModel, Field


class ChatMessage(BaseModel):
    cell_id: str
    message: BaseMessage
    next: Optional[Dict] = Field(default=None)
