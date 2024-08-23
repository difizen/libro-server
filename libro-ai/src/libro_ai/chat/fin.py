# 扩展 FinExpert
from typing import Any, List
import requests
import json
from langchain_core.messages import AIMessage, HumanMessage
from .object import ChatObject, ChatObjectProvider
from .executor import ChatExecutor
from .source import CHAT_SOURCE

from nbformat import v4
from libro_flow import LibroNotebookClient

from IPython.display import display, clear_output, HTML

from tqdm.notebook import tqdm_notebook
import threading
import time


def getMsgContent(msg):
    if isinstance(msg, HumanMessage):
        return {
            "type": "human",
            "content": getTextContent(msg)
        }
    if isinstance(msg, AIMessage):
        return {
            "type": "ai",
            "content": getTextContent(msg)
        }


def getTextContent(msg):
    if isinstance(msg.content, str):
        return msg.content
    if isinstance(msg.content, List):
        text_content = msg.content[0]
        return text_content.get("text")


def getSource(str):
    source = str
    prefix = source[0:9]
    if prefix == "```python":
        source = source[9:len(source)]
    prefix = source[0:3]
    if prefix == "```":
        source = source[3:len(source)]
    suffix = source[len(source)-3:len(source)]
    if suffix == "```":
        source = source[0:len(source)-3]
    return source


def check(result, to_display=False):
    start = result.find('```')
    end = result.find('```', start+1)
    source = getSource(result[start: end])
    if source == '':
        return None
    try:
        if to_display:
            display(HTML("""
            <div style="display: flex; align-items: center">
            <span style="color:rgb(22, 119, 255);padding:0 12px" role="img" aria-label="exclamation-circle" class="anticon anticon-exclamation-circle"><svg viewBox="64 64 896 896" focusable="false" data-icon="exclamation-circle" width="1em" height="1em" fill="currentColor" aria-hidden="true" style="
                width: 32px;
            "><path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm-32 232c0-4.4 3.6-8 8-8h48c4.4 0 8 3.6 8 8v272c0 4.4-3.6 8-8 8h-48c-4.4 0-8-3.6-8-8V296zm32 440a48.01 48.01 0 010-96 48.01 48.01 0 010 96z"></path></svg></span>
            自检中
            </div>"""))
        nb = v4.new_notebook(cells=[
            v4.new_code_cell(source=source),
        ])
        client = LibroNotebookClient(
            nb=nb,
        )
        client.execute()
        if to_display:
            clear_output()
            display(HTML("""
            <div style="display: flex; align-items: center">
            <span style="color:rgb(82, 196, 26);padding:0 12px" role="img" aria-label="exclamation-circle" class="anticon anticon-exclamation-circle"><svg viewBox="64 64 896 896" focusable="false" data-icon="exclamation-circle" width="1em" height="1em" fill="currentColor" aria-hidden="true" style="
                width: 32px;
            "><path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm193.5 301.7l-210.6 292a31.8 31.8 0 01-51.7 0L318.5 484.9c-3.8-5.3 0-12.7 6.5-12.7h46.9c10.2 0 19.9 4.9 25.9 13.3l71.2 98.8 157.2-218c6-8.3 15.6-13.3 25.9-13.3H699c6.5 0 10.3 7.4 6.5 12.7z"></path></svg></span>
            自检成功
            </div>"""))
        return True
    except Exception as e:
        if to_display:
            clear_output()
            display(HTML("""
            <div style="display: flex; align-items: center">
            <span style="color:rgb(255, 77, 79);padding:0 12px" role="img" aria-label="exclamation-circle" class="anticon anticon-exclamation-circle"><svg viewBox="64 64 896 896" focusable="false" data-icon="exclamation-circle" width="1em" height="1em" fill="currentColor" aria-hidden="true" style="
                width: 32px;
            "><path d="M512 64c247.4 0 448 200.6 448 448S759.4 960 512 960 64 759.4 64 512 264.6 64 512 64zm127.98 274.82h-.04l-.08.06L512 466.75 384.14 338.88c-.04-.05-.06-.06-.08-.06a.12.12 0 00-.07 0c-.03 0-.05.01-.09.05l-45.02 45.02a.2.2 0 00-.05.09.12.12 0 000 .07v.02a.27.27 0 00.06.06L466.75 512 338.88 639.86c-.05.04-.06.06-.06.08a.12.12 0 000 .07c0 .03.01.05.05.09l45.02 45.02a.2.2 0 00.09.05.12.12 0 00.07 0c.02 0 .04-.01.08-.05L512 557.25l127.86 127.87c.04.04.06.05.08.05a.12.12 0 00.07 0c.03 0 .05-.01.09-.05l45.02-45.02a.2.2 0 00.05-.09.12.12 0 000-.07v-.02a.27.27 0 00-.05-.06L557.25 512l127.87-127.86c.04-.04.05-.06.05-.08a.12.12 0 000-.07c0-.03-.01-.05-.05-.09l-45.02-45.02a.2.2 0 00-.09-.05.12.12 0 00-.07 0z"></path></svg></span>
            自检失败，请手动调试代码
            </div>"""))
            # display(e)
        return False


