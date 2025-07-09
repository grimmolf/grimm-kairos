"""
Complete Workflow Executor for Kairos Integration

Orchestrates the complete strategy testing workflow including authentication,
testing, backtesting, and screenshot capture with comprehensive reporting.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import json

from ..core import GrimmAuthManager, TradingViewTestRunner, StrategyBacktester, ChartScreenshotManager
from ..config import MNQConfiguration, WorkflowTemplates

logger = logging.getLogger(__name__)


class CompleteWorkflow:
    """
    Complete end-to-end workflow for strategy testing and validation.
    
    Coordinates all integration components to provide a seamless
    strategy development and testing experience.
    """
    
    def __init__(self, 
                 output_dir: Optional[str] = None,
                 auth_credentials: Optional[str] = None):
        """
        Initialize complete workflow.
        
        Args:
            output_dir: Directory for all workflow outputs
            auth_credentials: Path to Google OAuth credentials
        """
        self.output_dir = Path(output_dir or "./workflow_results")
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.auth_manager = GrimmAuthManager(auth_credentials)
        self.test_runner = None
        self.backtest_runner = None
        self.screenshot_manager = None
        
        # Configuration
        self.mnq_config = MNQConfiguration()
        
        # Results storage
        self.workflow_results = {
            'start_time': None,
            'end_time': None,
            'duration': 0,
            'strategy_name': None,
            'authentication': {'success': False},
            'indicator_testing': {'success': False, 'results': []},
            'backtesting': {'success': False, 'results': []},
            'screenshots': {'success': False, 'results': []},
            'overall_success': False,
            'errors': []
        }
        
    async def authenticate(self) -> bool:
        """Authenticate with Google OAuth."""
        try:
            logger.info("Starting authentication...")
            success = self.auth_manager.authenticate()
            
            self.workflow_results['authentication'] = {
                'success': success,
                'email': self.auth_manager.get_user_email() if success else None,
                'timestamp': datetime.now().isoformat()
            }
            
            if success:
                logger.info(f"Authentication successful for {self.auth_manager.get_user_email()}")
            else:
                logger.error("Authentication failed")
                
            return success
            
        except Exception as e:
            error_msg = f"Authentication error: {e}"
            logger.error(error_msg)
            self.workflow_results['errors'].append(error_msg)
            return False
    
    async def initialize_components(self) -> bool:
        """Initialize all workflow components."""
        try:
            if not self.auth_manager.is_authenticated():
                logger.error("Authentication required before initializing components")
                return False
                
            # Initialize test runner
            self.test_runner = TradingViewTestRunner(
                self.auth_manager,
                results_dir=str(self.output_dir / "test_results")
            )
            
            # Initialize backtest runner
            self.backtest_runner = StrategyBacktester(
                self.auth_manager,
                results_dir=str(self.output_dir / "backtest_results")
            )
            
            # Initialize screenshot manager
            self.screenshot_manager = ChartScreenshotManager(
                self.auth_manager,
                output_dir=str(self.output_dir / "screenshots")
            )
            
            logger.info("All components initialized successfully")
            return True
            
        except Exception as e:
            error_msg = f"Component initialization error: {e}"
            logger.error(error_msg)
            self.workflow_results['errors'].append(error_msg)
            return False
    
    async def run_complete_workflow(self, strategy_path: str) -> Dict[str, Any]:
        """
        Run the complete strategy testing workflow.
        
        Args:
            strategy_path: Path to strategy directory
            
        Returns:
            Complete workflow results
        """
        self.workflow_results['start_time'] = datetime.now().isoformat()
        strategy_name = Path(strategy_path).name
        self.workflow_results['strategy_name'] = strategy_name
        
        logger.info(f"Starting complete workflow for strategy: {strategy_name}")
        
        try:
            # Step 1: Authentication
            if not await self.authenticate():
                self.workflow_results['overall_success'] = False
                return self.workflow_results
            
            # Step 2: Initialize components
            if not await self.initialize_components():
                self.workflow_results['overall_success'] = False
                return self.workflow_results
            
            # Step 3: Run indicator testing
            await self._run_indicator_testing(strategy_path)
            
            # Step 4: Run backtesting
            await self._run_backtesting(strategy_path)
            
            # Step 5: Capture screenshots
            await self._capture_screenshots(strategy_name)
            
            # Step 6: Generate comprehensive report
            await self._generate_workflow_report()
            
            # Calculate overall success
            self.workflow_results['overall_success'] = (
                self.workflow_results['authentication']['success'] and
                self.workflow_results['indicator_testing']['success'] and
                self.workflow_results['backtesting']['success'] and
                self.workflow_results['screenshots']['success']
            )
            
        except Exception as e:
            error_msg = f"Workflow execution error: {e}"
            logger.error(error_msg)
            self.workflow_results['errors'].append(error_msg)
            self.workflow_results['overall_success'] = False
        
        finally:
            self.workflow_results['end_time'] = datetime.now().isoformat()
            if self.workflow_results['start_time']:
                start_time = datetime.fromisoformat(self.workflow_results['start_time'])
                end_time = datetime.fromisoformat(self.workflow_results['end_time'])
                self.workflow_results['duration'] = (end_time - start_time).total_seconds()
        
        logger.info(f"Workflow completed. Success: {self.workflow_results['overall_success']}")
        return self.workflow_results
    
    async def _run_indicator_testing(self, strategy_path: str) -> None:
        """Run comprehensive indicator testing."""
        try:
            logger.info("Starting indicator testing...")
            
            from ..core.test_runner import TestConfiguration
            
            config = TestConfiguration(
                strategy_path=strategy_path,
                indicators=["RSI", "MACD", "EMA", "SMA", "Bollinger_Bands"],
                tickers=["MNQ1!"],
                timeframes=["5m", "15m", "1h", "4h"],
                test_duration=300,
                capture_screenshots=True,
                parallel_execution=True
            )
            
            results = await self.test_runner.test_strategy_indicators(config)
            
            # Process results
            successful_tests = [r for r in results if r.success]
            failed_tests = [r for r in results if not r.success]
            
            self.workflow_results['indicator_testing'] = {
                'success': len(successful_tests) > 0,
                'total_tests': len(results),
                'successful_tests': len(successful_tests),
                'failed_tests': len(failed_tests),
                'results': [
                    {
                        'indicator': r.indicator_name,
                        'ticker': r.ticker,
                        'timeframe': r.timeframe,
                        'success': r.success,
                        'execution_time': r.execution_time,
                        'values': r.values,
                        'signals': r.signals,
                        'error': r.error_message
                    }
                    for r in results
                ],
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Indicator testing completed: {len(successful_tests)}/{len(results)} successful")
            
        except Exception as e:
            error_msg = f"Indicator testing error: {e}"
            logger.error(error_msg)
            self.workflow_results['errors'].append(error_msg)
            self.workflow_results['indicator_testing']['success'] = False
    
    async def _run_backtesting(self, strategy_path: str) -> None:
        """Run comprehensive backtesting."""
        try:
            logger.info("Starting backtesting...")
            
            from ..core.backtest_runner import BacktestConfiguration
            
            config = BacktestConfiguration(
                strategy_path=strategy_path,
                tickers=["MNQ1!"],
                timeframes=["5m", "1h", "4h"],
                initial_capital=25000.0,
                commission=0.75,
                slippage=0.25,
                position_size_type="fixed",
                position_size_value=1.0,
                capture_screenshots=True,
                optimization_enabled=True
            )
            
            results = await self.backtest_runner.backtest_strategy(config)
            
            # Process results
            successful_backtests = [r for r in results if r.success]
            failed_backtests = [r for r in results if not r.success]
            
            # Calculate summary metrics
            summary_metrics = {}
            if successful_backtests:
                avg_win_rate = sum(r.metrics.win_rate for r in successful_backtests) / len(successful_backtests)
                avg_profit_factor = sum(r.metrics.profit_factor for r in successful_backtests) / len(successful_backtests)
                avg_max_drawdown = sum(r.metrics.max_drawdown_percent for r in successful_backtests) / len(successful_backtests)
                
                summary_metrics = {
                    'average_win_rate': avg_win_rate,
                    'average_profit_factor': avg_profit_factor,
                    'average_max_drawdown': avg_max_drawdown,
                    'best_timeframe': max(successful_backtests, key=lambda x: x.metrics.profit_factor).timeframe,
                    'meets_benchmarks': self._evaluate_performance_benchmarks(successful_backtests)
                }
            
            self.workflow_results['backtesting'] = {
                'success': len(successful_backtests) > 0,
                'total_backtests': len(results),
                'successful_backtests': len(successful_backtests),
                'failed_backtests': len(failed_backtests),
                'summary_metrics': summary_metrics,
                'results': [
                    {
                        'ticker': r.ticker,
                        'timeframe': r.timeframe,
                        'success': r.success,
                        'metrics': {
                            'total_trades': r.metrics.total_trades if r.metrics else 0,
                            'win_rate': r.metrics.win_rate if r.metrics else 0,
                            'profit_factor': r.metrics.profit_factor if r.metrics else 0,
                            'total_pnl': r.metrics.total_pnl if r.metrics else 0,
                            'max_drawdown_percent': r.metrics.max_drawdown_percent if r.metrics else 0
                        } if r.metrics else {},
                        'trade_count': len(r.trades),
                        'error': r.error_message
                    }
                    for r in results
                ],
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Backtesting completed: {len(successful_backtests)}/{len(results)} successful")
            
        except Exception as e:
            error_msg = f"Backtesting error: {e}"
            logger.error(error_msg)
            self.workflow_results['errors'].append(error_msg)
            self.workflow_results['backtesting']['success'] = False
    
    async def _capture_screenshots(self, strategy_name: str) -> None:
        """Capture comprehensive screenshots."""
        try:
            logger.info("Starting screenshot capture...")
            
            results = await self.screenshot_manager.capture_strategy_screenshots(
                strategy_name=strategy_name,
                tickers=["MNQ1!"],
                timeframes=["5m", "1h", "4h", "1d"]
            )
            
            # Process results
            successful_screenshots = [r for r in results if r.success]
            failed_screenshots = [r for r in results if not r.success]
            
            # Create comparison image if multiple screenshots
            comparison_path = None
            if len(successful_screenshots) > 1:
                screenshot_paths = [r.file_path for r in successful_screenshots]
                comparison_path = str(self.output_dir / "screenshots" / "comparison.png")
                await self.screenshot_manager.create_comparison_image(screenshot_paths, comparison_path)
            
            self.workflow_results['screenshots'] = {
                'success': len(successful_screenshots) > 0,
                'total_screenshots': len(results),
                'successful_screenshots': len(successful_screenshots),
                'failed_screenshots': len(failed_screenshots),
                'comparison_image': comparison_path,
                'results': [
                    {
                        'success': r.success,
                        'file_path': r.file_path,
                        'thumbnail_path': r.thumbnail_path,
                        'file_size': r.file_size,
                        'capture_time': r.capture_time.isoformat() if r.capture_time else None,
                        'metadata': r.metadata,
                        'error': r.error_message
                    }
                    for r in results
                ],
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Screenshot capture completed: {len(successful_screenshots)}/{len(results)} successful")
            
        except Exception as e:
            error_msg = f"Screenshot capture error: {e}"
            logger.error(error_msg)
            self.workflow_results['errors'].append(error_msg)
            self.workflow_results['screenshots']['success'] = False
    
    def _evaluate_performance_benchmarks(self, backtest_results: List[Any]) -> Dict[str, bool]:
        """Evaluate backtest results against performance benchmarks."""
        benchmarks = self.mnq_config.get_performance_benchmarks()
        
        evaluation = {}
        
        if backtest_results:
            # Average metrics across all successful backtests
            avg_win_rate = sum(r.metrics.win_rate for r in backtest_results) / len(backtest_results)
            avg_profit_factor = sum(r.metrics.profit_factor for r in backtest_results) / len(backtest_results)
            max_drawdown = max(r.metrics.max_drawdown_percent for r in backtest_results)
            
            evaluation = {
                'win_rate_benchmark': avg_win_rate >= benchmarks['min_win_rate'],
                'profit_factor_benchmark': avg_profit_factor >= benchmarks['min_profit_factor'],
                'drawdown_benchmark': max_drawdown <= benchmarks['max_drawdown'],
                'overall_benchmark': (
                    avg_win_rate >= benchmarks['min_win_rate'] and
                    avg_profit_factor >= benchmarks['min_profit_factor'] and
                    max_drawdown <= benchmarks['max_drawdown']
                )
            }
        
        return evaluation
    
    async def _generate_workflow_report(self) -> None:
        """Generate comprehensive workflow report."""
        try:
            # Save detailed results as JSON
            results_file = self.output_dir / "workflow_results.json"
            with open(results_file, 'w') as f:
                json.dump(self.workflow_results, f, indent=2)
            
            # Generate summary report
            summary_file = self.output_dir / "workflow_summary.md"
            summary_content = self._generate_summary_markdown()
            
            with open(summary_file, 'w') as f:
                f.write(summary_content)
            
            logger.info(f"Workflow report generated: {results_file}")
            logger.info(f"Summary report generated: {summary_file}")
            
        except Exception as e:
            error_msg = f"Report generation error: {e}"
            logger.error(error_msg)
            self.workflow_results['errors'].append(error_msg)
    
    def _generate_summary_markdown(self) -> str:
        """Generate workflow summary in Markdown format."""
        results = self.workflow_results
        
        summary = f"""# Strategy Workflow Summary

