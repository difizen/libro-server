import json
from typing import List
from abc import ABC, abstractmethod
from pydantic import BaseModel

from .source import WHERE_CHAT_ITEM_FROM
from .executor import ChatExecutor

class ChatItem(BaseModel):
    name: str = None
    type: str = WHERE_CHAT_ITEM_FROM.CUSTOM
    order: int = 0
    def to_executor() -> ChatExecutor:
        pass
    def to_key(self) -> str:
        return self.type+":"+self.name

class ChatItemProvider(BaseModel, ABC):
    name: str = "custom"

    @abstractmethod
    def list(self) -> List[ChatItem]:
        """List chat executors."""