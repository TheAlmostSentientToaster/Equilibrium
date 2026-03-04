from application.ports import RepositoryPort

class DbAdapter:
    def __init__(self, repository_port: RepositoryPort):
        self.repository_port = repository_port

    def get_messages_all(self) -> list[str]:
        pass