## Strategy: {results['strategy_name']}

**Execution Time:** {results['start_time']} - {results['end_time']}  
**Duration:** {results['duration']:.2f} seconds  
**Overall Success:** {'✅ PASSED' if results['overall_success'] else '❌ FAILED'}

---

## Authentication
- **Status:** {'✅ Success' if results['authentication']['success'] else '❌ Failed'}
- **Email:** {results['authentication'].get('email', 'N/A')}

## Indicator Testing
- **Status:** {'✅ Success' if results['indicator_testing']['success'] else '❌ Failed'}
- **Tests Run:** {results['indicator_testing'].get('total_tests', 0)}
- **Successful:** {results['indicator_testing'].get('successful_tests', 0)}
- **Failed:** {results['indicator_testing'].get('failed_tests', 0)}

## Backtesting  
- **Status:** {'✅ Success' if results['backtesting']['success'] else '❌ Failed'}
- **Backtests Run:** {results['backtesting'].get('total_backtests', 0)}
- **Successful:** {results['backtesting'].get('successful_backtests', 0)}
- **Failed:** {results['backtesting'].get('failed_backtests', 0)}
"""
        
        # Add backtest summary metrics if available
        if results['backtesting'].get('summary_metrics'):
            metrics = results['backtesting']['summary_metrics']
            summary += f"""
