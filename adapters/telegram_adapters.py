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
        self.message_service = message_service
        self.photo_service = photo_service
        self.command_service = command_service
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
                command_parts = [command_text[1:]]

                await self.receive_command(command_parts[0], user_id, user_name, chat_context)
            else:
                content = update.message.text
                await self.receive_message(content, user_id, user_name, chat_context)

    async def receive_photo(self, photo_data: bytearray, user_id: int, user_name: str, chat_context: ChatContext):
        await self.photo_service.receive_photo(photo=photo_data, user_id=user_id, user_name=user_name, chat_context=chat_context)

    async def receive_message(self, content:str, user_id:int, user_name: str, chat_context:ChatContext):
        await self.message_service.receive_message(Message(message_id=None, content=content, user_id=user_id, user_name=user_name), chat_context=chat_context)

    async def receive_command(self, content:str, user_id: int, user_name: str, chat_context: ChatContext):
        content_split = content.split()
        content_split[1] = content_split[1].replace(',', '.')
        content = " ".join(content_split)
        await self.command_service.handle_command(command=Command(content, user_id, user_name), chat_context=chat_context)


class TelegramOutboundAdapter(OutputMessagePort):
    def __init__(self, bot):
        self.bot = bot

    async def send_messages(self, messages: list[Message], chat_context: ChatContext):
        response = "\n".join([message.content for message in messages])
        await self.bot.send_message(
            chat_id=chat_context.chat_id,
            text=response
        )

    async def send_broadcast(self, messages: list[Message], users: list[int]):
        for user in users:
            await self.send_messages(messages, ChatContext(user))

    async def send_image(self, image_path: str, chat_context: ChatContext):
        await self.bot.send_photo(
            chat_id=chat_context.chat_id,
            photo=image_path
        )