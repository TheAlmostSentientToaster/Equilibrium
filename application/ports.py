from abc import ABC, abstractmethod
from Domain.Message import Message

class MessagePort(ABC):
    @abstractmethod
    def handle_message(self, content: str, user: str) -> list[str]:
        pass

class RepositoryPort(ABC):
    @abstractmethod
    def save_message(self, message: Message) -> bool:
        pass

    @abstractmethod
    def get_all_messages(self) -> list[str]:
        pass