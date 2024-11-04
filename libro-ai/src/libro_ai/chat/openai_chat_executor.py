from typing import Optional
from pydantic import Field

from .executor import LLMChat
from ..utils import is_langchain_installed
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage,AIMessage
from langchain_core.prompt_values import StringPromptValue
from langchain.callbacks import get_openai_callback
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from IPython.display import display
from libro_core.config import libro_config


class OpenAIChat(LLMChat):
    name: str = "chatgpt"
    model: str = Field(default="gpt-3.5-turbo")
    chat: ChatOpenAI = None
    api_key: Optional[str] = None

    def load(self):
        if is_langchain_installed():
            extra_params = {}
            if self.api_key:
                extra_params["api_key"] = self.api_key
            self.chat = ChatOpenAI(model_name=self.model, **extra_params)
            return True
        return False

    def run(self, value:StringPromptValue,language = None,stream=False, sync=True, system_prompt = None, **kwargs):
        if not self.chat:
            self.load()
        input = []
        if system_prompt is None:
            input = [HumanMessage(content=value.text)]
        else:
            input = [SystemMessage(content=system_prompt),HumanMessage(content=value.text)]
        
        if stream:
            try:
                if not self.chat:
                    raise Exception("Chat model not loaded")
                chat = self.chat
                with get_openai_callback() as cb:
                    if sync:
                        result = chat.stream(input, **kwargs)
                        return result
                    else:

                        result = chat.astream(input, **kwargs)
                        return result
            except Exception as e:
                return ""
        else:
            try:
                if not self.chat:
                    raise Exception("Chat model not loaded")
                chat = self.chat
                with get_openai_callback() as cb:
                    if sync:
                        result = chat.invoke(input, **kwargs)
                        return result
                    else:
                        result = chat.ainvoke(input, **kwargs)
                        return result
            except Exception as e:
                return ""

    def display(self, value, **kwargs):
        if isinstance(value, str):
            data = {"application/vnd.libro.prompt+json": value}
            display(data, raw=True)
        if isinstance(value, AIMessage):
            data = {"application/vnd.libro.prompt+json": value.content}
            display(data, raw=True)


class DalleChat(LLMChat):
    name: str = "dalle-3"
    model: str = Field(default="dall-e-3")
    dalle: DallEAPIWrapper = None
    api_key: Optional[str] = None

    def load(self):
        extra_params = {}
        if is_langchain_installed():
            if self.api_key:
                extra_params["api_key"] = self.api_key
            self.dalle = DallEAPIWrapper(**extra_params)
            self.dalle.model_name = self.model
            return True
        return False

    def run(self, value, **kwargs):
        if not self.dalle:
            self.load()
        try:
            if not self.dalle:
                raise Exception("Chat model not loaded")
            dalle = self.dalle
            result = dalle.run(value.text)
            return result
        except Exception as e:
            return ""

    def display(self, value, **kwargs):
        data = {"text/html": f"<img src = {value}>"}
        display(data, raw=True)
        # HTML(f'<img src = {value}>',raw=True)
