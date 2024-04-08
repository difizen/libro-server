from typing import Any, Dict, List, Optional
from pydantic import Field
from IPython.display import display

from .source import CHAT_SOURCE

from .executor import LLMChat,ChatExecutor
from .item import ChatItem, ChatItemProvider
from ..utils import is_langchain_installed

MODEL_NAME_ALIASES = {
    "text-davinci-003": "gpt3",
    "gpt-3.5-turbo":"chatgpt",
    "gpt-4": "gpt4",
    "dall-e-3": "dalle-3",
    "dall-e-2": "dalle-2",

}

ALIASE_NAME_MODEL = {
    "gpt3":"text-davinci-003",
    "chatgpt": "gpt-3.5-turbo",
    "gpt4": "gpt-4",
    "dalle-3": "dall-e-3",
    "dalle-2": "dall-e-2",
}

class OpenAIChatItemProvider(ChatItemProvider):
    name: str = "openai"
    cache: Dict[str, ChatExecutor] = {}
    models: List[str] = ["gpt-3.5-turbo","gpt-4"]

    def get_or_create_executor(self, name: str) -> ChatExecutor:
        model = ALIASE_NAME_MODEL.get(name, name)
        if model in self.cache:
            return self.cache[model]
        from .openai_chat_executor import OpenAIChat
        executor = OpenAIChat(model=model, name=name)
        if executor.load():
            self.cache[model] = executor
        return executor

    def list(self) -> List[ChatItem]:
        if not is_langchain_installed():
            return []
        return map(lambda n: ChatItem(name=MODEL_NAME_ALIASES.get(n, n), to_executor=lambda:self.get_or_create_executor(n), type=CHAT_SOURCE["LLM"]), self.models)

class DALLEChatItemProvider(ChatItemProvider):
    name: str = "dalle"
    cache: Dict[str, ChatExecutor] = {}
    models: List[str] = ["dall-e-3","dall-e-2"]

    def get_or_create_executor(self, name: str) -> ChatExecutor:
        model = ALIASE_NAME_MODEL.get(name, name)
        if model in self.cache:
            return self.cache[model]
        from .openai_chat_executor import DalleChat
        executor = DalleChat(model=model, name=name)
        if executor.load():
            self.cache[model] = executor
        return executor

    def list(self) -> List[ChatItem]:
        if not is_langchain_installed():
            return []
        return map(lambda n: ChatItem(name=MODEL_NAME_ALIASES.get(n, n), to_executor=lambda:self.get_or_create_executor(n), type=CHAT_SOURCE["LLM"]), self.models)