v = 0
def parse_file_knowledge_service(params, to_display=False):
    try:
        tqdm = None
        should_stop = None
        thread = None
        global v
        v = 0

        def tqdm_run(stop_event):
            while not stop_event.is_set():
                global v
                if v < 15:
                    v = v + 1
                    tqdm.update(0.5)
                time.sleep(0.8)

        if to_display:
            tqdm = tqdm_notebook(total=10)
            should_stop = threading.Event()
            thread = threading.Thread(target=tqdm_run, args=[should_stop])
            thread.start()
        file_path = '/config/config.txt'  # 文件路径
        with open(file_path, 'r', encoding='utf-8') as file:
            userId = file.read()
        url = f'https://zxzcopilotbff-pre.alipay.com/api/libro/parseFileKnowledge?userId={userId}'
        resp = requests.post(
            url,
            headers={
                "Content-Type": "application/json;charset=UTF-8",
            },
            data=json.dumps(params,ensure_ascii=False).encode("utf-8"),
            timeout=200,
        )
        resp = resp.json()
        result = ""
        if to_display:
            should_stop.set()
            thread.join()
            tqdm.update(10)
            tqdm.close()
            clear_output()
        if resp["success"] is True:
            res_str = resp.get('data').get('file_info')[0]
            if res_str is not None:
                return json.loads(res_str)
    except Exception as e:
        print("生成失败:", e)
        raise e

def agent_service(service_id, params, to_display=False):
    try:
        tqdm = None
        should_stop = None
        thread = None
        global v
        v = 0

        def tqdm_run(stop_event):
            while not stop_event.is_set():
                global v
                if v < 15:
                    v = v + 1
                    tqdm.update(0.5)
                time.sleep(0.8)

        if to_display:
            tqdm = tqdm_notebook(total=10)
            should_stop = threading.Event()
            thread = threading.Thread(target=tqdm_run, args=[should_stop])
            thread.start()
        file_path = '/config/config.txt'  # 文件路径
        with open(file_path, 'r', encoding='utf-8') as file:
            userId = file.read()
        url = f'https://zxzcopilotbff-pre.alipay.com/api/libro/queryAgent?userId={userId}'
        resp = requests.post(
            url,
            headers={
                "Content-Type": "application/json;charset=UTF-8",
            },
            data=json.dumps(
                {
                    "service_id": service_id,
                    "params": params,
                },
                ensure_ascii=False,
            ).encode("utf-8"),
            timeout=200,
        )
        resp = resp.json()
        result = ""
        if to_display:
            should_stop.set()
            thread.join()
            tqdm.update(10)
            tqdm.close()
            clear_output()
        if resp["success"] is True:
            res_str = resp.get("result")
            if res_str is not None:
                return json.loads(res_str)
    except Exception as e:
        print("生成失败:", e)
        raise e


r = None
finished = 0


