from typing import List
from abc import ABC, abstractmethod
from pydantic import BaseModel

from .source import CHAT_SOURCE
from .executor import ChatExecutor

class ChatItem(BaseModel):
    name: str = None
    type: str = CHAT_SOURCE["CUSTOM"]
    order: int = 0
    to_executor: lambda: ChatExecutor = None

    def __init__(self, name: str, type: str = CHAT_SOURCE["CUSTOM"], order: int = 0, to_executor=None):
        super().__init__(name=name, type=type, order=order)
        self.to_executor = to_executor

    @property
    def key(self):
        return '%s:%s'%(self.type, self.name)
    
    def model_dump(self):
        '''Dump to dict'''
        return {
            **super().model_dump(exclude="to_executor"),
            "key":self.key
        }

class ChatItemProvider(BaseModel, ABC):
    name: str = "custom"

    @abstractmethod
    def list(self) -> List[ChatItem]:
        """List chat executors."""