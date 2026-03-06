import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MESSAGES_DB_PATH = os.getenv('MESSAGES_DB_PATH')
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')