from dataclasses import dataclass
from typing import Optional


@dataclass
class Photo:
    id: Optional[int]
    photo: bytearray
    user: Optional[str]