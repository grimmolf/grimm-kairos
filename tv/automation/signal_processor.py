"""
Signal Processing and Management
Handles processing of signals from strategies and indicators
"""

import logging
import time
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from ..utils.selectors import CSSSelectors


class SignalProcessor:
    """
    Processes and manages trading signals from TradingView
    """
    
    def __init__(self, browser: WebDriver, config: Dict[str, Any]):
        self.browser = browser
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.wait = WebDriverWait(browser, config.get('wait_time', 30))
        self.selectors = CSSSelectors()
        
    def process_strategy_signals(self, strategy_name: str) -> Dict[str, Any]:
        """
        Process signals from a trading strategy
        
        Args:
            strategy_name: Name of the strategy to process
            
        Returns:
            Dictionary containing strategy performance and signals
        """
        try:
            # Open strategy tester
            if not self._open_strategy_tester():
                return {}
                
            # Verify strategy is loaded
            if not self._verify_strategy_loaded(strategy_name):
                self.logger.error(f"Strategy '{strategy_name}' not loaded")
                return {}
                
            # Get performance metrics
            performance = self._get_performance_metrics()
            
            # Get trade list
            trades = self._get_trade_list()
            
            # Get current signal
            current_signal = self._get_current_signal()
            
            return {
                'strategy': strategy_name,
                'timestamp': datetime.now().isoformat(),
                'performance': performance,
                'trades': trades,
                'current_signal': current_signal,
                'status': 'success'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to process strategy signals: {e}")
            return {
                'strategy': strategy_name,
                'status': 'error',
                'error': str(e)
            }
            
    def _open_strategy_tester(self) -> bool:
        """Open the strategy tester panel"""
        try:
            # Check if already open
            tester_tab = self.browser.find_element(
                By.CSS_SELECTOR,
                self.selectors.get('tab_strategy_tester')
            )
            
            # If not active, click it
            if 'false' in tester_tab.get_attribute('data-active'):
                tester_tab.click()
                time.sleep(1)
                
            return True
            
        except NoSuchElementException:
            self.logger.error("Strategy tester tab not found")
            return False
            
    def _verify_strategy_loaded(self, strategy_name: str) -> bool:
        """Verify that the specified strategy is loaded"""
        try:
            strategy_elem = self.browser.find_element(
                By.CSS_SELECTOR,
                self.selectors.get('strategy_id')
            )
            
            loaded_strategy = strategy_elem.get_attribute('data-strategy-title')
            return strategy_name.lower() in loaded_strategy.lower()
            
        except NoSuchElementException:
            return False
            
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Extract performance metrics from strategy tester"""
        metrics = {}
        
        try:
            # Try to get overview metrics first
            overview_selectors = {
                'net_profit': 'performance_overview_net_profit',
                'net_profit_percent': 'performance_overview_net_profit_percentage',
                'total_trades': 'performance_overview_total_closed_trades',
                'percent_profitable': 'performance_overview_percent_profitable',
                'profit_factor': 'performance_overview_profit_factor',
                'max_drawdown': 'performance_overview_max_drawdown',
                'max_drawdown_percent': 'performance_overview_max_drawdown_percentage',
                'avg_trade': 'performance_overview_avg_trade',
                'avg_trade_percent': 'performance_overview_avg_trade_percentage',
                'avg_bars_in_trade': 'performance_overview_avg_bars_in_trade',
            }
            
            for key, selector_name in overview_selectors.items():
                try:
                    elem = self.browser.find_element(
                        By.CSS_SELECTOR,
                        self.selectors.get(selector_name)
                    )
                    value = elem.text.strip()
                    metrics[key] = self._parse_metric_value(value)
                except NoSuchElementException:
                    pass
                    
            # If overview not available, try performance summary tab
            if not metrics:
                self._switch_to_performance_summary()
                metrics = self._get_summary_metrics()
                
        except Exception as e:
            self.logger.warning(f"Error getting performance metrics: {e}")
            
        return metrics
        
    def _switch_to_performance_summary(self) -> None:
        """Switch to performance summary tab"""
        try:
            summary_tab = self.browser.find_element(
                By.CSS_SELECTOR,
                self.selectors.get('tab_strategy_tester_performance_summary')
            )
            if summary_tab.get_attribute('aria-selected') == 'false':
                summary_tab.click()
                time.sleep(0.5)
        except NoSuchElementException:
            pass
            
    def _get_summary_metrics(self) -> Dict[str, Any]:
        """Get metrics from performance summary tab"""
        metrics = {}
        
        summary_selectors = {
            'net_profit': 'performance_summary_net_profit',
            'net_profit_percent': 'performance_summary_net_profit_percentage',
            'total_trades': 'performance_summary_total_closed_trades',
            'percent_profitable': 'performance_summary_percent_profitable',
            'profit_factor': 'performance_summary_profit_factor',
            'max_drawdown': 'performance_summary_max_drawdown',
            'max_drawdown_percent': 'performance_summary_max_drawdown_percentage',
            'avg_trade': 'performance_summary_avg_trade',
            'avg_trade_percent': 'performance_summary_avg_trade_percentage',
            'avg_bars_in_trade': 'performance_summary_avg_bars_in_trade',
        }
        
        for key, selector_name in summary_selectors.items():
            try:
                elem = self.browser.find_element(
                    By.CSS_SELECTOR,
                    self.selectors.get(selector_name)
                )
                value = elem.text.strip()
                metrics[key] = self._parse_metric_value(value)
            except NoSuchElementException:
                pass
                
        return metrics
        
    def _parse_metric_value(self, value: str) -> Any:
        """Parse metric value to appropriate type"""
        if not value:
            return None
            
        # Remove currency symbols and commas
        value = value.replace('$', '').replace(',', '').strip()
        
        # Handle percentages
        if '%' in value:
            value = value.replace('%', '').strip()
            try:
                return float(value)
            except ValueError:
                return value
                
        # Handle negative values in parentheses
        if value.startswith('(') and value.endswith(')'):
            value = '-' + value[1:-1]
            
        # Try to convert to number
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            return value
            
    def _get_trade_list(self) -> List[Dict[str, Any]]:
        """Get list of trades from strategy tester"""
        trades = []
        
        try:
            # Switch to list of trades tab if available
            # This would need implementation based on TradingView's current UI
            # For now, return empty list
            pass
            
        except Exception as e:
            self.logger.warning(f"Error getting trade list: {e}")
            
        return trades
        
    def _get_current_signal(self) -> Optional[str]:
        """Get current signal from strategy"""
        try:
            # This would check for current buy/sell signal indicators
            # Implementation depends on how signals are displayed in the UI
            return None
            
        except Exception as e:
            self.logger.warning(f"Error getting current signal: {e}")
            return None
            
    def process_indicator_signals(self, indicators: List[str]) -> Dict[str, Any]:
        """
        Process signals from multiple indicators
        
        Args:
            indicators: List of indicator names to process
            
        Returns:
            Dictionary containing indicator values and signals
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'indicators': {}
        }
        
        try:
            # Open data window
            if not self._open_data_window():
                return results
                
            # Process each indicator
            for indicator in indicators:
                value = self._get_indicator_value(indicator)
                if value is not None:
                    results['indicators'][indicator] = value
                    
            results['status'] = 'success'
            
        except Exception as e:
            self.logger.error(f"Failed to process indicator signals: {e}")
            results['status'] = 'error'
            results['error'] = str(e)
            
        return results
        
    def _open_data_window(self) -> bool:
        """Open the data window panel"""
        try:
            # Click object tree button
            obj_tree_btn = self.wait.until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    self.selectors.get('btn_object_tree_and_data_window')
                ))
            )
            obj_tree_btn.click()
            time.sleep(0.5)
            
            # Switch to data window tab
            data_window_tab = self.wait.until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    self.selectors.get('btn_data_window')
                ))
            )
            
            # Click if not active
            if data_window_tab.get_attribute('tabindex') != '0':
                data_window_tab.click()
                time.sleep(0.5)
                
            return True
            
        except TimeoutException:
            self.logger.error("Failed to open data window")
            return False
            
    def _get_indicator_value(self, indicator_name: str) -> Optional[Any]:
        """Get current value of an indicator"""
        try:
            # Use XPath to find indicator by name
            xpath = self.selectors.get_xpath(
                'data_window_indicator',
                indicator_name
            )
            
            indicator_elem = self.browser.find_element(By.XPATH, xpath)
            
            # Get the value element (usually next sibling or child)
            value_elem = indicator_elem.find_element(
                By.XPATH,
                "./following-sibling::span[1]"
            )
            
            value_text = value_elem.text.strip()
            return self._parse_metric_value(value_text)
            
        except NoSuchElementException:
            self.logger.warning(f"Indicator '{indicator_name}' not found")
            return None
            
    def create_signal_alert(self, signal_config: Dict[str, Any]) -> bool:
        """
        Create an alert based on signal configuration
        
        Args:
            signal_config: Configuration for the signal alert
            
        Returns:
            True if alert created successfully
        """
        try:
            # This would use the AlertCreator to create alerts based on signals
            # For now, this is a placeholder
            from .alert_creator import AlertCreator
            
            alert_creator = AlertCreator(self.browser, self.config)
            
            # Convert signal config to alert config
            alert_config = self._convert_signal_to_alert_config(signal_config)
            
            return alert_creator.create_alert(alert_config)
            
        except Exception as e:
            self.logger.error(f"Failed to create signal alert: {e}")
            return False
            
    def _convert_signal_to_alert_config(self, signal_config: Dict[str, Any]) -> Dict[str, Any]:
        """Convert signal configuration to alert configuration"""
        alert_config = {
            'name': signal_config.get('name', 'Signal Alert'),
            'message': signal_config.get('message', 'Signal triggered'),
            'condition_type': signal_config.get('type', 'Indicator'),
            'notify_on_app': True,
            'send_email': signal_config.get('send_email', False),
            'webhook_enabled': signal_config.get('webhook_enabled', False),
            'webhook_url': signal_config.get('webhook_url'),
            'expiration_minutes': signal_config.get('expiration_minutes', 86400)
        }
        
        # Add condition-specific settings
        if 'indicator' in signal_config:
            alert_config['condition_source'] = signal_config['indicator']
            
        if 'operator' in signal_config:
            alert_config['operator'] = signal_config['operator']
            
        if 'value' in signal_config:
            alert_config['value'] = signal_config['value']
            
        return alert_config
        
    def export_signals(self, signals: Dict[str, Any], export_format: str = 'json') -> str:
        """
        Export signals to specified format
        
        Args:
            signals: Signal data to export
            export_format: Format to export to (json, csv, etc.)
            
        Returns:
            Exported data as string
        """
        if export_format == 'json':
            return json.dumps(signals, indent=2)
        elif export_format == 'csv':
            # Convert to CSV format
            csv_lines = []
            
            # Add headers
            csv_lines.append('Timestamp,Type,Value,Signal')
            
            # Add data rows
            if 'indicators' in signals:
                for name, value in signals['indicators'].items():
                    csv_lines.append(f"{signals['timestamp']},Indicator,{name},{value}")
                    
            return '\n'.join(csv_lines)
        else:
            return str(signals)
            
    def monitor_signals(self, callback, indicators: List[str], interval: int = 60) -> None:
        """
        Monitor signals and call callback when they change
        
        Args:
            callback: Function to call with signal data
            indicators: List of indicators to monitor
            interval: Check interval in seconds
        """
        last_values = {}
        
        try:
            while True:
                # Get current signals
                signals = self.process_indicator_signals(indicators)
                
                # Check for changes
                changed = False
                for indicator, value in signals.get('indicators', {}).items():
                    if indicator not in last_values or last_values[indicator] != value:
                        changed = True
                        last_values[indicator] = value
                        
                # Call callback if changed
                if changed:
                    callback(signals)
                    
                # Wait before next check
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.logger.info("Signal monitoring stopped")
        except Exception as e:
            self.logger.error(f"Error monitoring signals: {e}")