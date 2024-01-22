from typing import Any, Dict, List, Optional
from numpy import isin
from pydantic import Field

from .source import CHAT_SOURCE

from .executor import LLMChat
from ..utils import is_langchain_installed
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langchain.callbacks import get_openai_callback
from IPython.display import display

class OpenAIChat(LLMChat):
    name: str = "chatgpt"
    model: str = Field(default="gpt-3.5-turbo")
    chat: ChatOpenAI = None

    def load(self):
        if is_langchain_installed():
            self.chat = ChatOpenAI(model_name=self.model)
            return True
        return False
    def run(self,value,**kwargs):
        if not self.chat:
            self.load()
        try:
            if not self.chat:
                raise Exception("Chat model not loaded")
            chat = self.chat
            with get_openai_callback() as cb:
                result = chat.invoke(value,**kwargs)
                # print(f"Total Tokens: {cb.total_tokens}")
                # print(f"Prompt Tokens: {cb.prompt_tokens}")
                # print(f"Completion Tokens: {cb.completion_tokens}")
                return result
            # result = chat.invoke(value,**kwargs)
            # return result
        except Exception as e:
            return ""
    def display(self,value,**kwargs):
        if isinstance(value, str):
            data = {
                "application/vnd.libro.prompt+json": value
            }
            display(data, raw=True)
        if isinstance(value, AIMessage):
            data = {
                "application/vnd.libro.prompt+json": value.content
            }
            display(data, raw=True)
        return self.run(value,**kwargs)
