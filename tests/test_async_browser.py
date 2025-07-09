"""
Test suite for async browser functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException

from tv.core.async_browser import AsyncBrowserManager, AsyncTradingViewClient
from tests import TEST_CONFIG


class TestAsyncBrowserManager:
    """Test cases for AsyncBrowserManager"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.config = TEST_CONFIG.copy()
        self.config.update({
            'max_workers': 2,
            'wait_time': 10
        })
        
    @pytest.mark.asyncio
    async def test_init(self):
        """Test async browser manager initialization"""
        async with AsyncBrowserManager(self.config) as manager:
            assert manager.config == self.config
            assert manager.executor is not None
            assert manager._browser_pool == []
            
    @pytest.mark.asyncio
    @patch('tv.core.async_browser.ModernBrowserManager')
    async def test_create_browser_async(self, mock_manager_class):
        """Test async browser creation"""
        mock_manager = Mock()
        mock_browser = Mock(spec=WebDriver)
        mock_manager.create_browser.return_value = mock_browser
        mock_manager_class.return_value = mock_manager
        
        async with AsyncBrowserManager(self.config) as manager:
            browser = await manager.create_browser_async()
            
            assert browser == mock_browser
            mock_manager.create_browser.assert_called_once()
            
    @pytest.mark.asyncio
    @patch('tv.core.async_browser.ModernBrowserManager')
    async def test_get_browser_from_pool(self, mock_manager_class):
        """Test getting browser from pool"""
        mock_manager = Mock()
        mock_browser = Mock(spec=WebDriver)
        mock_manager.create_browser.return_value = mock_browser
        mock_manager_class.return_value = mock_manager
        
        async with AsyncBrowserManager(self.config) as manager:
            # Add browser to pool
            manager._browser_pool.append(mock_browser)
            
            browser = await manager.get_browser()
            
            assert browser == mock_browser
            assert len(manager._browser_pool) == 0
            
    @pytest.mark.asyncio
    @patch('tv.core.async_browser.ModernBrowserManager')
    async def test_return_browser_to_pool(self, mock_manager_class):
        """Test returning browser to pool"""
        mock_manager = Mock()
        mock_browser = Mock(spec=WebDriver)
        mock_manager_class.return_value = mock_manager
        
        async with AsyncBrowserManager(self.config) as manager:
            await manager.return_browser(mock_browser)
            
            assert mock_browser in manager._browser_pool
            
    @pytest.mark.asyncio
    @patch('tv.core.async_browser.ModernBrowserManager')
    async def test_navigate_async(self, mock_manager_class):
        """Test async navigation"""
        mock_manager = Mock()
        mock_browser = Mock(spec=WebDriver)
        mock_browser.get = Mock()
        mock_manager_class.return_value = mock_manager
        
        async with AsyncBrowserManager(self.config) as manager:
            await manager.navigate_async(mock_browser, 'https://example.com')
            
            mock_browser.get.assert_called_once_with('https://example.com')
            
    @pytest.mark.asyncio
    @patch('tv.core.async_browser.ModernBrowserManager')
    @patch('tv.core.async_browser.WebDriverWait')
    async def test_wait_for_element_async(self, mock_wait_class, mock_manager_class):
        """Test async element waiting"""
        mock_manager = Mock()
        mock_browser = Mock(spec=WebDriver)
        mock_wait = Mock()
        mock_wait.until.return_value = Mock()
        mock_wait_class.return_value = mock_wait
        mock_manager_class.return_value = mock_manager
        
        async with AsyncBrowserManager(self.config) as manager:
            manager.timing_manager.wait_for_element = Mock(return_value=True)
            
            result = await manager.wait_for_element_async(mock_browser, '.test-selector')
            
            assert result is True
            
    @pytest.mark.asyncio
    @patch('tv.core.async_browser.ModernBrowserManager')
    @patch('tv.core.async_browser.WebDriverWait')
    @patch('tv.core.async_browser.EC')
    async def test_click_element_async(self, mock_ec, mock_wait_class, mock_manager_class):
        """Test async element clicking"""
        mock_manager = Mock()
        mock_browser = Mock(spec=WebDriver)
        mock_element = Mock()
        mock_element.click = Mock()
        mock_wait = Mock()
        mock_wait.until.return_value = mock_element
        mock_wait_class.return_value = mock_wait
        mock_manager_class.return_value = mock_manager
        
        async with AsyncBrowserManager(self.config) as manager:
            result = await manager.click_element_async(mock_browser, '.test-selector')
            
            assert result is True
            mock_element.click.assert_called_once()
            
    @pytest.mark.asyncio
    @patch('tv.core.async_browser.ModernBrowserManager')
    @patch('tv.core.async_browser.WebDriverWait')
    async def test_click_element_async_timeout(self, mock_wait_class, mock_manager_class):
        """Test async element clicking with timeout"""
        mock_manager = Mock()
        mock_browser = Mock(spec=WebDriver)
        mock_wait = Mock()
        mock_wait.until.side_effect = TimeoutException()
        mock_wait_class.return_value = mock_wait
        mock_manager_class.return_value = mock_manager
        
        async with AsyncBrowserManager(self.config) as manager:
            result = await manager.click_element_async(mock_browser, '.test-selector')
            
            assert result is False
            
    @pytest.mark.asyncio
    @patch('tv.core.async_browser.ModernBrowserManager')
    @patch('tv.core.async_browser.WebDriverWait')
    @patch('tv.core.async_browser.EC')
    async def test_get_text_async(self, mock_ec, mock_wait_class, mock_manager_class):
        """Test async text retrieval"""
        mock_manager = Mock()
        mock_browser = Mock(spec=WebDriver)
        mock_element = Mock()
        mock_element.text = "Test text"
        mock_wait = Mock()
        mock_wait.until.return_value = mock_element
        mock_wait_class.return_value = mock_wait
        mock_manager_class.return_value = mock_manager
        
        async with AsyncBrowserManager(self.config) as manager:
            result = await manager.get_text_async(mock_browser, '.test-selector')
            
            assert result == "Test text"
            
    @pytest.mark.asyncio
    @patch('tv.core.async_browser.ModernBrowserManager')
    @patch('tv.core.async_browser.WebDriverWait')
    @patch('tv.core.async_browser.EC')
    async def test_type_text_async(self, mock_ec, mock_wait_class, mock_manager_class):
        """Test async text input"""
        mock_manager = Mock()
        mock_browser = Mock(spec=WebDriver)
        mock_element = Mock()
        mock_element.clear = Mock()
        mock_element.send_keys = Mock()
        mock_wait = Mock()
        mock_wait.until.return_value = mock_element
        mock_wait_class.return_value = mock_wait
        mock_manager_class.return_value = mock_manager
        
        async with AsyncBrowserManager(self.config) as manager:
            result = await manager.type_text_async(mock_browser, '.test-selector', 'test text')
            
            assert result is True
            mock_element.clear.assert_called_once()
            mock_element.send_keys.assert_called_once_with('test text')
            
    @pytest.mark.asyncio
    @patch('tv.core.async_browser.ModernBrowserManager')
    async def test_execute_script_async(self, mock_manager_class):
        """Test async script execution"""
        mock_manager = Mock()
        mock_browser = Mock(spec=WebDriver)
        mock_browser.execute_script = Mock(return_value="script result")
        mock_manager_class.return_value = mock_manager
        
        async with AsyncBrowserManager(self.config) as manager:
            result = await manager.execute_script_async(mock_browser, "return 'test';")
            
            assert result == "script result"
            mock_browser.execute_script.assert_called_once_with("return 'test';")
            
    @pytest.mark.asyncio
    @patch('tv.core.async_browser.ModernBrowserManager')
    async def test_take_screenshot_async(self, mock_manager_class):
        """Test async screenshot capture"""
        mock_manager = Mock()
        mock_browser = Mock(spec=WebDriver)
        mock_browser.save_screenshot = Mock(return_value=True)
        mock_manager_class.return_value = mock_manager
        
        async with AsyncBrowserManager(self.config) as manager:
            result = await manager.take_screenshot_async(mock_browser, 'test.png')
            
            assert result is True
            mock_browser.save_screenshot.assert_called_once_with('test.png')
            
    @pytest.mark.asyncio
    @patch('tv.core.async_browser.ModernBrowserManager')
    async def test_parallel_operations(self, mock_manager_class):
        """Test parallel operation execution"""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        
        async def mock_operation_1():
            return "result1"
            
        async def mock_operation_2():
            return "result2"
            
        async with AsyncBrowserManager(self.config) as manager:
            operations = [mock_operation_1, mock_operation_2]
            results = await manager.parallel_operations(operations)
            
            assert results == ["result1", "result2"]
            
    @pytest.mark.asyncio
    @patch('tv.core.async_browser.ModernBrowserManager')
    async def test_batch_element_operations(self, mock_manager_class):
        """Test batch element operations"""
        mock_manager = Mock()
        mock_browser = Mock(spec=WebDriver)
        mock_manager_class.return_value = mock_manager
        
        async with AsyncBrowserManager(self.config) as manager:
            # Mock the individual operation methods
            manager.click_element_async = AsyncMock(return_value=True)
            manager.get_text_async = AsyncMock(return_value="test text")
            manager.type_text_async = AsyncMock(return_value=True)
            
            operations = [
                {'type': 'click', 'selector': '.button'},
                {'type': 'text', 'selector': '.text'},
                {'type': 'type', 'selector': '.input', 'text': 'test'}
            ]
            
            results = await manager.batch_element_operations(mock_browser, operations)
            
            assert len(results) == 3
            assert results[0] is True
            assert results[1] == "test text"
            assert results[2] is True
            
    @pytest.mark.asyncio
    @patch('tv.core.async_browser.ModernBrowserManager')
    async def test_cleanup(self, mock_manager_class):
        """Test cleanup of resources"""
        mock_manager = Mock()
        mock_browser = Mock(spec=WebDriver)
        mock_browser.quit = Mock()
        mock_manager_class.return_value = mock_manager
        
        manager = AsyncBrowserManager(self.config)
        manager._browser_pool.append(mock_browser)
        
        await manager.cleanup()
        
        mock_browser.quit.assert_called_once()
        assert len(manager._browser_pool) == 0


