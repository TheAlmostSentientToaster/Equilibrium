from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from application.ports import InputMessagePort
from domain.chat_context import ChatContext

import base64


class MessageRequest(BaseModel):
    content: str
    user_id: int
    user_name: str
    chat_id: int

class PhotoRequest(BaseModel):
    photo_data: str
    user_id: int
    user_name: str
    chat_id: int

class WebServer:
    def __init__(self, mobile_inbound_adapter: InputMessagePort):
        self.mobile_inbound_adapter = mobile_inbound_adapter
        self.app = FastAPI()
        self.app.post("/message")(self.receive_message)
        self.app.post("/command")(self.receive_command)
        self.app.post("/photo")(self.receive_photo)

    async def receive_message(self, request: MessageRequest):
        await self.mobile_inbound_adapter.receive_message(request.content, request.user_id, request.user_name, ChatContext(request.chat_id))
        return {"status": "success", "message": "Message received"}

    async def receive_command(self, request: MessageRequest):
        await  self.mobile_inbound_adapter.receive_command(request.content, request.user_id, request.user_name, ChatContext(request.chat_id))
        return {"status": "success", "message": "Command received"}

    async def receive_photo(self, request: PhotoRequest):
        try:
            photo_bytes = bytearray(base64.b64decode(request.photo_data))
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid base64 data")

        await  self.mobile_inbound_adapter.receive_photo(photo_bytes, request.user_id, request.user_name, ChatContext(request.chat_id))
        return {"status": "success", "message": "Photo received"}