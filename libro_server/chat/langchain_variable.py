from typing import Dict, List

from .source import CHAT_SOURCE
from .item import ChatItem, ChatItemProvider
from .executor import ChatExecutor
from ..utils.langchain import get_langchain_variable_dict_list

class LangChainVariableChat(ChatExecutor):
    variable: dict = None
    def __init__(self,variable:dict):
        super().__init__(name=variable["name"])
        self.variable = variable
    def runChat(self,chat,value,**kwargs):
        from langchain_core.language_models.chat_models import BaseChatModel
        if isinstance(chat, BaseChatModel):
            return chat.invoke(value,**kwargs)
        return None
    def runChain(self,chain,value,**kwargs):
        from langchain.chains import LLMChain
        if isinstance(chain, LLMChain):
            return chain.run(value,**kwargs)
        return None
    def run(self,value,**kwargs):
        from IPython import get_ipython
        ipython = get_ipython()
        v = ipython.user_ns[self.name]
        if (self.variable["isChain"]):
            return self.runChain(v,value,**kwargs)
        elif (self.variable["isChat"]):
            return self.runChat(v,value,**kwargs)
        else:
            return None

class LangChainVariableChatItemProvider(ChatItemProvider):
    name: str = "langchain_variable"
    cache: Dict[str, ChatExecutor] = {}

    def get_or_create_executor(self, v: dict) -> ChatExecutor:
        if v["name"] in self.cache:
            return self.cache[v["name"]]
        executor = LangChainVariableChat(variable=v)
        self.cache[v["name"]] = executor
        return executor

    def list(self) -> List[ChatItem]:
        variables = get_langchain_variable_dict_list()
        return map(lambda v: ChatItem(name=v["name"], to_executor=lambda:self.get_or_create_executor(v), type=CHAT_SOURCE["VARIABLE"]), variables)