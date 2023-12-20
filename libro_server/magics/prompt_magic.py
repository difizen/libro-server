# -*- coding: utf-8 -*-

from IPython.core.magic import Magics, magics_class, line_cell_magic

from notebook.base.handlers import log
from ..model import model_registry

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
    {"model_name":"MyGPT","prompt":"do something"}
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


        model_name = args["model_name"]
        if(model_registry.promptModelRegistry.has_model(model_name)):
            model = model_registry.promptModelRegistry.get_model(model_name)
            res = model.run(args["prompt"])
            return MimeTypeForPrompt(val={"data": res})
        else:
            raise Exception("model %s not registered!" % model_name)
