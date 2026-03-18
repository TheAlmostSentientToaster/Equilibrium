import re

from typing import Optional
from collections import Counter

from config import Config
from domain.bill_line import BillLine
from domain.interfaces.image_processing_interface import ImageProcessingInterface
from domain.interfaces.ocr_reading_interface import OcrReadingInterface
from domain.interfaces.price_extraction_interface import PriceExtractionInterface
from domain.interfaces.text_analyzing_interface import TextAnalyzingInterface


class PriceExtractionService(PriceExtractionInterface):
    num_like = re.compile(r"[0-9OIlS,.]+")

    def __init__(self, ocr_reader: OcrReadingInterface, image_processor: ImageProcessingInterface, text_analyzer: TextAnalyzingInterface, config: Config):
        self.reader = ocr_reader
        self.image_processor = image_processor
        self.text_analyzer = text_analyzer
        self. config = config

    def extract_prices_from_line(self, line: BillLine) -> BillLine:
        candidates = self.num_like.findall(line.line)
        new_line = BillLine(line.line, line.key_words, line.numbers)

        for c in candidates:
            norm = self.normalize_number_token(c)
            if re.fullmatch(r"\d{1,4}\.\d{2}", norm):
                new_line.numbers.append(float(norm))
                new_line.line = new_line.line.replace(norm, "|")

        return new_line

    def normalize_number_token(self, token: str) -> str:
        token = (token
                 .replace("O", "0")
                 .replace("o", "0")
                 .replace("I", "1")
                 .replace("l", "1")
                 .replace("S", "5")
                 .replace(",", ".")
                 )
        return token

    def normalize_spaces(self, token: str) -> str:
        token = re.sub(r"(\d)\s\.\s(\d)", r"\1.\2", token)
        token = re.sub(r"(\d)\.\s(\d)", r"\1.\2", token)
        token = re.sub(r"(\d)\s\.(\d)", r"\1.\2", token)

        token = re.sub(r"(?<=\d)\s+(?=\d)", ".", token)

        return token

    #A lot can be improved here
    def extract_price_from_list(self, lines: list[BillLine]) -> Optional[str]:
        if not lines:
            return None

        suspicious_lines = []
        all_numbers =[]

        for line in lines:
            if line.key_words.__contains__("zu zahlen"):
                suspicious_lines.append(line)
            for number in line.numbers:
                all_numbers.append(number)

        if len(suspicious_lines) == 1:
            if len(suspicious_lines[0].numbers) == 1:
                return suspicious_lines[0].numbers[0]
            if len(suspicious_lines[0].numbers) == 2:
                return str(self.biggest(suspicious_lines[0].numbers))

        counter = Counter(all_numbers)
        return counter.most_common(1)[0][0]

    def biggest(self, numbers: list[float]) -> float:
        champion = numbers[0]

        for number in numbers:
            if number > champion:
                champion = number

        return champion

    def extract_price_from_picture(self, picture: bytes) -> Optional[str]:
        possible_payments = []

        text_matrix = self.reader.read_text(picture)
        lines_of_document = self.text_analyzer.get_all_lines(text_matrix)
        relevant_lines = self.text_analyzer.get_relevant_lines(lines_of_document)

        for line in relevant_lines:
            temp_line = line
            line = self.extract_prices_from_line(line)

            line.line = self.normalize_spaces(line.line)
            line = self.extract_prices_from_line(line)

            line.line = self.normalize_number_token(line.line)
            line.line = self.normalize_spaces(line.line)
            line = self.extract_prices_from_line(line)

            line.line = temp_line.line

            if len(line.numbers) > 0:
                possible_payments.append(line)

        price = self.extract_price_from_list(possible_payments)

        return price

    def coordinate_price_search(self, photo: bytearray) -> Optional[float]:
        photo = bytes(photo)
        price = self.extract_price_from_picture(photo)
        if price is None:
            picture_processed = self.image_processor.preprocess(photo)
            price = self.extract_price_from_picture(picture_processed)

        return float(price) if price is not None else None