from domain.chat_context import ChatContext
from domain.command import Command
from application.ports import OutputMessagePort
from domain.interfaces.balance_calculation_interface import BalanceCalculationInterface
from domain.message import Message


class CommandService:
    def __init__(self, output_message_port: OutputMessagePort, balance_calculation_interface: BalanceCalculationInterface,  message: type[Message]):
        self.output_message_port = output_message_port
        self.balance_calculation_interface = balance_calculation_interface
        self.message = message

    async def handle_command(self, command: Command, chat_context: ChatContext):
        responses = list()

        if command.content == "balance":
            balances = self.balance_calculation_interface.calculate_balance()

            for balance in balances:
                message = self.message(
                message_id=None,
                content=balance[0] + ": " + str(balance[1]) + "€",
                user_id=None,
                user_name=None
                )
                responses.append(message)
        elif command.content == "start":
            response = [self.message(
                message_id=None,
                content="Welcome to Equilibrium.",
                user_id=None,
                user_name=None
            )]
            responses.append(response)
        else:
            response = [self.message(
                message_id=None,
                content="Unknown command.",
                user_id=None,
                user_name=None
            )]
            responses.append(response)

        await self.output_message_port.send_messages(responses, chat_context)