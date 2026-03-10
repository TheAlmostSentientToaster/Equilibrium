from domain.chat_context import ChatContext
from domain.command import Command
from application.ports import OutputMessagePort
from domain.message import Message


class CommandService:
    def __init__(self, output_message_port: OutputMessagePort,  message: type[Message]):
        self.output_message_port = output_message_port
        self.message = message

    async def handle_command(self, command: Command, chat_context: ChatContext):
        if command.content == "balance":
            #call domain service, that calls DB and calculates balance

            response = self.message(
                message_id=None,
                content="Your balance is 100€.",
                user_id=None,
                user_name=None
            )
            await self.output_message_port.send_messages([response], chat_context)
        else:
            response = self.message(
                message_id=None,
                content="Unknown command.",
                user_id=None,
                user_name=None
            )
            await self.output_message_port.send_messages([response], chat_context)