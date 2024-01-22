from abc import ABC, abstractmethod
import requests
from pydantic import BaseModel
from IPython.display import display
from typing import Any, Dict, List, Mapping, Optional, Tuple, Union

class ChatExecutor(BaseModel, ABC):
    name: str = "custom"
    order: int = 0

    @abstractmethod
    def run(
        self,value,**kwargs,
    ) -> str:
        """Chat and get result."""
    
    def display(
        self,value,**kwargs,
    ) -> str:
        data = {
            "application/vnd.libro.prompt+json": value
        }
        display(data, raw=True)

class LLMChat(ChatExecutor):
    name: str = "custom"

    @abstractmethod
    def load(
        self,config: dict
    ) -> bool:
        """Load LLM from Config Dict."""

    @abstractmethod
    def run(
        self,value,**kwargs,
    ) -> str:
        """Chat and get result."""

class APIChat(ChatExecutor):
    name: str = "api"
    url: str
    headers: Dict[str, str]
    data: Dict[str, Any]
    
    def get_request_config(self):
        return {
            "url":self.url,
            "headers":self.headers,
            "json":self.data
        }
    

    def handle_request(self,value,**kwargs):
        handled_request_config = {
            **self.get_request_config(),
            **kwargs,
        }
        return handled_request_config

    def handle_response(self,response):
        return response

    def run(self,value,**kwargs):
        config = self.handle_request(value,**kwargs)
        result = requests.post(**config)
        handled_result = self.handle_response(result.json())
        return handled_result


