from telegram import Update # pip install python-telegram-bot==20.7
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from application.ports import InputMessagePort, OutputMessagePort
from Domain.Message import Message

class TelegramInboundAdapter(InputMessagePort):
    def __init__(self, receive_message_service):
        self.receive_message_service = receive_message_service

    async def on_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        content = update.message.text
        user = update.message.from_user.first_name
        self.receive_message_service(content=content, user=user)

    def run(self, token: str):
        app = ApplicationBuilder().token(token).build()
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.on_update))
        app.run_polling()

class TelegramOutboundAdapter(OutputMessagePort):

        async def send_messages(self):
            messages = self.output_message_port.send_messages()
            response = "\n".join([message.content for message in messages])
            await update.message.reply_text(response)