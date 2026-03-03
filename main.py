import os
from dotenv import load_dotenv
from core.message_service import MessageService
from adapters.telegram_adapter import TelegamBotAdapter

load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')
if not TOKEN:
    raise RuntimeError("Token not found")

service = MessageService()
bot = TelegamBotAdapter(service)
bot.run(TOKEN)