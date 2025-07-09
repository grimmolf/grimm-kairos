"""
Timing utilities for web automation
Handles waits, retries, and performance monitoring
"""

import time
import logging
from typing import Callable, Any, Optional, Dict
from functools import wraps
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


class TimingManager:
    """
    Manages timing-related operations for web automation
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def wait_for_element(
        self, 
        browser: WebDriver, 
        selector: str, 
        timeout: Optional[int] = None,
        by: By = By.CSS_SELECTOR
    ) -> bool:
        """
        Wait for element to be present
        
        Args:
            browser: WebDriver instance
            selector: Element selector
            timeout: Maximum wait time
            by: Locator strategy
            
        Returns:
            True if element found, False otherwise
        """
        timeout = timeout or self.config.get('wait_time', 30)
        
        try:
            WebDriverWait(browser, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            return True
        except TimeoutException:
            return False
            
    def wait_for_clickable(
        self, 
        browser: WebDriver, 
        selector: str, 
        timeout: Optional[int] = None,
        by: By = By.CSS_SELECTOR
    ) -> bool:
        """
        Wait for element to be clickable
        
        Args:
            browser: WebDriver instance
            selector: Element selector
            timeout: Maximum wait time
            by: Locator strategy
            
        Returns:
            True if element clickable, False otherwise
        """
        timeout = timeout or self.config.get('wait_time', 30)
        
        try:
            WebDriverWait(browser, timeout).until(
                EC.element_to_be_clickable((by, selector))
            )
            return True
        except TimeoutException:
            return False
            
    def wait_for_text(
        self, 
        browser: WebDriver, 
        selector: str, 
        text: str,
        timeout: Optional[int] = None,
        by: By = By.CSS_SELECTOR
    ) -> bool:
        """
        Wait for element to contain specific text
        
        Args:
            browser: WebDriver instance
            selector: Element selector
            text: Expected text
            timeout: Maximum wait time
            by: Locator strategy
            
        Returns:
            True if text found, False otherwise
        """
        timeout = timeout or self.config.get('wait_time', 30)
        
        try:
            WebDriverWait(browser, timeout).until(
                EC.text_to_be_present_in_element((by, selector), text)
            )
            return True
        except TimeoutException:
            return False
            
    def retry_on_failure(
        self, 
        func: Callable, 
        max_retries: int = 3, 
        delay: float = 1.0,
        exceptions: tuple = (Exception,)
    ) -> Any:
        """
        Retry function on failure
        
        Args:
            func: Function to retry
            max_retries: Maximum retry attempts
            delay: Delay between retries
            exceptions: Exception types to catch
            
        Returns:
            Function result or raises last exception
        """
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return func()
            except exceptions as e:
                last_exception = e
                if attempt < max_retries:
                    self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                    time.sleep(delay)
                else:
                    self.logger.error(f"All {max_retries + 1} attempts failed")
                    
        raise last_exception
        
    def smart_delay(self, operation: str) -> None:
        """
        Apply smart delay based on operation type
        
        Args:
            operation: Type of operation (e.g., 'click', 'type', 'navigate')
        """
        delays = {
            'click': self.config.get('click_delay', 0.5),
            'type': self.config.get('type_delay', 0.1),
            'navigate': self.config.get('navigate_delay', 2.0),
            'submit': self.config.get('submit_delay', 1.0),
            'dropdown': self.config.get('dropdown_delay', 0.3),
            'dialog': self.config.get('dialog_delay', 0.5),
            'api': self.config.get('api_delay', 0.2)
        }
        
        delay = delays.get(operation, 0.5)
        if delay > 0:
            time.sleep(delay)
            
    def performance_timer(self, operation_name: str = "Operation"):
        """
        Context manager for timing operations
        
        Args:
            operation_name: Name of operation being timed
        """
        return PerformanceTimer(operation_name, self.logger)
        
    def wait_until_stable(
        self, 
        browser: WebDriver, 
        selector: str, 
        stable_time: float = 1.0,
        timeout: int = 10
    ) -> bool:
        """
        Wait until element is stable (no changes for specified time)
        
        Args:
            browser: WebDriver instance
            selector: Element selector
            stable_time: Time element must be stable
            timeout: Maximum wait time
            
        Returns:
            True if element stable, False otherwise
        """
        start_time = time.time()
        last_change_time = start_time
        last_text = ""
        
        while time.time() - start_time < timeout:
            try:
                element = browser.find_element(By.CSS_SELECTOR, selector)
                current_text = element.text
                
                if current_text != last_text:
                    last_change_time = time.time()
                    last_text = current_text
                    
                # Check if stable for required time
                if time.time() - last_change_time >= stable_time:
                    return True
                    
            except Exception:
                # Element not found, reset timer
                last_change_time = time.time()
                
            time.sleep(0.1)
            
        return False
        
    def wait_for_page_load(self, browser: WebDriver, timeout: int = 30) -> bool:
        """
        Wait for page to fully load
        
        Args:
            browser: WebDriver instance
            timeout: Maximum wait time
            
        Returns:
            True if page loaded, False otherwise
        """
        try:
            WebDriverWait(browser, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            return True
        except TimeoutException:
            return False
            
    def progressive_delay(self, attempt: int, base_delay: float = 1.0) -> None:
        """
        Apply progressive delay for retries
        
        Args:
            attempt: Current attempt number (0-based)
            base_delay: Base delay in seconds
        """
        delay = base_delay * (2 ** attempt)  # Exponential backoff
        time.sleep(min(delay, 10.0))  # Cap at 10 seconds


class PerformanceTimer:
    """
    Context manager for timing operations
    """
    
    def __init__(self, operation_name: str, logger: logging.Logger):
        self.operation_name = operation_name
        self.logger = logger
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        if exc_type is None:
            self.logger.info(f"{self.operation_name} completed in {duration:.2f}s")
        else:
            self.logger.error(f"{self.operation_name} failed after {duration:.2f}s")
            
    def elapsed(self) -> float:
        """Get elapsed time"""
        return time.time() - self.start_time if self.start_time else 0


def timing_decorator(operation_name: str = None):
    """
    Decorator for timing function execution
    
    Args:
        operation_name: Name of operation (defaults to function name)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            name = operation_name or func.__name__
            logger = logging.getLogger(func.__module__)
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"{name} completed in {duration:.2f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"{name} failed after {duration:.2f}s: {e}")
                raise
                
        return wrapper
    return decorator