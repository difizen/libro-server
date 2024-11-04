from typing import Optional
from pydantic import Field

from .executor import LLMChat
from ..utils import is_langchain_installed
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import HumanMessage, SystemMessage,AIMessage
from langchain_core.prompt_values import StringPromptValue
from IPython.display import display
from libro_core.config import libro_config


class TongyiChat(LLMChat):
    name: str = "tongyi"
    model: str = Field(default="qwen-max")
    chat: ChatTongyi = None
    api_key: Optional[str] = None

    def load(self):
        if is_langchain_installed():
            extra_params = {}
            if self.api_key:
                extra_params["api_key"] = self.api_key
            self.chat = ChatTongyi(model_name=self.model, **extra_params)
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
                if sync:
                    result = chat.stream(input, streaming = True,**kwargs)
                    return result
                else:

                    result = chat.astream(input, streaming = True, **kwargs)
                    return result
            except Exception as e:

                return ""
        else:
            try:
                if not self.chat:
                    raise Exception("Chat model not loaded")
                chat = self.chat
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
