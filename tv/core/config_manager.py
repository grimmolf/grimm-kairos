"""
Configuration Manager for Kairos
Centralized configuration handling with validation and defaults
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta

import yaml
from kairos import tools


class ConfigManager:
    """
    Manages all configuration for Kairos including:
    - Loading from multiple sources (files, env vars, CLI args)
    - Validation and type checking
    - Default values
    - Runtime configuration updates
    """
    
    # Default configuration values
    DEFAULTS = {
        # Browser settings
        'web_browser': 'chrome',
        'run_in_background': True,
        'wait_time': 30,
        'wait_time_implicit': 0,
        'page_load_timeout': 60,
        'resolution': '1920,1080',
        'download_path': './downloads',
        
        # Authentication
        'username': None,
        'password': None,
        'totp_key': None,
        
        # Alert settings
        'max_alerts': 300,
        'expiration_minutes': 86400,  # 60 days
        'alert_cooldown': 1,
        'clear_inactive_alerts': True,
        'restart_inactive_alerts': False,
        
        # Screener settings
        'screener_sort_by': 'ticker',
        'screener_sort_order': 'asc',
        
        # Export settings
        'export_trades_to_csv': True,
        'export_summary_to_csv': True,
        'csv_path': './csv',
        
        # Email settings
        'send_email': False,
        'email_to': None,
        'email_subject': 'TradingView Alert',
        
        # Webhook settings
        'send_webhook': False,
        'webhook_url': None,
        'webhook_method': 'POST',
        
        # Google Sheets settings
        'send_to_gsheets': False,
        'gsheets_id': None,
        'gsheets_range': 'A1',
        
        # Logging
        'log_level': 'INFO',
        'log_to_file': True,
        'log_file': './log/kairos.log',
        
        # Advanced settings
        'captcha_api_key': None,
        'user_data_directory': None,
        'share_user_data': False,
        'options': None,
        'profile_path': None,
    }
    
    def __init__(self, config_file: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.config = self.DEFAULTS.copy()
        self._config_file = config_file or self._find_config_file()
        self._load_config()
        
    def _find_config_file(self) -> Optional[str]:
        """Find configuration file in standard locations"""
        search_paths = [
            '_kairos.cfg',
            'kairos.cfg',
            'config/kairos.cfg',
            os.path.expanduser('~/.kairos/config.cfg'),
            '/etc/kairos/config.cfg'
        ]
        
        for path in search_paths:
            if os.path.exists(path):
                self.logger.info(f"Found config file: {path}")
                return path
                
        return None
        
    def _load_config(self) -> None:
        """Load configuration from file"""
        if not self._config_file or not os.path.exists(self._config_file):
            self.logger.warning("No configuration file found, using defaults")
            return
            
        try:
            # Detect file format
            if self._config_file.endswith('.yaml') or self._config_file.endswith('.yml'):
                self._load_yaml_config()
            elif self._config_file.endswith('.json'):
                self._load_json_config()
            else:
                self._load_cfg_config()
                
            self.logger.info(f"Configuration loaded from {self._config_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to load config file: {e}")
            
    def _load_yaml_config(self) -> None:
        """Load YAML configuration file"""
        with open(self._config_file, 'r') as f:
            yaml_config = yaml.safe_load(f)
            if yaml_config:
                self.config.update(yaml_config)
                
    def _load_json_config(self) -> None:
        """Load JSON configuration file"""
        with open(self._config_file, 'r') as f:
            json_config = json.load(f)
            if json_config:
                self.config.update(json_config)
                
    def _load_cfg_config(self) -> None:
        """Load traditional CFG format (key=value)"""
        with open(self._config_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Type conversion
                    if value.lower() in ('true', 'false'):
                        value = value.lower() == 'true'
                    elif value.isdigit():
                        value = int(value)
                    elif self._is_float(value):
                        value = float(value)
                        
                    self.config[key] = value
                    
    def _is_float(self, value: str) -> bool:
        """Check if string is a valid float"""
        try:
            float(value)
            return '.' in value
        except ValueError:
            return False
            
    def load_from_env(self) -> None:
        """Load configuration from environment variables"""
        env_prefix = 'KAIROS_'
        
        for key in self.DEFAULTS:
            env_key = f"{env_prefix}{key.upper()}"
            if env_key in os.environ:
                value = os.environ[env_key]
                
                # Type conversion based on default type
                default_type = type(self.DEFAULTS[key])
                if default_type == bool:
                    value = value.lower() in ('true', '1', 'yes')
                elif default_type == int:
                    value = int(value)
                elif default_type == float:
                    value = float(value)
                    
                self.config[key] = value
                self.logger.debug(f"Loaded {key} from environment")
                
    def update_from_args(self, args: Dict[str, Any]) -> None:
        """Update configuration from command line arguments"""
        for key, value in args.items():
            if value is not None:
                self.config[key] = value
                
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
        
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.config[key] = value
        
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration as dictionary"""
        return self.config.copy()
        
    def validate(self) -> List[str]:
        """
        Validate configuration and return list of errors
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Required fields for certain features
        if self.config.get('send_email'):
            if not self.config.get('email_to'):
                errors.append("Email recipient (email_to) required when send_email is enabled")
                
        if self.config.get('send_webhook'):
            if not self.config.get('webhook_url'):
                errors.append("Webhook URL required when send_webhook is enabled")
                
        if self.config.get('send_to_gsheets'):
            if not self.config.get('gsheets_id'):
                errors.append("Google Sheets ID required when send_to_gsheets is enabled")
                
        # Value range validation
        if self.config.get('max_alerts', 0) < 0:
            errors.append("max_alerts must be non-negative")
            
        if self.config.get('wait_time', 30) < 1:
            errors.append("wait_time must be at least 1 second")
            
        # Path validation
        download_path = self.config.get('download_path')
        if download_path and not os.path.exists(download_path):
            try:
                os.makedirs(download_path, exist_ok=True)
            except Exception:
                errors.append(f"Cannot create download path: {download_path}")
                
        return errors
        
    def get_alert_config(self) -> Dict[str, Any]:
        """Get alert-specific configuration"""
        return {
            'max_alerts': self.config.get('max_alerts'),
            'expiration_minutes': self.config.get('expiration_minutes'),
            'clear_inactive': self.config.get('clear_inactive_alerts'),
            'restart_inactive': self.config.get('restart_inactive_alerts'),
            'cooldown': self.config.get('alert_cooldown'),
        }
        
    def get_browser_config(self) -> Dict[str, Any]:
        """Get browser-specific configuration"""
        return {
            'web_browser': self.config.get('web_browser'),
            'run_in_background': self.config.get('run_in_background'),
            'resolution': self.config.get('resolution'),
            'wait_time': self.config.get('wait_time'),
            'wait_time_implicit': self.config.get('wait_time_implicit'),
            'page_load_timeout': self.config.get('page_load_timeout'),
            'user_data_directory': self.config.get('user_data_directory'),
            'share_user_data': self.config.get('share_user_data'),
            'options': self.config.get('options'),
            'webdriver_path': self.config.get('webdriver_path'),
            'web_browser_path': self.config.get('web_browser_path'),
        }
        
    def get_export_config(self) -> Dict[str, Any]:
        """Get export-specific configuration"""
        return {
            'csv': {
                'enabled': self.config.get('export_trades_to_csv'),
                'summary': self.config.get('export_summary_to_csv'),
                'path': self.config.get('csv_path'),
            },
            'email': {
                'enabled': self.config.get('send_email'),
                'to': self.config.get('email_to'),
                'subject': self.config.get('email_subject'),
            },
            'webhook': {
                'enabled': self.config.get('send_webhook'),
                'url': self.config.get('webhook_url'),
                'method': self.config.get('webhook_method'),
            },
            'gsheets': {
                'enabled': self.config.get('send_to_gsheets'),
                'id': self.config.get('gsheets_id'),
                'range': self.config.get('gsheets_range'),
            }
        }
        
    def save(self, path: Optional[str] = None) -> None:
        """Save current configuration to file"""
        save_path = path or self._config_file or '_kairos.cfg'
        
        # Create backup if file exists
        if os.path.exists(save_path):
            backup_path = f"{save_path}.backup"
            os.rename(save_path, backup_path)
            
        try:
            with open(save_path, 'w') as f:
                f.write("# Kairos Configuration File\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
                
                # Group settings by category
                categories = {
                    'Browser Settings': ['web_browser', 'run_in_background', 'resolution', 'wait_time'],
                    'Authentication': ['username', 'password', 'totp_key'],
                    'Alert Settings': ['max_alerts', 'expiration_minutes', 'alert_cooldown'],
                    'Export Settings': ['send_email', 'send_webhook', 'send_to_gsheets'],
                }
                
                for category, keys in categories.items():
                    f.write(f"\n# {category}\n")
                    for key in keys:
                        if key in self.config:
                            value = self.config[key]
                            if value is not None:
                                f.write(f"{key}={value}\n")
                                
                # Write remaining settings
                f.write("\n# Other Settings\n")
                written_keys = set(sum(categories.values(), []))
                for key, value in self.config.items():
                    if key not in written_keys and value is not None:
                        f.write(f"{key}={value}\n")
                        
            self.logger.info(f"Configuration saved to {save_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            # Restore backup if save failed
            if os.path.exists(f"{save_path}.backup"):
                os.rename(f"{save_path}.backup", save_path)
                
    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access"""
        return self.config[key]
        
    def __setitem__(self, key: str, value: Any) -> None:
        """Allow dictionary-style assignment"""
        self.config[key] = value
        
    def __contains__(self, key: str) -> bool:
        """Allow 'in' operator"""
        return key in self.config