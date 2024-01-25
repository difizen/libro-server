from .executor import LLMChat, ChatExecutor
from .openai import OpenAIChatObjectProvider
from .object_manager import ChatObjectManager
from .source import CHAT_SOURCE
from .object import ChatObject, ChatObjectProvider
from .langchain_variable import LangChainVariableChatObjectProvider
from .chat_record import ChatMessage, ChatRecord, ChatRecordProvider

chat_object_manager = ChatObjectManager()
chat_object_manager.register_provider(OpenAIChatObjectProvider())
chat_object_manager.register_provider(LangChainVariableChatObjectProvider())

chat_record_provider = ChatRecordProvider()

__all__ = [
    "LLMChat",
    "ChatExecutor",
    "chat_object_manager",
    "chat_record_provider",
    "ChatObject",
    "ChatObjectProvider",
    "ChatMessage",
    "ChatRecord",
    "ChatRecordProvider",
    "CHAT_SOURCE",
]
