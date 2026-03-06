from Domain.ChatContext import ChatContext
from application.ports import OutputMessagePort, InputMessagePort, RepositoryPort
from Domain.Message import Message

class MessageService:
    def __init__(self, repository_port: RepositoryPort, output_message_port: OutputMessagePort):
        self.repository_port = repository_port
        self.output_message_port = output_message_port

    async def receive_message(self, content: str, user: str, chat_context: ChatContext):
        message = Message(id=None, content=content, user=user)
        self.repository_port.save_message(message)
        await self.send_messages(chat_context)

    async def send_messages(self, chat_context: ChatContext):
        messages = self.repository_port.get_all_messages()
        await self.output_message_port.send_messages(messages=messages, chat_context=chat_context)