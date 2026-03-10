from application.ports import RepositoryPort
from domain.interfaces.balance_calculation_interface import BalanceCalculationInterface

class BalanceCalculationService(BalanceCalculationInterface):
    def __init__(self, repository_port: RepositoryPort):
        self.repository_port = repository_port

    def calculate_balance(self) -> list:
        deposits = self.repository_port.get_sums_of_deposits()
        users_count = len(deposits)
        total_sum = 0
        balances = list()

        for deposit in deposits:
            total_sum += deposit[1]
        average_sum = total_sum / users_count

        for deposit in deposits:
            balances.append((deposit[0], deposit[1] - average_sum))

        return balances