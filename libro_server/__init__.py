from ._version import __version__

from .app import LibroApp

from .magics import load_ipython_extension, unload_ipython_extension

from .flow import define_nb_args,execute_notebook,to_nb_output,load_nb_output

from .chat import chat_provider, ChatProvider, ChatExecutor, ChatItem, ChatItemProvider

from .utils import is_ipython, is_langchain_installed,  get_variable_list, get_variable_dict_list, get_langchain_variable_dict_list

def _jupyter_server_extension_points():
    """
    Returns a list of dictionaries with metadata describing
    where to find the `_load_jupyter_server_extension` function.
    """
    return [
        {
            "module": "libro_server",
            "app": LibroApp
        }
    ]
