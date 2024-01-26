from typing import List
from langchain.schema.messages import BaseMessage


def get_message_str(message: BaseMessage or List[BaseMessage]):
    if isinstance(message, list):
        return "\n".join(list(map(lambda m: m.content, message)))
    return message.content
