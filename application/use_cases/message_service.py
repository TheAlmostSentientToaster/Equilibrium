from application.ports import MessagePort, RepositoryPort


class MessageService(MessagePort):
    def __init__(self, repository_port=RepositoryPort):
        self._messages: list[str] = []

    def handle_message(self, text: str) -> list[str]:
        self._messages.append(text)
        return self._messages