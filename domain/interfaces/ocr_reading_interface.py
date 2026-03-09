from abc import ABC, abstractmethod
from typing import Any

class OcrReadingInterface(ABC):
    @abstractmethod
    def read_text(self, photo: bytearray) -> list[dict[str, Any]]:
        pass