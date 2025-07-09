"""
Test suite for browser manager functionality
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import WebDriverException

from tv.core.browser_manager import ModernBrowserManager, create_modern_browser
from tests import TEST_CONFIG


class TestModernBrowserManager:
    """Test cases for ModernBrowserManager"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.config = TEST_CONFIG.copy()
        self.config.update({
            'run_in_background': True,
            'resolution': '1920,1080',
            'wait_time': 10,
            'user_data_directory': None
        })
        self.manager = ModernBrowserManager(self.config)
        
    def test_init(self):
        """Test manager initialization"""
        assert self.manager.config == self.config
        assert self.manager._instance_counter == 0
        assert self.manager.logger is not None
        
    @patch('tv.core.browser_manager.webdriver.Chrome')
    @patch('tv.core.browser_manager.Service')
    def test_create_browser_success(self, mock_service, mock_chrome):
        """Test successful browser creation"""
        # Mock WebDriver
        mock_browser = Mock(spec=WebDriver)
        mock_chrome.return_value = mock_browser
        
        # Mock service
        mock_service_instance = Mock()
        mock_service.return_value = mock_service_instance
        
        # Test browser creation
        browser = self.manager.create_browser()
        
        # Assertions
        assert browser == mock_browser
        assert self.manager._instance_counter == 1
        mock_chrome.assert_called_once()
        mock_service.assert_called_once()
        
    @patch('tv.core.browser_manager.webdriver.Chrome')
    def test_create_browser_failure(self, mock_chrome):
        """Test browser creation failure"""
        # Mock Chrome to raise exception
        mock_chrome.side_effect = WebDriverException("Test error")
        
        # Test browser creation failure
        with pytest.raises(WebDriverException):
            self.manager.create_browser()
            
    def test_configure_chrome_options_headless(self):
        """Test Chrome options configuration for headless mode"""
        options = self.manager._configure_chrome_options(True, '1920,1080', None)
        
        # Check that headless option is set
        assert '--headless=new' in options.arguments
        assert '--disable-gpu' in options.arguments
        assert '--window-size=1920,1080' in options.arguments
        
    def test_configure_chrome_options_visible(self):
        """Test Chrome options configuration for visible mode"""
        options = self.manager._configure_chrome_options(False, '1920,1080', None)
        
        # Check that headless option is not set
        assert '--headless=new' not in options.arguments
        assert '--window-size=1920,1080' in options.arguments
        
    def test_configure_chrome_options_with_custom_binary(self):
        """Test Chrome options with custom binary path"""
        self.config['web_browser_path'] = '/custom/chrome/path'
        manager = ModernBrowserManager(self.config)
        
        options = manager._configure_chrome_options(True, '1920,1080', None)
        
        assert options.binary_location == '/custom/chrome/path'
        
    def test_configure_chrome_options_with_custom_options(self):
        """Test Chrome options with custom options"""
        self.config['options'] = '--test-option1,--test-option2'
        manager = ModernBrowserManager(self.config)
        
        options = manager._configure_chrome_options(True, '1920,1080', None)
        
        assert '--test-option1' in options.arguments
        assert '--test-option2' in options.arguments
        
    def test_configure_downloads(self):
        """Test download configuration"""
        with tempfile.TemporaryDirectory() as temp_dir:
            options = Mock()
            options.add_experimental_option = Mock()
            
            self.manager._configure_downloads(options, temp_dir)
            
            # Check that experimental option was set
            options.add_experimental_option.assert_called_once()
            call_args = options.add_experimental_option.call_args
            assert call_args[0][0] == "prefs"
            assert "download.default_directory" in call_args[0][1]
            
    def test_setup_user_data_directory(self):
        """Test user data directory setup"""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.config['user_data_directory'] = temp_dir
            self.config['share_user_data'] = True
            manager = ModernBrowserManager(self.config)
            
            user_data_dir = manager._setup_user_data_directory()
            
            assert user_data_dir is not None
            assert temp_dir in user_data_dir
            assert os.path.exists(user_data_dir)
            
    def test_setup_user_data_directory_disabled(self):
        """Test user data directory when disabled"""
        self.config['user_data_directory'] = None
        manager = ModernBrowserManager(self.config)
        
        user_data_dir = manager._setup_user_data_directory()
        
        assert user_data_dir is None
        
    @patch('tv.core.browser_manager.webdriver.Chrome')
    def test_configure_browser_settings(self, mock_chrome):
        """Test browser settings configuration"""
        mock_browser = Mock(spec=WebDriver)
        mock_browser.implicitly_wait = Mock()
        mock_browser.set_page_load_timeout = Mock()
        mock_browser.set_window_size = Mock()
        
        self.manager._configure_browser_settings(mock_browser)
        
        # Check that settings were applied
        mock_browser.implicitly_wait.assert_called_once()
        mock_browser.set_page_load_timeout.assert_called_once()
        mock_browser.set_window_size.assert_called_once()
        
    @patch('tv.core.browser_manager.webdriver.Chrome')
    def test_apply_anti_detection(self, mock_chrome):
        """Test anti-detection measures"""
        mock_browser = Mock(spec=WebDriver)
        mock_browser.execute_script = Mock()
        mock_browser.execute_cdp_cmd = Mock()
        mock_browser.capabilities = {'browserVersion': '120.0.6099.71'}
        
        self.manager._apply_anti_detection(mock_browser)
        
        # Check that anti-detection measures were applied
        mock_browser.execute_script.assert_called()
        mock_browser.execute_cdp_cmd.assert_called()
        
    def test_get_driver_version(self):
        """Test driver version extraction"""
        mock_browser = Mock(spec=WebDriver)
        mock_browser.capabilities = {'browserVersion': '120.0.6099.71'}
        
        version = self.manager._get_driver_version(mock_browser)
        
        assert version == '120'
        
    def test_get_driver_version_fallback(self):
        """Test driver version fallback"""
        mock_browser = Mock(spec=WebDriver)
        mock_browser.capabilities = {}
        
        version = self.manager._get_driver_version(mock_browser)
        
        assert version == '120'
        
    def test_destroy_browser(self):
        """Test browser destruction"""
        mock_browser = Mock(spec=WebDriver)
        mock_browser.quit = Mock()
        
        self.manager.destroy_browser(mock_browser)
        
        mock_browser.quit.assert_called_once()
        
    def test_destroy_browser_with_error(self):
        """Test browser destruction with error"""
        mock_browser = Mock(spec=WebDriver)
        mock_browser.quit = Mock(side_effect=Exception("Test error"))
        
        # Should not raise exception
        self.manager.destroy_browser(mock_browser)
        
        mock_browser.quit.assert_called_once()


