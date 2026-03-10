from abc import ABC, abstractmethod
from typing import Optional

from domain.chat_context import ChatContext
from domain.message import Message
from domain.photo import Photo


#Driven Ports
class InputMessagePort(ABC):
    @abstractmethod
    def receive_message(self, content:str, user_id: int, user_name: str, chat_context:ChatContext):
        pass

    @abstractmethod
    def receive_photo(self, photo_data: bytearray, user_id: int, user_name: str, chat_context: ChatContext):
        pass

#Driving Ports
class OutputMessagePort(ABC):
    @abstractmethod
    async def send_messages(self, messages: list[Message], chat_context: ChatContext):
        pass

class RepositoryPort(ABC):
    @abstractmethod
    def save_message(self, message: Message) -> bool:
        pass

    @abstractmethod
    def get_all_messages(self) -> list[Message]:
        pass

    @abstractmethod
    def save_photo(self, photo: Photo) -> bool:
        pass

    @abstractmethod#
    def save_photo_on_disk(self, photo: bytearray) -> Optional[str]:
        pass