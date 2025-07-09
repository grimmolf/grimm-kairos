"""
TradingView Test Runner for Automated Indicator Testing

Integrates grimm-kairos automation with trading-setups strategies
for automated indicator testing and validation.
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

# Add grimm-kairos to path
kairos_path = Path(__file__).parent.parent.parent.parent / "grimm-kairos"
if kairos_path.exists():
    sys.path.insert(0, str(kairos_path))

try:
    from tv.core import ConfigManager, ModernBrowserManager, PerformanceMonitor
    from tv.automation import AlertCreator, SignalProcessor  
    from tv.utils import CSSSelectors, TimingUtils
    KAIROS_AVAILABLE = True
except ImportError:
    KAIROS_AVAILABLE = False
    logging.warning("Grimm-kairos not available. Please ensure it's installed and in the Python path.")

from .auth_manager import GrimmAuthManager

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Results from an indicator test."""
    strategy_name: str
    indicator_name: str 
    ticker: str
    timeframe: str
    success: bool
    values: Dict[str, float]
    signals: List[Dict[str, Any]]
    execution_time: float
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None


@dataclass 
class TestConfiguration:
    """Configuration for indicator testing."""
    strategy_path: str
    indicators: List[str]
    tickers: List[str] = None
    timeframes: List[str] = None
    test_duration: int = 300  # seconds
    capture_screenshots: bool = True
    parallel_execution: bool = True
    

