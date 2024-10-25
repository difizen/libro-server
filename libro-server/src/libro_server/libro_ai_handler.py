import json
import time
from jupyter_server.base.handlers import APIHandler
from jupyter_server.auth.decorator import allow_unauthenticated
from libro_ai.chat import chat_object_manager
from jupyter_server.auth.decorator import allow_unauthenticated
from tornado.web import HTTPError, authenticated
from langchain.prompts import PromptTemplate


import tornado
from tornado.web import HTTPError
from tornado import gen
from tornado.iostream import StreamClosedError


class LibroChatHandler(APIHandler):
    @allow_unauthenticated
    def options(self) -> None:
        self.finish({})

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
        system_prompt: str = model.get("system_prompt")
        if (
            (chat_key is None or chat_key == "")
            or (prompt is None or prompt == "")
        ):
            raise Exception("Invalid prompt parameters!")

        dict = chat_object_manager.get_object_dict()
        if chat_key in dict:
            object = dict.get(chat_key)
            if object:
                template = PromptTemplate.from_template(prompt)
                formattedPrompt = template.invoke({})
                executor = object.to_executor()
                # Use langchain prompt to support prompt templates and other features
                res = executor.run(formattedPrompt,sync = False,system_prompt = system_prompt)
                response_data = {
                    "res": res.content
                }
        self.finish(json.dumps(response_data))


class LibroChatStreamHandler(APIHandler):
    @allow_unauthenticated
    def options(self) -> None:
        self.finish({})

    @gen.coroutine
    def publish(self, data):
        """Pushes data to a listener."""
        try:
            self.write(data)
            yield self.flush()
        except StreamClosedError as e:
            pass

    @gen.coroutine
    def post(self):
        # 获取 POST 请求中的 JSON 数据
        model = self.get_json_body()
        if model is None:
            raise HTTPError(400, "can not get arguments")
        chat_key: str = model.get("chat_key")
        if chat_key is None or chat_key == "":
            chat_key = model.get("model_name")
        prompt: str = model.get("prompt")
        system_prompt: str = model.get("system_prompt")
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
            template = PromptTemplate.from_template(prompt)
            formattedPrompt = template.invoke({})
            # 生成流式响应
            final_result = ""
            try:

                for chunk in executor.run(formattedPrompt,stream=True, sync=False,system_prompt = system_prompt):
                    # Construct an event with data and event type
                    event_id = int(time.time())  # Simple event ID
                    event_type = "chunk"
                    data = json.dumps({"output": chunk.content},
                                      ensure_ascii=False)
                    message = f"id: {event_id}\n"
                    message += f"event: {event_type}\n"
                    message += f"data: {data}\n\n"
                    self.publish(message)
                    final_result += chunk.content
                    # yield tornado.gen.sleep(1)
                event_id = int(time.time())  # Simple event ID
                event_type = "result"
                data = json.dumps({"output": final_result},
                                  ensure_ascii=False)
                message = f"id: {event_id}\n"
                message += f"event: {event_type}\n"
                message += f"data: {data}\n\n"
                self.publish(message)
            except Exception as e:
                message = "event: error\n"
                message += f"data: error: {str(e)}\n\n"
                self.publish(message)
            self.finish()
