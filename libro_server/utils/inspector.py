from importlib import __import__
from typing import List

from .base import is_ipython


def get_variable_list()-> List[str]:
    if not is_ipython():
        return []
    from IPython import get_ipython
    from IPython.core.magics.namespace import NamespaceMagics
    ipython = get_ipython()
    nms = NamespaceMagics()
    nms.shell = ipython.kernel.shell
    values = nms.who_ls()
    return values

def get_variable_dict_list(condition: lambda x:bool, to_dict: lambda x: dict)-> List[dict]:
    variables = get_variable_list()
    vardic = [
        to_dict(v)
        for v in variables if condition(v)
    ]
    return vardic

