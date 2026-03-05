from abc import ABC, abstractmethod
from Domain.ChatContext import ChatContext
from Domain.Message import Message

#Driven Ports
class InputMessagePort(ABC):
    @abstractmethod
    def receive_message(self, content:str, user:str, chat_context:ChatContext):
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