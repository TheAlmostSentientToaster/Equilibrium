import os
from dotenv import load_dotenv
from application.use_cases.message_service import MessageService
from adapters.telegram_adapters import TelegramOutboundAdapter, TelegramInboundAdapter
from adapters.db_adapter import DbAdapter

load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')
if not TOKEN:
    raise RuntimeError("Token not found")

db_adapter = DbAdapter()
message_service = MessageService(repository_port=db_adapter)
bot = TelegramOutboundAdapter(message_service)
bot.run(TOKEN)