import easyocr

from typing import Any
from domain.interfaces.ocr_reading_interface import OcrReadingInterface


class OcrReadingService(OcrReadingInterface):
    def __init__(self, reader: easyocr.Reader):
        self.reader = reader

    def read_text(self, photo: bytearray) -> list[dict[str, Any]]:
        return self.reader.readtext(photo)