from application.ports import OutputMessagePort, RepositoryPort
from domain.chat_context import ChatContext
from domain.message import Message

class BaseService:
    def __init__(self, output_message_port: OutputMessagePort, repository_port: RepositoryPort):
        self.output_message_port = output_message_port
        self.repository_port = repository_port

    async def send_message(self, message: str, chat_context: ChatContext):
        message = Message(message_id=None, content=message, user_id= None, user_name=None)
        messages = [message]
        await self.output_message_port.send_messages(messages=messages, chat_context=chat_context)

    async def send_broadcast(self, message: Message, exceptions: list[int]):
        users = self.repository_port.get_all_users()

        for exception in exceptions:
            users.remove(exception)
        await self.output_message_port.send_broadcast([message], users)