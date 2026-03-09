from abc import ABC, abstractmethod


class ImageProcessingInterface(ABC):
    @abstractmethod
    def preprocess(self, photo: bytes):
        pass