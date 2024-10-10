import asyncio
from libro_flow.libro_schema_form_widget import SchemaFormWidget
import nbformat
import os
from pydantic import BaseModel
from IPython.display import display
from .libro_client import LibroNotebookClient
from jupyter_client.manager import KernelManager
from typing import Any, Union, Callable, TypeVar

ArgsType = TypeVar("ArgsType", bound=BaseModel)


def inspect_execution_result():
    from IPython.core.getipython import get_ipython

    ipython = get_ipython()
    user_ns = ipython.user_ns  # type: ignore
    try:
        result_dump_path = user_ns["__libro_execute_result_dump_path__"]
        return result_dump_path
    except (TypeError, KeyError):
        pass


def notebook_args(ArgsModel: type[ArgsType]) -> ArgsType:
    from IPython.core.getipython import get_ipython

    ipython = get_ipython()
    args_model = ArgsModel()
    user_ns = ipython.user_ns  # type: ignore

    args_dict = user_ns.get("__libro_execute_args_dict__")
    if args_dict is not None:
        args_model = ArgsModel(**args_dict)

    for args_key, args_value in args_model.__dict__.items():
        user_ns[args_key] = args_value
    user_ns["__libro_execute_args__"] = args_model
    widget = SchemaFormWidget(dataModel=args_model)
    data = {"application/vnd.libro.args+json": args_model.model_json_schema()}
    display(data, raw=True)
    display(widget)
    return args_model


def dump_execution_result(result, path=None):
    import pickle
    from IPython.core.getipython import get_ipython
    import tempfile
    import uuid
    import os

    ipython = get_ipython()
    user_ns = ipython.user_ns  # type: ignore
    result_path = user_ns.get("__libro_execute_result__")
    if result_path is None:
        result_path = path
    if result_path is None:
        result_dir = tempfile.mkdtemp()
        _uuid = uuid.uuid4().hex[:16].lower()
        result_file_name = "libro_execute_result_" + _uuid + ".pickle"
        result_path = os.path.join(result_dir, result_file_name)
        user_ns["__libro_execute_result__"] = result_path
    if not result_path.endswith(".pickle"):
        raise Exception("Output path should endwith .pickle!")
    # 将数据序列化为字节流
    with open(result_path, "wb") as f:
        pickle.dump(result, f)
        user_ns["__libro_execute_result_dump_path__"] = result_path
    return result_path


def load_execution_result(pickle_file_path):
    import pickle

    with open(pickle_file_path, "rb") as f:
        nb_output = pickle.load(f)
    return nb_output


def load_notebook_node(execute):
    # 获取文件后缀名
    _, ext = os.path.splitext(execute)
    
    if ext == '.ipynb':
        # 加载 .ipynb 文件
        nb = nbformat.read(execute, as_version=4)
        nb_upgraded = nbformat.v4.upgrade(nb)
        if nb_upgraded is not None:
            nb = nb_upgraded   
        return nb
    elif ext == '.py':
        # 加载 .py 文件并转换为 notebook
        return load_python_as_notebook(execute)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def load_python_as_notebook(python_path):
    # 创建一个空的 notebook 节点
    nb = nbformat.v4.new_notebook()
    
    # 读取 .py 文件内容
    with open(python_path, 'r') as f:
        python_code = f.read()

    # 将 Python 代码转换为单个代码单元格
    code_cell = nbformat.v4.new_code_cell(source=python_code)
    
    # 将代码单元格加入到 notebook
    nb.cells.append(code_cell)
    
    return nb


def execute_notebook(
    notebook: Any,
    args=None,
    execute_result_path: str | None = None,
    execute_record_path: str | None = None,
    notebook_parser: Callable | None = None,
    km: Union[KernelManager, None] = None,
    **kwargs: Any,
):
    if notebook_parser is not None:
        nb = notebook_parser(notebook)
    else:
        nb = load_notebook_node(notebook)
    client = LibroNotebookClient(
        nb=nb,
        km=km,
        args=args,
        execute_result_path=execute_result_path,
        execute_record_path=execute_record_path,
        **kwargs,
    )
    client.update_execution()
    asyncio.create_task(client.async_execute())
    display(client.execute_result_path)
    return client

def execute_notebook_sync(
    execute: Any,
    args=None,
    execute_result_path: str | None = None,
    execute_record_path: str | None = None,
    notebook_parser: Callable | None = None,
    km: Union[KernelManager, None] = None,
    **kwargs: Any,
):
    if notebook_parser is not None:
        nb = notebook_parser(execute)
    else:
        nb = load_notebook_node(execute)
    client = LibroNotebookClient(
        nb=nb,
        km=km,
        args=args,
        execute_result_path=execute_result_path,
        execute_record_path=execute_record_path,
        **kwargs,
    )
    client.update_execution()
    client.execute()
    display(client.execute_result_path)
    return client

def execute_notebook_sync_to_markdown(
    execute: Any,
    iframe_url:str,
    jp_base_url: str,
    args=None,
    execute_result_path: str | None = None,
    execute_record_path: str | None = None,
    notebook_parser: Callable | None = None,
    km: Union[KernelManager, None] = None,
    **kwargs: Any,
):
    if notebook_parser is not None:
        nb = notebook_parser(execute)
    else:
        nb = load_notebook_node(execute)
    client = LibroNotebookClient(
        nb=nb,
        km=km,
        args=args,
        execute_result_path=execute_result_path,
        execute_record_path=execute_record_path,
        iframe_url = iframe_url,
        jp_base_url = jp_base_url,
        **kwargs,
    )
    client.update_execution()
    md = client.execute_to_markdown()
    display(client.execute_result_path)
    return md
