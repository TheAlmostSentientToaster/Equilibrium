from domain.chat_context import ChatContext
from application.ports import OutputMessagePort, RepositoryPort, MessageServicePort
from domain.message import Message

class MessageService(MessageServicePort):
    def __init__(self, repository_port: RepositoryPort, output_message_port: OutputMessagePort):
        self.repository_port = repository_port
        self.output_message_port = output_message_port

    async def receive_message(self, message: Message, chat_context: ChatContext):
        self.repository_port.save_message(message)
        await self.send_all_messages(chat_context)

    async def send_all_messages(self, chat_context: ChatContext):
        messages = self.repository_port.get_all_messages()
        await self.output_message_port.send_messages(messages=messages, chat_context=chat_context)