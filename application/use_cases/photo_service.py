from domain.chat_context import ChatContext
from application.ports import OutputMessagePort, RepositoryPort
from domain.photo import Photo
from domain.message import Message


def extract_price() -> float:
    # to be implemented
    return 2.50


class PhotoService:
    def __init__(self, repository_port: RepositoryPort, output_message_port: OutputMessagePort):
        self.repository_port = repository_port
        self.output_message_port = output_message_port

    async def receive_photo(self, photo: bytearray, user: str, chat_context: ChatContext):
        bill = Photo(id=None, photo=photo, user=user)
        self.repository_port.save_photo(bill)
        price = extract_price()
        message = "You just payed " + str(price)
        await self.send_message(message, chat_context)

    async def send_message(self, message: str, chat_context: ChatContext):
        message = Message(id=None, content=message, user= None)
        messages = [message]
        await self.output_message_port.send_messages(messages=messages, chat_context=chat_context)