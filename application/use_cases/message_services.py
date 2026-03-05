from Domain.ChatContext import ChatContext
from application.ports import OutputMessagePort, InputMessagePort, RepositoryPort
from Domain.Message import Message

class SendMessageService:
    def __init__(self, repository_port: RepositoryPort, output_message_port: OutputMessagePort):
        self.repository_port = repository_port
        self.output_message_port = output_message_port

    async def send_messages(self, chat_context: ChatContext):
        messages = self.repository_port.get_all_messages()
        await self.output_message_port.send_messages(messages=messages, chat_context=chat_context)

class ReceiveMessageService:
    def __init__(self, repository_port: RepositoryPort, send_message_service: SendMessageService):
        self.repository_port = repository_port
        self.send_message_service = send_message_service

    async def receive_message(self, content: str, user: str, chat_context: ChatContext):
        message = Message(id=None, content=content, user=user)
        self.repository_port.save_message(message)
        await self.send_message_service.send_messages(chat_context)