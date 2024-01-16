import keyword
import re
from .base import is_ipython
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

def is_langchain_chain(name):
    """
    Is this a name of a Python variable that can be called as a LangChain chain?
    """
    # Reserved word in Python?
    if keyword.iskeyword(name):
        return False
    if not is_ipython():
        return False    
    from IPython import get_ipython
    if not is_langchain_installed():
        return False
    from langchain.chains import LLMChain

    acceptable_name = re.compile("^[a-zA-Z0-9_]+$")
    if not acceptable_name.match(name):
        return False
    ipython = get_ipython()
    return name in ipython.user_ns and isinstance(ipython.user_ns[name], LLMChain)

def is_langchain_chat_model(name):
    """
    Is this a name of a Python variable that can be called as a LangChain chain?
    """
    # Reserved word in Python?
    if keyword.iskeyword(name):
        return False
    if not is_ipython():
        return False    
    from IPython import get_ipython
    if not is_langchain_installed():
        return False
    from langchain_core.language_models.chat_models import BaseChatModel

    acceptable_name = re.compile("^[a-zA-Z0-9_]+$")
    if not acceptable_name.match(name):
        return False
    ipython = get_ipython()
    return name in ipython.user_ns and isinstance(ipython.user_ns[name], BaseChatModel)



def langchain_variable(name)->dict:
    isChain = is_langchain_chain(name)
    isModel = is_langchain_chat_model(name)
    if not isChain and not isModel:
        return None
    return {
        "isChain": isChain,
        "isModel": isModel,
        "name": name,
    }

def get_langchain_variable_dict_list():
    return get_variable_dict_list(langchain_variable, lambda x: x)