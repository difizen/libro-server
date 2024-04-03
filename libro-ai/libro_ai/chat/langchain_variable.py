from typing import Dict, List

from .source import CHAT_SOURCE
from .item import ChatItem, ChatItemProvider
from .executor import ChatExecutor
from ..utils.langchain import get_langchain_variable_dict_list, is_langchain_installed
class LangChainVariableChatItemProvider(ChatItemProvider):
    name: str = "langchain_variable"
    cache: Dict[str, ChatExecutor] = {}

    def get_or_create_executor(self, v: dict) -> ChatExecutor:
        if v["name"] in self.cache:
            return self.cache[v["name"]]
        from .langchain_variable_executor import LangChainVariableChat
        executor = LangChainVariableChat(variable=v)
        self.cache[v["name"]] = executor
        return executor

    def list(self) -> List[ChatItem]:
        if not is_langchain_installed():
            return []
        variables = get_langchain_variable_dict_list()
        return map(lambda v: ChatItem(name=v["name"], to_executor=lambda:self.get_or_create_executor(v), type=CHAT_SOURCE["VARIABLE"]), variables)