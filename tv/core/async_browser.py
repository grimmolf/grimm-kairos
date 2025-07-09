"""
Async Browser Manager for Kairos
Provides async/await interface for browser operations
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List, Callable, Awaitable
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .browser_manager import ModernBrowserManager
from .auth_manager import AuthenticationManager
from ..utils.selectors import CSSSelectors
from ..utils.timing_utils import TimingManager


class AsyncBrowserManager:
    """
    Async wrapper for browser operations
    Enables non-blocking browser automation
    """
    
    def __init__(self, config: Dict[str, Any], max_workers: int = 4):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.browser_manager = ModernBrowserManager(config)
        self.selectors = CSSSelectors()
        self.timing_manager = TimingManager(config)
        
        # Browser pool for concurrent operations
        self._browser_pool: List[WebDriver] = []
        self._pool_lock = asyncio.Lock()
        
    async def __aenter__(self):
        """Async context manager entry"""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()
        
    async def get_browser(self) -> WebDriver:
        """
        Get browser instance from pool or create new one
        
        Returns:
            WebDriver instance
        """
        async with self._pool_lock:
            if self._browser_pool:
                return self._browser_pool.pop()
            else:
                # Create new browser in thread pool
                loop = asyncio.get_event_loop()
                browser = await loop.run_in_executor(
                    self.executor,
                    self.browser_manager.create_browser
                )
                return browser
                
    async def return_browser(self, browser: WebDriver) -> None:
        """
        Return browser to pool
        
        Args:
            browser: WebDriver instance to return
        """
        async with self._pool_lock:
            self._browser_pool.append(browser)
            
    async def create_browser_async(self, **kwargs) -> WebDriver:
        """
        Create browser asynchronously
        
        Args:
            **kwargs: Browser creation parameters
            
        Returns:
            WebDriver instance
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            lambda: self.browser_manager.create_browser(**kwargs)
        )
        
    async def navigate_async(self, browser: WebDriver, url: str) -> None:
        """
        Navigate to URL asynchronously
        
        Args:
            browser: WebDriver instance
            url: URL to navigate to
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self.executor,
            lambda: browser.get(url)
        )
        
    async def wait_for_element_async(
        self, 
        browser: WebDriver, 
        selector: str, 
        timeout: int = 30
    ) -> bool:
        """
        Wait for element asynchronously
        
        Args:
            browser: WebDriver instance
            selector: CSS selector
            timeout: Timeout in seconds
            
        Returns:
            True if element found
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            lambda: self.timing_manager.wait_for_element(browser, selector, timeout)
        )
        
    async def click_element_async(
        self, 
        browser: WebDriver, 
        selector: str, 
        wait_timeout: int = 30
    ) -> bool:
        """
        Click element asynchronously
        
        Args:
            browser: WebDriver instance
            selector: CSS selector
            wait_timeout: Timeout for waiting
            
        Returns:
            True if clicked successfully
        """
        loop = asyncio.get_event_loop()
        
        def _click_element():
            try:
                element = WebDriverWait(browser, wait_timeout).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                element.click()
                return True
            except TimeoutException:
                return False
                
        return await loop.run_in_executor(self.executor, _click_element)
        
    async def get_text_async(
        self, 
        browser: WebDriver, 
        selector: str, 
        wait_timeout: int = 30
    ) -> Optional[str]:
        """
        Get element text asynchronously
        
        Args:
            browser: WebDriver instance
            selector: CSS selector
            wait_timeout: Timeout for waiting
            
        Returns:
            Element text or None
        """
        loop = asyncio.get_event_loop()
        
        def _get_text():
            try:
                element = WebDriverWait(browser, wait_timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                return element.text
            except TimeoutException:
                return None
                
        return await loop.run_in_executor(self.executor, _get_text)
        
    async def type_text_async(
        self, 
        browser: WebDriver, 
        selector: str, 
        text: str, 
        clear_first: bool = True
    ) -> bool:
        """
        Type text into element asynchronously
        
        Args:
            browser: WebDriver instance
            selector: CSS selector
            text: Text to type
            clear_first: Whether to clear field first
            
        Returns:
            True if successful
        """
        loop = asyncio.get_event_loop()
        
        def _type_text():
            try:
                element = WebDriverWait(browser, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if clear_first:
                    element.clear()
                element.send_keys(text)
                return True
            except TimeoutException:
                return False
                
        return await loop.run_in_executor(self.executor, _type_text)
        
    async def execute_script_async(
        self, 
        browser: WebDriver, 
        script: str, 
        *args
    ) -> Any:
        """
        Execute JavaScript asynchronously
        
        Args:
            browser: WebDriver instance
            script: JavaScript code
            *args: Script arguments
            
        Returns:
            Script result
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            lambda: browser.execute_script(script, *args)
        )
        
    async def take_screenshot_async(
        self, 
        browser: WebDriver, 
        filename: str
    ) -> bool:
        """
        Take screenshot asynchronously
        
        Args:
            browser: WebDriver instance
            filename: Screenshot filename
            
        Returns:
            True if successful
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            lambda: browser.save_screenshot(filename)
        )
        
    async def parallel_operations(
        self, 
        operations: List[Callable[[], Awaitable[Any]]]
    ) -> List[Any]:
        """
        Execute multiple operations in parallel
        
        Args:
            operations: List of async operations
            
        Returns:
            List of results
        """
        tasks = [op() for op in operations]
        return await asyncio.gather(*tasks, return_exceptions=True)
        
    async def batch_element_operations(
        self, 
        browser: WebDriver, 
        operations: List[Dict[str, Any]]
    ) -> List[Any]:
        """
        Execute batch element operations
        
        Args:
            browser: WebDriver instance
            operations: List of operation dictionaries
            
        Returns:
            List of results
        """
        async def _execute_operation(op: Dict[str, Any]) -> Any:
            op_type = op.get('type')
            selector = op.get('selector')
            
            if op_type == 'click':
                return await self.click_element_async(browser, selector)
            elif op_type == 'text':
                return await self.get_text_async(browser, selector)
            elif op_type == 'type':
                return await self.type_text_async(browser, selector, op.get('text', ''))
            elif op_type == 'wait':
                return await self.wait_for_element_async(browser, selector)
            else:
                return None
                
        tasks = [_execute_operation(op) for op in operations]
        return await asyncio.gather(*tasks, return_exceptions=True)
        
    async def cleanup(self) -> None:
        """Clean up resources"""
        try:
            # Close all browsers in pool
            async with self._pool_lock:
                for browser in self._browser_pool:
                    try:
                        await asyncio.get_event_loop().run_in_executor(
                            self.executor,
                            browser.quit
                        )
                    except Exception as e:
                        self.logger.warning(f"Error closing browser: {e}")
                self._browser_pool.clear()
                
            # Shutdown executor
            self.executor.shutdown(wait=True)
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


class AsyncTradingViewClient:
    """
    High-level async client for TradingView operations
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.browser_manager = AsyncBrowserManager(config)
        
    async def __aenter__(self):
        await self.browser_manager.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.browser_manager.__aexit__(exc_type, exc_val, exc_tb)
        
    async def login_async(self, username: str, password: str) -> bool:
        """
        Login to TradingView asynchronously
        
        Args:
            username: TradingView username
            password: TradingView password
            
        Returns:
            True if login successful
        """
        browser = await self.browser_manager.get_browser()
        
        try:
            # Navigate to TradingView
            await self.browser_manager.navigate_async(browser, 'https://www.tradingview.com/')
            
            # Create auth manager and login
            loop = asyncio.get_event_loop()
            auth_manager = AuthenticationManager(self.config, browser)
            
            result = await loop.run_in_executor(
                self.browser_manager.executor,
                lambda: auth_manager.login(username, password)
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Async login failed: {e}")
            return False
        finally:
            await self.browser_manager.return_browser(browser)
            
    async def create_alerts_batch(self, alert_configs: List[Dict[str, Any]]) -> List[bool]:
        """
        Create multiple alerts in parallel
        
        Args:
            alert_configs: List of alert configurations
            
        Returns:
            List of success flags
        """
        async def _create_single_alert(config: Dict[str, Any]) -> bool:
            browser = await self.browser_manager.get_browser()
            
            try:
                from ..automation.alert_creator import AlertCreator
                
                loop = asyncio.get_event_loop()
                alert_creator = AlertCreator(browser, self.config)
                
                return await loop.run_in_executor(
                    self.browser_manager.executor,
                    lambda: alert_creator.create_alert(config)
                )
                
            except Exception as e:
                self.logger.error(f"Error creating alert: {e}")
                return False
            finally:
                await self.browser_manager.return_browser(browser)
                
        tasks = [_create_single_alert(config) for config in alert_configs]
        return await asyncio.gather(*tasks, return_exceptions=True)
        
    async def process_signals_parallel(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """
        Process signals for multiple symbols in parallel
        
        Args:
            symbols: List of symbols to process
            
        Returns:
            List of signal results
        """
        async def _process_single_symbol(symbol: str) -> Dict[str, Any]:
            browser = await self.browser_manager.get_browser()
            
            try:
                from ..automation.signal_processor import SignalProcessor
                
                loop = asyncio.get_event_loop()
                signal_processor = SignalProcessor(browser, self.config)
                
                # Navigate to symbol chart
                chart_url = f"https://www.tradingview.com/chart/?symbol={symbol}"
                await self.browser_manager.navigate_async(browser, chart_url)
                
                # Process indicators
                indicators = self.config.get('indicators', [])
                return await loop.run_in_executor(
                    self.browser_manager.executor,
                    lambda: signal_processor.process_indicator_signals(indicators)
                )
                
            except Exception as e:
                self.logger.error(f"Error processing symbol {symbol}: {e}")
                return {'symbol': symbol, 'error': str(e)}
            finally:
                await self.browser_manager.return_browser(browser)
                
        tasks = [_process_single_symbol(symbol) for symbol in symbols]
        return await asyncio.gather(*tasks, return_exceptions=True)
        
    async def monitor_signals_async(
        self, 
        symbols: List[str], 
        callback: Callable[[Dict[str, Any]], Awaitable[None]],
        interval: int = 60
    ) -> None:
        """
        Monitor signals asynchronously
        
        Args:
            symbols: List of symbols to monitor
            callback: Async callback function
            interval: Check interval in seconds
        """
        self.logger.info(f"Starting async signal monitoring for {len(symbols)} symbols")
        
        try:
            while True:
                # Process all symbols in parallel
                results = await self.process_signals_parallel(symbols)
                
                # Call callback for each result
                for result in results:
                    if not isinstance(result, Exception):
                        await callback(result)
                        
                # Wait before next cycle
                await asyncio.sleep(interval)
                
        except asyncio.CancelledError:
            self.logger.info("Signal monitoring cancelled")
        except Exception as e:
            self.logger.error(f"Error in signal monitoring: {e}")
            
    async def export_data_async(
        self, 
        data: Dict[str, Any], 
        export_configs: List[Dict[str, Any]]
    ) -> List[bool]:
        """
        Export data to multiple destinations asynchronously
        
        Args:
            data: Data to export
            export_configs: List of export configurations
            
        Returns:
            List of success flags
        """
        async def _export_single(config: Dict[str, Any]) -> bool:
            try:
                export_type = config.get('type')
                
                if export_type == 'webhook':
                    return await self._export_webhook_async(data, config)
                elif export_type == 'email':
                    return await self._export_email_async(data, config)
                elif export_type == 'file':
                    return await self._export_file_async(data, config)
                else:
                    return False
                    
            except Exception as e:
                self.logger.error(f"Export failed: {e}")
                return False
                
        tasks = [_export_single(config) for config in export_configs]
        return await asyncio.gather(*tasks, return_exceptions=True)
        
    async def _export_webhook_async(self, data: Dict[str, Any], config: Dict[str, Any]) -> bool:
        """Export via webhook asynchronously"""
        import aiohttp
        
        url = config.get('url')
        if not url:
            return False
            
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=data) as response:
                    return response.status == 200
            except Exception as e:
                self.logger.error(f"Webhook export failed: {e}")
                return False
                
    async def _export_email_async(self, data: Dict[str, Any], config: Dict[str, Any]) -> bool:
        """Export via email asynchronously"""
        # This would implement async email sending
        # For now, return True as placeholder
        return True
        
    async def _export_file_async(self, data: Dict[str, Any], config: Dict[str, Any]) -> bool:
        """Export to file asynchronously"""
        import aiofiles
        import json
        
        filename = config.get('filename')
        if not filename:
            return False
            
        try:
            async with aiofiles.open(filename, 'w') as f:
                await f.write(json.dumps(data, indent=2))
            return True
        except Exception as e:
            self.logger.error(f"File export failed: {e}")
            return False