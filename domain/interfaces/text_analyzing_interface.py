from abc import ABC, abstractmethod


class TextAnalyzingInterface(ABC):
    @abstractmethod
    def get_all_lines(self, text_matrix):
        pass

    @abstractmethod
    def get_relevant_lines(self, photo: bytes):
        pass