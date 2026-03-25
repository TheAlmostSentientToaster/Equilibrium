import pytest

from domain.domain_services.comparison_service import ComparisonService


class TestComparisonService:

    def test_comparison_service_with_valid_input(self):
        service = ComparisonService("456,789")
        assert service.verify(456) == True

    def test_comparison_service_with_invalid_value(self):
        service = ComparisonService("456,789")
        assert service.verify(101112) is False

    def test_empty_string_input(self):
        service = ComparisonService("")
        assert service.verify(123) is False

    def test_malformed_input(self):
        with pytest.raises(ValueError):
            ComparisonService("123,abc,456")

    def test_duplicate_values(self):
        service = ComparisonService("123,123,456")
        assert service.verify(123) is True

    def test_whitespace_handling(self):
        service = ComparisonService(" 123 , 456 , 789 ")
        assert service.verify(123) is True