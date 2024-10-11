import os
from uuid import uuid4, UUID
from nbclient import NotebookClient
from nbclient.util import ensure_async, run_sync
import nbformat
import datetime
from nbformat import NotebookNode
from typing import Any
import json
from pydantic import BaseModel, Field
import requests
from traitlets import Callable
import html  # 用于处理转义字符

# 定义MIME类型的优先级
MIME_PRIORITY = ['text/markdown', 'text/html', 'image/png', 'image/jpeg', 'text/plain']

def cellStartExecution(cell, **kwargs):
    cell.metadata.execution["shell.execute_reply.started"] = datetime.datetime.now(
        datetime.timezone.utc
    ).isoformat()


def select_mimetype(data):
    """从输出数据中选择最合适的MIME类型."""
    for mimetype in MIME_PRIORITY:
        if mimetype in data:
            return mimetype
    return None

def convert_output_to_markdown(output):
    """将单个输出转换为Markdown字符串，选择最合适的MIME类型."""
    markdown_str = ""

    # 处理stream类型输出（标准输出/标准错误）
    if output['output_type'] == 'stream':
        markdown_str += f"```\n{html.unescape(output['text'])}\n```"

    # 处理执行结果或显示数据
    elif output['output_type'] in ['execute_result', 'display_data']:
        data = output.get('data', {})
        
        # 选择最合适的MIME类型
        mimetype = select_mimetype(data)

        if mimetype:
            if mimetype == 'text/plain':
                markdown_str += f"```{html.unescape(data['text/plain'])}```"
            elif mimetype == 'text/html':
                markdown_str += f"<div>{html.unescape(data['text/html'])}</div>"
            elif mimetype == 'text/markdown':
                markdown_str += f"{html.unescape(data['text/markdown'])}"
            elif mimetype == 'image/png':
                markdown_str += f"![Image](data:image/png;base64,{data['image/png']})"
            elif mimetype == 'image/jpeg':
                markdown_str += f"![Image](data:image/jpeg;base64,{data['image/jpeg']})"
    # 处理错误输出
    elif output['output_type'] == 'error':
        error_traceback = '<br/>'.join(html.unescape(output['traceback']))
        markdown_str += f"```{html.unescape(error_traceback)}```"
    
    return markdown_str

def upload_notebook_to_jupyter(server_url, token, notebook_path, destination_path):
    """
    上传 .ipynb 文件到 Jupyter Server。
    
    :param server_url: Jupyter Server 的 URL（例如 http://localhost:8888）
    :param token: Jupyter Server 的 Token 认证信息
    :param notebook_path: 本地 .ipynb 文件路径
    :param destination_path: 目标路径（相对于 Jupyter 根目录）
    """
    # 读取要上传的 .ipynb 文件内容
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook_content = json.load(f)
    
    # 构建 API URL
    url = f"{server_url}/api/contents/{destination_path}"
    
    # 设置 headers，包含认证 token
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json",
    }
    
    # 构建请求 payload
    data = {
        "type": "notebook",  # 这里指定文件类型为 "notebook"
        "format": "json",    # Jupyter Notebook 文件是 JSON 格式的
        "content": notebook_content  # 直接传递 JSON 格式的文件内容
    }
    
    # 发送 PUT 请求上传文件
    response = requests.put(url, headers=headers, json=data)
    
    # 检查响应状态
    if response.status_code == 201:
        print(f"Notebook 上传成功: {notebook_path} -> {destination_path}")
    else:
        print(f"Notebook 上传失败: {response.status_code} - {response.text}")

