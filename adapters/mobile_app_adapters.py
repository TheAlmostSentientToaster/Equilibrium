from application.ports import InputMessagePort, OutputMessagePort
from domain.command import Command
from domain.message import Message
from domain.chat_context import ChatContext

class MobileAppOutboundAdapter(OutputMessagePort):
    async def send_messages(self, messages: list[Message], chat_context: ChatContext):
        pass

    async def send_broadcast(self, messages: list[Message], users: list[int]):
        pass

    async def send_image(self, image_path: str, chat_context: ChatContext):
        pass

class MobileAppInboundAdapter(InputMessagePort):
    def __init__(self,
                 message_service,
                 photo_service,
                 command_service,
                 user_verification_service):
        self.message_service = message_service
        self.photo_service = photo_service
        self.command_service = command_service
        self.user_verification_service = user_verification_service

    def receive_photo(self, photo_data: bytearray, user_id: int, user_name: str, chat_context: ChatContext):
        pass

    def receive_message(self, content: str, user_id: int, user_name: str, chat_context: ChatContext):
        pass

    def receive_command(self, command: Command, chat_context: ChatContext):
        pass