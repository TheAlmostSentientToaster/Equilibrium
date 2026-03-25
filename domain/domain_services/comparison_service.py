from domain.interfaces.comparison_interface import ComparisonInterface
import logging

logger = logging.getLogger(__name__)

class ComparisonService(ComparisonInterface):
    def __init__(self, list_of_values: str):
        if list_of_values:
            self.list_of_values = [int(value.strip()) for value in list_of_values.split(',')]
        else:
            self.list_of_values = []
            logger.warning(f"User white list is None or empty.")

    def verify(self, value_to_compare:int) -> bool:
        if value_to_compare in self.list_of_values:
            return True
        else:
            return False