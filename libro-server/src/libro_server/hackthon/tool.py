from libro_flow.libro_execution import execute_notebook, execute_notebook_sync, load_execution_result
from libro_server.hackthon.utils import get_res_file_path,get_record_file_path
from libro_server.hackthon_globals import Notebooks, tool_id_to_run_id,run_id_to_notebooks
from langchain.agents import Tool
import os

def create_tool_func(file_path):
    def tool_func(*args, callbacks, **kwargs) -> str:
        print("tool_func",callbacks.__dict__)
        tool_id = str(callbacks.parent_run_id)
        run_id = tool_id_to_run_id[tool_id]
        notebookInfo = run_id_to_notebooks.get(run_id)
        notebooks = None
        if notebookInfo is None:
            notebooks = Notebooks()
            run_id_to_notebooks[run_id] = {"status":"loading","render_notebooks":notebooks}
        else:
            notebooks:Notebooks = notebookInfo["render_notebooks"]
        print('tool file path',file_path)
        res_path = get_res_file_path(file_path)
        record_path = get_record_file_path(file_path)
        print('res_path,record_path',res_path,record_path)
        client = execute_notebook_sync(
            notebook=file_path, args=args, execute_result_path = res_path,execute_record_path=record_path
        )
        print('execute_notebook',client)
        if notebooks.get_notebook_by_path(file_path) is None:
            notebooks.add_notebook(file_path,client)
        print("notebooks",notebooks)
        execution_result_path = client.get_status().execute_result_path
        print("execution_result_path",execution_result_path)
        res = load_execution_result(execution_result_path)
        print("tool res",res)
        return res
    return tool_func

def create_tools(path):
    tools = []
    for file_name in os.listdir(path):
        print("file_name",file_name)
        if os.path.isfile(os.path.join(path, file_name)) and str(file_name).endswith('.ipynb'):
            # 为每个文件创建一个方法，方法名与文件名相关联
            tool_func = create_tool_func(os.path.join(path, file_name))
            tool_name = str(file_name).replace('.ipynb','')
            # 将文件名和对应的方法传递给ClassA，创建ClassA的实例
            tool = Tool(name = tool_name, func = tool_func, description=tool_name)
            tools.append(tool)
    return tools

tools = create_tools('/Users/ximo.lk/Public/code/opensource/libro-server/examples/hackthon')