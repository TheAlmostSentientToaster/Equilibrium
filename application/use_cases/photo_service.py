from domain.chat_context import ChatContext
from application.ports import OutputMessagePort, RepositoryPort, PhotoServicePort
from domain.interfaces.price_extraction_interface import PriceExtractionInterface
from domain.photo import Photo
from domain.message import Message


class PhotoService(PhotoServicePort):
    def __init__(self, repository_port: RepositoryPort, output_message_port: OutputMessagePort, price_extraction_service: PriceExtractionInterface):
        self.repository_port = repository_port
        self.output_message_port = output_message_port
        self.price_extraction_service = price_extraction_service

    async def receive_photo(self, photo: bytearray, user_id: int, user_name: str, chat_context: ChatContext):
        await self.send_message("Processing your image.",chat_context)

        bill = Photo(id=None, photo=photo, user_id=user_id, sum=None, user_name= user_name)
        price = self.price_extraction_service.coordinate_price_search(bill.photo)
        bill.sum = price

        payment_id = self.repository_port.save_photo(bill)

        if price:
            message = f"You just paid {str(price)}\nPress /X{payment_id} to delete Payment.\nHold /C{payment_id} to change the amount."
        else:
            message = 'Seems we could not find the total sum on the bill'
        await self.send_message(message, chat_context)

        if price:
            message = f"{user_name} just paid {str(price)}€\nPress /D{payment_id} to show it."
            users = self.repository_port.get_all_users()
            users.remove(user_id)
            await self.output_message_port.send_broadcast([Message(None, message, None, None)], users)


    async def send_message(self, message: str, chat_context: ChatContext):
        message = Message(message_id=None, content=message, user_id= None, user_name=None)
        messages = [message]
        await self.output_message_port.send_messages(messages=messages, chat_context=chat_context)