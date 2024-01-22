from ._version import __version__

from .magics import load_ipython_extension, unload_ipython_extension

from .flow import define_nb_args, execute_notebook, to_nb_output, load_nb_output

from .chat import (
    chat_object_manager,
    ChatObjectProvider,
    ChatExecutor,
    ChatObject,
    ChatObjectProvider,
)

from .utils import (
    is_ipython,
    is_langchain_installed,
    get_variable_list,
    get_variable_dict_list,
    get_langchain_variable_dict_list,
)
from .utils import (
    is_ipython,
    is_langchain_installed,
    get_variable_list,
    get_variable_dict_list,
    get_langchain_variable_dict_list,
)
