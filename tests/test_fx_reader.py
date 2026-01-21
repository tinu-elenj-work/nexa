"""
Unit tests for FX Rate Reader
"""

import pytest
import pandas as pd
import os
from unittest.mock import Mock, patch, MagicMock
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fx_reader import FXRateReader


class TestFXRateReader:
    """Test cases for FX Rate Reader"""
    
    def test_init_default_path(self):
        """Test initialization with default path"""
        reader = FXRateReader()
        
        assert reader.fx_file_path == "fx/FX.xlsx"
        assert reader.fx_data is None
        assert reader.rates_cache == {}
    
    def test_init_custom_path(self):
        """Test initialization with custom path"""
        custom_path = "custom/fx_rates.xlsx"
        reader = FXRateReader(custom_path)
        
        assert reader.fx_file_path == custom_path
        assert reader.fx_data is None
        assert reader.rates_cache == {}
    
    @patch('pandas.read_excel')
    @patch('os.path.exists')
    def test_load_fx_data_success(self, mock_exists, mock_read_excel):
        """Test successful FX data loading"""
        mock_exists.return_value = True
        mock_read_excel.return_value = pd.DataFrame([
            {
                'Date': '2024-01-01',
                'From_Currency': 'USD',
                'To_Currency': 'ZAR',
                'Rate': 18.5
            }
        ])
        
        reader = FXRateReader()
        result = reader.load_fx_data()
        
        assert result is True
        assert reader.fx_data is not None
        assert len(reader.fx_data) == 1
        mock_read_excel.assert_called_once_with('fx/FX.xlsx', sheet_name='ExchangeRates')
    
    @patch('os.path.exists')
    def test_load_fx_data_file_not_found(self, mock_exists):
        """Test FX data loading when file doesn't exist"""
        mock_exists.return_value = False
        
        reader = FXRateReader()
        result = reader.load_fx_data()
        
        assert result is False
        assert reader.fx_data is None
    
    @patch('pandas.read_excel')
    @patch('os.path.exists')
    def test_load_fx_data_exception(self, mock_exists, mock_read_excel):
        """Test FX data loading with exception"""
        mock_exists.return_value = True
        mock_read_excel.side_effect = Exception("Read error")
        
        reader = FXRateReader()
        result = reader.load_fx_data()
        
        assert result is False
        assert reader.fx_data is None
    
    def test_get_fx_rate_same_currency(self):
        """Test FX rate for same currency"""
        reader = FXRateReader()
        
        result = reader.get_fx_rate('USD', 'USD')
        
        assert result == 1.0
    
    @patch.object(FXRateReader, 'load_fx_data')
    def test_get_fx_rate_load_failure(self, mock_load):
        """Test FX rate retrieval when data loading fails"""
        mock_load.return_value = False
        
        reader = FXRateReader()
        result = reader.get_fx_rate('USD', 'ZAR')
        
        assert result is None
    
    def test_get_fx_rate_cached(self):
        """Test FX rate retrieval from cache"""
        reader = FXRateReader()
        reader.rates_cache['USD_ZAR'] = 18.5
        
        result = reader.get_fx_rate('USD', 'ZAR')
        
        assert result == 18.5
    
    def test_get_fx_rate_from_data(self):
        """Test FX rate retrieval from data"""
        reader = FXRateReader()
        reader.fx_data = pd.DataFrame([
            {
                'Date': '2024-01-01',
                'From_Currency': 'USD',
                'To_Currency': 'ZAR',
                'Rate': 18.5
            },
            {
                'Date': '2024-01-01',
                'From_Currency': 'GBP',
                'To_Currency': 'ZAR',
                'Rate': 23.2
            }
        ])
        
        result = reader.get_fx_rate('USD', 'ZAR')
        
        assert result == 18.5
        assert 'USD_ZAR' in reader.rates_cache
        assert reader.rates_cache['USD_ZAR'] == 18.5
    
    def test_get_fx_rate_not_found(self):
        """Test FX rate retrieval when rate not found"""
        reader = FXRateReader()
        reader.fx_data = pd.DataFrame([
            {
                'Date': '2024-01-01',
                'From_Currency': 'USD',
                'To_Currency': 'ZAR',
                'Rate': 18.5
            }
        ])
        
        result = reader.get_fx_rate('EUR', 'ZAR')
        
        assert result is None
    
    def test_get_fx_rate_multiple_dates(self):
        """Test FX rate retrieval with multiple dates (should use latest)"""
        reader = FXRateReader()
        reader.fx_data = pd.DataFrame([
            {
                'Date': '2024-01-01',
                'From_Currency': 'USD',
                'To_Currency': 'ZAR',
                'Rate': 18.0
            },
            {
                'Date': '2024-01-02',
                'From_Currency': 'USD',
                'To_Currency': 'ZAR',
                'Rate': 18.5
            },
            {
                'Date': '2024-01-03',
                'From_Currency': 'USD',
                'To_Currency': 'ZAR',
                'Rate': 19.0
            }
        ])
        
        result = reader.get_fx_rate('USD', 'ZAR')
        
        assert result == 19.0  # Should use the latest date
    
    def test_get_fx_rate_reverse_conversion(self):
        """Test FX rate for reverse conversion"""
        reader = FXRateReader()
        reader.fx_data = pd.DataFrame([
            {
                'Date': '2024-01-01',
                'From_Currency': 'USD',
                'To_Currency': 'ZAR',
                'Rate': 18.5
            }
        ])
        
        result = reader.get_fx_rate('ZAR', 'USD')
        
        assert result == pytest.approx(1/18.5, rel=1e-6)
    
    def test_get_fx_rate_cross_conversion(self):
        """Test FX rate for cross conversion (USD -> GBP via ZAR)"""
        reader = FXRateReader()
        reader.fx_data = pd.DataFrame([
            {
                'Date': '2024-01-01',
                'From_Currency': 'USD',
                'To_Currency': 'ZAR',
                'Rate': 18.5
            },
            {
                'Date': '2024-01-01',
                'From_Currency': 'GBP',
                'To_Currency': 'ZAR',
                'Rate': 23.2
            }
        ])
        
        result = reader.get_fx_rate('USD', 'GBP')
        
        # USD -> ZAR -> GBP: 18.5 / 23.2
        expected_rate = 18.5 / 23.2
        assert result == pytest.approx(expected_rate, rel=1e-6)
    
    def test_get_fx_rate_cross_conversion_not_found(self):
        """Test FX rate for cross conversion when intermediate rate not found"""
        reader = FXRateReader()
        reader.fx_data = pd.DataFrame([
            {
                'Date': '2024-01-01',
                'From_Currency': 'USD',
                'To_Currency': 'ZAR',
                'Rate': 18.5
            }
            # Missing GBP -> ZAR rate
        ])
        
        result = reader.get_fx_rate('USD', 'GBP')
        
        assert result is None
    
    def test_get_fx_rate_with_date(self):
        """Test FX rate retrieval for specific date"""
        reader = FXRateReader()
        reader.fx_data = pd.DataFrame([
            {
                'Date': '2024-01-01',
                'From_Currency': 'USD',
                'To_Currency': 'ZAR',
                'Rate': 18.0
            },
            {
                'Date': '2024-01-02',
                'From_Currency': 'USD',
                'To_Currency': 'ZAR',
                'Rate': 18.5
            }
        ])
        
        result = reader.get_fx_rate('USD', 'ZAR', '2024-01-01')
        
        assert result == 18.0
    
    def test_get_fx_rate_with_date_not_found(self):
        """Test FX rate retrieval for specific date not found"""
        reader = FXRateReader()
        reader.fx_data = pd.DataFrame([
            {
                'Date': '2024-01-01',
                'From_Currency': 'USD',
                'To_Currency': 'ZAR',
                'Rate': 18.0
            }
        ])
        
        result = reader.get_fx_rate('USD', 'ZAR', '2024-01-02')
        
        assert result is None
    
    def test_get_all_rates(self):
        """Test retrieval of all available rates"""
        reader = FXRateReader()
        reader.fx_data = pd.DataFrame([
            {
                'Date': '2024-01-01',
                'From_Currency': 'USD',
                'To_Currency': 'ZAR',
                'Rate': 18.5
            },
            {
                'Date': '2024-01-01',
                'From_Currency': 'GBP',
                'To_Currency': 'ZAR',
                'Rate': 23.2
            },
            {
                'Date': '2024-01-01',
                'From_Currency': 'EUR',
                'To_Currency': 'ZAR',
                'Rate': 20.1
            }
        ])
        
        result = reader.get_all_rates()
        
        assert result is not None
        assert len(result) == 3
        assert result.iloc[0]['From_Currency'] == 'USD'
        assert result.iloc[0]['Rate'] == 18.5
    
    def test_get_all_rates_no_data(self):
        """Test retrieval of all rates when no data loaded"""
        reader = FXRateReader()
        
        result = reader.get_all_rates()
        
        assert result is None
    
    def test_get_available_currencies(self):
        """Test retrieval of available currencies"""
        reader = FXRateReader()
        reader.fx_data = pd.DataFrame([
            {
                'Date': '2024-01-01',
                'From_Currency': 'USD',
                'To_Currency': 'ZAR',
                'Rate': 18.5
            },
            {
                'Date': '2024-01-01',
                'From_Currency': 'GBP',
                'To_Currency': 'ZAR',
                'Rate': 23.2
            },
            {
                'Date': '2024-01-01',
                'From_Currency': 'EUR',
                'To_Currency': 'ZAR',
                'Rate': 20.1
            }
        ])
        
        result = reader.get_available_currencies()
        
        assert result is not None
        assert 'USD' in result
        assert 'GBP' in result
        assert 'EUR' in result
        assert 'ZAR' in result
        assert len(result) == 4
    
    def test_get_available_currencies_no_data(self):
        """Test retrieval of available currencies when no data loaded"""
        reader = FXRateReader()
        
        result = reader.get_available_currencies()
        
        assert result is None
    
    def test_cache_management(self):
        """Test that cache is properly managed"""
        reader = FXRateReader()
        reader.fx_data = pd.DataFrame([
            {
                'Date': '2024-01-01',
                'From_Currency': 'USD',
                'To_Currency': 'ZAR',
                'Rate': 18.5
            }
        ])
        
        # First call should populate cache
        result1 = reader.get_fx_rate('USD', 'ZAR')
        assert result1 == 18.5
        assert 'USD_ZAR' in reader.rates_cache
        
        # Second call should use cache
        result2 = reader.get_fx_rate('USD', 'ZAR')
        assert result2 == 18.5
        
        # Cache should still contain the rate
        assert 'USD_ZAR' in reader.rates_cache
        assert reader.rates_cache['USD_ZAR'] == 18.5
    
    def test_clear_cache(self):
        """Test cache clearing functionality"""
        reader = FXRateReader()
        reader.rates_cache['USD_ZAR'] = 18.5
        reader.rates_cache['GBP_ZAR'] = 23.2
        
        reader.clear_cache()
        
        assert reader.rates_cache == {}
