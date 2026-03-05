from telegram import Update # pip install python-telegram-bot==20.7
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from application.ports import InputMessagePort, OutputMessagePort
from Domain.Message import Message
from Domain.ChatContext import ChatContext

class TelegramInboundAdapter(InputMessagePort):
    def __init__(self, receive_message_service, application):
        self.receive_message_service = receive_message_service
        self.application = application

    async def on_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        content = update.message.text
        user = update.message.from_user.first_name
        chat_context = ChatContext(chat_id=update.message.chat_id)
        await self.receive_message(content, user, chat_context)

    #def run(self, token: str):
    #    app = ApplicationBuilder().token(token).build()
    #    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.on_update))
    #    app.run_polling()

    async def receive_message(self, content:str, user:str, chat_context:ChatContext):
        await self.receive_message_service(content=content, user=user, chat_context=chat_context)

class TelegramOutboundAdapter(OutputMessagePort):
    def __init__(self, bot):
        self.bot = bot

    async def send_messages(self, messages: list[Message], chat_context: ChatContext):
        response = "\n".join([message.content for message in messages])
        await self.bot.send_message(
            chat_id=chat_context.chat_id,
            text=response
        )