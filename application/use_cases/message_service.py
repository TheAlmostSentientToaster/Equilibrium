from application.ports import OutputMessagePort, InputMessagePort, RepositoryPort
from Domain.Message import Message

class ReceiveMessageService(InputMessagePort):
    def __init__(self, repository_port: RepositoryPort):
        self.repository_port = repository_port

    def receive_message(self, content: str, user: str):
        message = Message(id=None, content=content, user=user)
        self.repository_port.save_message(message)

class SendMessageService(OutputMessagePort):
    def __init__(self, repository_port: RepositoryPort):
        self.repository_port = repository_port

    def send_messages(self) -> list[Message]:
        return self.repository_port.get_all_messages()