class TestCreateModernBrowser:
    """Test cases for create_modern_browser factory function"""
    
    @patch('tv.core.browser_manager.ModernBrowserManager')
    def test_create_modern_browser(self, mock_manager_class):
        """Test browser creation via factory function"""
        mock_manager = Mock()
        mock_browser = Mock(spec=WebDriver)
        mock_manager.create_browser.return_value = mock_browser
        mock_manager_class.return_value = mock_manager
        
        config = {'test': 'config'}
        result = create_modern_browser(config, resolution='1920,1080')
        
        # Assertions
        mock_manager_class.assert_called_once_with(config)
        mock_manager.create_browser.assert_called_once_with(resolution='1920,1080')
        assert result == mock_browser


@pytest.fixture
def mock_tools():
    """Mock tools module"""
    with patch('tv.core.browser_manager.tools') as mock:
        mock.get_operating_system.return_value = 'linux'
        mock.set_permission = Mock()
        yield mock


class TestBrowserManagerIntegration:
    """Integration tests for browser manager"""
    
    def test_browser_manager_with_mock_tools(self, mock_tools):
        """Test browser manager with mocked tools"""
        config = TEST_CONFIG.copy()
        manager = ModernBrowserManager(config)
        
        # Test that tools are used correctly
        options = manager._configure_chrome_options(True, '1920,1080', None)
        
        # Should have Linux-specific options
        assert '--no-sandbox' in options.arguments
        
    @patch('tv.core.browser_manager.Path')
    def test_custom_webdriver_path(self, mock_path):
        """Test custom webdriver path configuration"""
        # Mock path to exist
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance
        
        config = TEST_CONFIG.copy()
        config['webdriver_path'] = '/custom/chromedriver'
        manager = ModernBrowserManager(config)
        
        service = manager._configure_chrome_service()
        
        # Should use custom path
        mock_path.assert_called_with('/custom/chromedriver')
        mock_path_instance.exists.assert_called_once()
        
    def test_performance_optimizations(self):
        """Test performance optimization options"""
        config = TEST_CONFIG.copy()
        config['captcha_extension'] = False
        manager = ModernBrowserManager(config)
        
        options = manager._configure_chrome_options(True, '1920,1080', None)
        
        # Check performance options
        assert '--disable-extensions' in options.arguments
        assert '--disable-notifications' in options.arguments
        assert '--disable-gpu' in options.arguments
        assert '--memory-pressure-off' in options.arguments


if __name__ == '__main__':
    pytest.main([__file__, '-v'])