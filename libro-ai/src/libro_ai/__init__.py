from ._version import __version__

import jupyter_server.serverapp
from libro_ai.libro_ai_handler import LibroChatHandler, LibroChatStreamHandler

from .extensions import (
    load_ipython_extension,
    unload_ipython_extension,
    _load_jupyter_server_extension,
)


from .chat import (
    chat_object_manager,
    ChatObjectProvider,
    ChatExecutor,
    ChatObject,
    ChatObjectProvider,
    chat_record_provider,
)

from .utils import (
    is_ipython,
    is_langchain_installed,
    get_variable_list,
    get_variable_dict_list,
    get_langchain_variable_dict_list,
)

def _load_jupyter_server_extension(serverapp: jupyter_server.serverapp.ServerApp):
    """
    This function is called when the extension is loaded.
    """
    print('test')
    handlers = [(rf"/libro/api/chat", LibroChatHandler),
                (rf"/libro/api/chatstream", LibroChatStreamHandler)
                ]
    serverapp.web_app.add_handlers(".*$", handlers)