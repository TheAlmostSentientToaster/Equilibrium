import os
from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import ApplicationBuilder, MessageHandler, filters

from application.use_cases.message_services import MessageService
from adapters.telegram_adapters import TelegramOutboundAdapter, TelegramInboundAdapter
from adapters.db_adapter import DbAdapter

load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')
if not TOKEN:
    raise RuntimeError("Token not found")

db_adapter = DbAdapter()
app = ApplicationBuilder().token(TOKEN).build()
bot = Bot(token=TOKEN)

telegram_outbound_adapter = TelegramOutboundAdapter(bot)

message_service = MessageService(repository_port=db_adapter, output_message_port=telegram_outbound_adapter)

telegram_inbound_adapter = TelegramInboundAdapter(message_service.receive_message, app)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_inbound_adapter.on_update))
app.run_polling()