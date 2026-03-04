from abc import ABC, abstractmethod

class MessagePort(ABC):
    @abstractmethod
    def handle_message(self, text: str) -> list[str]:
        pass

class RepositoryPort(ABC):
    @abstractmethod
    def save_message(self, message: str) -> bool:
        pass

    @abstractmethod
    def get_all_messages(self) -> list[str]:
        pass