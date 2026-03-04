import os
from dotenv import load_dotenv
from application.use_cases.message_service import MessageService
from adapters.telegram_adapter import TelegramAdapter

load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')
if not TOKEN:
    raise RuntimeError("Token not found")

service = MessageService()
bot = TelegramAdapter(service)
bot.run(TOKEN)