import time

from libro_flow.libro_client import LibroNotebookClient

run_id_to_notebooks = {}

run_id_to_agent_task = {}

tool_id_to_run_id = {}

# class Notebook:
#     def __init__(self, file_path, code_cells_executed):
#         self.file_path = file_path
#         self.code_cells_executed = code_cells_executed
    
#     def to_dict(self):
#         """将Notebook实例的属性转换为字典"""
#         return {
#             'file_path': self.file_path,
#             'code_cells_executed': self.code_cells_executed
#         }

class Notebooks:
    def __init__(self):
        self.stack:List[LibroNotebookClient]= []  # 保存实例的列表，维持栈的结构
        self.stack_map:dict[str, LibroNotebookClient] = {}  # 保存路径到实例的映射
    
    def add_notebook(self,file_path:str, client:LibroNotebookClient):
        self.stack.append(client)
        self.stack_map[file_path] = client
    
    def get_notebook_by_path(self, file_path):
        return self.stack_map.get(file_path)
    
    def __iter__(self):
        self._index = len(self.stack)  # 设置为栈的顶端
        return self
    
    def __next__(self):
        if self._index > 0:
            self._index -= 1
            return self.stack[self._index]
        else:
            raise StopIteration

from typing import List, TypedDict

# 定义一个TypedDict，指定字典键和相应的类型
class NotebooksInfo(TypedDict):
    status: str
    render_notebooks: Notebooks

# 将这个结构存储到映射中
# run_id_to_notebooks[run_id] = {"status": status, "render_notebooks": notebook_stack}

