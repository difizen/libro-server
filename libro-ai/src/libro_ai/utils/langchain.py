from pydantic import BaseModel
from .inspector import get_variable_dict_list

def is_langchain_installed():
    """
    Is LangChain installed?
    """
    try:
        import langchain
        return True
    except ImportError:
        return False

def langchain_variable(name)->dict:
    from IPython import get_ipython
    ipython = get_ipython()

    def is_langchain_chain(name):
        from langchain.chains import LLMChain
        return name in ipython.user_ns and isinstance(ipython.user_ns[name], LLMChain)

    def is_langchain_chat_model(name):
        from langchain_core.language_models.chat_models import BaseChatModel
        return name in ipython.user_ns and isinstance(ipython.user_ns[name], BaseChatModel)

    isChain = is_langchain_chain(name)
    isChat = is_langchain_chat_model(name)
    if not isChain and not isChat:
        return None
    return {
        "isChain": isChain,
        "isChat": isChat,
        "name": name,
    }

def get_langchain_variable_dict_list():
    if not is_langchain_installed():
        return []
    return get_variable_dict_list(langchain_variable)