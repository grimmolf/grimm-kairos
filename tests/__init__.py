"""
Test suite for Kairos TradingView automation
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test configuration
TEST_CONFIG = {
    'test_timeout': 30,
    'test_browser': 'chrome',
    'headless': True,
    'test_url': 'https://www.tradingview.com/',
    'test_symbol': 'BTCUSD',
    'test_timeframe': '1h'
}

# Test data directory
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(TEST_DATA_DIR, exist_ok=True)