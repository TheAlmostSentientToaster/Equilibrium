from telegram import Bot
from telegram.ext import ApplicationBuilder, MessageHandler, filters

from application.use_cases.message_services import MessageService
from adapters.telegram_adapters import TelegramOutboundAdapter, TelegramInboundAdapter
from adapters.db_adapter import DbAdapter
from config import Config

TOKEN = Config.TELEGRAM_TOKEN
if not TOKEN:
    raise RuntimeError("Token not found")

app = ApplicationBuilder().token(TOKEN).build()
bot = Bot(token=TOKEN)

db_adapter = DbAdapter()
telegram_outbound_adapter = TelegramOutboundAdapter(bot)
message_service = MessageService(repository_port=db_adapter, output_message_port=telegram_outbound_adapter)
telegram_inbound_adapter = TelegramInboundAdapter(message_service.receive_message, app)

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_inbound_adapter.on_update))
app.run_polling()