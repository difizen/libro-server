from typing import List, Union
from langchain.schema.messages import BaseMessage
from langchain_core.prompt_values import StringPromptValue

MODEL_NAME_ALIASES = {
    "text-davinci-003": "gpt3",
    "gpt-3.5-turbo": "chatgpt",
    "gpt-4": "gpt4",
    "dall-e-3": "dalle-3",
    "dall-e-2": "dalle-2",
    "qwen-max": "qwen-max",
    "qwen-plus": "qwen-plus",
    "qwen-turbo": "qwen-turbo",
}

ALIASE_NAME_MODEL = {
    "gpt3": "text-davinci-003",
    "chatgpt": "gpt-3.5-turbo",
    "gpt4": "gpt-4",
    "dalle-3": "dall-e-3",
    "dalle-2": "dall-e-2",
    "qwen-max": "qwen-max",
    "qwen-plus": "qwen-plus",
    "qwen-turbo": "qwen-turbo",
}

def get_message_str(message: Union[StringPromptValue, BaseMessage, List[BaseMessage]]):
    if isinstance(message, list):
        return "\n".join(list(map(lambda m: m.content, message)))  # type: ignore
    if isinstance(message, BaseMessage):
        return message.content
    return message.text
