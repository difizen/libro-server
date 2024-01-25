from ..utils import is_ipython
from .executor import ChatExecutor
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain.chains import LLMChain
from langchain_core.runnables import Runnable


class LangChainVariableChat(ChatExecutor):
    variable: dict = None

    def __init__(self, variable: dict):
        super().__init__(name=variable["name"])
        self.variable = variable

    def run(self, value, **kwargs):
        from IPython import get_ipython

        ipython = get_ipython()
        v: Runnable = ipython.user_ns[self.name]
        return v.invoke(value, **kwargs)

    def display(self, value, **kwargs):
        if is_ipython():
            from IPython.display import display

            if isinstance(value, str):
                data = {"application/vnd.libro.prompt+json": value}
                display(data, raw=True)
            if isinstance(value, AIMessage):
                data = {"application/vnd.libro.prompt+json": value.content}
                display(data, raw=True)
