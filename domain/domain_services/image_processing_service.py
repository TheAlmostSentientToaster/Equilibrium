from domain.interfaces.image_processing_interface import ImageProcessingInterface
import cv2
import numpy as np

class ImageProcessingService(ImageProcessingInterface):

    def preprocess(self, photo: bytes):
        np_array = np.frombuffer(photo, np.uint8)
        img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(blur, 255, 1, 1, 11, 10)
        return thresh