class LibroExecution(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    current_index: int = 0
    cell_count: int = 0
    code_cells_executed: int = 0
    start_time: str = ""
    end_time: str = ""
    execute_result_path: str = ""
    execute_record_path: str = ""


class LibroNotebookClient(NotebookClient):
    execution: LibroExecution = LibroExecution()
    iframe_url: str | None
    jp_base_url: str | None
    upload_path: str | None
    render_by_iframe: bool = False

    def __init__(
        self,
        nb: NotebookNode,
        km=None,
        args: dict | None = None,
        execute_result_path: str | None = None,
        execute_record_path: str | None = None,
        iframe_url: str | None = None,
        jp_base_url: str | None = None,
        upload_path: str | None = None,
        **kw,
    ):
        super().__init__(nb=nb, km=km, **kw)
        if isinstance(args, dict):
            self.args = json.dumps(args)
        else:
            self.args = args
        self.execute_result_path = execute_result_path
        self.execute_record_path = execute_record_path
        self.iframe_url = iframe_url
        self.jp_base_url = jp_base_url
        self.start_time = None
        self.end_time = None
        self.upload_path = upload_path

    on_cell_execute = Callable(
        default_value=cellStartExecution,
        allow_none=True,
    ).tag(config=True)

    async def inspect_execution_result(self):
        assert self.kc is not None
        cell_allows_errors = (not self.force_raise_errors) and (self.allow_errors)
        inspect_msg = await ensure_async(
            self.kc.execute(
                "from libro_flow import inspect_execution_result\n\rinspect_execution_result()",
                store_history=False,
                stop_on_error=not cell_allows_errors,
            )
        )
        # print(inspect_msg)
        # self.kc._async_get_shell_msg(msg_id)
        reply = await self.async_wait_for_reply(inspect_msg)
        if reply is not None:
            print(reply)

    def get_status(self):
        status = self.execution
        return status

    def update_execution(self):
        self.execution = LibroExecution()

    async def async_execute(
        self, reset_kc: bool = False, **kwargs: Any
    ) -> NotebookNode:
        if reset_kc and self.owns_km:
            await self._async_cleanup_kernel()
        self.reset_execution_trackers()

        async with self.async_setup_kernel(**kwargs):
            assert self.kc is not None
            self.log.info("Executing notebook with kernel: %s" % self.kernel_name)
            msg_id = await ensure_async(self.kc.kernel_info())
            info_msg = await self.async_wait_for_reply(msg_id)
            if info_msg is not None:
                if "language_info" in info_msg["content"]:
                    self.nb.metadata["language_info"] = info_msg["content"][
                        "language_info"
                    ]
                else:
                    raise RuntimeError(
                        'Kernel info received message content has no "language_info" key. '
                        "Content is:\n" + str(info_msg["content"])
                    )
            cell_allows_errors = (not self.force_raise_errors) and (self.allow_errors)
            self.start_time = datetime.datetime.now(datetime.timezone.utc)
            self.execution.start_time = self.start_time.isoformat()
            self.nb.metadata["libro_execute_start_time"] = self.start_time.isoformat()
            await ensure_async(
                self.kc.execute(
                    f"__libro_execute_args_dict__={self.args}\n",
                    store_history=False,
                    stop_on_error=not cell_allows_errors,
                )
            )
            if self.execute_result_path is not None:
                await ensure_async(
                    self.kc.execute(
                        f"__libro_execute_result__='{self.execute_result_path}'\n",
                        store_history=False,
                        stop_on_error=not cell_allows_errors,
                    )
                )
                self.execution.execute_result_path = self.execute_result_path
            if self.execute_record_path is not None:
                self.execution.execute_record_path = self.execute_record_path
            self.execution.cell_count = len(self.nb.cells)
            for index, cell in enumerate(self.nb.cells):
                try:
                    await self.async_execute_cell(
                        cell, index, execution_count=self.code_cells_executed + 1
                    )
                except Exception:
                    self.render_by_iframe = True
                self.execution.current_index = index
                self.execution.code_cells_executed = self.code_cells_executed
                try:
                    if cell.metadata.execution is None:
                        cell.metadata.execution = {}
                    cell.metadata.execution["shell.execute_reply.end"] = (
                        datetime.datetime.now(datetime.timezone.utc).isoformat()
                    )
                except:
                    pass
                if self.execute_record_path is not None:
                    with open(self.execute_record_path, "w", encoding="utf-8") as f:
                        nbformat.write(self.nb, f)
                    if self.render_by_iframe:
                        if self.upload_path is None:
                            filename = os.path.basename(self.execute_record_path)
                            # 构建目标路径为 /upload 文件夹加上文件名
                            self.upload_path = f"upload/{filename}"
                        upload_notebook_to_jupyter(server_url=self.jp_base_url,token='',notebook_path=self.execute_record_path,destination_path=self.upload_path)
            self.set_widgets_metadata()
            self.kc.shutdown()
            # await self.inspect_execution_result()
            self.end_time = datetime.datetime.now(datetime.timezone.utc)
            self.execution.end_time = self.end_time.isoformat()
            self.nb.metadata["libro_execute_end_time"] = self.end_time.isoformat()
            log = None
        return self.nb

    execute = run_sync(async_execute)

    async def async_execute_to_md(
        self, reset_kc: bool = False, **kwargs: Any
    ) -> str:
        notebook = await self.async_execute(reset_kc,**kwargs)
        # 遍历每个cell，提取output并转成Markdown格式
        markdown_outputs = []
        for cell in notebook['cells']:
            if cell['cell_type'] == 'code' and 'outputs' in cell:
                for output in cell['outputs']:
                    markdown_outputs.append(convert_output_to_markdown(output))
        
        # 将所有输出拼接成一个Markdown字符串
        return '<br/>'.join(markdown_outputs)
    
    execute_to_markdown = run_sync(async_execute_to_md)
