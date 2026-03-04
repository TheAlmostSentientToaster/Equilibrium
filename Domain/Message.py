from dataclasses import dataclass
from typing import Optional


@dataclass
class Message:
    id: Optional[int]
    content: str
    user: Optional[str]
