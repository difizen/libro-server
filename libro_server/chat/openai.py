from typing import Dict, List
from pydantic import Field

from .source import WHERE_CHAT_ITEM_FROM

from .executor import LLMChat,ChatExecutor
from .item import ChatItem, ChatItemProvider
from ..utils import is_langchain_installed

MODEL_NAME_ALIASES = {
    "text-davinci-003": "gpt3",
    "gpt-3.5-turbo":"chatgpt",
    "gpt-4": "gpt4",
}

ALIASE_NAME_MODEL = {
    "gpt3":"text-davinci-003",
    "chatgpt": "gpt-3.5-turbo",
    "gpt4": "gpt-4",
}

class OpenAIChat(LLMChat):
    name: str = "chatgpt"
    model: str = Field(default="gpt-3.5-turbo")
    chat: dict = None

    def load(self):
        if is_langchain_installed():
            from langchain_community.chat_models import ChatOpenAI
            self.chat = ChatOpenAI(model_name=self.model)
            return True
        return False
    def run(self,value,**kwargs):
        if not hasattr(self,"llm"):
            self.load()
        try:
            result = self.chat(value,**kwargs)
            return result
        except Exception as e:
            return ""

class OpenAIChatItemProvider(ChatItemProvider):
    name: str = "openai"
    cache: Dict[str, ChatExecutor] = {}
    models: List[str] = ["gpt-3.5-turbo","gpt-4"]

    def get_or_create_executor(self, name: str) -> ChatExecutor:
        if name in self.cache:
            return self.cache[name]
        model = ALIASE_NAME_MODEL.get(name, name)
        executor = OpenAIChat(model=model, name=name)
        if executor.load():
            self.cache[model] = executor
        return executor

    def list(self) -> List[ChatItem]:
        return map(lambda n: ChatItem(name=MODEL_NAME_ALIASES.get(n, n), to_executor=self.get_or_create_executor, type=WHERE_CHAT_ITEM_FROM.LLM), self.models)