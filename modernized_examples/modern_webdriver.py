"""
Modern WebDriver Implementation for Kairos
Replaces deprecated chromedriver_autoinstaller and selenium-stealth
Uses Selenium 4+ native features for better performance and reliability
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import (
    WebDriverException, 
    TimeoutException, 
    NoSuchElementException
)


class ModernWebDriverManager:
    """
    Modern WebDriver manager using Selenium 4+ features
    Eliminates need for chromedriver_autoinstaller and selenium-stealth
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def create_browser(self, headless: bool = True) -> WebDriver:
        """
        Create a modern Chrome WebDriver instance with anti-detection
        
        Args:
            headless: Run in headless mode
            
        Returns:
            WebDriver instance
        """
        options = self._get_chrome_options(headless)
        service = self._get_chrome_service()
        
        try:
            driver = webdriver.Chrome(service=service, options=options)
            self._configure_driver(driver)
            return driver
            
        except WebDriverException as e:
            self.logger.error(f"Failed to create WebDriver: {e}")
            raise
    
    def _get_chrome_options(self, headless: bool) -> Options:
        """
        Configure Chrome options with modern anti-detection features
        Replaces selenium-stealth functionality
        """
        options = Options()
        
        # Basic options
        if headless:
            options.add_argument('--headless=new')  # Modern headless mode
        
        # Anti-detection (replaces selenium-stealth)
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Performance optimizations
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')  # Faster page loads
        
        # Memory optimization
        options.add_argument('--memory-pressure-off')
        options.add_argument('--max_old_space_size=4096')
        
        # TradingView specific optimizations
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-ipc-flooding-protection')
        
        # User data directory (if configured)
        if user_data_dir := self.config.get('user_data_directory'):
            options.add_argument(f'--user-data-dir={user_data_dir}')
            
        # Custom binary path (if configured)
        if browser_path := self.config.get('web_browser_path'):
            options.binary_location = browser_path
            
        return options
    
    def _get_chrome_service(self) -> Service:
        """
        Configure Chrome service - Selenium 4+ auto-manages ChromeDriver
        Eliminates need for chromedriver_autoinstaller
        """
        service_args = []
        
        # Add service arguments if needed
        if self.config.get('verbose_logging'):
            service_args.append('--verbose')
            
        # Custom driver path (optional)
        driver_path = self.config.get('webdriver_path')
        
        if driver_path and Path(driver_path).exists():
            return Service(executable_path=driver_path, service_args=service_args)
        else:
            # Let Selenium 4+ auto-manage ChromeDriver
            return Service(service_args=service_args)
    
    def _configure_driver(self, driver: WebDriver) -> None:
        """Configure driver with optimized settings"""
        
        # Set timeouts
        driver.implicitly_wait(self.config.get('implicit_wait', 0))
        driver.set_page_load_timeout(self.config.get('page_load_timeout', 60))
        
        # Set window size
        resolution = self.config.get('resolution', '1920,1080')
        width, height = map(int, resolution.split(','))
        driver.set_window_size(width, height)
        
        # Execute anti-detection script
        driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        # Set user agent if needed
        if user_agent := self.config.get('user_agent'):
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": user_agent
            })


class EnhancedElementLocator:
    """
    Enhanced element location with modern practices
    Uses built-in WebDriverWait instead of custom polling
    """
    
    def __init__(self, driver: WebDriver, default_timeout: int = 10):
        self.driver = driver
        self.wait = WebDriverWait(driver, default_timeout)
        self.logger = logging.getLogger(__name__)
    
    def find_element_safely(
        self, 
        locator: tuple, 
        timeout: Optional[int] = None,
        condition: str = 'presence'
    ) -> Optional[Any]:
        """
        Safely find element with proper error handling
        
        Args:
            locator: (By.METHOD, selector) tuple
            timeout: Custom timeout in seconds
            condition: 'presence', 'visible', 'clickable'
            
        Returns:
            WebElement or None if not found
        """
        wait = WebDriverWait(self.driver, timeout) if timeout else self.wait
        
        conditions = {
            'presence': EC.presence_of_element_located,
            'visible': EC.visibility_of_element_located,
            'clickable': EC.element_to_be_clickable
        }
        
        try:
            condition_func = conditions.get(condition, EC.presence_of_element_located)
            return wait.until(condition_func(locator))
            
        except TimeoutException:
            self.logger.warning(f"Element not found: {locator}")
            return None
        except Exception as e:
            self.logger.error(f"Error finding element {locator}: {e}")
            return None
    
    def find_elements_safely(
        self, 
        locator: tuple, 
        timeout: Optional[int] = None
    ) -> List[Any]:
        """Safely find multiple elements"""
        wait = WebDriverWait(self.driver, timeout) if timeout else self.wait
        
        try:
            wait.until(EC.presence_of_element_located(locator))
            return self.driver.find_elements(*locator)
            
        except TimeoutException:
            self.logger.warning(f"Elements not found: {locator}")
            return []
        except Exception as e:
            self.logger.error(f"Error finding elements {locator}: {e}")
            return []


# Example usage in modernized Kairos
def create_modern_browser(config: Dict[str, Any]) -> WebDriver:
    """
    Factory function to create modernized browser instance
    Replaces the old create_browser function in tv.py
    """
    manager = ModernWebDriverManager(config)
    return manager.create_browser(
        headless=config.get('run_in_background', True)
    )


# Modern CSS selector patterns (replacing hardcoded selectors)
MODERN_SELECTORS = {
    # More resilient selectors using data attributes when possible
    'alert_button': '[data-name="alerts"], #header-toolbar-alerts',
    'create_alert_dialog': '[data-name="alerts-create-edit-dialog"]',
    'symbol_search': '[data-name="symbol-search-items-dialog"] input',
    'watchlist_dialog': '[data-name="watchlists-dialog"]',
    
    # Fallback selectors for robustness
    'fallback_alert_button': 'button[title*="Alert"], .tv-header__button--alerts',
}