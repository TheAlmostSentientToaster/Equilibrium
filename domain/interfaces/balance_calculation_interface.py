from abc import ABC, abstractmethod

class BalanceCalculationInterface(ABC):
    @abstractmethod
    def calculate_balance(self) -> list:
        pass