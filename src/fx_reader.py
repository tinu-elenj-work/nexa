#!/usr/bin/env python3
"""
FX Rate Reader for Xero Consolidation
"""

import pandas as pd
import os
from datetime import date
from typing import Dict, Optional

class FXRateReader:
    """Reads and manages FX rates from Excel file"""
    
    def __init__(self, fx_file_path="fx/FX.xlsx"):
        self.fx_file_path = fx_file_path
        self.fx_data = None
        self.rates_cache = {}
        
    def load_fx_data(self):
        """Load FX data from Excel file"""
        try:
            if not os.path.exists(self.fx_file_path):
                print(f"❌ FX file not found: {self.fx_file_path}")
                return False
                
            # Read the Excel file
            self.fx_data = pd.read_excel(self.fx_file_path, sheet_name='ExchangeRates')
            return True
            
        except Exception as e:
            print(f"❌ Error loading FX data: {e}")
            return False
    
    def get_fx_rate(self, from_currency: str, to_currency: str = "ZAR") -> Optional[float]:
        """Get FX rate for converting from_currency to to_currency"""
        if self.fx_data is None:
            if not self.load_fx_data():
                return None
        
        # If converting to same currency, return 1
        if from_currency == to_currency:
            return 1.0
            
        # Cache key for performance
        cache_key = f"{from_currency}_{to_currency}"
        if cache_key in self.rates_cache:
            return self.rates_cache[cache_key]
        
        rate = self._lookup_rate_from_data(from_currency, to_currency)
        
        if rate:
            self.rates_cache[cache_key] = rate
            
        return rate
    
    def _lookup_rate_from_data(self, from_currency: str, to_currency: str) -> Optional[float]:
        """Internal method to lookup rate from loaded data"""
        try:
            if to_currency == 'ZAR':
                # Converting to ZAR - look up the rate directly
                currency_row = self.fx_data[self.fx_data['Currency'] == from_currency]
                if not currency_row.empty:
                    return float(currency_row['Rate'].iloc[0])
            
            return None
            
        except Exception as e:
            return None
    
    def get_available_currencies(self) -> list:
        """Get list of available currencies in the FX data"""
        if self.fx_data is None:
            if not self.load_fx_data():
                return []
        
        # Extract currency codes from the Currency column
        currencies = set(self.fx_data['Currency'].tolist())
        return sorted(list(currencies))
    
    def get_fx_rates_summary(self) -> dict:
        """Get summary of all available FX rates"""
        if self.fx_data is None:
            if not self.load_fx_data():
                return {}
        
        summary = {}
        for _, row in self.fx_data.iterrows():
            currency = row['Currency']
            rate = row['Rate']
            if currency != 'ZAR':
                summary[f"{currency}_ZAR"] = rate
        
        return summary
