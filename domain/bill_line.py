from dataclasses import dataclass
from typing import Optional


@dataclass
class BillLine:
    line: str
    key_words: list[str]
    numbers: list[float]