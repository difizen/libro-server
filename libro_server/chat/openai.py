from typing import List
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
    executors: List[ChatExecutor] = None
    models: List[str] = ["gpt-3.5-turbo","gpt-4"]
    def list(self) -> List[ChatItem]:
        if self.executors is None:
            self.executors = []
            for model in self.models:
                alias = MODEL_NAME_ALIASES.get(model, model)
                executor = OpenAIChat(model=model, name=alias)
                if executor.load():
                    self.executors.append(executor)
        return map(lambda x: ChatItem(name=x.name, order=x.order, to_executor=lambda: x, type=WHERE_CHAT_ITEM_FROM.LLM), self.executors)