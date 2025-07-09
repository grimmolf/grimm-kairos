"""
Test suite for configuration manager functionality
"""

import pytest
import tempfile
import os
import json
import yaml
from unittest.mock import Mock, patch, mock_open

from tv.core.config_manager import ConfigManager
from tests import TEST_CONFIG


class TestConfigManager:
    """Test cases for ConfigManager"""
    
    def test_init_with_defaults(self):
        """Test initialization with default values"""
        config_manager = ConfigManager()
        
        # Check that defaults are loaded
        assert config_manager.get('web_browser') == 'chrome'
        assert config_manager.get('run_in_background') is True
        assert config_manager.get('wait_time') == 30
        assert config_manager.get('max_alerts') == 300
        
    def test_init_with_config_file(self):
        """Test initialization with config file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            f.write("web_browser=firefox\n")
            f.write("wait_time=60\n")
            f.write("run_in_background=false\n")
            config_file = f.name
            
        try:
            config_manager = ConfigManager(config_file)
            
            # Check that config file values override defaults
            assert config_manager.get('web_browser') == 'firefox'
            assert config_manager.get('wait_time') == 60
            assert config_manager.get('run_in_background') is False
            
        finally:
            os.unlink(config_file)
            
    def test_find_config_file(self):
        """Test config file discovery"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            f.write("test=value\n")
            config_file = f.name
            
        try:
            # Copy to expected location
            expected_path = '_kairos.cfg'
            os.rename(config_file, expected_path)
            
            config_manager = ConfigManager()
            found_file = config_manager._find_config_file()
            
            assert found_file == expected_path
            
        finally:
            if os.path.exists(expected_path):
                os.unlink(expected_path)
                
    def test_load_yaml_config(self):
        """Test YAML configuration loading"""
        yaml_data = {
            'web_browser': 'firefox',
            'wait_time': 45,
            'export_settings': {
                'csv_path': './test_csv'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(yaml_data, f)
            config_file = f.name
            
        try:
            config_manager = ConfigManager(config_file)
            
            assert config_manager.get('web_browser') == 'firefox'
            assert config_manager.get('wait_time') == 45
            assert config_manager.get('export_settings') == {'csv_path': './test_csv'}
            
        finally:
            os.unlink(config_file)
            
    def test_load_json_config(self):
        """Test JSON configuration loading"""
        json_data = {
            'web_browser': 'edge',
            'wait_time': 25,
            'alert_settings': {
                'max_alerts': 500
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(json_data, f)
            config_file = f.name
            
        try:
            config_manager = ConfigManager(config_file)
            
            assert config_manager.get('web_browser') == 'edge'
            assert config_manager.get('wait_time') == 25
            assert config_manager.get('alert_settings') == {'max_alerts': 500}
            
        finally:
            os.unlink(config_file)
            
    def test_load_cfg_config(self):
        """Test CFG format configuration loading"""
        cfg_content = """
# Test configuration
web_browser=chrome
wait_time=35
run_in_background=true
max_alerts=250
download_path=/tmp/downloads
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            f.write(cfg_content)
            config_file = f.name
            
        try:
            config_manager = ConfigManager(config_file)
            
            assert config_manager.get('web_browser') == 'chrome'
            assert config_manager.get('wait_time') == 35
            assert config_manager.get('run_in_background') is True
            assert config_manager.get('max_alerts') == 250
            assert config_manager.get('download_path') == '/tmp/downloads'
            
        finally:
            os.unlink(config_file)
            
    def test_load_from_env(self):
        """Test loading configuration from environment variables"""
        config_manager = ConfigManager()
        
        with patch.dict(os.environ, {
            'KAIROS_WEB_BROWSER': 'firefox',
            'KAIROS_WAIT_TIME': '50',
            'KAIROS_RUN_IN_BACKGROUND': 'false',
            'KAIROS_MAX_ALERTS': '400'
        }):
            config_manager.load_from_env()
            
            assert config_manager.get('web_browser') == 'firefox'
            assert config_manager.get('wait_time') == 50
            assert config_manager.get('run_in_background') is False
            assert config_manager.get('max_alerts') == 400
            
    def test_update_from_args(self):
        """Test updating configuration from command line arguments"""
        config_manager = ConfigManager()
        
        args = {
            'web_browser': 'safari',
            'wait_time': 40,
            'run_in_background': False,
            'invalid_key': None  # Should be ignored
        }
        
        config_manager.update_from_args(args)
        
        assert config_manager.get('web_browser') == 'safari'
        assert config_manager.get('wait_time') == 40
        assert config_manager.get('run_in_background') is False
        assert config_manager.get('invalid_key') is None
        
    def test_validate_success(self):
        """Test successful configuration validation"""
        config_manager = ConfigManager()
        
        # Set valid configuration
        config_manager.set('max_alerts', 100)
        config_manager.set('wait_time', 30)
        
        errors = config_manager.validate()
        
        assert len(errors) == 0
        
    def test_validate_errors(self):
        """Test configuration validation with errors"""
        config_manager = ConfigManager()
        
        # Set invalid configuration
        config_manager.set('max_alerts', -1)
        config_manager.set('wait_time', 0)
        config_manager.set('send_email', True)
        config_manager.set('send_webhook', True)
        config_manager.set('send_to_gsheets', True)
        
        errors = config_manager.validate()
        
        assert len(errors) > 0
        assert any('max_alerts must be non-negative' in error for error in errors)
        assert any('wait_time must be at least 1 second' in error for error in errors)
        assert any('Email recipient' in error for error in errors)
        assert any('Webhook URL' in error for error in errors)
        assert any('Google Sheets ID' in error for error in errors)
        
    def test_get_alert_config(self):
        """Test getting alert-specific configuration"""
        config_manager = ConfigManager()
        
        config_manager.set('max_alerts', 200)
        config_manager.set('expiration_minutes', 1440)
        config_manager.set('clear_inactive_alerts', False)
        
        alert_config = config_manager.get_alert_config()
        
        assert alert_config['max_alerts'] == 200
        assert alert_config['expiration_minutes'] == 1440
        assert alert_config['clear_inactive'] is False
        
    def test_get_browser_config(self):
        """Test getting browser-specific configuration"""
        config_manager = ConfigManager()
        
        config_manager.set('web_browser', 'firefox')
        config_manager.set('resolution', '1600,900')
        config_manager.set('run_in_background', False)
        
        browser_config = config_manager.get_browser_config()
        
        assert browser_config['web_browser'] == 'firefox'
        assert browser_config['resolution'] == '1600,900'
        assert browser_config['run_in_background'] is False
        
    def test_get_export_config(self):
        """Test getting export-specific configuration"""
        config_manager = ConfigManager()
        
        config_manager.set('export_trades_to_csv', True)
        config_manager.set('send_email', True)
        config_manager.set('email_to', 'test@example.com')
        config_manager.set('send_webhook', True)
        config_manager.set('webhook_url', 'https://example.com/webhook')
        
        export_config = config_manager.get_export_config()
        
        assert export_config['csv']['enabled'] is True
        assert export_config['email']['enabled'] is True
        assert export_config['email']['to'] == 'test@example.com'
        assert export_config['webhook']['enabled'] is True
        assert export_config['webhook']['url'] == 'https://example.com/webhook'
        
    def test_save_config(self):
        """Test saving configuration to file"""
        config_manager = ConfigManager()
        
        config_manager.set('web_browser', 'chrome')
        config_manager.set('wait_time', 45)
        config_manager.set('test_setting', 'test_value')
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            config_file = f.name
            
        try:
            config_manager.save(config_file)
            
            # Verify file was created and contains expected content
            assert os.path.exists(config_file)
            
            with open(config_file, 'r') as f:
                content = f.read()
                
            assert 'web_browser=chrome' in content
            assert 'wait_time=45' in content
            assert 'test_setting=test_value' in content
            
        finally:
            os.unlink(config_file)
            
    def test_save_config_with_backup(self):
        """Test saving configuration with backup creation"""
        config_manager = ConfigManager()
        
        # Create existing config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            f.write("old_setting=old_value\n")
            config_file = f.name
            
        try:
            config_manager.save(config_file)
            
            # Verify backup was created
            backup_file = f"{config_file}.backup"
            assert os.path.exists(backup_file)
            
            with open(backup_file, 'r') as f:
                backup_content = f.read()
                
            assert 'old_setting=old_value' in backup_content
            
        finally:
            os.unlink(config_file)
            backup_file = f"{config_file}.backup"
            if os.path.exists(backup_file):
                os.unlink(backup_file)
                
    def test_dictionary_access(self):
        """Test dictionary-style access to configuration"""
        config_manager = ConfigManager()
        
        # Test getitem
        assert config_manager['web_browser'] == 'chrome'
        
        # Test setitem
        config_manager['test_key'] = 'test_value'
        assert config_manager.get('test_key') == 'test_value'
        
        # Test contains
        assert 'web_browser' in config_manager
        assert 'nonexistent_key' not in config_manager
        
    def test_is_float(self):
        """Test float detection method"""
        config_manager = ConfigManager()
        
        assert config_manager._is_float('3.14') is True
        assert config_manager._is_float('42') is False
        assert config_manager._is_float('not_a_number') is False
        assert config_manager._is_float('3.14.15') is False
        
    def test_type_conversion(self):
        """Test type conversion in CFG loading"""
        cfg_content = """
bool_true=true
bool_false=false
integer_value=42
float_value=3.14
string_value=hello world
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            f.write(cfg_content)
            config_file = f.name
            
        try:
            config_manager = ConfigManager(config_file)
            
            assert config_manager.get('bool_true') is True
            assert config_manager.get('bool_false') is False
            assert config_manager.get('integer_value') == 42
            assert config_manager.get('float_value') == 3.14
            assert config_manager.get('string_value') == 'hello world'
            
        finally:
            os.unlink(config_file)


class TestConfigManagerIntegration:
    """Integration tests for ConfigManager"""
    
    def test_full_configuration_lifecycle(self):
        """Test complete configuration lifecycle"""
        # Create initial config
        config_manager = ConfigManager()
        
        # Update from various sources
        config_manager.set('web_browser', 'firefox')
        config_manager.set('wait_time', 25)
        
        # Validate
        errors = config_manager.validate()
        assert len(errors) == 0
        
        # Save
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            config_file = f.name
            
        try:
            config_manager.save(config_file)
            
            # Load new instance from saved file
            new_config_manager = ConfigManager(config_file)
            
            # Verify settings persisted
            assert new_config_manager.get('web_browser') == 'firefox'
            assert new_config_manager.get('wait_time') == 25
            
        finally:
            os.unlink(config_file)
            
    def test_configuration_precedence(self):
        """Test configuration precedence (file < env < args)"""
        # Create config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            f.write("web_browser=chrome\n")
            f.write("wait_time=30\n")
            config_file = f.name
            
        try:
            config_manager = ConfigManager(config_file)
            
            # Override with environment
            with patch.dict(os.environ, {
                'KAIROS_WEB_BROWSER': 'firefox',
                'KAIROS_WAIT_TIME': '40'
            }):
                config_manager.load_from_env()
                
                assert config_manager.get('web_browser') == 'firefox'
                assert config_manager.get('wait_time') == 40
                
                # Override with args
                config_manager.update_from_args({
                    'web_browser': 'safari',
                    'wait_time': 50
                })
                
                assert config_manager.get('web_browser') == 'safari'
                assert config_manager.get('wait_time') == 50
                
        finally:
            os.unlink(config_file)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])