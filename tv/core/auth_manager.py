"""
TradingView Authentication Manager
Handles login, session management, and authentication state
Extracted from tv.py for better modularity
"""

import logging
import time
from typing import Optional, Dict, Any, Tuple
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from ..utils.selectors import CSSSelectors
from kairos import tools


class AuthenticationManager:
    """
    Manages TradingView authentication and session state
    """
    
    def __init__(self, config: Dict[str, Any], browser: WebDriver):
        self.config = config
        self.browser = browser
        self.logger = logging.getLogger(__name__)
        self.wait = WebDriverWait(browser, config.get('wait_time', 30))
        self.selectors = CSSSelectors()
        
    def is_logged_in(self) -> bool:
        """
        Check if user is currently logged in to TradingView
        
        Returns:
            True if logged in, False otherwise
        """
        try:
            # Check for logged-in account element
            account_elem = self.browser.find_element(
                By.CSS_SELECTOR, 
                self.selectors.get('account')
            )
            return account_elem is not None
        except NoSuchElementException:
            return False
            
    def get_username(self) -> Optional[str]:
        """
        Get the current logged-in username
        
        Returns:
            Username string or None if not logged in
        """
        try:
            username_elem = self.wait.until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR, 
                    self.selectors.get('username')
                ))
            )
            return username_elem.text if username_elem else None
        except TimeoutException:
            return None
            
    def get_account_level(self) -> Optional[str]:
        """
        Get the account subscription level (Basic, Pro, Premium, etc.)
        
        Returns:
            Account level string or None
        """
        try:
            level_elem = self.browser.find_element(
                By.CSS_SELECTOR,
                self.selectors.get('account_level')
            )
            return level_elem.text if level_elem else None
        except NoSuchElementException:
            return None
            
    def login(self, username: str, password: str, totp_code: Optional[str] = None) -> bool:
        """
        Perform login to TradingView
        
        Args:
            username: TradingView username or email
            password: Account password
            totp_code: Optional 2FA code
            
        Returns:
            True if login successful, False otherwise
        """
        try:
            # Navigate to TradingView if not already there
            current_url = self.browser.current_url
            if 'tradingview.com' not in current_url:
                self.browser.get('https://www.tradingview.com/')
                time.sleep(2)
                
            # Handle cookie consent if needed
            self._handle_cookie_consent()
            
            # Check if already logged in
            if self.is_logged_in():
                self.logger.info(f"Already logged in as {self.get_username()}")
                return True
                
            # Click sign in button
            self._click_sign_in()
            
            # Choose email login method
            self._select_email_login()
            
            # Enter credentials
            self._enter_credentials(username, password)
            
            # Handle 2FA if needed
            if totp_code or self._needs_2fa():
                if not self._handle_2fa(totp_code):
                    return False
                    
            # Verify login success
            return self._verify_login_success()
            
        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            return False
            
    def _handle_cookie_consent(self) -> None:
        """Handle cookie consent dialog if present"""
        try:
            # Try to find and click accept all cookies button
            accept_btn = self.browser.find_element(
                By.CSS_SELECTOR,
                self.selectors.get('btn_accept_all_cookies')
            )
            if accept_btn:
                accept_btn.click()
                time.sleep(1)
        except NoSuchElementException:
            # No cookie dialog present
            pass
            
    def _click_sign_in(self) -> None:
        """Click the sign in button"""
        try:
            # Click anonymous account button first
            anon_btn = self.wait.until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    self.selectors.get('anonymous_account')
                ))
            )
            anon_btn.click()
            time.sleep(0.5)
            
            # Then click sign in
            signin_btn = self.wait.until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    self.selectors.get('anonymous_signin')
                ))
            )
            signin_btn.click()
            
        except TimeoutException:
            raise Exception("Could not find sign in button")
            
    def _select_email_login(self) -> None:
        """Select email login method"""
        try:
            email_btn = self.wait.until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    self.selectors.get('btn_login_by_email')
                ))
            )
            email_btn.click()
            time.sleep(0.5)
        except TimeoutException:
            # May already be on email login screen
            pass
            
    def _enter_credentials(self, username: str, password: str) -> None:
        """Enter username and password"""
        # Enter username
        username_input = self.wait.until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                self.selectors.get('input_username')
            ))
        )
        username_input.clear()
        username_input.send_keys(username)
        
        # Enter password
        password_input = self.wait.until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                self.selectors.get('input_password')
            ))
        )
        password_input.clear()
        password_input.send_keys(password)
        
        # Submit form
        password_input.submit()
        
    def _needs_2fa(self) -> bool:
        """Check if 2FA is required"""
        try:
            self.wait.until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.selectors.get('input_2fa')
                ))
            )
            return True
        except TimeoutException:
            return False
            
    def _handle_2fa(self, totp_code: Optional[str]) -> bool:
        """Handle 2FA verification"""
        if not totp_code:
            self.logger.error("2FA required but no code provided")
            return False
            
        try:
            totp_input = self.wait.until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.selectors.get('input_2fa')
                ))
            )
            totp_input.clear()
            totp_input.send_keys(totp_code)
            totp_input.submit()
            return True
        except TimeoutException:
            self.logger.error("Could not find 2FA input field")
            return False
            
    def _verify_login_success(self) -> bool:
        """Verify that login was successful"""
        max_attempts = 10
        for i in range(max_attempts):
            if self.is_logged_in():
                username = self.get_username()
                level = self.get_account_level()
                self.logger.info(f"Successfully logged in as {username} ({level})")
                return True
            time.sleep(1)
            
        return False
        
    def logout(self) -> bool:
        """
        Logout from TradingView
        
        Returns:
            True if logout successful
        """
        try:
            if not self.is_logged_in():
                self.logger.info("Already logged out")
                return True
                
            # Click user menu
            user_menu = self.wait.until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    self.selectors.get('btn_user_menu')
                ))
            )
            user_menu.click()
            time.sleep(0.5)
            
            # Click logout
            logout_btn = self.wait.until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    self.selectors.get('btn_logout')
                ))
            )
            logout_btn.click()
            
            # Verify logout
            time.sleep(2)
            return not self.is_logged_in()
            
        except Exception as e:
            self.logger.error(f"Logout failed: {e}")
            return False
            
    def check_captcha(self) -> bool:
        """
        Check if CAPTCHA is present
        
        Returns:
            True if CAPTCHA detected
        """
        try:
            captcha = self.browser.find_element(
                By.CSS_SELECTOR,
                self.selectors.get('captcha')
            )
            return captcha is not None
        except NoSuchElementException:
            return False
            
    def handle_captcha(self, api_key: Optional[str] = None) -> bool:
        """
        Handle CAPTCHA challenge
        
        Args:
            api_key: Optional 2captcha API key for automated solving
            
        Returns:
            True if CAPTCHA handled successfully
        """
        if not self.check_captcha():
            return True
            
        if api_key and self.config.get('captcha_api_key'):
            # Automated CAPTCHA solving not implemented yet
            # This would integrate with 2captcha or similar service
            self.logger.warning("Automated CAPTCHA solving not yet implemented")
            
        # Manual CAPTCHA handling
        self.logger.info("CAPTCHA detected - please solve manually")
        
        # Wait for user to solve CAPTCHA
        max_wait = 120  # 2 minutes
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            if not self.check_captcha():
                self.logger.info("CAPTCHA solved successfully")
                return True
            time.sleep(2)
            
        self.logger.error("CAPTCHA timeout - not solved within time limit")
        return False
        
    def get_session_info(self) -> Dict[str, Any]:
        """
        Get current session information
        
        Returns:
            Dictionary with session details
        """
        return {
            'logged_in': self.is_logged_in(),
            'username': self.get_username(),
            'account_level': self.get_account_level(),
            'url': self.browser.current_url,
            'cookies': self.browser.get_cookies()
        }