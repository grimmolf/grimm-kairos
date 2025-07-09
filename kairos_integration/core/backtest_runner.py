"""
Strategy Backtesting Runner for TradingView Automation

Automates strategy backtesting using grimm-kairos with performance analysis,
optimization, and comprehensive reporting.
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import time

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
class BacktestConfiguration:
    """Configuration for strategy backtesting."""
    strategy_path: str
    tickers: List[str] = None
    timeframes: List[str] = None
    start_date: str = None  # YYYY-MM-DD format
    end_date: str = None
    initial_capital: float = 100000.0
    commission: float = 0.75  # Per side for futures
    slippage: float = 0.25  # Points
    position_size_type: str = "fixed"  # fixed, percent_of_equity, contracts
    position_size_value: float = 1.0
    max_drawdown_limit: float = 0.20  # 20%
    capture_screenshots: bool = True
    optimization_enabled: bool = False
    optimization_parameters: Dict[str, Any] = None


@dataclass 
class BacktestMetrics:
    """Comprehensive backtest performance metrics."""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    total_pnl: float
    max_drawdown: float
    max_drawdown_percent: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    average_win: float
    average_loss: float
    largest_win: float
    largest_loss: float
    consecutive_wins: int
    consecutive_losses: int
    recovery_factor: float
    expectancy: float
    kelly_criterion: float
    var_95: float  # Value at Risk
    execution_time: float
    start_date: str
    end_date: str
    days_traded: int


@dataclass
class BacktestResult:
    """Complete backtest results."""
    strategy_name: str
    ticker: str
    timeframe: str
    config: BacktestConfiguration
    metrics: BacktestMetrics
    trades: List[Dict[str, Any]]
    equity_curve: List[Dict[str, float]]
    monthly_returns: Dict[str, float]
    optimization_results: Optional[Dict[str, Any]] = None
    screenshot_paths: List[str] = None
    error_message: Optional[str] = None
    success: bool = True


class StrategyBacktester:
    """
    Automated strategy backtesting using TradingView and grimm-kairos.
    
    Features:
    - Automated strategy loading and execution
    - Comprehensive performance metrics
    - Multi-symbol and multi-timeframe testing
    - Parameter optimization
    - Screenshot capture
    - Detailed reporting
    """
    
    def __init__(self,
                 auth_manager: GrimmAuthManager,
                 kairos_config: Optional[Dict[str, Any]] = None,
                 results_dir: Optional[str] = None):
        """
        Initialize strategy backtester.
        
        Args:
            auth_manager: Authenticated GrimmAuthManager instance
            kairos_config: Kairos configuration overrides
            results_dir: Directory for backtest results
        """
        if not KAIROS_AVAILABLE:
            raise ImportError("Grimm-kairos is required for backtesting functionality")
            
        self.auth_manager = auth_manager
        self.results_dir = Path(results_dir or "./backtest_results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Setup Kairos configuration
        self.config = ConfigManager()
        if kairos_config:
            for key, value in kairos_config.items():
                self.config.set(key, value)
                
        self._configure_defaults()
        
        # Initialize components
        self.browser_manager = None
        self.performance_monitor = None
        self.selectors = CSSSelectors()
        
        # Default test settings
        self.default_tickers = ["MNQ1!"]  # NQ Futures
        self.default_timeframes = ["5m", "15m", "1h", "4h", "1d"]
        
    def _configure_defaults(self) -> None:
        """Configure default settings for backtesting."""
        defaults = {
            'web_browser': 'chrome',
            'run_in_background': False,
            'wait_time': 45,  # Longer waits for backtesting
            'performance_monitoring': True,
            'read_from_data_window': True,
            'wait_until_chart_is_loaded': True
        }
        
        for key, value in defaults.items():
            if not self.config.has(key):
                self.config.set(key, value)
                
    async def initialize(self) -> bool:
        """Initialize backtester components."""
        try:
            self.performance_monitor = PerformanceMonitor(self.config)
            self.browser_manager = ModernBrowserManager(self.config)
            
            if not self.auth_manager.is_authenticated():
                logger.error("Authentication required for backtesting")
                return False
                
            logger.info("Strategy backtester initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize backtester: {e}")
            return False
            
    async def backtest_strategy(self, config: BacktestConfiguration) -> List[BacktestResult]:
        """
        Run comprehensive backtest for a strategy.
        
        Args:
            config: Backtest configuration
            
        Returns:
            List of backtest results for each ticker/timeframe combination
        """
        if not await self.initialize():
            return []
            
        results = []
        tickers = config.tickers or self.default_tickers
        timeframes = config.timeframes or self.default_timeframes
        
        try:
            with self.performance_monitor.performance_timer('strategy_backtesting'):
                # Load strategy
                strategy_data = await self._load_strategy(config.strategy_path)
                if not strategy_data:
                    return []
                    
                # Run backtest for each ticker/timeframe
                for ticker in tickers:
                    for timeframe in timeframes:
                        try:
                            result = await self._run_single_backtest(
                                strategy_data,
                                ticker,
                                timeframe,
                                config
                            )
                            results.append(result)
                            
                        except Exception as e:
                            logger.error(f"Backtest failed for {ticker} {timeframe}: {e}")
                            results.append(BacktestResult(
                                strategy_name=strategy_data.get('name', 'Unknown'),
                                ticker=ticker,
                                timeframe=timeframe,
                                config=config,
                                metrics=None,
                                trades=[],
                                equity_curve=[],
                                monthly_returns={},
                                error_message=str(e),
                                success=False
                            ))
                            
            # Save results
            await self._save_backtest_results(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Strategy backtesting failed: {e}")
            return results
            
    async def _load_strategy(self, strategy_path: str) -> Optional[Dict[str, Any]]:
        """Load strategy files and configuration."""
        try:
            strategy_dir = Path(strategy_path)
            if not strategy_dir.exists():
                logger.error(f"Strategy directory not found: {strategy_path}")
                return None
                
            # Look for Pine Script strategy file
            pinescript_dir = strategy_dir / "pinescript"
            strategy_file = None
            
            if pinescript_dir.exists():
                # Find strategy.pine file
                for file in pinescript_dir.glob("*.pine"):
                    if "strategy" in file.name.lower():
                        strategy_file = file
                        break
                        
            if not strategy_file:
                logger.error(f"No Pine Script strategy file found in {strategy_path}")
                return None
                
            # Read strategy content
            with open(strategy_file, 'r') as f:
                strategy_content = f.read()
                
            return {
                'name': strategy_dir.name,
                'path': str(strategy_dir),
                'strategy_file': str(strategy_file),
                'strategy_content': strategy_content,
                'pinescript_dir': str(pinescript_dir)
            }
            
        except Exception as e:
            logger.error(f"Failed to load strategy: {e}")
            return None
            
    async def _run_single_backtest(self,
                                 strategy_data: Dict[str, Any],
                                 ticker: str,
                                 timeframe: str,
                                 config: BacktestConfiguration) -> BacktestResult:
        """Run backtest for single ticker/timeframe combination."""
        start_time = datetime.now()
        
        try:
            browser = self.browser_manager.create_browser()
            
            try:
                # Navigate to TradingView strategy tester
                await self._navigate_to_strategy_tester(browser, ticker, timeframe)
                
                # Login if needed
                await self._ensure_logged_in(browser)
                
                # Load strategy code
                await self._load_strategy_in_pine_editor(browser, strategy_data)
                
                # Configure backtest parameters
                await self._configure_backtest_settings(browser, config)
                
                # Run backtest
                await self._execute_backtest(browser)
                
                # Extract results
                metrics = await self._extract_backtest_metrics(browser)
                trades = await self._extract_trade_list(browser)
                equity_curve = await self._extract_equity_curve(browser)
                monthly_returns = await self._extract_monthly_returns(browser)
                
                # Capture screenshots
                screenshot_paths = []
                if config.capture_screenshots:
                    screenshot_paths = await self._capture_backtest_screenshots(
                        browser, strategy_data['name'], ticker, timeframe
                    )
                    
                # Run optimization if enabled
                optimization_results = None
                if config.optimization_enabled:
                    optimization_results = await self._run_optimization(browser, config)
                    
                execution_time = (datetime.now() - start_time).total_seconds()
                
                return BacktestResult(
                    strategy_name=strategy_data['name'],
                    ticker=ticker,
                    timeframe=timeframe,
                    config=config,
                    metrics=metrics,
                    trades=trades,
                    equity_curve=equity_curve,
                    monthly_returns=monthly_returns,
                    optimization_results=optimization_results,
                    screenshot_paths=screenshot_paths,
                    success=True
                )
                
            finally:
                self.browser_manager.destroy_browser(browser)
                
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Single backtest failed: {e}")
            
            return BacktestResult(
                strategy_name=strategy_data.get('name', 'Unknown'),
                ticker=ticker,
                timeframe=timeframe,
                config=config,
                metrics=None,
                trades=[],
                equity_curve=[],
                monthly_returns={},
                error_message=str(e),
                success=False
            )
            
    async def _navigate_to_strategy_tester(self, browser, ticker: str, timeframe: str) -> None:
        """Navigate to TradingView Pine Script editor with strategy tester."""
        url = f"https://www.tradingview.com/pine-editor/#chart={ticker}&interval={timeframe}"
        browser.get(url)
        
        # Wait for page to load
        await asyncio.sleep(self.config.get('wait_time', 45))
        
    async def _ensure_logged_in(self, browser) -> None:
        """Ensure user is logged into TradingView."""
        # Similar to test_runner login logic
        try:
            login_selectors = [
                "[data-name='header-user-menu-sign-in']",
                ".tv-header__user-menu-sign-in"
            ]
            
            for selector in login_selectors:
                try:
                    login_btn = browser.find_element("css selector", selector)
                    if login_btn.is_displayed():
                        await self._perform_google_login(browser)
                        break
                except:
                    continue
                    
        except Exception as e:
            logger.warning(f"Login check failed: {e}")
            
    async def _perform_google_login(self, browser) -> None:
        """Perform Google OAuth login."""
        # Reuse login logic from test_runner
        try:
            login_btn = browser.find_element("css selector", "[data-name='header-user-menu-sign-in']")
            login_btn.click()
            await asyncio.sleep(2)
            
            google_btn = browser.find_element("css selector", "[data-name='google']")
            google_btn.click()
            await asyncio.sleep(10)  # Wait for OAuth flow
            
        except Exception as e:
            logger.error(f"Google login failed: {e}")
            
    async def _load_strategy_in_pine_editor(self, browser, strategy_data: Dict[str, Any]) -> None:
        """Load strategy code into Pine Script editor."""
        try:
            # Clear existing code
            code_editor = browser.find_element("css selector", ".monaco-editor")
            code_editor.click()
            
            # Select all and delete
            browser.execute_script("document.execCommand('selectAll');")
            browser.execute_script("document.execCommand('delete');")
            
            await asyncio.sleep(1)
            
            # Insert strategy code
            strategy_content = strategy_data['strategy_content']
            browser.execute_script(f"document.execCommand('insertText', false, {json.dumps(strategy_content)});")
            
            await asyncio.sleep(2)
            
            # Compile strategy
            compile_btn = browser.find_element("css selector", "[data-name='save-load-dialog-save-script']")
            compile_btn.click()
            
            await asyncio.sleep(5)  # Wait for compilation
            
        except Exception as e:
            logger.error(f"Failed to load strategy code: {e}")
            
    async def _configure_backtest_settings(self, browser, config: BacktestConfiguration) -> None:
        """Configure backtest parameters."""
        try:
            # Open strategy properties
            properties_btn = browser.find_element("css selector", "[data-name='strategy-properties']")
            properties_btn.click()
            
            await asyncio.sleep(2)
            
            # Set initial capital
            capital_input = browser.find_element("css selector", "input[name='initial_capital']")
            capital_input.clear()
            capital_input.send_keys(str(config.initial_capital))
            
            # Set commission
            commission_input = browser.find_element("css selector", "input[name='commission']")
            commission_input.clear()
            commission_input.send_keys(str(config.commission))
            
            # Set slippage
            slippage_input = browser.find_element("css selector", "input[name='slippage']")
            slippage_input.clear()
            slippage_input.send_keys(str(config.slippage))
            
            # Set date range if specified
            if config.start_date:
                start_date_input = browser.find_element("css selector", "input[name='start_date']")
                start_date_input.clear()
                start_date_input.send_keys(config.start_date)
                
            if config.end_date:
                end_date_input = browser.find_element("css selector", "input[name='end_date']")
                end_date_input.clear()
                end_date_input.send_keys(config.end_date)
                
            # Apply settings
            apply_btn = browser.find_element("css selector", "[data-name='apply-settings']")
            apply_btn.click()
            
            await asyncio.sleep(3)
            
        except Exception as e:
            logger.error(f"Failed to configure backtest settings: {e}")
            
    async def _execute_backtest(self, browser) -> None:
        """Execute the backtest."""
        try:
            # Strategy should run automatically when loaded
            # Wait for backtest to complete
            await asyncio.sleep(10)
            
            # Check if strategy is running
            strategy_status = browser.find_element("css selector", "[data-name='strategy-status']")
            
            # Wait for completion (look for specific indicators)
            timeout = 300  # 5 minutes max
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    # Check if backtest is complete
                    results_tab = browser.find_element("css selector", "[data-name='strategy-tester-results']")
                    if results_tab.is_displayed():
                        break
                except:
                    pass
                    
                await asyncio.sleep(5)
                
        except Exception as e:
            logger.error(f"Backtest execution failed: {e}")
            
    async def _extract_backtest_metrics(self, browser) -> BacktestMetrics:
        """Extract comprehensive backtest metrics."""
        try:
            # Click on Performance Summary tab
            summary_tab = browser.find_element("css selector", "[data-name='performance-summary']")
            summary_tab.click()
            
            await asyncio.sleep(2)
            
            # Extract metrics from the strategy tester
            metrics_elements = browser.find_elements("css selector", ".strategy-performance-metrics")
            
            # Default metrics if extraction fails
            metrics = BacktestMetrics(
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                profit_factor=0.0,
                total_pnl=0.0,
                max_drawdown=0.0,
                max_drawdown_percent=0.0,
                sharpe_ratio=0.0,
                sortino_ratio=0.0,
                calmar_ratio=0.0,
                average_win=0.0,
                average_loss=0.0,
                largest_win=0.0,
                largest_loss=0.0,
                consecutive_wins=0,
                consecutive_losses=0,
                recovery_factor=0.0,
                expectancy=0.0,
                kelly_criterion=0.0,
                var_95=0.0,
                execution_time=0.0,
                start_date="",
                end_date="",
                days_traded=0
            )
            
            # Extract actual values (would need specific selectors for TradingView)
            # This is a simplified example
            try:
                total_trades_elem = browser.find_element("css selector", "[data-field='total-closed-trades']")
                metrics.total_trades = int(total_trades_elem.text.strip())
                
                win_rate_elem = browser.find_element("css selector", "[data-field='percent-profitable']")
                metrics.win_rate = float(win_rate_elem.text.strip().replace('%', '')) / 100
                
                profit_factor_elem = browser.find_element("css selector", "[data-field='profit-factor']")
                metrics.profit_factor = float(profit_factor_elem.text.strip())
                
                total_pnl_elem = browser.find_element("css selector", "[data-field='net-profit']")
                metrics.total_pnl = float(total_pnl_elem.text.strip().replace('$', '').replace(',', ''))
                
                max_dd_elem = browser.find_element("css selector", "[data-field='max-drawdown']")
                metrics.max_drawdown_percent = float(max_dd_elem.text.strip().replace('%', '')) / 100
                
            except Exception as e:
                logger.warning(f"Could not extract all metrics: {e}")
                
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to extract backtest metrics: {e}")
            return None
            
    async def _extract_trade_list(self, browser) -> List[Dict[str, Any]]:
        """Extract individual trade details."""
        try:
            # Click on List of Trades tab
            trades_tab = browser.find_element("css selector", "[data-name='list-of-trades']")
            trades_tab.click()
            
            await asyncio.sleep(2)
            
            trades = []
            
            # Extract trade rows
            trade_rows = browser.find_elements("css selector", ".trade-list-row")
            
            for row in trade_rows[:100]:  # Limit to first 100 trades
                try:
                    cells = row.find_elements("css selector", "td")
                    if len(cells) >= 6:
                        trade = {
                            'entry_time': cells[0].text.strip(),
                            'exit_time': cells[1].text.strip(),
                            'type': cells[2].text.strip(),
                            'qty': cells[3].text.strip(),
                            'entry_price': cells[4].text.strip(),
                            'exit_price': cells[5].text.strip(),
                            'pnl': cells[6].text.strip() if len(cells) > 6 else '',
                            'cumulative_pnl': cells[7].text.strip() if len(cells) > 7 else '',
                            'run_up': cells[8].text.strip() if len(cells) > 8 else '',
                            'drawdown': cells[9].text.strip() if len(cells) > 9 else ''
                        }
                        trades.append(trade)
                except:
                    continue
                    
            return trades
            
        except Exception as e:
            logger.error(f"Failed to extract trade list: {e}")
            return []
            
    async def _extract_equity_curve(self, browser) -> List[Dict[str, float]]:
        """Extract equity curve data."""
        try:
            # This would require more complex extraction from TradingView charts
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error(f"Failed to extract equity curve: {e}")
            return []
            
    async def _extract_monthly_returns(self, browser) -> Dict[str, float]:
        """Extract monthly returns breakdown."""
        try:
            # This would extract monthly performance data
            # For now, return empty dict
            return {}
            
        except Exception as e:
            logger.error(f"Failed to extract monthly returns: {e}")
            return {}
            
    async def _capture_backtest_screenshots(self, browser, strategy_name: str, 
                                          ticker: str, timeframe: str) -> List[str]:
        """Capture screenshots of backtest results."""
        screenshots = []
        
        try:
            screenshot_dir = self.results_dir / "screenshots" / strategy_name
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Screenshot 1: Performance Summary
            summary_file = screenshot_dir / f"summary_{ticker}_{timeframe}_{timestamp}.png"
            browser.save_screenshot(str(summary_file))
            screenshots.append(str(summary_file))
            
            # Screenshot 2: Equity Curve
            equity_tab = browser.find_element("css selector", "[data-name='equity-curve']")
            equity_tab.click()
            await asyncio.sleep(2)
            
            equity_file = screenshot_dir / f"equity_{ticker}_{timeframe}_{timestamp}.png"
            browser.save_screenshot(str(equity_file))
            screenshots.append(str(equity_file))
            
            # Screenshot 3: Strategy on Chart
            chart_tab = browser.find_element("css selector", "[data-name='strategy-chart']")
            chart_tab.click()
            await asyncio.sleep(2)
            
            chart_file = screenshot_dir / f"chart_{ticker}_{timeframe}_{timestamp}.png"
            browser.save_screenshot(str(chart_file))
            screenshots.append(str(chart_file))
            
            logger.info(f"Captured {len(screenshots)} backtest screenshots")
            
        except Exception as e:
            logger.error(f"Screenshot capture failed: {e}")
            
        return screenshots
        
    async def _run_optimization(self, browser, config: BacktestConfiguration) -> Dict[str, Any]:
        """Run strategy optimization if enabled."""
        try:
            # Open strategy optimization
            optimization_tab = browser.find_element("css selector", "[data-name='strategy-optimization']")
            optimization_tab.click()
            
            await asyncio.sleep(2)
            
            # Configure optimization parameters
            if config.optimization_parameters:
                for param, settings in config.optimization_parameters.items():
                    # Set parameter ranges
                    param_input = browser.find_element("css selector", f"input[name='{param}']")
                    # Configure min, max, step values
                    
            # Start optimization
            optimize_btn = browser.find_element("css selector", "[data-name='start-optimization']")
            optimize_btn.click()
            
            # Wait for optimization to complete
            await asyncio.sleep(60)  # Adjust based on complexity
            
            # Extract optimization results
            results = {
                'status': 'completed',
                'best_parameters': {},
                'performance_by_parameter': []
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            return {'status': 'failed', 'error': str(e)}
            
    async def _save_backtest_results(self, results: List[BacktestResult]) -> None:
        """Save backtest results to files."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            for result in results:
                if not result.success:
                    continue
                    
                # Create result directory
                result_dir = self.results_dir / f"{result.strategy_name}_{result.ticker}_{result.timeframe}_{timestamp}"
                result_dir.mkdir(parents=True, exist_ok=True)
                
                # Save comprehensive results
                result_data = {
                    'strategy_name': result.strategy_name,
                    'ticker': result.ticker,
                    'timeframe': result.timeframe,
                    'config': asdict(result.config),
                    'metrics': asdict(result.metrics) if result.metrics else None,
                    'trades': result.trades,
                    'equity_curve': result.equity_curve,
                    'monthly_returns': result.monthly_returns,
                    'optimization_results': result.optimization_results,
                    'screenshot_paths': result.screenshot_paths,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Save as JSON
                with open(result_dir / "backtest_results.json", 'w') as f:
                    json.dump(result_data, f, indent=2)
                    
                # Save metrics summary
                if result.metrics:
                    metrics_summary = f"""
Backtest Results Summary
Strategy: {result.strategy_name}
Symbol: {result.ticker}
Timeframe: {result.timeframe}

Performance Metrics:
Total Trades: {result.metrics.total_trades}
Win Rate: {result.metrics.win_rate:.2%}
Profit Factor: {result.metrics.profit_factor:.2f}
Total P&L: ${result.metrics.total_pnl:,.2f}
Max Drawdown: {result.metrics.max_drawdown_percent:.2%}
Sharpe Ratio: {result.metrics.sharpe_ratio:.2f}
                    """
                    
                    with open(result_dir / "summary.txt", 'w') as f:
                        f.write(metrics_summary)
                        
            logger.info(f"Saved backtest results for {len([r for r in results if r.success])} successful tests")
            
        except Exception as e:
            logger.error(f"Failed to save backtest results: {e}")
            
    async def run_quick_backtest(self, strategy_path: str) -> Dict[str, Any]:
        """Run a quick backtest on MNQ1! 1h timeframe."""
        config = BacktestConfiguration(
            strategy_path=strategy_path,
            tickers=["MNQ1!"],
            timeframes=["1h"],
            initial_capital=100000.0,
            commission=0.75,
            slippage=0.25,
            capture_screenshots=True
        )
        
        results = await self.backtest_strategy(config)
        
        # Generate summary
        successful_results = [r for r in results if r.success]
        
        summary = {
            'total_backtests': len(results),
            'successful_backtests': len(successful_results),
            'failed_backtests': len(results) - len(successful_results),
            'results': results
        }
        
        if successful_results:
            avg_win_rate = sum(r.metrics.win_rate for r in successful_results) / len(successful_results)
            avg_profit_factor = sum(r.metrics.profit_factor for r in successful_results) / len(successful_results)
            
            summary.update({
                'average_win_rate': avg_win_rate,
                'average_profit_factor': avg_profit_factor
            })
            
        return summary


# Factory function
def create_strategy_backtester(auth_manager: GrimmAuthManager,
                             config: Optional[Dict[str, Any]] = None) -> StrategyBacktester:
    """Create and configure a strategy backtester instance."""
    return StrategyBacktester(auth_manager, config)


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        logging.basicConfig(level=logging.INFO)
        
        # Create auth manager and authenticate
        auth = GrimmAuthManager()
        if not auth.authenticate():
            print("Authentication failed")
            return
            
        # Create backtester
        backtester = StrategyBacktester(auth)
        
        # Run quick backtest
        strategy_path = "../strategies/example-strategy"
        summary = await backtester.run_quick_backtest(strategy_path)
        
        print(f"Backtest completed: {summary['successful_backtests']}/{summary['total_backtests']} successful")
        if 'average_win_rate' in summary:
            print(f"Average Win Rate: {summary['average_win_rate']:.2%}")
            print(f"Average Profit Factor: {summary['average_profit_factor']:.2f}")
        
    asyncio.run(main())