class TradingViewTestRunner:
    """
    Automated TradingView indicator testing using grimm-kairos.
    
    Provides automated testing of trading strategy indicators with:
    - Multi-symbol testing (default: MNQ1!)
    - Multi-timeframe analysis
    - Screenshot capture
    - Performance monitoring
    - Parallel execution
    """
    
    def __init__(self, 
                 auth_manager: GrimmAuthManager,
                 kairos_config: Optional[Dict[str, Any]] = None,
                 results_dir: Optional[str] = None):
        """
        Initialize test runner.
        
        Args:
            auth_manager: Authenticated GrimmAuthManager instance
            kairos_config: Kairos configuration overrides
            results_dir: Directory for test results (default: ./test_results)
        """
        if not KAIROS_AVAILABLE:
            raise ImportError("Grimm-kairos is required for test runner functionality")
            
        self.auth_manager = auth_manager
        self.results_dir = Path(results_dir or "./test_results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Setup Kairos configuration
        self.config = ConfigManager()
        if kairos_config:
            for key, value in kairos_config.items():
                self.config.set(key, value)
                
        # Set defaults optimized for testing
        self._configure_defaults()
        
        # Initialize components
        self.browser_manager = None
        self.performance_monitor = None
        self.selectors = CSSSelectors()
        self.timing_utils = TimingUtils()
        
        # Default test configuration
        self.default_tickers = ["MNQ1!"]  # NQ Futures as specified
        self.default_timeframes = ["1m", "5m", "15m", "1h", "4h", "1d"]
        
    def _configure_defaults(self) -> None:
        """Configure default settings optimized for testing."""
        defaults = {
            'web_browser': 'chrome',
            'run_in_background': False,  # Show browser for testing
            'wait_time': 30,
            'max_alerts': 50,
            'read_from_data_window': True,
            'wait_until_chart_is_loaded': True,
            'change_symbol_with_space': True,
            'performance_monitoring': True,
            'async_settings': {
                'max_workers': 4,
                'connection_pool_size': 10
            }
        }
        
        for key, value in defaults.items():
            if not self.config.has(key):
                self.config.set(key, value)
                
    async def initialize(self) -> bool:
        """Initialize test runner components."""
        try:
            # Initialize performance monitoring
            self.performance_monitor = PerformanceMonitor(self.config)
            
            # Initialize browser manager
            self.browser_manager = ModernBrowserManager(self.config)
            
            # Verify authentication
            if not self.auth_manager.is_authenticated():
                logger.error("Authentication required before running tests")
                return False
                
            logger.info("Test runner initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize test runner: {e}")
            return False
            
    async def test_strategy_indicators(self, 
                                     config: TestConfiguration) -> List[TestResult]:
        """
        Test all indicators for a strategy.
        
        Args:
            config: Test configuration
            
        Returns:
            List of test results for each indicator/ticker/timeframe combination
        """
        if not await self.initialize():
            return []
            
        results = []
        tickers = config.tickers or self.default_tickers
        timeframes = config.timeframes or self.default_timeframes
        
        try:
            with self.performance_monitor.performance_timer('strategy_testing'):
                # Load strategy
                strategy_data = await self._load_strategy(config.strategy_path)
                if not strategy_data:
                    return []
                    
                # Test each indicator
                for indicator_name in config.indicators:
                    for ticker in tickers:
                        for timeframe in timeframes:
                            try:
                                result = await self._test_single_indicator(
                                    strategy_data['name'],
                                    indicator_name,
                                    ticker, 
                                    timeframe,
                                    config
                                )
                                results.append(result)
                                
                            except Exception as e:
                                logger.error(f"Failed to test {indicator_name} on {ticker} {timeframe}: {e}")
                                results.append(TestResult(
                                    strategy_name=strategy_data.get('name', 'Unknown'),
                                    indicator_name=indicator_name,
                                    ticker=ticker,
                                    timeframe=timeframe,
                                    success=False,
                                    values={},
                                    signals=[],
                                    execution_time=0,
                                    error_message=str(e)
                                ))
                                
            # Save results
            await self._save_test_results(results, config.strategy_path)
            
            return results
            
        except Exception as e:
            logger.error(f"Strategy testing failed: {e}")
            return results
            
    async def _load_strategy(self, strategy_path: str) -> Optional[Dict[str, Any]]:
        """Load strategy configuration from path."""
        try:
            strategy_dir = Path(strategy_path)
            if not strategy_dir.exists():
                logger.error(f"Strategy directory not found: {strategy_path}")
                return None
                
            # Look for README.md or strategy configuration
            readme_file = strategy_dir / "README.md"
            if readme_file.exists():
                # Parse strategy metadata from README
                with open(readme_file, 'r') as f:
                    content = f.read()
                    
                return {
                    'name': strategy_dir.name,
                    'path': str(strategy_dir),
                    'readme_content': content,
                    'pinescript_dir': strategy_dir / "pinescript",
                    'thinkscript_dir': strategy_dir / "thinkscript"
                }
                
            logger.warning(f"No README.md found in {strategy_path}")
            return {
                'name': strategy_dir.name,
                'path': str(strategy_dir)
            }
            
        except Exception as e:
            logger.error(f"Failed to load strategy: {e}")
            return None
            
    async def _test_single_indicator(self,
                                   strategy_name: str,
                                   indicator_name: str,
                                   ticker: str,
                                   timeframe: str,
                                   config: TestConfiguration) -> TestResult:
        """Test a single indicator on a specific ticker/timeframe."""
        start_time = datetime.now()
        
        try:
            with self.performance_monitor.performance_timer(f'test_{indicator_name}'):
                # Create browser session
                browser = self.browser_manager.create_browser()
                
                try:
                    # Navigate to TradingView
                    await self._navigate_to_tradingview(browser, ticker, timeframe)
                    
                    # Login if needed
                    await self._ensure_logged_in(browser)
                    
                    # Load strategy/indicator
                    indicator_values = await self._extract_indicator_values(
                        browser, indicator_name
                    )
                    
                    # Generate signals
                    signals = await self._generate_signals(
                        browser, indicator_name, indicator_values
                    )
                    
                    # Capture screenshot if requested
                    screenshot_path = None
                    if config.capture_screenshots:
                        screenshot_path = await self._capture_screenshot(
                            browser, strategy_name, indicator_name, ticker, timeframe
                        )
                        
                    execution_time = (datetime.now() - start_time).total_seconds()
                    
                    return TestResult(
                        strategy_name=strategy_name,
                        indicator_name=indicator_name,
                        ticker=ticker,
                        timeframe=timeframe,
                        success=True,
                        values=indicator_values,
                        signals=signals,
                        execution_time=execution_time,
                        screenshot_path=screenshot_path
                    )
                    
                finally:
                    self.browser_manager.destroy_browser(browser)
                    
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Indicator test failed: {e}")
            
            return TestResult(
                strategy_name=strategy_name,
                indicator_name=indicator_name,
                ticker=ticker,
                timeframe=timeframe,
                success=False,
                values={},
                signals=[],
                execution_time=execution_time,
                error_message=str(e)
            )
            
    async def _navigate_to_tradingview(self, browser, ticker: str, timeframe: str) -> None:
        """Navigate to TradingView with specified ticker and timeframe."""
        url = f"https://www.tradingview.com/chart/?symbol={ticker}&interval={timeframe}"
        browser.get(url)
        
        # Wait for chart to load
        await asyncio.sleep(self.config.get('wait_time', 30))
        
    async def _ensure_logged_in(self, browser) -> None:
        """Ensure user is logged in to TradingView."""
        try:
            # Check if login button is present
            login_selectors = [
                "[data-name='header-user-menu-sign-in']",
                ".tv-header__user-menu-sign-in",
                "button[data-name='sign-in']"
            ]
            
            for selector in login_selectors:
                try:
                    login_btn = browser.find_element("css selector", selector)
                    if login_btn.is_displayed():
                        # Need to login
                        logger.info("Logging in to TradingView...")
                        await self._perform_google_login(browser)
                        break
                except:
                    continue
                    
        except Exception as e:
            logger.warning(f"Login check failed: {e}")
            
    async def _perform_google_login(self, browser) -> None:
        """Perform Google OAuth login for TradingView."""
        try:
            # Click login button
            login_btn = browser.find_element("css selector", "[data-name='header-user-menu-sign-in']")
            login_btn.click()
            
            await asyncio.sleep(2)
            
            # Look for Google login option
            google_btn = browser.find_element("css selector", "[data-name='google']")
            google_btn.click()
            
            await asyncio.sleep(3)
            
            # Handle Google OAuth flow
            # This would integrate with the auth_manager's session data
            session_data = self.auth_manager.get_session_data()
            if session_data.get('email'):
                # Fill in email if needed
                try:
                    email_input = browser.find_element("css selector", "input[type='email']")
                    email_input.send_keys(session_data['email'])
                    
                    next_btn = browser.find_element("css selector", "#identifierNext")
                    next_btn.click()
                    
                    await asyncio.sleep(2)
                except:
                    pass
                    
            # Wait for login completion
            await asyncio.sleep(10)
            
        except Exception as e:
            logger.error(f"Google login failed: {e}")
            
    async def _extract_indicator_values(self, browser, indicator_name: str) -> Dict[str, float]:
        """Extract current indicator values from TradingView."""
        try:
            # This would use kairos signal processing logic
            signal_processor = SignalProcessor(browser, self.config)
            
            # Extract indicator values using kairos methods
            values = await signal_processor.get_indicator_values(indicator_name)
            
            return values or {}
            
        except Exception as e:
            logger.error(f"Failed to extract indicator values: {e}")
            return {}
            
    async def _generate_signals(self, browser, indicator_name: str, values: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate trading signals based on indicator values."""
        try:
            signals = []
            
            # Basic signal generation logic
            # This would be expanded based on specific indicator logic
            if values:
                signal = {
                    'timestamp': datetime.now().isoformat(),
                    'indicator': indicator_name,
                    'values': values,
                    'signal_type': 'analysis',
                    'strength': self._calculate_signal_strength(values)
                }
                signals.append(signal)
                
            return signals
            
        except Exception as e:
            logger.error(f"Signal generation failed: {e}")
            return []
            
    def _calculate_signal_strength(self, values: Dict[str, float]) -> str:
        """Calculate signal strength from indicator values."""
        # Simple heuristic - would be customized per indicator
        if not values:
            return "neutral"
            
        # Example logic for common indicators
        avg_value = sum(values.values()) / len(values)
        if avg_value > 70:
            return "strong"
        elif avg_value > 30:
            return "moderate"
        else:
            return "weak"
            
    async def _capture_screenshot(self, browser, strategy_name: str, indicator_name: str, 
                                ticker: str, timeframe: str) -> str:
        """Capture screenshot of current chart."""
        try:
            screenshot_dir = self.results_dir / "screenshots" / strategy_name
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"{indicator_name}_{ticker}_{timeframe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            screenshot_path = screenshot_dir / filename
            
            browser.save_screenshot(str(screenshot_path))
            
            logger.info(f"Screenshot saved: {screenshot_path}")
            return str(screenshot_path)
            
        except Exception as e:
            logger.error(f"Screenshot capture failed: {e}")
            return None
            
    async def _save_test_results(self, results: List[TestResult], strategy_path: str) -> None:
        """Save test results to file."""
        try:
            strategy_name = Path(strategy_path).name
            results_file = self.results_dir / f"{strategy_name}_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Convert results to JSON-serializable format
            json_results = []
            for result in results:
                json_results.append({
                    'strategy_name': result.strategy_name,
                    'indicator_name': result.indicator_name,
                    'ticker': result.ticker,
                    'timeframe': result.timeframe,
                    'success': result.success,
                    'values': result.values,
                    'signals': result.signals,
                    'execution_time': result.execution_time,
                    'error_message': result.error_message,
                    'screenshot_path': result.screenshot_path,
                    'timestamp': datetime.now().isoformat()
                })
                
            with open(results_file, 'w') as f:
                json.dump(json_results, f, indent=2)
                
            logger.info(f"Test results saved: {results_file}")
            
        except Exception as e:
            logger.error(f"Failed to save test results: {e}")
            
    async def run_quick_test(self, strategy_path: str) -> Dict[str, Any]:
        """Run a quick test of strategy on MNQ1! 1h timeframe."""
        config = TestConfiguration(
            strategy_path=strategy_path,
            indicators=["RSI", "MACD", "EMA"],  # Common indicators
            tickers=["MNQ1!"],
            timeframes=["1h"],
            test_duration=60,
            capture_screenshots=True
        )
        
        results = await self.test_strategy_indicators(config)
        
        # Generate summary
        summary = {
            'total_tests': len(results),
            'successful_tests': sum(1 for r in results if r.success),
            'failed_tests': sum(1 for r in results if not r.success),
            'average_execution_time': sum(r.execution_time for r in results) / len(results) if results else 0,
            'results': results
        }
        
        return summary


# Factory function
def create_test_runner(auth_manager: GrimmAuthManager, 
                      config: Optional[Dict[str, Any]] = None) -> TradingViewTestRunner:
    """Create and configure a test runner instance."""
    return TradingViewTestRunner(auth_manager, config)


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        
        # Create auth manager and authenticate
        auth = GrimmAuthManager()
        if not auth.authenticate():
            print("Authentication failed")
            return
            
        # Create test runner
        test_runner = TradingViewTestRunner(auth)
        
        # Run quick test
        strategy_path = "../strategies/example-strategy"
        summary = await test_runner.run_quick_test(strategy_path)
        
        print(f"Test completed: {summary['successful_tests']}/{summary['total_tests']} successful")
        
    asyncio.run(main())