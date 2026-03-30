import pytest
from unittest.mock import Mock

from domain.domain_services.balance_calculation_service import BalanceCalculationService


class TestBalanceCalculationService:

    def test_calculate_balances_with_equal_deposits(self):
        """Test balance calculation when all users deposited the same amount"""
        mock_repository = Mock()
        mock_repository.get_sums_of_deposits.return_value = [(1, 100.0), (2, 100.0), (3, 100.0)]
        
        service = BalanceCalculationService(mock_repository)
        result = service.calculate_balances()
        
        expected = [(1, 0.0), (2, 0.0), (3, 0.0)]
        assert result == expected
        mock_repository.get_sums_of_deposits.assert_called_once()

    def test_calculate_balances_with_unequal_deposits(self):
        """Test balance calculation with different deposit amounts"""
        mock_repository = Mock()
        mock_repository.get_sums_of_deposits.return_value = [(1, 150.0), (2, 75.0), (3, 75.0)]
        
        service = BalanceCalculationService(mock_repository)
        result = service.calculate_balances()
        
        expected = [(1, 50.0), (2, -25.0), (3, -25.0)]
        assert result == expected

    def test_calculate_balances_with_single_user(self):
        """Test balance calculation with only one user"""
        mock_repository = Mock()
        mock_repository.get_sums_of_deposits.return_value = [(1, 100.0)]
        
        service = BalanceCalculationService(mock_repository)
        result = service.calculate_balances()
        
        expected = [(1, 0.0)]
        assert result == expected

    def test_calculate_balances_with_zero_deposits(self):
        """Test balance calculation when all deposits are zero"""
        mock_repository = Mock()
        mock_repository.get_sums_of_deposits.return_value = [(1, 0.0), (2, 0.0)]
        
        service = BalanceCalculationService(mock_repository)
        result = service.calculate_balances()
        
        expected = [(1, 0.0), (2, 0.0)]
        assert result == expected

    def test_calculate_balances_rounding_behavior(self):
        """Test that balance calculations are properly rounded to 2 decimal places"""
        mock_repository = Mock()
        mock_repository.get_sums_of_deposits.return_value = [(1, 100.333), (2, 100.666)]
        
        service = BalanceCalculationService(mock_repository)
        result = service.calculate_balances()
        
        expected = [(1, -0.17), (2, 0.17)]
        assert result == expected

    def test_calculate_balances_with_large_numbers(self):
        """Test balance calculation with large monetary values"""
        mock_repository = Mock()
        mock_repository.get_sums_of_deposits.return_value = [(1, 10000.0), (2, 5000.0), (3, 15000.0)]
        
        service = BalanceCalculationService(mock_repository)
        result = service.calculate_balances()
        
        expected = [(1, 0.0), (2, -5000.0), (3, 5000.0)]
        assert result == expected

    def test_calculate_balances_with_empty_deposits(self):
        """Test balance calculation when no deposits exist"""
        mock_repository = Mock()
        mock_repository.get_sums_of_deposits.return_value = []
        
        service = BalanceCalculationService(mock_repository)
        
        with pytest.raises(ZeroDivisionError):
            service.calculate_balances()

    def test_calculate_deposits(self):
        """Test that calculate_deposits returns the raw deposits from repository"""
        mock_repository = Mock()
        expected_deposits = [(1, 100.0), (2, 200.0), (3, 150.0)]
        mock_repository.get_sums_of_deposits.return_value = expected_deposits
        
        service = BalanceCalculationService(mock_repository)
        result = service.calculate_deposits()
        
        assert result == expected_deposits
        mock_repository.get_sums_of_deposits.assert_called_once()

    def test_calculate_deposits_empty_list(self):
        """Test calculate_deposits when repository returns empty list"""
        mock_repository = Mock()
        mock_repository.get_sums_of_deposits.return_value = []
        
        service = BalanceCalculationService(mock_repository)
        result = service.calculate_deposits()
        
        assert result == []
        mock_repository.get_sums_of_deposits.assert_called_once()

    def test_service_initialization(self):
        """Test that service is properly initialized with repository port"""
        mock_repository = Mock()
        service = BalanceCalculationService(mock_repository)
        
        assert service.repository_port == mock_repository

    def test_multiple_calculate_balances_calls(self):
        """Test that multiple calls to calculate_balances work correctly"""
        mock_repository = Mock()
        mock_repository.get_sums_of_deposits.return_value = [(1, 100.0), (2, 200.0)]
        
        service = BalanceCalculationService(mock_repository)
        
        # First call
        result1 = service.calculate_balances()
        expected1 = [(1, -50.0), (2, 50.0)]
        assert result1 == expected1
        
        # Second call
        result2 = service.calculate_balances()
        expected2 = [(1, -50.0), (2, 50.0)]
        assert result2 == expected2
        
        # Verify repository was called twice
        assert mock_repository.get_sums_of_deposits.call_count == 2
