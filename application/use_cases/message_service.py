from application.ports import MessagePort, RepositoryPort
from Domain.Message import Message

class MessageService(MessagePort):
    def __init__(self, repository_port: RepositoryPort):
        self._messages: list[str] = []
        self.repository_port = repository_port

    def handle_message(self, content: str, user: str) -> list[str]:
        message = Message(id=None, content=content, user=user)
        self.repository_port.save_message(message)
        return self.repository_port.get_all_messages()