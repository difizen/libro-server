from langchain_openai import ChatOpenAI
from langchain.callbacks import get_openai_callback
from .executor import LLMChat
from ..utils import is_langchain_installed
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompt_values import StringPromptValue
from langchain_core.messages import AIMessage
from IPython.display import display
from libro_core.config import libro_config
from pydantic import Field

class DebugChat(LLMChat):
    name: str = "debug"
    model: str = Field(default="gpt-4o")
    system_message:SystemMessage = SystemMessage(content="你是一个代码调试小助手，在 notebook 执行时，输出了一些报错信息，请尝试解释报错并给出解决方案，每次对话都会给出代码以及报错信息")
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

    def run(self, value:StringPromptValue, stream = False,**kwargs):
        if not self.chat:
            self.load()
        if stream:
            try:
                if not self.chat:
                    raise Exception("Chat model not loaded")
                chat = self.chat
                human_message = HumanMessage(content=value.text)
                with get_openai_callback() as cb:
                    result = chat.stream([self.system_message,human_message], **kwargs)
                    return result
            except Exception as e:
                return ""
        else:
            try:
                if not self.chat:
                    raise Exception("Chat model not loaded")
                chat = self.chat
                human_message = HumanMessage(content=value.text)
                with get_openai_callback() as cb:
                    result = chat.invoke([self.system_message,human_message], **kwargs)
                    return result.content
            except Exception as e:
                return ""
            
    def display(self, value, **kwargs):
        if isinstance(value, str):
            data = {"application/vnd.libro.prompt+json": value}
            display(data, raw=True)
        if isinstance(value, AIMessage):
            data = {"application/vnd.libro.prompt+json": value.content}
            display(data, raw=True)