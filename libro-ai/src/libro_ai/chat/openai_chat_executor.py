from pydantic import Field

from .executor import LLMChat
from ..utils import is_langchain_installed
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langchain.callbacks import get_openai_callback
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from IPython.display import display
from libro_core.config import libro_config

class OpenAIChat(LLMChat):
    name: str = "chatgpt"
    model: str = Field(default="gpt-3.5-turbo")
    chat: ChatOpenAI = None

    def load(self):
        if is_langchain_installed():
            extra_params = {}
            libro_ai_config = libro_config.get_config().get("llm")
            if libro_ai_config is not None:
                if api_key := libro_ai_config.get("OPENAI_API_KEY"):
                    extra_params["api_key"] = api_key
            self.chat = ChatOpenAI(model_name=self.model,**extra_params)
            return True
        return False

    def run(self, value, **kwargs):
        if not self.chat:
            self.load()
        try:
            if not self.chat:
                raise Exception("Chat model not loaded")
            chat = self.chat
            with get_openai_callback() as cb:
                result = chat.invoke(value, **kwargs)
                # print(f"Total Tokens: {cb.total_tokens}")
                # print(f"Prompt Tokens: {cb.prompt_tokens}")
                # print(f"Completion Tokens: {cb.completion_tokens}")
                return result
            # result = chat.invoke(value,**kwargs)
            # return result
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

    def load(self):
        if is_langchain_installed():
            self.dalle = DallEAPIWrapper()
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
