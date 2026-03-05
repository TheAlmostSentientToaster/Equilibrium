from telegram import Update # pip install python-telegram-bot==20.7
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from application.ports import InputMessagePort, OutputMessagePort

class TelegramAdapter:
    def __init__(self, input_message_port: InputMessagePort, output_message_port: OutputMessagePort):
        self.input_message_port = input_message_port
        self.output_message_port = output_message_port

    async def on_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        content = update.message.text
        user = update.message.from_user.first_name

        self.input_message_port.receive_message(content, user)

        messages = self.output_message_port.send_messages()
        response = "\n".join(messages)
        await update.message.reply_text(response)

    def run(self, token: str):
        app = ApplicationBuilder().token(token).build()
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.on_update))
        app.run_polling()