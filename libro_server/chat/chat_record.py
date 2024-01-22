from typing import List, Dict, Optional
from pydantic import BaseModel
from langchain_core.messages import BaseMessage


class ChatMessage(BaseModel):
    message: BaseMessage
    cell_id: str
    prev: Optional[Dict] = None
    next: Optional[Dict] = None


class ChatRecord(BaseModel):
    start_message: Optional[ChatMessage] = None

    def get_messages(self) -> List[BaseMessage]:
        messages = []
        current = self.start_message
        while current:
            messages.append(current.message)
            current = current.next
        return messages

    def append_message(self, cell_id: str, message: BaseMessage, reset: bool = False):
        chat_message = ChatMessage(message=message, cell_id=cell_id)
        if not self.start_message:
            self.start_message = chat_message
            return
        if reset:
            current = self.start_message
            while current.next and isinstance(current.next, ChatMessage):
                if current.next.cell_id == cell_id:
                    current.next = chat_message
                    break
                current = current.next
        else:
            current = self.start_message
            while current and isinstance(current, ChatMessage):
                if (
                    current.cell_id == cell_id
                    and current.next
                    and isinstance(current.next, ChatMessage)
                    and current.next.cell_id != cell_id
                ):
                    current.next = chat_message
                    break
                current = current.next


class ChatRecordProvider(BaseModel):
    record_dict: Dict[str, ChatRecord] = {}

    def get_record(self, cell_id: str) -> ChatRecord:
        return self.record_dict[cell_id]

    def set_record(self, cell_id: str, record: ChatRecord):
        self.record_dict[cell_id] = record

    def get_records(self) -> List[str]:
        return list(self.record_dict.keys())
