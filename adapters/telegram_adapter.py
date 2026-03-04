from telegram import Update # pip install python-telegram-bot==20.7
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from application.ports import MessagePort

class TelegramAdapter:
    def __init__(self, message_port: MessagePort):
        self.message_port = message_port

    async def on_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        messages = self.message_port.handle_message(text)

        response = "\n".join(messages)
        await update.message.reply_text(response)

    def run(self, token: str):
        app = ApplicationBuilder().token(token).build()
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.on_update))
        app.run_polling()