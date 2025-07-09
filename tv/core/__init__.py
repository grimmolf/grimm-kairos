"""
Core WebDriver and authentication management for Kairos
Modularized from the monolithic tv.py file
"""

from .browser_manager import ModernBrowserManager, create_modern_browser
from .auth_manager import AuthenticationManager
from .config_manager import ConfigManager
from .async_browser import AsyncBrowserManager, AsyncTradingViewClient
from .session_manager import SessionManager, ResourceManager
from .performance_monitor import PerformanceMonitor, initialize_performance_monitoring

__all__ = [
    'ModernBrowserManager',
    'create_modern_browser',
    'AuthenticationManager', 
    'ConfigManager',
    'AsyncBrowserManager',
    'AsyncTradingViewClient',
    'SessionManager',
    'ResourceManager',
    'PerformanceMonitor',
    'initialize_performance_monitoring'
]