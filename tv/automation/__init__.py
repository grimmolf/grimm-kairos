"""
Automation modules for TradingView interactions
Extracted from the monolithic tv.py file for better maintainability
"""

from .alert_creator import AlertCreator
from .signal_processor import SignalProcessor

__all__ = [
    'AlertCreator',
    'SignalProcessor'
]