import json
from jupyter_server.base.handlers import APIHandler
from libro_ai.chat import chat_object_manager
from tornado.web import HTTPError

class LibroChatHandler(APIHandler):
    def post(self):
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