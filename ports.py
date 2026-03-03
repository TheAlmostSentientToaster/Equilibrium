from abc import ABC, abstractmethod

class BotMessagePort(ABC):
    @abstractmethod
    def handle_message(self, text: str) -> list[str]:
        pass