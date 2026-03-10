import os
from dotenv import load_dotenv

load_dotenv()

class Config:

    MESSAGES_DB_PATH = os.getenv('MESSAGES_DB_PATH')
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    OCR_LANGUAGE = os.getenv('OCR_LANGUAGE')
    KEYWORDS_FOR_PRICE_SEARCH = os.getenv('KEYWORDS_FOR_PRICE_SEARCH')
    IMAGE_PATH = os.getenv('IMAGES_PATH')

    @classmethod
    def validate(cls):
        if not cls.TELEGRAM_TOKEN:
            raise ValueError("TELEGRAM_TOKEN environment variable is required")
        if not cls.MESSAGES_DB_PATH:
            raise ValueError("MESSAGES_DB_PATH environment variable is required")
        if not cls.OCR_LANGUAGE:
            raise ValueError("OCR_LANGUAGE environment variable is required")
        if not cls.KEYWORDS_FOR_PRICE_SEARCH:
            raise ValueError("KEYWORDS_FOR_PRICE_SEARCH environment variable is required")
        if not cls.IMAGE_PATH:
            raise ValueError("IMAGE_PATH environment variable is required")
