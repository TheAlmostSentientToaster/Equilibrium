from application.ports import UserVerificationPort, OutputMessagePort, RepositoryPort
from application.use_cases.base_service import BaseService
from domain.chat_context import ChatContext
from domain.interfaces.comparison_interface import ComparisonInterface
from domain.message import Message


class UserVerificationService(UserVerificationPort, BaseService):
    def __init__(self, output_message_port: OutputMessagePort, comparison_interface: ComparisonInterface, repository_port: RepositoryPort):
        BaseService.__init__(self, output_message_port, repository_port)
        self.output_message_port = output_message_port
        self.comparison_interface = comparison_interface

    async def verify_user(self, user_id: int, chat_context: ChatContext) -> bool:
        if self.comparison_interface.verify(value_to_compare=user_id):
            return True
        else:
            await self.send_message("Access denied", chat_context)
            return False