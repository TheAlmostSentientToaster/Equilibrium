from telegram import Update # pip install python-telegram-bot==20.7
from telegram.ext import Application, ContextTypes
from application.ports import InputMessagePort, OutputMessagePort, MessageServicePort, PhotoServicePort, \
    CommandServicePort, UserVerificationPort
from domain.command import Command
from domain.message import Message
from domain.chat_context import ChatContext

class TelegramInboundAdapter(InputMessagePort):
    def __init__(self,
                 message_service: MessageServicePort,
                 photo_service: PhotoServicePort,
                 command_service: CommandServicePort,
                 user_verification_service: UserVerificationPort,
                 application: Application):
        self.message_service = message_service.receive_message
        self.photo_service = photo_service.receive_photo
        self.command_service = command_service.handle_command
        self.user_verification_service = user_verification_service
        self.application = application

    async def on_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.from_user.id
        user_name = update.message.from_user.first_name
        chat_context = ChatContext(chat_id=update.message.chat_id)

        if await self.user_verification_service.verify_user(user_id, chat_context):
            if update.message.photo:
                photo = update.message.photo[-1]
                file = await context.bot.get_file(photo.file_id)
                photo_bytes = await file.download_as_bytearray()
                await self.receive_photo(photo_bytes, user_id, user_name, chat_context)
            elif update.message.text and update.message.text.startswith('/'):
                command_text = update.message.text
                command_parts = command_text[1:].split()
                command = Command(
                    content=command_parts[0],
                    user_id=user_id,
                    user_name=user_name
                )
                await self.receive_command(command, chat_context)
            else:
                content = update.message.text
                await self.receive_message(content, user_id, user_name, chat_context)

    async def receive_photo(self, photo_data: bytearray, user_id: int, user_name: str, chat_context: ChatContext):
        await self.photo_service(photo=photo_data, user_id=user_id, user_name=user_name, chat_context=chat_context)

    async def receive_message(self, content:str, user_id:int, user_name: str, chat_context:ChatContext):
        await self.message_service(content=content, user_id=user_id, user_name=user_name, chat_context=chat_context)

    async def receive_command(self, command: Command, chat_context: ChatContext):
        await self.command_service(command=command, chat_context=chat_context)


class TelegramOutboundAdapter(OutputMessagePort):
    def __init__(self, bot):
        self.bot = bot

    async def send_messages(self, messages: list[Message], chat_context: ChatContext):
        response = "\n".join([message.content for message in messages])
        await self.bot.send_message(
            chat_id=chat_context.chat_id,
            text=response
        )