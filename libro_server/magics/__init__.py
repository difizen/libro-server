from .prompt_magic import PromptMagic
from .exception import store_exception
from IPython import InteractiveShell


def load_ipython_extension(ipython: InteractiveShell):
    ipython.register_magics(PromptMagic)
    ipython.set_custom_exc((BaseException,), store_exception)


def unload_ipython_extension(ipython: InteractiveShell):
    ipython.set_custom_exc((BaseException,), ipython.CustomTB)
