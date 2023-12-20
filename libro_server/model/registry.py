import json
from .base_model import CustomModel

class ModelRegistry:
    """
    model registry
    """
    def __init__(self):
        self.models = {}

    def register_model(self, model):
        if model.model_name in self.models:
            return f"Model {model.model_name} already exists"
        if isinstance(model, CustomModel) == False:
            raise TypeError('Model is not a instance of class CustomModel')
        self.models[model.model_name] = model
        return f"Model {model.model_name} registered"

    def get_model(self, name):
        if name in self.models:
            return self.models[name]
        return None

    def has_model(self, name):
        if name in self.models:
            return True
        return False

    def get_models(self):
        return self.models

    def delete_model(self, name):
        if name in self.models:
            del self.models[name]
            return f"Model {name} deleted"
        return f"Model {name} does not exist"

    def get_model_json(self,name):
        cur_model = self.get_model(self, name)
        model_json = json.dumps(cur_model.__dict__)
        return model_json

model_registry = ModelRegistry()
