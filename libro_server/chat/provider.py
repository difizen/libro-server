from abc import ABC, abstractmethod
import json
from typing import List, Dict
from pydantic import BaseModel
from .item import ChatItem,ChatItemProvider
from .executor import ChatExecutor


class ChatProvider(BaseModel):
    providers: List[ChatItemProvider] = []
    executors: Dict[str, ChatExecutor] = {}
    

    def register_provider(self, provider:ChatItemProvider):
        if provider.name in self.providers:
            print(f"Provider {provider.name} already exists")
            return
        if isinstance(provider, ChatItemProvider) == False:
            raise TypeError('provider must be ChatItemProvider')
        if provider.name in map(lambda x: x.name, self.providers):
            print(f"Provider {provider.name} already exists")
            return
        self.providers.append(provider)
    
    def get_provider_dict(self) -> Dict[str, ChatItem]:
        chat_items: Dict[str, ChatItem] = {}
        for provider in self.providers:
            for item in provider.list():
                key = item.key
                exists = chat_items.get(key)
                if exists:
                    if exists.order > item.order:
                        continue
                chat_items[key] = item
        return chat_items

    def get_provider_list(self) -> List[ChatItem]:
        """List chat items."""
        list = sorted(self.get_provider_dict().values(), key=lambda x: x.order)
        return list
    
    def dump_list_json(self) -> str:
        """List chat items."""
        list = self.get_provider_list()
        return json.dumps([item.model_dump() for item in list])
    


 