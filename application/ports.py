from abc import ABC, abstractmethod
from Domain.Message import Message
from telegram import Update

#Driven Ports
class InputMessagePort(ABC):
    @abstractmethod
    def receive_message(self, content:str, user:str):
        pass

#Driving Ports
class OutputMessagePort(ABC):
    @abstractmethod
    def send_messages(self):
        pass

class RepositoryPort(ABC):
    @abstractmethod
    def save_message(self, message: Message) -> bool:
        pass

    @abstractmethod
    def get_all_messages(self) -> list[Message]:
        pass