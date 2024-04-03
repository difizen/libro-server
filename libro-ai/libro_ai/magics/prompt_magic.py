# -*- coding: utf-8 -*-

from ast import arg
from IPython.core.magic import Magics, magics_class, line_cell_magic

from notebook.base.handlers import log
from ..chat import chat_provider
from langchain.prompts import PromptTemplate

logger = log()


def preprocessing_line_prompt(line, local_ns):
    import base64
    try:
        user_input = str(base64.decodebytes(line.encode()), "utf-8")
        import json
        # 将JSON字符串解析成Python对象
        json_obj = json.loads(user_input)
        prompt = json_obj.get("prompt")
        # 替换prompt content变量
        if(prompt):
            for key, value in local_ns.items():
                if not key.startswith("_"):
                    prompt = prompt.replace("{{" + key + "}}", str(value))
            json_obj["prompt"] = prompt
        return json_obj
    except Exception as e:
        raise Exception("preprocess_prompt error", e)
    
def preprocessing_cell_prompt(cell, local_ns):
    import base64
    try:
        import json
        # 将JSON字符串解析成Python对象
        json_obj = json.loads(cell)
        prompt = json_obj.get("prompt")
        # 替换prompt content变量
        if(prompt):
            for key, value in local_ns.items():
                if not key.startswith("_"):
                    prompt = prompt.replace("{{" + key + "}}", str(value))
            json_obj["prompt"] = prompt
        return json_obj
    except Exception as e:
        raise Exception("preprocess_prompt error", e)

class MimeTypeForPrompt(object):
    def __init__(self, smiles=None, val: object = None):
        self.smiles = smiles
        self.data = val

    def _repr_mimebundle_(self, include=None, exclude=None):
        return {
            "application/vnd.libro.prompt+json": self.data,
        }

@magics_class
class PromptMagic(Magics):
    """
    %%prompt 
    {"chat_key":"MyGPT","prompt":"do something"}
    """

    LLM_generate_res = ''

    def __init__(self, shell=None):
        super(PromptMagic, self).__init__(shell)
    
    @line_cell_magic
    def prompt(self, line="", cell=None):
        local_ns = self.shell.user_ns
        if cell is None:
            (
                args
            ) = preprocessing_line_prompt(line, local_ns)
        else:
            (
                args
            ) = preprocessing_cell_prompt(cell, local_ns)


        chat_key:str = args["model_name"]
        prompt:str = args["prompt"]
        dict = chat_provider.get_provider_dict()
        if chat_key in dict:
            exist = dict.get(chat_key)
            if exist:
                executor = exist.to_executor()
                # Use langchain prompt to support prompt templates and other features
                template = PromptTemplate.from_template(prompt)
                formattedPrompt = template.invoke(local_ns)
                res = executor.run(formattedPrompt)
                display_res = executor.display(res)
                # Set variable
                try:
                    if "variable_name" in args:
                        variable_name:str = args["variable_name"]
                        if variable_name and variable_name != "" and not variable_name.isidentifier():
                            raise Exception('Invalid variable name "{}".'.format(variable_name))
                        local_ns[variable_name] = res
                except Exception as e:
                    raise Exception("set variable error", e)
        else:
            raise Exception("Chat executor for %s not found!" % chat_key)
