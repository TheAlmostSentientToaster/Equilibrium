from application.ports import UserVerificationPort, OutputMessagePort
from domain.chat_context import ChatContext
from domain.interfaces.comparison_interface import ComparisonInterface
from domain.message import Message


class UserVerificationService(UserVerificationPort):
    def __init__(self, output_message_port: OutputMessagePort, comparison_interface: ComparisonInterface):
        self.output_message_port = output_message_port
        self.comparison_interface = comparison_interface

    async def verify_user(self, user_id: int, chat_context: ChatContext) -> bool:
        if self.comparison_interface.verify(value_to_compare=user_id):
            return True
        else:
            await self.send_message("Access denied", chat_context)
            return False

    async def send_message(self, message: str, chat_context: ChatContext):
        message = Message(message_id=None, content=message, user_id=None, user_name=None)
        messages = [message]
        await self.output_message_port.send_messages(messages=messages, chat_context=chat_context)