import re

from typing import List, Optional
from collections import Counter

from config import Config
from domain.interfaces.image_processing_interface import ImageProcessingInterface
from domain.interfaces.ocr_reading_interface import OcrReadingInterface
from domain.interfaces.price_extraction_interface import PriceExtractionInterface
from domain.interfaces.text_analyzing_interface import TextAnalyzingInterface


class PriceExtractionService(PriceExtractionInterface):
    num_like = re.compile(r"[0-9OIlS,.]+")

    def __init__(self, ocr_reader: OcrReadingInterface, image_processor: ImageProcessingInterface, text_analyzer: TextAnalyzingInterface, config: type[Config]):
        self.reader = ocr_reader
        self.image_processor = image_processor
        self.text_analyzer = text_analyzer
        self. config = config

    def extract_obvious_prices(self, line):
        candidates = self.num_like.findall(line)
        prices = []

        for c in candidates:
            norm = self.normalize_number_token(c)
            if re.fullmatch(r"\d{1,4}\.\d{2}", norm):
                prices.append(float(norm))

        return prices

    def normalize_number_token(self, token: str) -> str:
        token = (token
                 .replace("O", "0")
                 .replace("o", "0")
                 .replace("I", "1")
                 .replace("l", "1")
                 .replace("S", "5")
                 .replace(",", ".")
                 )

        token = re.sub(r"(\d)\s\.\s(\d)", r"\1.\2", token)
        token = re.sub(r"(\d)\.\s(\d)", r"\1.\2", token)
        token = re.sub(r"(\d)\s\.(\d)", r"\1.\2", token)

        token = re.sub(r"(?<=\d)\s+(?=\d)", ".", token)

        return token

    def extract_not_so_obvious_prices(self, line):
        candidates = self.num_like.findall(line)

        for c in candidates:
            norm = self.normalize_number_token(c)
            if re.fullmatch(r"\d{1,4}\.\d{2}", norm):
                line = re.sub(c, "", line)

        line = self.normalize_number_token(line)
        return self.extract_obvious_prices(line)

    def extract_price_from_list(self, strings: List[str]) -> Optional[str]:
        if not strings:
            return None

        counter = Counter(strings)
        return counter.most_common(1)[0][0]

    def extract_price_from_picture(self, picture):
        possible_payments = []

        text_matrix = self.reader.read_text(picture)
        lines_of_document = self.text_analyzer.get_all_lines(text_matrix)
        relevant_lines = self.text_analyzer.get_relevant_lines(lines_of_document)
        for line in relevant_lines:
            possible_payments = possible_payments + self.extract_obvious_prices(line)
            possible_payments = possible_payments + self.extract_not_so_obvious_prices(line)
        price = self.extract_price_from_list(possible_payments)

        return price

    def extract_price(self, photo: bytearray) -> Optional[float]:
        photo = bytes(photo)
        price = self.extract_price_from_picture(photo)
        if price is None:
            picture_processed = self.image_processor.preprocess(photo)
            price = self.extract_price_from_picture(picture_processed)

        return float(price) if price is not None else None