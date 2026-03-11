from domain.interfaces.comparison_interface import ComparisonInterface


class ComparisonService(ComparisonInterface):
    def __init__(self, list_of_values: str):
        self.list_of_values = [int(value.strip()) for value in list_of_values.split(',')]

    def verify(self, value_to_compare:int) -> bool:
        if value_to_compare in self.list_of_values:
            return True
        else:
            return False