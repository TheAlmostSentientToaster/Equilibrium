from dataclasses import dataclass
from typing import Optional

@dataclass
class Command:
    content: str
    user_id: Optional[int]
    user_name: Optional[str]