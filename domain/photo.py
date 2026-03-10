from dataclasses import dataclass
from typing import Optional


@dataclass
class Photo:
    id: Optional[int]
    photo: bytearray
    user_id: Optional[int]
    sum: Optional[float]
    user_name: Optional[str]