class TestAsyncTradingViewClient:
    """Test cases for AsyncTradingViewClient"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.config = TEST_CONFIG.copy()
        
    @pytest.mark.asyncio
    @patch('tv.core.async_browser.AsyncBrowserManager')
    async def test_init(self, mock_manager_class):
        """Test async TradingView client initialization"""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        
        async with AsyncTradingViewClient(self.config) as client:
            assert client.config == self.config
            assert client.browser_manager == mock_manager
            
    @pytest.mark.asyncio
    @patch('tv.core.async_browser.AsyncBrowserManager')
    @patch('tv.core.async_browser.AuthenticationManager')
    async def test_login_async(self, mock_auth_class, mock_manager_class):
        """Test async login"""
        mock_manager = Mock()
        mock_browser = Mock(spec=WebDriver)
        mock_manager.get_browser = AsyncMock(return_value=mock_browser)
        mock_manager.return_browser = AsyncMock()
        mock_manager.navigate_async = AsyncMock()
        mock_manager.executor = Mock()
        mock_manager_class.return_value = mock_manager
        
        mock_auth = Mock()
        mock_auth.login = Mock(return_value=True)
        mock_auth_class.return_value = mock_auth
        
        async with AsyncTradingViewClient(self.config) as client:
            result = await client.login_async('testuser', 'testpass')
            
            assert result is True
            mock_manager.get_browser.assert_called_once()
            mock_manager.return_browser.assert_called_once()
            mock_manager.navigate_async.assert_called_once()
            
    @pytest.mark.asyncio
    @patch('tv.core.async_browser.AsyncBrowserManager')
    @patch('tv.core.async_browser.AlertCreator')
    async def test_create_alerts_batch(self, mock_alert_class, mock_manager_class):
        """Test batch alert creation"""
        mock_manager = Mock()
        mock_browser = Mock(spec=WebDriver)
        mock_manager.get_browser = AsyncMock(return_value=mock_browser)
        mock_manager.return_browser = AsyncMock()
        mock_manager.executor = Mock()
        mock_manager_class.return_value = mock_manager
        
        mock_alert_creator = Mock()
        mock_alert_creator.create_alert = Mock(return_value=True)
        mock_alert_class.return_value = mock_alert_creator
        
        alert_configs = [
            {'name': 'Alert 1', 'condition_type': 'Price'},
            {'name': 'Alert 2', 'condition_type': 'Indicator'}
        ]
        
        async with AsyncTradingViewClient(self.config) as client:
            results = await client.create_alerts_batch(alert_configs)
            
            assert len(results) == 2
            # Results should be either True or Exception instances
            
    @pytest.mark.asyncio
    @patch('tv.core.async_browser.AsyncBrowserManager')
    @patch('tv.core.async_browser.SignalProcessor')
    async def test_process_signals_parallel(self, mock_signal_class, mock_manager_class):
        """Test parallel signal processing"""
        mock_manager = Mock()
        mock_browser = Mock(spec=WebDriver)
        mock_manager.get_browser = AsyncMock(return_value=mock_browser)
        mock_manager.return_browser = AsyncMock()
        mock_manager.navigate_async = AsyncMock()
        mock_manager.executor = Mock()
        mock_manager_class.return_value = mock_manager
        
        mock_signal_processor = Mock()
        mock_signal_processor.process_indicator_signals = Mock(return_value={'signal': 'test'})
        mock_signal_class.return_value = mock_signal_processor
        
        symbols = ['BTCUSD', 'ETHUSD']
        
        async with AsyncTradingViewClient(self.config) as client:
            results = await client.process_signals_parallel(symbols)
            
            assert len(results) == 2
            
    @pytest.mark.asyncio
    @patch('tv.core.async_browser.AsyncBrowserManager')
    async def test_export_data_async(self, mock_manager_class):
        """Test async data export"""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        
        data = {'test': 'data'}
        export_configs = [
            {'type': 'file', 'filename': 'test.json'},
            {'type': 'webhook', 'url': 'https://example.com/webhook'}
        ]
        
        async with AsyncTradingViewClient(self.config) as client:
            # Mock the export methods
            client._export_file_async = AsyncMock(return_value=True)
            client._export_webhook_async = AsyncMock(return_value=True)
            
            results = await client.export_data_async(data, export_configs)
            
            assert len(results) == 2
            
    @pytest.mark.asyncio
    @patch('tv.core.async_browser.AsyncBrowserManager')
    @patch('aiofiles.open')
    async def test_export_file_async(self, mock_aiofiles_open, mock_manager_class):
        """Test async file export"""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        
        mock_file = AsyncMock()
        mock_file.write = AsyncMock()
        mock_aiofiles_open.return_value.__aenter__.return_value = mock_file
        
        data = {'test': 'data'}
        config = {'filename': 'test.json'}
        
        async with AsyncTradingViewClient(self.config) as client:
            result = await client._export_file_async(data, config)
            
            assert result is True
            mock_file.write.assert_called_once()
            
    @pytest.mark.asyncio
    @patch('tv.core.async_browser.AsyncBrowserManager')
    @patch('aiohttp.ClientSession')
    async def test_export_webhook_async(self, mock_session_class, mock_manager_class):
        """Test async webhook export"""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        
        mock_response = Mock()
        mock_response.status = 200
        mock_session = Mock()
        mock_session.post.return_value.__aenter__.return_value = mock_response
        mock_session_class.return_value.__aenter__.return_value = mock_session
        
        data = {'test': 'data'}
        config = {'url': 'https://example.com/webhook'}
        
        async with AsyncTradingViewClient(self.config) as client:
            result = await client._export_webhook_async(data, config)
            
            assert result is True
            mock_session.post.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])