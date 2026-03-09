from abc import ABC, abstractmethod
from typing import Optional

class PriceExtractionInterface(ABC):
    @abstractmethod
    def extract_price(self, photo: bytearray) -> Optional[float]:
        pass