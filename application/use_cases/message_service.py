from application.ports import MessagePort

class MessageService(MessagePort):
    def __init__(self):
        self._messages: list[str] = []

    def handle_message(self, text: str) -> list[str]:
        self._messages.append(text)
        return self._messages