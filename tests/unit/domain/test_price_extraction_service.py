import pytest
from unittest.mock import Mock

from domain.domain_services.price_extraction_service import PriceExtractionService
from domain.bill_line import BillLine
from domain.interfaces.ocr_reading_interface import OcrReadingInterface
from domain.interfaces.image_processing_interface import ImageProcessingInterface
from domain.interfaces.text_analyzing_interface import TextAnalyzingInterface
from config import Config


class TestPriceExtractionService:
    
    @pytest.fixture
    def mock_ocr_reader(self):
        return Mock(spec=OcrReadingInterface)
    
    @pytest.fixture
    def mock_image_processor(self):
        return Mock(spec=ImageProcessingInterface)
    
    @pytest.fixture
    def mock_text_analyzer(self):
        return Mock(spec=TextAnalyzingInterface)
    
    @pytest.fixture
    def mock_config(self):
        config = Mock(spec=Config)
        config.KEYWORDS_FOR_PRICE_SEARCH = "zu zahlen,summe,gesamt,total,betrag"
        return config
    
    @pytest.fixture
    def price_service(self, mock_ocr_reader, mock_image_processor, mock_text_analyzer, mock_config):
        return PriceExtractionService(
            ocr_reader=mock_ocr_reader,
            image_processor=mock_image_processor,
            text_analyzer=mock_text_analyzer,
            config=mock_config
        )

    def test_extract_prices_from_line_with_valid_prices(self, price_service):
        line = BillLine(line="Summe 12.34 netto 5,67", key_words=["summe"], numbers=[])
        
        new_line = price_service.extract_prices_from_line(line)
        
        assert len(new_line.numbers) == 2
        assert 12.34 in new_line.numbers
        assert 5.67 in new_line.numbers

    def test_extract_prices_from_line_with_invalid_prices(self, price_service):
        line = BillLine(line="Summe 12345.67 netto 65.674", key_words=[], numbers=[])
        
        new_line = price_service.extract_prices_from_line(line)
        
        assert len(new_line.numbers) == 0

    def test_extract_prices_from_line_with_bad_content(self, price_service):
        line = BillLine(line="Zu zahlen: 11 50", key_words=[], numbers=[])

        new_line = price_service.extract_prices_from_line(line)

        assert len(new_line.numbers) == 0
        assert 11.50 not in new_line.numbers

    def test_normalize_number_token_replaces_letters(self, price_service):
        result = price_service.normalize_number_token("OIlS")
        assert result == "0115"

    def test_normalize_number_token_replaces_lowercase_letters(self, price_service):
        result = price_service.normalize_number_token("ols")
        assert result == "015"

    def test_normalize_number_token_replaces_comma_with_dot(self, price_service):
        result = price_service.normalize_number_token("12,34")
        assert result == "12.34"

    def test_normalize_spaces_handles_spaces_around_dot(self, price_service):
        result = price_service.normalize_spaces("12 . 34")
        assert result == "12.34"

    def test_normalize_spaces_handles_space_after_dot(self, price_service):
        result = price_service.normalize_spaces("12. 34")
        assert result == "12.34"

    def test_normalize_spaces_handles_space_before_dot(self, price_service):
        result = price_service.normalize_spaces("12 .34")
        assert result == "12.34"

    def test_normalize_spaces_handles_spaces_between_digits(self, price_service):
        result = price_service.normalize_spaces("12 34")
        assert result == "12.34"

    def test_orchestrate_price_extraction_from_lines_in_complex_case(self, price_service):
        lines = [
            BillLine(line="Total 12 54 after Il S4", key_words=["total"], numbers=[]),
            BillLine(line="Summe 33.47 dramalama", key_words=["summe"], numbers=[]),
            BillLine(line="Hier gibt es keine Zahlungen.", key_words=[], numbers=[])
        ]

        resulting_lines = price_service.orchestrate_price_extraction_from_lines(lines)

        assert len(resulting_lines) == 2
        assert len(resulting_lines[0]) == 2
        assert resulting_lines[1] == False
        assert len(resulting_lines[0][0].numbers) == 2
        assert len(resulting_lines[0][1].numbers) == 1

    def test_extract_price_from_list_empty_list(self, price_service):
        result = price_service.extract_price_from_list([])
        assert result is None

    def test_extract_price_from_list_single_suspicious_line_single_number(self, price_service):
        line = BillLine(line="zu zahlen 12.34", key_words=["zu zahlen"], numbers=[12.34])
        result = price_service.extract_price_from_list([line])
        assert result == 12.34

    def test_extract_price_from_list_single_suspicious_line_two_numbers(self, price_service):
        line = BillLine(line="zu zahlen 12.34 56.78", key_words=["zu zahlen"], numbers=[12.34, 56.78])
        result = price_service.extract_price_from_list([line])
        assert result == "56.78"

    def test_extract_price_from_list_multiple_lines_most_common(self, price_service):
        line1 = BillLine(line="Total 12.34", key_words=[], numbers=[12.34])
        line2 = BillLine(line="Subtotal 12.34", key_words=[], numbers=[12.34])
        line3 = BillLine(line="Tax 5.67", key_words=[], numbers=[5.67])
        result = price_service.extract_price_from_list([line1, line2, line3])
        assert result == "12.34"

    def test_extract_price_from_list_no_suspicious_lines(self, price_service):
        line1 = BillLine(line="Item 9.99", key_words=[], numbers=[9.99])
        line2 = BillLine(line="Item 14.99", key_words=[], numbers=[14.99])
        line3 = BillLine(line="Item 9.99", key_words=[], numbers=[9.99])
        result = price_service.extract_price_from_list([line1, line2, line3])
        assert result == "9.99"

    def test_biggest_single_number(self, price_service):
        result = price_service.biggest([12.34])
        assert result == 12.34

    def test_biggest_multiple_numbers(self, price_service):
        result = price_service.biggest([12.34, 56.78, 34.56])
        assert result == 56.78

    def test_biggest_negative_numbers(self, price_service):
        result = price_service.biggest([-12.34, -5.67, -34.56])
        assert result == -5.67

    def test_extract_price_from_picture_success(self, price_service, mock_ocr_reader, mock_text_analyzer):
        picture_data = b"fake_image_data"
        text_matrix = [{"text": "Total 12.34"}]
        lines = ["Total 12.34"]
        bill_lines = [BillLine(line="Total 12.34", key_words=[], numbers=[12.34])]
        
        mock_ocr_reader.read_text.return_value = text_matrix
        mock_text_analyzer.get_all_lines.return_value = lines
        mock_text_analyzer.get_relevant_lines.return_value = bill_lines
        
        result = price_service.extract_price_from_picture(picture_data)
        
        assert result == "12.34"
        mock_ocr_reader.read_text.assert_called_once_with(picture_data)
        mock_text_analyzer.get_all_lines.assert_called_once_with(text_matrix)
        mock_text_analyzer.get_relevant_lines.assert_called_once_with(lines)

    def test_extract_price_from_picture_no_prices(self, price_service, mock_ocr_reader, mock_text_analyzer):
        picture_data = b"fake_image_data"
        text_matrix = [{"text": "No prices here"}]
        lines = ["No prices here"]
        bill_lines = [BillLine(line="No prices here", key_words=[], numbers=[])]
        
        mock_ocr_reader.read_text.return_value = text_matrix
        mock_text_analyzer.get_all_lines.return_value = lines
        mock_text_analyzer.get_relevant_lines.return_value = bill_lines
        
        result = price_service.extract_price_from_picture(picture_data)
        
        assert result is None

    def test_coordinate_price_search_success_first_attempt(self, price_service, mock_ocr_reader, mock_text_analyzer):
        photo = bytearray(b"fake_image_data")
        text_matrix = [{"text": "Total 25.50"}]
        lines = ["Total 25.50"]
        bill_lines = [BillLine(line="Total 25.50", key_words=[], numbers=[25.50])]
        
        mock_ocr_reader.read_text.return_value = text_matrix
        mock_text_analyzer.get_all_lines.return_value = lines
        mock_text_analyzer.get_relevant_lines.return_value = bill_lines
        
        result = price_service.coordinate_price_search(photo)
        
        assert result == 25.50
        mock_ocr_reader.read_text.assert_called_once()

    def test_coordinate_price_search_no_price_found(self, price_service, mock_ocr_reader, mock_text_analyzer, mock_image_processor):
        photo = bytearray(b"fake_image_data")
        processed_photo = b"processed_image_data"
        
        mock_ocr_reader.read_text.return_value = None
        mock_image_processor.preprocess.return_value = processed_photo
        mock_text_analyzer.get_all_lines.return_value = []
        mock_text_analyzer.get_relevant_lines.return_value = []
        
        result = price_service.coordinate_price_search(photo)
        
        assert result is None

    def test_coordinate_price_search_returns_float(self, price_service, mock_ocr_reader, mock_text_analyzer):
        photo = bytearray(b"fake_image_data")
        text_matrix = [{"text": "Total 45.75"}]
        lines = ["Total 45.75"]
        bill_lines = [BillLine(line="Total 45.75", key_words=[], numbers=[45.75])]
        
        mock_ocr_reader.read_text.return_value = text_matrix
        mock_text_analyzer.get_all_lines.return_value = lines
        mock_text_analyzer.get_relevant_lines.return_value = bill_lines
        
        result = price_service.coordinate_price_search(photo)
        
        assert isinstance(result, float)
        assert result == 45.75

    def test_initialization(self, mock_ocr_reader, mock_image_processor, mock_text_analyzer, mock_config):
        service = PriceExtractionService(
            ocr_reader=mock_ocr_reader,
            image_processor=mock_image_processor,
            text_analyzer=mock_text_analyzer,
            config=mock_config
        )
        
        assert service.reader == mock_ocr_reader
        assert service.image_processor == mock_image_processor
        assert service.text_analyzer == mock_text_analyzer
        assert service.config == mock_config