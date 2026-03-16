from domain.chat_context import ChatContext
from domain.command import Command
from application.ports import OutputMessagePort, CommandServicePort, RepositoryPort, HttpOutboundPort
from domain.interfaces.balance_calculation_interface import BalanceCalculationInterface
from domain.message import Message

class CommandService(CommandServicePort):
    def __init__(self, output_message_port: OutputMessagePort, balance_calculation_interface: BalanceCalculationInterface, repository_port: RepositoryPort, http_outbound_port: HttpOutboundPort, message: type[Message]):
        self.output_message_port = output_message_port
        self.balance_calculation_interface = balance_calculation_interface
        self.repository_port = repository_port
        self.message = message
        self.http_output_port = http_outbound_port

    def post_command_hints(self, token: str):
        url = f"https://api.telegram.org/bot{token}/setMyCommands"

        commands = {
            "commands": [
                {"command": "balance", "description": "Shows current balance between contributors."},
                {"command": "ping", "description": "Pings the server."},
                {"command": "add_payment", "description": "Hold and add amount and comment."}
            ]
        }

        self.http_output_port.post(url=url, json=commands)

    async def handle_command(self, command: Command, chat_context: ChatContext):
        responses = list()

        if command.content == "balance":
            balances = self.balance_calculation_interface.calculate_balances()
            deposits = self.balance_calculation_interface.calculate_deposits()
            responses = responses + self.command_balance(balances, deposits)

        elif command.content == "start":
            responses.append(self.command_start())

        elif command.content.startswith("X"):
            responses.append(await self.command_delete_payment(command))

        elif command.content.startswith("ping"):
            responses.append(self.command_ping())

        elif command.content.startswith("add_payment"):
            responses.append(await self.command_add_payment(command))

        elif command.content.startswith("C"):
            responses.append(await self.command_change_payment(command))

        elif command.content.startswith("D"):
            responses.append(await self.command_display_bill(command))
            return

        else:
            responses.append(self.command_unknown())

        await self.output_message_port.send_messages(responses, chat_context)

    def command_ping(self) -> Message:
        response = self.message(
                message_id=None,
                content="Ping!",
                user_id=None,
                user_name=None
        )
        return response

    def command_unknown(self) -> Message:
        response = self.message(
            message_id=None,
            content="Unknown command.",
            user_id=None,
            user_name=None
        )
        return response

    async def command_delete_payment(self, command: Command) -> Message:
        content_split = command.content.split()
        payment_id = content_split[0][1:]

        deletion_success = self.repository_port.delete_payment(command)
        if deletion_success:
            response = self.message(
                message_id=None,
                content="Payment deleted successfully.",
                user_id=None,
                user_name=None
            )
        else:
            response = self.message(
                message_id=None,
                content="Payment already deleted or ID not found.\nSee logs for more Information.",
                user_id=None,
                user_name=None
            )

        if deletion_success:
            broadcast_message = f"{command.user_name} just deleted payment {str(payment_id)}\n"
            users = self.repository_port.get_all_users()
            users.remove(command.user_id)
            await self.output_message_port.send_broadcast([Message(None, broadcast_message, None, None)], users)

        return response

    def command_start(self) -> Message:
        response = self.message(
            message_id=None,
            content="Welcome to Equilibrium.",
            user_id=None,
            user_name=None
        )
        return response

    def command_balance(self, balances: list, deposits: list) -> list[Message]:
        messages = list()

        for deposit in deposits:
            message = self.message(
                message_id=None,
                content=deposit[0] + " paid in total: " + str(deposit[1]) + "€",
                user_id=None,
                user_name=None
            )
            messages.append(message)

        messages.append(self.message(
            message_id=None,
            content="",
            user_id=None,
            user_name=None
        ))

        for balance in balances:
            message = self.message(
                message_id=None,
                content=balance[0] + " has left to pay: " + str( -1 * balance[1]) + "€",
                user_id=None,
                user_name=None
            )
            messages.append(message)
        return messages

    async def command_add_payment(self, command: Command) -> Message:
        content_split = command.content.split()

        if len(content_split) < 2:
            message = self.message(
                message_id=None,
                user_id=None,
                content=f"Amount required.",
                user_name=None
            )
            return message

        amount = content_split[1]

        payment_id = self.repository_port.add_payment(command)

        if payment_id:
            message = self.message(
                message_id=None,
                user_id=None,
                content=f"Payment of {amount}€ added successfully.\nPress /X{payment_id} to delete.\nHold /C{payment_id} to change the amount.",
                user_name=None
            )
        else:
            message = self.message(
                message_id=None,
                user_id=None,
                content=f"Adding payment failed.\nSee logs for further information.",
                user_name=None
            )

        if payment_id:
            broadcast_message = f"{command.user_name} just added {str(amount)}€\n"
            users = self.repository_port.get_all_users()
            users.remove(command.user_id)
            await self.output_message_port.send_broadcast([Message(None, broadcast_message, None, None)], users)

        return message

    async def command_change_payment(self, command: Command) -> Message:
        content_split = command.content.split()
        payment_id = content_split[0][1:]

        if len(content_split) < 2:
            message = self.message(
                message_id=None,
                user_id=None,
                content=f"Amount of payment missing",
                user_name=None
            )
            return message

        amount = content_split[1]

        change_success = self.repository_port.change_payment(command)
        if change_success:
            message = self.message(
                message_id=None,
                user_id=None,
                content=f"Payment changed to {amount}",
                user_name=None
            )
        else:
            message = self.message(
                message_id=None,
                user_id=None,
                content=f"Changing payment failed.\nSee logs for further information.",
                user_name=None
            )

        if change_success:
            broadcast_message = f"{command.user_name} just changed payment {payment_id} to {str(amount)}€\n"
            users = self.repository_port.get_all_users()
            users.remove(command.user_id)
            await self.output_message_port.send_broadcast([Message(None, broadcast_message, None, None)], users)

        return message

    async def command_display_bill(self, command: Command):
        payment_id = command.content[1:]
        picture_path = self.repository_port.get_bill_path(int(payment_id))
        await self.output_message_port.send_image(picture_path, ChatContext(command.user_id))
        pass