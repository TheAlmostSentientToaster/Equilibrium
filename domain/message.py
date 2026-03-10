from dataclasses import dataclass
from typing import Optional


@dataclass
class Message:
    message_id: Optional[int]
    content: str
    user_id: Optional[int]
