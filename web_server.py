from fastapi import FastAPI
from pydantic import BaseModel

from application.ports import InputMessagePort
from domain.chat_context import ChatContext


class MessageRequest(BaseModel):
    content: str
    user_id: int
    user_name: str
    chat_id: int

class WebServer:
    def __init__(self, mobile_inbound_adapter: InputMessagePort):
        self.mobile_inbound_adapter = mobile_inbound_adapter
        self.app = FastAPI()
        self.app.post("/message")(self.receive_message)

    async def receive_message(self, request: MessageRequest):
        await self.mobile_inbound_adapter.receive_message(request.content, request.user_id, request.user_name, ChatContext(request.chat_id))
        return {"status": "success", "message": "Message received"}