from abc import ABC, abstractmethod

class ComparisonInterface(ABC):
    @abstractmethod
    def verify(self, value_to_compare:int) -> bool:
        pass