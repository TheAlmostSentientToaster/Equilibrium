from application.ports import MessagePort, RepositoryPort


class MessageService(MessagePort):
    def __init__(self, repository_port: RepositoryPort):
        self._messages: list[str] = []
        self.repository_port = repository_port

    def handle_message(self, text: str) -> list[str]:
        self.repository_port.save_message(text)
        return self.repository_port.get_all_messages()