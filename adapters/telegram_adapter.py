from telegram import Update # pip install python-telegram-bot==20.7
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters, CallbackContext
from ports import BotMessagePort

class TelegamBotAdapter:
    def __init__(self, bot_message_port: BotMessagePort):
        self.bot_message_port = bot_message_port

    async def on_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        messages = self.bot_message_port.handle_message(text)

        response = "\n".join(messages)
        await update.message.reply_text(response)

    def run(self, token: str):
        app = ApplicationBuilder().token(token).build()
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.on_update))
        app.run_polling()