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

    def distance_to_last_key_smaller_then(self, line: BillLine, candidate: str, max_distance: int) -> bool:
        for key in line.key_words:
            key_pos = line.line.lower().find(key.lower())

            if key_pos != -1:
                key_pos += len(key)

            candidate_pos = line.line.find(candidate)

            if key_pos != -1 and candidate_pos != -1:
                distance = candidate_pos - key_pos
                if 0 < distance <= max_distance:
                    return True
        return False

    def no_separator_between(self, line: BillLine, candidate: str, separator: str) -> bool:
        candidate_pos = line.line.find(candidate)
        if candidate_pos == -1:
            print("Candidate not found. That should not happen...")
            return True

        last_key_pos = -1
        for key in line.key_words:
            key_pos = line.line.lower().find(key.lower())
            if key_pos != -1 and last_key_pos < key_pos < candidate_pos:
                last_key_pos = key_pos

        if last_key_pos == -1:
            return False

        start_pos = min(candidate_pos, last_key_pos)
        end_pos = max(candidate_pos, last_key_pos)

        substring_between = line.line[start_pos:end_pos]
        return separator not in substring_between

    def extract_prices_from_line(self, line: BillLine) -> BillLine:
        separator = '|'
        candidates = self.num_like.findall(line.line)
        new_line = BillLine(line.line, line.key_words, line.numbers)

        for candidate in candidates:
            norm = self.normalize_number_token(candidate)

            if (re.fullmatch(r"\d{1,4}\.\d{2}", norm)
                    and self.no_separator_between(line, candidate, separator)):
                if float(norm) not in new_line.numbers:
                    new_line.numbers.append(float(norm))
                new_line.line = new_line.line.replace(norm, separator)

        return new_line

    def normalize_number_token(self, token: str) -> str:
        token = (token
                 .replace("O", "0")
                 .replace("o", "0")
                 .replace("I", "1")
                 .replace("l", "1")
                 .replace("S", "5")
                 .replace("s", "5")
                 .replace(",", ".")
                 )
        return token

    def normalize_spaces(self, token: str) -> str:
        token = re.sub(r"(\d)\s\.\s(\d)", r"\1.\2", token)
        token = re.sub(r"(\d)\.\s(\d)", r"\1.\2", token)
        token = re.sub(r"(\d)\s\.(\d)", r"\1.\2", token)

        token = re.sub(r"(?<=\d)\s+(?=\d)", ".", token)

        return token

    def extract_price_from_list(self, lines: list[BillLine]) -> Optional[str]:
        if not lines:
            return None

        suspicious_lines = []
        all_numbers =[]

        for line in lines:
            lower_key_words = {kw.strip().lower() for kw in line.key_words}
            lower_master_key = self.config.KEYWORDS_FOR_PRICE_SEARCH.split(',')[0].lower()

            if lower_key_words.__contains__(lower_master_key):
                suspicious_lines.append(line)

            for number in line.numbers:
                all_numbers.append(number)

        if len(suspicious_lines) == 1:
            if len(suspicious_lines[0].numbers) == 1:
                return suspicious_lines[0].numbers[0]
            if len(suspicious_lines[0].numbers) == 2:
                return str(self.biggest(suspicious_lines[0].numbers))

        if len(lines) == 1 and len(lines[0].numbers) > 1:
            return str(self.biggest(lines[0].numbers))

        counter = Counter(all_numbers)
        most_common_number = str(counter.most_common(1)[0][0])
        return most_common_number

    def biggest(self, numbers: list[float]) -> float:
        champion = numbers[0]

        for number in numbers:
            if number > champion:
                champion = number

        return champion

    def orchestrate_price_extraction_from_lines(self, lines: list[BillLine]) -> tuple[list[BillLine],bool]:
        possible_payments = []
        call_me_again = False

        for line in lines:
            temp_line = line
            line = self.extract_prices_from_line(line)

            line.line = self.normalize_spaces(line.line)
            line = self.extract_prices_from_line(line)

            line.line = self.normalize_number_token(line.line)
            line.key_words = [self.normalize_number_token(keyword) for keyword in line.key_words]
            line.line = self.normalize_spaces(line.line)
            line = self.extract_prices_from_line(line)

            line.line = temp_line.line
            line.key_words = temp_line.key_words

            line.line = self.normalize_number_token(line.line)
            line.key_words = [self.normalize_number_token(keyword) for keyword in line.key_words]
            line = self.extract_prices_from_line(line)

            line.line = temp_line.line
            line.key_words = temp_line.key_words

            if len(line.numbers) > 0:
                possible_payments.append(line)

            lower_key_words = [keyword.lower() for keyword in line.key_words]
            lower_master_key = self.config.KEYWORDS_FOR_PRICE_SEARCH.split(',')[0].lower()
            if len(line.numbers) < 1 and lower_key_words.__contains__(lower_master_key):
                call_me_again = True

        return possible_payments, call_me_again

    def extract_price_from_picture(self, picture: bytes) -> tuple[Optional[str], bool]:
        text_matrix = self.reader.read_text(picture)
        lines_of_document = self.text_analyzer.get_all_lines(text_matrix)
        relevant_lines = self.text_analyzer.get_relevant_lines(lines_of_document)

        extract = self.orchestrate_price_extraction_from_lines(relevant_lines)
        possible_payments = extract[0]
        call_me_again = extract[1]

        relevant_lines_without_whitespaces = [BillLine(line.line.replace(" ", ""), line.key_words, line.numbers) for line in relevant_lines]
        extracts_without_whitespaces = self.orchestrate_price_extraction_from_lines(relevant_lines_without_whitespaces)
        for line in extracts_without_whitespaces[0]:
            arsch = line.line
            possible_payments.append(line)

        extracted_price = self.extract_price_from_list(possible_payments)
        if extracted_price is not None:
            price = str(extracted_price)
        else:
            price = None

        return price, call_me_again

    def coordinate_price_search(self, photo: bytearray) -> Optional[float]:
        photo = bytes(photo)
        extraction = self.extract_price_from_picture(photo)
        price = extraction[0]

        if price is None or extraction[1]:
            picture_processed = self.image_processor.preprocess(photo)
            price_processed = self.extract_price_from_picture(picture_processed)[0]

            if price_processed is not None:
                price = price_processed

        return float(price) if price is not None else None