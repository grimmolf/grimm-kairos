"""
TradingView Alert Creation and Management
Handles creating, editing, and managing alerts
"""

import logging
import time
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from ..utils.selectors import CSSSelectors


class AlertCreator:
    """
    Manages alert creation and modification on TradingView
    """
    
    def __init__(self, browser: WebDriver, config: Dict[str, Any]):
        self.browser = browser
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.wait = WebDriverWait(browser, config.get('wait_time', 30))
        self.selectors = CSSSelectors()
        
    def create_alert(self, alert_config: Dict[str, Any]) -> bool:
        """
        Create a new alert based on configuration
        
        Args:
            alert_config: Dictionary containing alert parameters
            
        Returns:
            True if alert created successfully
        """
        try:
            # Open alert dialog
            if not self._open_alert_dialog():
                return False
                
            # Configure alert conditions
            if not self._configure_conditions(alert_config):
                self._close_alert_dialog()
                return False
                
            # Set alert options
            self._set_alert_options(alert_config)
            
            # Configure notifications
            self._configure_notifications(alert_config)
            
            # Set expiration
            self._set_expiration(alert_config)
            
            # Set name and message
            self._set_name_and_message(alert_config)
            
            # Submit alert
            return self._submit_alert()
            
        except Exception as e:
            self.logger.error(f"Failed to create alert: {e}")
            self._close_alert_dialog()
            return False
            
    def _open_alert_dialog(self) -> bool:
        """Open the alert creation dialog"""
        try:
            # Click alert button in header
            alert_btn = self.wait.until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    self.selectors.get('btn_create_alert')
                ))
            )
            alert_btn.click()
            
            # Wait for dialog to appear
            self.wait.until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.selectors.get('dlg_alert')
                ))
            )
            
            time.sleep(0.5)  # Animation delay
            return True
            
        except TimeoutException:
            self.logger.error("Failed to open alert dialog")
            return False
            
    def _close_alert_dialog(self) -> None:
        """Close the alert dialog"""
        try:
            close_btn = self.browser.find_element(
                By.CSS_SELECTOR,
                self.selectors.get('btn_alert_cancel')
            )
            close_btn.click()
        except NoSuchElementException:
            pass
            
    def _configure_conditions(self, alert_config: Dict[str, Any]) -> bool:
        """Configure alert conditions"""
        try:
            # First dropdown - alert type/source
            condition_type = alert_config.get('condition_type', 'Price')
            if not self._select_dropdown_option(
                self.selectors.get('dlg_create_alert_first_row_first_item'),
                condition_type
            ):
                return False
                
            # Check if second item exists (for complex conditions)
            if self._element_exists(self.selectors.get('exists_dlg_create_alert_first_row_second_item')):
                if 'condition_source' in alert_config:
                    self._select_dropdown_option(
                        self.selectors.get('dlg_create_alert_first_row_second_item'),
                        alert_config['condition_source']
                    )
                    
            # Second row - condition operator
            if 'operator' in alert_config:
                self._select_dropdown_option(
                    self.selectors.get('dlg_create_alert_second_row'),
                    alert_config['operator']
                )
                
            # Third row and beyond - values and additional options
            self._configure_condition_values(alert_config)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to configure conditions: {e}")
            return False
            
    def _select_dropdown_option(self, selector: str, value: str) -> bool:
        """Select an option from a dropdown"""
        try:
            # Click dropdown
            dropdown = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            dropdown.click()
            time.sleep(0.3)
            
            # Find and click option
            options = self.browser.find_elements(
                By.CSS_SELECTOR,
                self.selectors.get('dlg_create_alert_options')
            )
            
            for option in options:
                if value.lower() in option.text.lower():
                    option.click()
                    return True
                    
            self.logger.warning(f"Option '{value}' not found in dropdown")
            return False
            
        except Exception as e:
            self.logger.error(f"Dropdown selection failed: {e}")
            return False
            
    def _configure_condition_values(self, alert_config: Dict[str, Any]) -> None:
        """Configure condition values (price levels, indicators, etc.)"""
        try:
            # Get all input fields and dropdowns in the third row and beyond
            elements = self.browser.find_elements(
                By.CSS_SELECTOR,
                self.selectors.get('inputs_and_selects_create_alert_3rd_row_and_above')
            )
            
            # Map configuration to inputs
            value_keys = ['value', 'value2', 'period', 'source']
            element_index = 0
            
            for key in value_keys:
                if key in alert_config and element_index < len(elements):
                    element = elements[element_index]
                    
                    if element.tag_name == 'input':
                        element.clear()
                        element.send_keys(str(alert_config[key]))
                    else:
                        # It's a dropdown
                        element.click()
                        time.sleep(0.3)
                        self._select_dropdown_value(alert_config[key])
                        
                    element_index += 1
                    
        except Exception as e:
            self.logger.warning(f"Error configuring values: {e}")
            
    def _set_alert_options(self, alert_config: Dict[str, Any]) -> None:
        """Set alert triggering options"""
        # Alert frequency is typically set in the condition dropdowns
        # This is a placeholder for future options
        pass
        
    def _configure_notifications(self, alert_config: Dict[str, Any]) -> None:
        """Configure notification settings"""
        try:
            # Switch to notifications tab
            notif_tab = self.wait.until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    self.selectors.get('dlg_create_alert_notifications_button')
                ))
            )
            notif_tab.click()
            time.sleep(0.3)
            
            # Configure notification checkboxes
            notifications = {
                'notify_on_app': self.selectors.get('dlg_create_alert_notifications_notify_on_app_checkbox'),
                'show_popup': self.selectors.get('dlg_create_alert_notifications_show_popup_checkbox'),
                'send_email': self.selectors.get('dlg_create_alert_notifications_send_email_checkbox'),
                'webhook_enabled': self.selectors.get('dlg_create_alert_notifications_webhook_checkbox'),
                'play_sound': self.selectors.get('dlg_create_alert_notifications_play_sound_checkbox'),
                'send_email_to_sms': self.selectors.get('dlg_create_alert_notifications_email_to_sms_checkbox'),
            }
            
            for key, selector in notifications.items():
                if key in alert_config:
                    self._set_checkbox(selector, alert_config[key])
                    
            # Configure webhook URL if enabled
            if alert_config.get('webhook_enabled') and 'webhook_url' in alert_config:
                webhook_input = self.browser.find_element(
                    By.CSS_SELECTOR,
                    self.selectors.get('dlg_create_alert_notifications_webhook_text')
                )
                webhook_input.clear()
                webhook_input.send_keys(alert_config['webhook_url'])
                
            # Configure sound settings
            if alert_config.get('play_sound'):
                if 'sound_duration' in alert_config:
                    self._set_sound_duration(alert_config['sound_duration'])
                if 'sound_ringtone' in alert_config:
                    self._set_sound_ringtone(alert_config['sound_ringtone'])
                    
        except Exception as e:
            self.logger.warning(f"Error configuring notifications: {e}")
            
    def _set_checkbox(self, selector: str, checked: bool) -> None:
        """Set checkbox state"""
        try:
            checkbox = self.browser.find_element(By.CSS_SELECTOR, selector)
            if checkbox.is_selected() != checked:
                checkbox.click()
        except NoSuchElementException:
            pass
            
    def _set_sound_duration(self, duration: str) -> None:
        """Set sound duration"""
        try:
            duration_btn = self.browser.find_element(
                By.CSS_SELECTOR,
                self.selectors.get('dlg_create_alert_notifications_sound_duration_button')
            )
            duration_btn.click()
            time.sleep(0.3)
            
            options = self.browser.find_elements(
                By.CSS_SELECTOR,
                self.selectors.get('dlg_create_alert_notifications_sound_duration_options')
            )
            
            for option in options:
                if duration in option.text:
                    option.click()
                    break
                    
        except Exception:
            pass
            
    def _set_sound_ringtone(self, ringtone: str) -> None:
        """Set sound ringtone"""
        try:
            ringtone_btn = self.browser.find_element(
                By.CSS_SELECTOR,
                self.selectors.get('dlg_create_alert_notifications_sound_ringtone_button')
            )
            ringtone_btn.click()
            time.sleep(0.3)
            
            options = self.browser.find_elements(
                By.CSS_SELECTOR,
                self.selectors.get('dlg_create_alert_notifications_sound_ringtone_options')
            )
            
            for option in options:
                if ringtone.lower() in option.text.lower():
                    option.click()
                    break
                    
        except Exception:
            pass
            
    def _set_expiration(self, alert_config: Dict[str, Any]) -> None:
        """Set alert expiration"""
        try:
            # Get expiration setting
            expiration_minutes = alert_config.get('expiration_minutes', 86400)  # 60 days default
            
            if expiration_minutes <= 0:
                # Set as open-ended
                self._set_open_ended_expiration()
            else:
                # Calculate expiration datetime
                expiration_dt = datetime.now() + timedelta(minutes=expiration_minutes)
                self._set_expiration_datetime(expiration_dt)
                
        except Exception as e:
            self.logger.warning(f"Error setting expiration: {e}")
            
    def _set_open_ended_expiration(self) -> None:
        """Set alert to never expire"""
        try:
            # Click expiration button
            exp_btn = self.browser.find_element(
                By.CSS_SELECTOR,
                self.selectors.get('dlg_create_alert_expiration_button')
            )
            exp_btn.click()
            time.sleep(0.3)
            
            # Check open-ended checkbox
            checkbox = self.browser.find_element(
                By.CSS_SELECTOR,
                self.selectors.get('dlg_create_alert_open_ended_checkbox')
            )
            if not checkbox.is_selected():
                checkbox.click()
                
            # Confirm
            confirm_btn = self.browser.find_element(
                By.CSS_SELECTOR,
                self.selectors.get('dlg_create_alert_expiration_confirmation_button')
            )
            confirm_btn.click()
            
        except Exception:
            pass
            
    def _set_expiration_datetime(self, expiration_dt: datetime) -> None:
        """Set specific expiration date and time"""
        try:
            # Click expiration button
            exp_btn = self.browser.find_element(
                By.CSS_SELECTOR,
                self.selectors.get('dlg_create_alert_expiration_button')
            )
            exp_btn.click()
            time.sleep(0.3)
            
            # Uncheck open-ended if checked
            checkbox = self.browser.find_element(
                By.CSS_SELECTOR,
                self.selectors.get('dlg_create_alert_open_ended_checkbox')
            )
            if checkbox.is_selected():
                checkbox.click()
                
            # Set date
            date_input = self.browser.find_element(
                By.CSS_SELECTOR,
                self.selectors.get('dlg_create_alert_expiration_date')
            )
            date_input.clear()
            date_input.send_keys(expiration_dt.strftime('%m/%d/%Y'))
            
            # Set time
            time_input = self.browser.find_element(
                By.CSS_SELECTOR,
                self.selectors.get('dlg_create_alert_expiration_time')
            )
            time_input.clear()
            time_input.send_keys(expiration_dt.strftime('%H:%M'))
            
            # Confirm
            confirm_btn = self.browser.find_element(
                By.CSS_SELECTOR,
                self.selectors.get('dlg_create_alert_expiration_confirmation_button')
            )
            confirm_btn.click()
            
        except Exception:
            pass
            
    def _set_name_and_message(self, alert_config: Dict[str, Any]) -> None:
        """Set alert name and message"""
        try:
            # Set name
            if 'name' in alert_config:
                name_input = self.browser.find_element(
                    By.CSS_SELECTOR,
                    self.selectors.get('dlg_create_alert_name')
                )
                name_input.clear()
                name_input.send_keys(alert_config['name'])
                
            # Set message
            if 'message' in alert_config:
                msg_input = self.browser.find_element(
                    By.CSS_SELECTOR,
                    self.selectors.get('dlg_create_alert_message')
                )
                msg_input.clear()
                msg_input.send_keys(alert_config['message'])
                
        except Exception as e:
            self.logger.warning(f"Error setting name/message: {e}")
            
    def _submit_alert(self) -> bool:
        """Submit the alert"""
        try:
            # Click submit button
            submit_btn = self.wait.until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    self.selectors.get('btn_dlg_create_alert_submit')
                ))
            )
            submit_btn.click()
            
            # Check for warnings
            if self._handle_alert_warnings():
                # Wait for dialog to close
                self.wait.until_not(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR,
                        self.selectors.get('dlg_alert')
                    ))
                )
                
                self.logger.info("Alert created successfully")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to submit alert: {e}")
            return False
            
    def _handle_alert_warnings(self) -> bool:
        """Handle any warning dialogs that appear"""
        try:
            # Check for repainting warning
            warning_checkbox = self.browser.find_element(
                By.CSS_SELECTOR,
                self.selectors.get('btn_create_alert_warning_continue_anyway_got_it')
            )
            if warning_checkbox:
                warning_checkbox.click()
                
                continue_btn = self.browser.find_element(
                    By.CSS_SELECTOR,
                    self.selectors.get('btn_create_alert_warning_continue_anyway')
                )
                continue_btn.click()
                
            return True
            
        except NoSuchElementException:
            # No warnings present
            return True
            
    def _element_exists(self, selector: str) -> bool:
        """Check if element exists"""
        try:
            self.browser.find_element(By.CSS_SELECTOR, selector)
            return True
        except NoSuchElementException:
            return False
            
    def _select_dropdown_value(self, value: str) -> None:
        """Select value from open dropdown"""
        options = self.browser.find_elements(
            By.CSS_SELECTOR,
            self.selectors.get('dlg_create_alert_options')
        )
        
        for option in options:
            if str(value).lower() in option.text.lower():
                option.click()
                break
                
    def get_alert_count(self) -> int:
        """Get current number of alerts"""
        try:
            counter = self.browser.find_element(
                By.CSS_SELECTOR,
                self.selectors.get('alerts_counter')
            )
            # Extract number from text like "5" or "5/10"
            text = counter.text
            if '/' in text:
                return int(text.split('/')[0])
            return int(text)
        except:
            return 0
            
    def clear_all_alerts(self) -> bool:
        """Clear all existing alerts"""
        try:
            # Open alert menu
            menu_btn = self.wait.until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    self.selectors.get('btn_alert_menu')
                ))
            )
            menu_btn.click()
            time.sleep(0.5)
            
            # Click clear all alerts
            clear_btn = self.browser.find_element(
                By.CSS_SELECTOR,
                self.selectors.get('item_clear_alerts')
            )
            clear_btn.click()
            
            # Confirm
            confirm_btn = self.wait.until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    self.selectors.get('btn_dlg_clear_alerts_confirm')
                ))
            )
            confirm_btn.click()
            
            self.logger.info("All alerts cleared")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to clear alerts: {e}")
            return False