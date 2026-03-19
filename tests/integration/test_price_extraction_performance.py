import logging
import easyocr
import pytest
import os
from datetime import datetime

from config import Config
from domain.domain_services.image_processing_service import ImageProcessingService
from domain.domain_services.ocr_reading_service import OcrReadingService
from domain.domain_services.price_extraction_service import PriceExtractionService
from domain.domain_services.text_analyzing_service import TextAnalyzingService

@pytest.fixture(scope="session", autouse=True)
def configure_logging():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"tests/logs/performance_test_{timestamp}.log"

    os.makedirs("tests/logs", exist_ok=True)

    # Get root logger and configure directly
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Clear existing handlers
    logger.handlers.clear()

    # Add file and stream handlers
    file_handler = logging.FileHandler(log_file, mode='w')
    stream_handler = logging.StreamHandler()

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

@pytest.fixture(scope="session")
def test_database():
    import sqlite3
    from pathlib import Path

    project_root = Path(__file__).parent.parent.parent
    db_path = project_root / Config.IMAGE_TESTING_DB_PATH

    conn = sqlite3.connect(str(db_path))
    yield conn
    conn.close()

@pytest.fixture
def get_testing_images_paths_and_features(test_database) -> list[tuple[str, float]]:
    cursor = test_database.cursor()
    cursor.execute("SELECT Image_path, Sum FROM Images")
    database_results = cursor.fetchall()
    return database_results

@pytest.fixture
def price_extraction_service() -> PriceExtractionService:
    reader = easyocr.Reader(['de'])
    ocr_service = OcrReadingService(reader)
    image_processor = ImageProcessingService()
    config = Config()
    text_analyzer = TextAnalyzingService(config)

    return PriceExtractionService(
        ocr_reader=ocr_service,
        image_processor=image_processor,
        text_analyzer=text_analyzer,
        config=config
    )

class TestPriceExtractionPerformance:
    def test_price_extraction_service(self, price_extraction_service, get_testing_images_paths_and_features, configure_logging):
        logger = logging.getLogger(__name__)
        logger.info("=== Test Starting ===")

        paths_and_features = get_testing_images_paths_and_features
        paths_count = len(paths_and_features)
        logger.info(f"Found {paths_count} paths. Processing.")

        successful_extractions = 0
        failed_extractions = 0
        failed_cases = []

        for path, feature in paths_and_features:
            image = self.get_testing_image(path)
            price = price_extraction_service.coordinate_price_search(image)

            if price == feature:
                successful_extractions += 1
            else:
                failed_extractions += 1
                failed_cases.append({
                    'path': path,
                    'expected': feature,
                    'actual': price
                })

        success_rate = (successful_extractions / paths_count) * 100
        failure_rate = (failed_extractions / paths_count) * 100

        logger.info(f"Total tests: {paths_count}")
        logger.info(f"Successful extractions: {successful_extractions} ({success_rate:.2f}%)")
        logger.info(f"Failed extractions: {failed_extractions} ({failure_rate:.2f}%)")

        if failed_cases:
            logger.info("Failed cases:")
            for case in failed_cases[:10]:
                logger.info(f"  Path: {case['path']}")
                logger.info(f"  Expected: {case['expected']}, Actual: {case['actual']}")

            if len(failed_cases) > 10:
                logger.info(f"  ... and {len(failed_cases) - 10} more failed cases")

    def get_testing_image(self, path: str) -> bytearray:
        with open(path, 'rb') as f:
            image = f.read()
        return bytearray(image)