from .app import LibroApp
from .magics import PromptMagic, store_exception
from IPython import InteractiveShell


def load_ipython_extension(ipython: InteractiveShell):
    ipython.register_magics(PromptMagic)
    ipython.set_custom_exc((BaseException,), store_exception)


def unload_ipython_extension(ipython: InteractiveShell):
    ipython.set_custom_exc((BaseException,), ipython.CustomTB)


def _jupyter_server_extension_points():
    """
    Returns a list of dictionaries with metadata describing
    where to find the `_load_jupyter_server_extension` function.
    """
    return [{"module": "libro_server", "app": LibroApp}]


def load_jupyter_server_extension(ipython):
    """Load the Jupyter server extension.
    Parameters
    ----------
    ipython: :class:`jupyter_client.ioloop.IOLoopKernelManager`
        Jupyter kernel manager instance.
    """
    load_ipython_extension(ipython)