class QuantExpert(ChatExecutor):
    def run(
        self,
        value,
        **kwargs,
    ) -> Any:
        """
        agent
        """
        try:
            global r, finished
            r = None
            finished = 0
            params = {}
            if isinstance(value, List):
                msg = value.pop()
                params = {
                    "input": getTextContent(msg),
                }
                if msg is not None:
                    if isinstance(msg.content, List):
                        if len(msg.content) == 2:
                            file_content = msg.content[1]
                            file_type = file_content.get("type")
                            if file_type == "image_url":
                                params["files"] = [
                                    {"type": "image", "url": file_content.get("image_url")}]
                            if file_type == "pdf_url":
                                display(HTML("""
                                <div style="display: flex; align-items: center">
                                <span style="color:rgb(22, 119, 255);padding:0 12px" role="img" aria-label="exclamation-circle" class="anticon anticon-exclamation-circle"><svg viewBox="64 64 896 896" focusable="false" data-icon="exclamation-circle" width="1em" height="1em" fill="currentColor" aria-hidden="true" style="
                                    width: 32px;
                                "><path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm-32 232c0-4.4 3.6-8 8-8h48c4.4 0 8 3.6 8 8v272c0 4.4-3.6 8-8 8h-48c-4.4 0-8-3.6-8-8V296zm32 440a48.01 48.01 0 010-96 48.01 48.01 0 010 96z"></path></svg></span>
                                解析 PDF 文件
                                </div>"""))
                                file_load_result_dict = parse_file_knowledge_service("file_upload_service", {
                                                                      "files": [{"type": "pdf", "url": file_content.get("pdf_url")}]})
                                tag = file_load_result_dict.get("tag")
                                params["files"] = [{"type": "pdf", "tag": tag}]
            if len(value) > 0:
                params["chat_history"] = list(map(getMsgContent, value))
            result_dic = agent_service("quant_expert_service", params, True)
            result = result_dic.get("output")
            should_check = result_dic.get("self_check")
            if not should_check:
                return result
            if result is not None:
                if not check(result, True):
                    clear_output()
                    display(HTML("""
                    <div style="display: flex; align-items: center">
                    <span style="color:rgb(22, 119, 255);padding:0 12px" role="img" aria-label="exclamation-circle" class="anticon anticon-exclamation-circle"><svg viewBox="64 64 896 896" focusable="false" data-icon="exclamation-circle" width="1em" height="1em" fill="currentColor" aria-hidden="true" style="
                        width: 32px;
                    "><path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm-32 232c0-4.4 3.6-8 8-8h48c4.4 0 8 3.6 8 8v272c0 4.4-3.6 8-8 8h-48c-4.4 0-8-3.6-8-8V296zm32 440a48.01 48.01 0 010-96 48.01 48.01 0 010 96z"></path></svg></span>
                    重试生成
                    </div>"""))

                    def get(i):
                        global r, finished
                        r_d = agent_service("quant_expert_service", params, False)
                        rs = r_d.get("output")
                        should_check = result_dic.get("self_check")
                        finished += 1
                        if not should_check:
                            r = rs
                        else:
                            if check(rs, False):
                                r = rs
                    start = time.perf_counter()
                    for i in range(2):
                        threading.Thread(target=get, args=(i,)).start()
                    while finished < 2:
                        time.sleep(1)
                    if r is not None:
                        clear_output()
                        display(HTML("""
                        <div style="display: flex; align-items: center">
                        <span style="color:rgb(82, 196, 26);padding:0 12px" role="img" aria-label="exclamation-circle" class="anticon anticon-exclamation-circle"><svg viewBox="64 64 896 896" focusable="false" data-icon="exclamation-circle" width="1em" height="1em" fill="currentColor" aria-hidden="true" style="
                            width: 32px;
                        "><path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm193.5 301.7l-210.6 292a31.8 31.8 0 01-51.7 0L318.5 484.9c-3.8-5.3 0-12.7 6.5-12.7h46.9c10.2 0 19.9 4.9 25.9 13.3l71.2 98.8 157.2-218c6-8.3 15.6-13.3 25.9-13.3H699c6.5 0 10.3 7.4 6.5 12.7z"></path></svg></span>
                        自检成功
                        </div>"""))
                        return r
                return result
            else:
                return "生成失败"

        except Exception as e:
            print("生成失败:", e)
            raise e


class ExpertProvider(ChatObjectProvider):
    name: str = "ant-quant-v2"
    quant: QuantExpert = QuantExpert(name="Quant-Expert")

    def list(self):
        return [
            ChatObject(
                name="Quant-Expert",
                to_executor=lambda: self.quant,
                type=CHAT_SOURCE["CUSTOM"],
            ),
        ]


# expert_provider = ExpertProvider()
# chat_object_manager.register_provider(expert_provider)
