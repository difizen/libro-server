import requests

class CustomModel:
    def __init__(self,model_name,**kwargs):
        self.model_name = model_name

    def run(self,value,**kwargs):
        pass

class APIModel(CustomModel):
    def __init__(self,model_name,url, headers, json, **kwargs):
        self.model_name = model_name
        self.request_config = {
            **{
                "url":url,
                "headers":headers,
                "json":json
            },
            **kwargs
        }

    def handle_request(self,value,**kwargs):
        handled_request_config = {
            **self.request_config,
            **kwargs,
        }
        return handled_request_config

    def handle_response(self,response):
        return response

    def update_config(self,**kwargs):
        self.request_config = {
            **self.request_config,
            **kwargs,
        }

    def run(self,value,**kwargs):
        config = self.handle_request(value,**kwargs)
        result = requests.post(**config)
        handled_result = self.handle_response(result.json())
        return handled_result
