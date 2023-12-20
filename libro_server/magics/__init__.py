from .prompt_magic import PromptMagic
from .exception import store_exception



def load_ipython_extension(ipython):
    ipython.register_magics(PromptMagic)
    ipython.set_custom_exc((BaseException,), store_exception)


def unload_ipython_extension(ipython):
    ipython.set_custom_exc((BaseException,), ipython.CustomTB)
