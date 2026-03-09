from domain.chat_context import ChatContext
from application.ports import OutputMessagePort, RepositoryPort
from domain.photo import Photo
from domain.message import Message
from domain.domain_services.price_extraction_service import PriceExtractionService


class PhotoService:
    def __init__(self, repository_port: RepositoryPort, output_message_port: OutputMessagePort, price_extraction_service: PriceExtractionService):
        self.repository_port = repository_port
        self.output_message_port = output_message_port
        self.price_extraction_service = price_extraction_service

    async def receive_photo(self, photo: bytearray, user: str, chat_context: ChatContext):
        bill = Photo(id=None, photo=photo, user=user)
        self.repository_port.save_photo(bill)
        price = self.price_extraction_service.extract_price(bill.photo)
        if price:
            message = "You just payed " + str(price)
        else:
            message = 'Something went wrong here'
        await self.send_message(message, chat_context)

    async def send_message(self, message: str, chat_context: ChatContext):
        message = Message(id=None, content=message, user= None)
        messages = [message]
        await self.output_message_port.send_messages(messages=messages, chat_context=chat_context)