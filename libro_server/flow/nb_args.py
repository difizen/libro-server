from pydantic import BaseModel
from nbformat import NotebookNode
from IPython.display import display
from .libro_client import LibroNotebookClient
from jupyter_client.manager import KernelManager
from typing import Any,Union
import tempfile
import uuid

def define_nb_args(ArgsModel:BaseModel):
    from IPython import get_ipython
    ipython = get_ipython()
    args_model = ArgsModel()
    try:
        args_dict = ipython.user_ns['__libro_input_dict__']
        args_model = ArgsModel(**args_dict)
    except (TypeError,KeyError):
        pass
    for args_key, args_value in args_model.__dict__.items():
        ipython.user_ns[args_key] = args_value
    ipython.user_ns['__libro_input__'] = args_model
    args_metadata = args_model.model_json_schema()
    data = {"application/vnd.libro.args+json": args_metadata}
    display(data, raw=True)

def to_nb_output(output,output_path = None):
    import pickle
    from IPython import get_ipython
    import tempfile
    import uuid
    import os
    ipython = get_ipython()
    try:
        to_output_path = ipython.user_ns['__libro_output__']
    except KeyError:
        to_output_path = output_path
    if to_output_path is None:
        libro_output_dir = tempfile.mkdtemp()
        _uuid = uuid.uuid4().hex[:16].lower()
        libro_output_name = "libro_output_" + _uuid + ".pickle"
        to_output_path = os.path.join(libro_output_dir, libro_output_name)
        ipython.user_ns['__libro_output__'] = to_output_path
    if not to_output_path.endswith('.pickle'):
        raise Exception("Output path should endwith .pickle!")
    # 将数据序列化为字节流
    with open(to_output_path, 'wb') as f:
        pickle.dump(output, f)
    return to_output_path

def load_nb_output(output_path):
    import pickle
    with open(output_path, 'rb') as f:
        nb_output = pickle.load(f)
    return nb_output

def load_notebook_node(notebook_path):
    import nbformat
    nb = nbformat.read(notebook_path, as_version=4)
    nb_upgraded = nbformat.v4.upgrade(nb)
    if nb_upgraded is not None:
        nb = nb_upgraded
    return nb

def execute_notebook(
    notebook_path:str,
    parameters = None,
    output_path = None,
    km: Union[KernelManager, None] = None,
    **kwargs: Any,
) -> NotebookNode:
    nb = load_notebook_node(notebook_path)
    return LibroNotebookClient(nb=nb, output_path=output_path, km=km, parameters=parameters, **kwargs).execute()
