from abc import ABC, abstractmethod
from typing import Optional

from domain.chat_context import ChatContext
from domain.message import Message
from domain.photo import Photo
from domain.command import Command


#Driven Ports
class InputMessagePort(ABC):
    @abstractmethod
    def receive_message(self, content:str, user_id: int, user_name: str, chat_context:ChatContext):
        pass

    @abstractmethod
    def receive_photo(self, photo_data: bytearray, user_id: int, user_name: str, chat_context: ChatContext):
        pass

    @abstractmethod
    def receive_command(self, command: Command, chat_context: ChatContext):
        pass

class CommandServicePort(ABC):
    @abstractmethod
    async def handle_command(self, command: Command, chat_context: ChatContext):
        pass

class MessageServicePort(ABC):
    @abstractmethod
    async def receive_message(self, content: str, user_id: int, user_name: str, chat_context: ChatContext):
        pass

    @abstractmethod
    async def send_all_messages(self, chat_context: ChatContext):
        pass

class PhotoServicePort(ABC):
    @abstractmethod
    async def receive_photo(self, photo: bytearray, user_id: int, user_name: str, chat_context: ChatContext):
        pass

    @abstractmethod
    async def send_message(self, message: str, chat_context: ChatContext):
        pass

class UserVerificationPort(ABC):
    @abstractmethod
    async def verify_user(self, user_id: int, chat_context: ChatContext):
        pass

    @abstractmethod
    async def send_message(self, message: str, chat_context: ChatContext):
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

    @abstractmethod
    def save_photo_on_disk(self, photo: bytearray) -> Optional[str]:
        pass

    @abstractmethod
    def get_sums_of_deposits(self) -> list:
        pass