### Performance Summary
- **Average Win Rate:** {metrics.get('average_win_rate', 0):.2%}
- **Average Profit Factor:** {metrics.get('average_profit_factor', 0):.2f}
- **Average Max Drawdown:** {metrics.get('average_max_drawdown', 0):.2%}
- **Best Timeframe:** {metrics.get('best_timeframe', 'N/A')}
- **Meets Benchmarks:** {'✅ Yes' if metrics.get('meets_benchmarks', {}).get('overall_benchmark', False) else '❌ No'}
"""
        
        summary += f"""
## Screenshots
- **Status:** {'✅ Success' if results['screenshots']['success'] else '❌ Failed'}
- **Screenshots Captured:** {results['screenshots'].get('successful_screenshots', 0)}
- **Comparison Image:** {'✅ Created' if results['screenshots'].get('comparison_image') else '❌ Not created'}

---

## Files Generated
- Detailed results: `workflow_results.json`
- Test results: `test_results/`
- Backtest results: `backtest_results/`
- Screenshots: `screenshots/`

## Errors
"""
        
        if results['errors']:
            for error in results['errors']:
                summary += f"- {error}\n"
        else:
            summary += "No errors encountered.\n"
        
        summary += f"""
---

*Generated by Kairos Integration Framework*  
*Timestamp: {datetime.now().isoformat()}*
"""
        
        return summary
    
    async def run_quick_workflow(self, strategy_path: str) -> Dict[str, Any]:
        """Run a quick validation workflow for rapid testing."""
        logger.info(f"Starting quick workflow for: {Path(strategy_path).name}")
        
        # Simplified workflow for quick testing
        if not await self.authenticate():
            return {'success': False, 'error': 'Authentication failed'}
        
        if not await self.initialize_components():
            return {'success': False, 'error': 'Component initialization failed'}
        
        try:
            # Quick test on MNQ1! 1h only
            test_summary = await self.test_runner.run_quick_test(strategy_path)
            backtest_summary = await self.backtest_runner.run_quick_backtest(strategy_path)
            
            return {
                'success': True,
                'strategy_name': Path(strategy_path).name,
                'test_summary': test_summary,
                'backtest_summary': backtest_summary,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}


# Factory function
def create_complete_workflow(output_dir: Optional[str] = None,
                           auth_credentials: Optional[str] = None) -> CompleteWorkflow:
    """Create and configure a complete workflow instance."""
    return CompleteWorkflow(output_dir, auth_credentials)


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        logging.basicConfig(level=logging.INFO)
        
        # Create workflow
        workflow = CompleteWorkflow()
        
        # Run complete workflow
        strategy_path = "../strategies/example-strategy"
        results = await workflow.run_complete_workflow(strategy_path)
        
        print(f"Workflow completed: {results['overall_success']}")
        print(f"Duration: {results['duration']:.2f} seconds")
        
        if results['backtesting'].get('summary_metrics'):
            metrics = results['backtesting']['summary_metrics']
            print(f"Average Win Rate: {metrics.get('average_win_rate', 0):.2%}")
            print(f"Average Profit Factor: {metrics.get('average_profit_factor', 0):.2f}")
    
    asyncio.run(main())