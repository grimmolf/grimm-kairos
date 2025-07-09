"""
Modern Browser Manager for Kairos
Extracted from tv.py for better maintainability and testing
Uses Selenium 4+ features and modern anti-detection
"""

import logging
import os
import re
import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import WebDriverException

from kairos import tools


class ModernBrowserManager:
    """
    Modern browser management with Selenium 4+ features
    Replaces the old create_browser function with better error handling
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._instance_counter = 0
        
    def create_browser(
        self, 
        run_in_background: bool = True,
        resolution: str = '1920,1080',
        download_path: Optional[str] = None
    ) -> WebDriver:
        """
        Create a modern Chrome WebDriver instance
        
        Args:
            run_in_background: Run in headless mode
            resolution: Browser window size
            download_path: Download directory path
            
        Returns:
            Configured WebDriver instance
            
        Raises:
            WebDriverException: If browser creation fails
        """
        try:
            options = self._configure_chrome_options(
                run_in_background, resolution, download_path
            )
            service = self._configure_chrome_service()
            
            browser = webdriver.Chrome(service=service, options=options)
            self._configure_browser_settings(browser)
            self._apply_anti_detection(browser)
            
            self.logger.info(f"Browser created successfully (instance {self._instance_counter})")
            self._instance_counter += 1
            
            return browser
            
        except Exception as e:
            self.logger.error(f"Failed to create browser: {e}")
            raise WebDriverException(f"Browser creation failed: {e}")
    
    def _configure_chrome_options(
        self, 
        run_in_background: bool,
        resolution: str,
        download_path: Optional[str]
    ) -> Options:
        """Configure Chrome options with modern anti-detection"""
        options = Options()
        
        # Custom browser binary path
        if self.config.get('web_browser_path'):
            options.binary_location = self.config['web_browser_path']
            
        # User data directory for session persistence
        if user_data_dir := self._setup_user_data_directory():
            options.add_argument(f'--user-data-dir={user_data_dir}')
            
        # Custom options from config
        if custom_options := self.config.get('options'):
            for option in custom_options.split(','):
                options.add_argument(option.strip())
        else:
            self._add_default_options(options, run_in_background, resolution)
            
        # Download preferences
        if download_path:
            self._configure_downloads(options, download_path)
            
        return options
    
    def _add_default_options(
        self, 
        options: Options, 
        run_in_background: bool, 
        resolution: str
    ) -> None:
        """Add default Chrome options for optimal performance"""
        
        # Modern anti-detection (replaces selenium-stealth)
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Performance optimizations
        captcha_extension = self.config.get('captcha_extension', False)
        if not captcha_extension:
            options.add_argument('--disable-extensions')
            
        options.add_argument('--disable-notifications')
        options.add_argument('--noerrdialogs')
        options.add_argument('--disable-session-crashed-bubble')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'--window-size={resolution}')
        options.add_argument('--log-level=3')  # Suppress console messages
        
        # Platform-specific optimizations
        os_type = tools.get_operating_system()
        if os_type == 'linux':
            options.add_argument('--no-sandbox')
            
        # Modern headless mode
        if run_in_background:
            options.add_argument('--headless=new')
            
        # Memory and performance optimizations
        options.add_argument('--memory-pressure-off')
        options.add_argument('--max_old_space_size=4096')
        options.add_argument('--disable-features=VizDisplayCompositor')
    
    def _configure_chrome_service(self) -> Service:
        """Configure Chrome service with Selenium 4+ auto-management"""
        
        # Custom driver path (optional)
        if driver_path := self.config.get('webdriver_path'):
            path = Path(driver_path)
            if path.exists():
                self.logger.info(f"Using custom webdriver: {path}")
                return Service(executable_path=str(path))
            else:
                self.logger.warning("Custom webdriver path not found, using Selenium Manager")
                
        # Let Selenium 4+ auto-manage ChromeDriver
        self.logger.info("Using Selenium Manager for automatic webdriver management")
        return Service()
    
    def _setup_user_data_directory(self) -> Optional[str]:
        """Setup user data directory for session persistence"""
        if not self.config.get('user_data_directory'):
            return None
            
        base_dir = self.config['user_data_directory']
        if self.config.get('share_user_data', False):
            # Create instance-specific directory
            kairos_dir = f"kairos_{self._instance_counter}"
            user_data_dir = os.path.join(base_dir, kairos_dir)
            
            if not os.path.exists(user_data_dir):
                os.makedirs(user_data_dir, exist_ok=True)
                tools.set_permission(user_data_dir)
                
            return user_data_dir
        else:
            return base_dir
    
    def _configure_downloads(self, options: Options, download_path: str) -> None:
        """Configure download settings"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        full_path = os.path.join(download_path, timestamp)
        
        try:
            os.makedirs(full_path, exist_ok=True)
            tools.set_permission(full_path)
            
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "download.default_directory": full_path,
                "download.prompt_for_download": False,
                "safebrowsing.enabled": False
            }
            options.add_experimental_option("prefs", prefs)
            
        except Exception as e:
            self.logger.warning(f"Failed to setup download directory: {e}")
    
    def _configure_browser_settings(self, browser: WebDriver) -> None:
        """Configure browser timeouts and settings"""
        
        # Timeouts
        implicit_wait = self.config.get('wait_time_implicit', 0)
        page_load_timeout = self.config.get('page_load_timeout', 60)
        
        browser.implicitly_wait(implicit_wait)
        browser.set_page_load_timeout(page_load_timeout)
        
        # Window size
        resolution = self.config.get('resolution', '1920,1080')
        if ',' in resolution:
            width, height = map(int, resolution.split(','))
            browser.set_window_size(width, height)
    
    def _apply_anti_detection(self, browser: WebDriver) -> None:
        """Apply modern anti-detection measures"""
        
        # Remove webdriver property
        browser.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        # Set realistic user agent
        driver_version = self._get_driver_version(browser)
        user_agent = (
            f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            f'AppleWebKit/537.36 (KHTML, like Gecko) '
            f'Chrome/{driver_version} Safari/537.36'
        )
        
        try:
            browser.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": user_agent
            })
        except Exception as e:
            self.logger.warning(f"Failed to set user agent: {e}")
    
    def _get_driver_version(self, browser: WebDriver) -> str:
        """Get Chrome driver version"""
        try:
            version_info = browser.capabilities.get('browserVersion', '120.0.0.0')
            return version_info.split('.')[0]  # Major version only
        except Exception:
            return '120'  # Fallback version
    
    def destroy_browser(self, browser: WebDriver) -> None:
        """Safely destroy browser instance"""
        if browser:
            try:
                browser.quit()
                self.logger.info("Browser destroyed successfully")
            except Exception as e:
                self.logger.warning(f"Error destroying browser: {e}")


# Factory function for backward compatibility
def create_modern_browser(config: Dict[str, Any], **kwargs) -> WebDriver:
    """
    Factory function to create a modern browser instance
    Maintains compatibility with existing code
    """
    manager = ModernBrowserManager(config)
    return manager.create_browser(**kwargs)