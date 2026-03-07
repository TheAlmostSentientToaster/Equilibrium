from telegram import Update # pip install python-telegram-bot==20.7
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from application.ports import InputMessagePort, OutputMessagePort
from domain.message import Message
from domain.chat_context import ChatContext

class TelegramInboundAdapter(InputMessagePort):
    def __init__(self, message_service, photo_service, application):
        self.message_service = message_service
        self.photo_service = photo_service
        self.application = application

    async def on_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.photo:
            photo = update.message.photo[-1]
            file = await context.bot.get_file(photo.file_id)
            photo_bytes = await file.download_as_bytearray()
            user = update.message.from_user.first_name
            chat_context = ChatContext(chat_id=update.message.chat_id)
            await self.receive_photo(photo_bytes, user, chat_context)
        else:
            content = update.message.text
            user = update.message.from_user.first_name
            chat_context = ChatContext(chat_id=update.message.chat_id)
            await self.receive_message(content, user, chat_context)

    async def receive_photo(self, photo_data: bytearray, user: str, chat_context: ChatContext):
        await self.photo_service(photo_data, user, chat_context)

    async def receive_message(self, content:str, user:str, chat_context:ChatContext):
        await self.message_service(content=content, user=user, chat_context=chat_context)

class TelegramOutboundAdapter(OutputMessagePort):
    def __init__(self, bot):
        self.bot = bot

    async def send_messages(self, messages: list[Message], chat_context: ChatContext):
        response = "\n".join([message.content for message in messages])
        await self.bot.send_message(
            chat_id=chat_context.chat_id,
            text=response
        )