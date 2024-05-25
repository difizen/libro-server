import time

run_id_to_notebooks = {}

class Notebook:
    def __init__(self, file_path, last_modified):
        self.file_path = file_path
        self.last_modified = last_modified
    
    def to_dict(self):
        """将Notebook实例的属性转换为字典"""
        return {
            'file_path': self.file_path,
            'last_modified': self.last_modified
        }


# 假设我们有一些 INotebook 实例和相应的 run_id 以及 status
notebooks = [
    Notebook("examples/parameterized.ipynb", time.time()).to_dict(),
    Notebook("examples/agent.ipynb", time.time()).to_dict()
]
status = "completed"
run_id = "run_123"

# 将这个结构存储到映射中
run_id_to_notebooks[run_id] = {"status": status, "render_notebooks": notebooks}

# 查看映射内容
print(run_id_to_notebooks)
