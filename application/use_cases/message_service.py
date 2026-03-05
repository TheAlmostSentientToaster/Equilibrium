from application.ports import OutputMessagePort, InputMessagePort, RepositoryPort
from Domain.Message import Message

class MessageService(InputMessagePort, OutputMessagePort):
    def __init__(self, repository_port: RepositoryPort):
        self._messages: list[str] = []
        self.repository_port = repository_port

    def receive_message(self, content: str, user: str):
        message = Message(id=None, content=content, user=user)
        self.repository_port.save_message(message)

    def send_messages(self):
        return self.repository_port.get_all_messages()