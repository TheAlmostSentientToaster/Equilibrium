from config import Config
from domain.interfaces.text_analyzing_interface import TextAnalyzingInterface
from rapidfuzz import fuzz

class TextAnalyzingService(TextAnalyzingInterface):
    def __init__(self, config: type[Config]):
        self.config = config

    def overlap_satisfied(self, a, b):
        height_a = a[0][3][1] - a[0][0][1]
        height_b = b[0][3][1] - b[0][0][1]
        overlap = a[0][3][1] - b[0][0][1]

        if overlap > height_a / 2 or overlap > height_b / 2:
            return True
        else:
            return False

    def get_all_lines(self, text_matrix):
        lines = []
        current_line = "" + text_matrix[0][1]

        for i in range(len(text_matrix)):
            if i + 1 == len(text_matrix):
                current_line = current_line + " " + text_matrix[i][1]
                lines.append(current_line)
                break

            if self.overlap_satisfied(text_matrix[i], text_matrix[i + 1]):
                current_line = current_line + " " + text_matrix[i][1]
            else:
                current_line = current_line + " " + text_matrix[i][1]
                lines.append(current_line)
                current_line = ""

        return lines

    def get_relevant_lines(self, lines_of_document):
        keywords = self.config.KEYWORDS_FOR_PRICE_SEARCH.split(',')
        relevant_lines = []

        for line in lines_of_document:
            for kw in keywords:
                if fuzz.partial_ratio(kw.casefold(), line.casefold()) > 75:
                    relevant_lines.append(line)

        return relevant_lines