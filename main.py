import easyocr

from telegram import Bot
from telegram.ext import ApplicationBuilder, MessageHandler, filters

from application.use_cases.command_service import CommandService
from application.use_cases.message_service import MessageService
from adapters.telegram_adapters import TelegramOutboundAdapter, TelegramInboundAdapter
from adapters.repository_adapter import DbAdapter
from application.use_cases.photo_service import PhotoService
from application.use_cases.user_verification_service import UserVerificationService
from config import Config
from domain import message
from domain.domain_services.balance_calculation_service import BalanceCalculationService
from domain.domain_services.comparison_service import ComparisonService
from domain.domain_services.image_processing_service import ImageProcessingService
from domain.domain_services.ocr_reading_service import OcrReadingService
from domain.domain_services.price_extraction_service import PriceExtractionService
from domain.domain_services.text_analyzing_service import TextAnalyzingService

config = Config()
config.validate()
TOKEN = config.TELEGRAM_TOKEN

app = ApplicationBuilder().token(TOKEN).build()
bot = Bot(token=TOKEN)
reader = easyocr.Reader([config.OCR_LANGUAGE])

db_adapter = DbAdapter(config.IMAGE_PATH)
telegram_outbound_adapter = TelegramOutboundAdapter(bot)
balance_calculation_service = BalanceCalculationService(db_adapter)
message_service = MessageService(repository_port=db_adapter, output_message_port=telegram_outbound_adapter)
command_service = CommandService(output_message_port=telegram_outbound_adapter, balance_calculation_interface=balance_calculation_service, repository_port=db_adapter, message=message.Message)
ocr_reading_service = OcrReadingService(reader)
image_processing_service = ImageProcessingService()
text_analyzing_service = TextAnalyzingService(config)
comparison_service = ComparisonService(config.USER_WHITELIST)
user_verification_service = UserVerificationService(output_message_port=telegram_outbound_adapter, comparison_interface=comparison_service)
price_extraction_service = PriceExtractionService(ocr_reading_service, image_processing_service, text_analyzing_service, config=config)
photo_service = PhotoService(repository_port=db_adapter, output_message_port=telegram_outbound_adapter, price_extraction_service=price_extraction_service)
telegram_inbound_adapter = TelegramInboundAdapter(message_service, photo_service, application= app, command_service=command_service, user_verification_service=user_verification_service)

app.add_handler(MessageHandler(
    filters.TEXT | filters.PHOTO,
    telegram_inbound_adapter.on_update))
app.run_polling()