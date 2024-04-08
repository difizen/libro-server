from .executor import ChatExecutor
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain.chains import LLMChain

class LangChainVariableChat(ChatExecutor):
    variable: dict = None
    def __init__(self,variable:dict):
        super().__init__(name=variable["name"])
        self.variable = variable
    def runChat(self,chat,value,**kwargs):
        if isinstance(chat, BaseChatModel):
            return chat.invoke(value,**kwargs)
        return None
    def runChain(self,chain,value,**kwargs):
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