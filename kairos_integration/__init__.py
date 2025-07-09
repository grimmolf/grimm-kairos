"""
Kairos Integration Framework for Trading Setups

This package provides integration between trading-setups and grimm-kairos
for automated TradingView indicator testing, strategy backtesting, and
chart screenshot capture.

Features:
- Google OAuth authentication for grimm@greysson.com
- Automated TradingView indicator testing
- Strategy backtesting automation
- Chart screenshot capture
- MNQ1! default ticker configuration
"""

__version__ = "1.0.0"
__author__ = "Grimm Trading Systems"

from .core.auth_manager import GrimmAuthManager
from .core.test_runner import TradingViewTestRunner
from .core.backtest_runner import StrategyBacktester
from .core.screenshot_manager import ChartScreenshotManager

__all__ = [
    'GrimmAuthManager',
    'TradingViewTestRunner', 
    'StrategyBacktester',
    'ChartScreenshotManager'
]