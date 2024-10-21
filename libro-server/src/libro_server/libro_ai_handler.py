import json
from jupyter_server.base.handlers import APIHandler
from libro_ai.chat import chat_object_manager
from jupyter_server.auth.decorator import allow_unauthenticated
from tornado.web import HTTPError, authenticated

class LibroChatHandler(APIHandler):
    @authenticated
    @allow_unauthenticated
    async def post(self):
        response_data = {
        }
        # 获取 POST 请求中的 JSON 数据
        model = self.get_json_body()
        if model is None:
            raise HTTPError(400, "can not get arguments")
        chat_key: str = model.get("chat_key")
        if chat_key is None or chat_key == "":
            chat_key = model.get("model_name")
        prompt: str = model.get("prompt")
        if (
            (chat_key is None or chat_key == "")
            or (prompt is None or prompt == "")
        ):
            raise Exception("Invalid prompt parameters!")

        dict = chat_object_manager.get_object_dict()
        if chat_key in dict:
            object = dict.get(chat_key)
            if object:
                executor = object.to_executor()
                # Use langchain prompt to support prompt templates and other features
                res = executor.run(prompt)
                response_data = {
                    "res": res.content
                }    
        self.finish(json.dumps(response_data))

class LibroChatStreamHandler(APIHandler):
    @authenticated
    @allow_unauthenticated
    async def post(self):
        # 获取 POST 请求中的 JSON 数据
        model = self.get_json_body()
        if model is None:
            raise HTTPError(400, "can not get arguments")
        chat_key: str = model.get("chat_key")
        if chat_key is None or chat_key == "":
            chat_key = model.get("model_name")
        prompt: str = model.get("prompt")
        # 流式输出响应
        self.set_header('Content-Type', 'text/event-stream')
        self.set_header('Cache-Control', 'no-cache')
        self.set_header('Connection', 'keep-alive')
        if (
            (chat_key is None or chat_key == "")
            or (prompt is None or prompt == "")
        ):
            raise Exception("Invalid prompt parameters!")

        dict = chat_object_manager.get_object_dict()
        if chat_key in dict:
            object = dict.get(chat_key)
            if object:
                executor = object.to_executor()
            # 生成流式响应
            final_result = ""
            try:
                for chunk in executor.run(prompt,stream=True):
                    self.write("event: chunk\n")
                    self.write(f"data: {chunk}\n\n")  # 发送 SSE 格式的数据
                    self.flush()  # 确保数据及时发送
                    final_result += chunk.content
                self.write("event: result\n")
                self.write(f"data: {final_result}\n\n")  # 发送最终结果
                self.flush()
            except Exception as e:
                self.write("event: error\n")
                self.write(f"data: error: {str(e)}\n\n")
                self.flush()
            self.finish()

