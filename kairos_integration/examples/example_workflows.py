"""
Example workflows demonstrating Kairos Integration Framework usage.

These examples show how to use the integration framework for common
trading strategy development and testing scenarios.
"""

import asyncio
import logging
from pathlib import Path
from datetime import datetime

# Import integration components
from kairos_integration import (
    GrimmAuthManager,
    TradingViewTestRunner,
    StrategyBacktester,
    ChartScreenshotManager,
    CompleteWorkflow
)

from kairos_integration.core.test_runner import TestConfiguration
from kairos_integration.core.backtest_runner import BacktestConfiguration
from kairos_integration.core.screenshot_manager import ScreenshotConfiguration
from kairos_integration.config import create_mnq_config


# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def example_1_complete_strategy_workflow():
    """
    Example 1: Complete end-to-end strategy testing workflow
    
    This example demonstrates the full workflow from authentication
    through testing, backtesting, and screenshot capture.
    """
    print("🚀 Example 1: Complete Strategy Workflow")
    print("=" * 50)
    
    try:
        # Initialize workflow
        workflow = CompleteWorkflow(output_dir="./example_results/complete_workflow")
        
        # Example strategy path (you would use your actual strategy)
        strategy_path = "strategies/example-rsi-strategy"
        
        print(f"📁 Testing strategy: {strategy_path}")
        
        # Run complete workflow
        results = await workflow.run_complete_workflow(strategy_path)
        
        # Display results
        print(f"\n📊 Workflow Results:")
        print(f"   Overall Success: {'✅' if results['overall_success'] else '❌'}")
        print(f"   Duration: {results['duration']:.2f} seconds")
        print(f"   Strategy: {results['strategy_name']}")
        
        # Authentication results
        auth_result = results['authentication']
        print(f"\n🔐 Authentication:")
        print(f"   Status: {'✅' if auth_result['success'] else '❌'}")
        print(f"   Email: {auth_result.get('email', 'N/A')}")
        
        # Indicator testing results
        test_result = results['indicator_testing']
        print(f"\n🧪 Indicator Testing:")
        print(f"   Status: {'✅' if test_result['success'] else '❌'}")
        print(f"   Tests: {test_result.get('successful_tests', 0)}/{test_result.get('total_tests', 0)}")
        
        # Backtesting results
        backtest_result = results['backtesting']
        print(f"\n📈 Backtesting:")
        print(f"   Status: {'✅' if backtest_result['success'] else '❌'}")
        print(f"   Backtests: {backtest_result.get('successful_backtests', 0)}/{backtest_result.get('total_backtests', 0)}")
        
        # Performance metrics
        if backtest_result.get('summary_metrics'):
            metrics = backtest_result['summary_metrics']
            print(f"\n📊 Performance Summary:")
            print(f"   Average Win Rate: {metrics.get('average_win_rate', 0):.2%}")
            print(f"   Average Profit Factor: {metrics.get('average_profit_factor', 0):.2f}")
            print(f"   Average Max Drawdown: {metrics.get('average_max_drawdown', 0):.2%}")
            print(f"   Best Timeframe: {metrics.get('best_timeframe', 'N/A')}")
            
            benchmarks = metrics.get('meets_benchmarks', {})
            if benchmarks.get('overall_benchmark'):
                print("   🎯 Meets all performance benchmarks!")
            else:
                print("   ⚠️  Does not meet all benchmarks")
        
        # Screenshot results
        screenshot_result = results['screenshots']
        print(f"\n📸 Screenshots:")
        print(f"   Status: {'✅' if screenshot_result['success'] else '❌'}")
        print(f"   Captured: {screenshot_result.get('successful_screenshots', 0)}")
        
        if screenshot_result.get('comparison_image'):
            print(f"   Comparison: {screenshot_result['comparison_image']}")
        
        # Errors
        if results['errors']:
            print(f"\n❌ Errors:")
            for error in results['errors']:
                print(f"   • {error}")
        
        print(f"\n✅ Example 1 completed!")
        return results
        
    except Exception as e:
        print(f"❌ Example 1 failed: {e}")
        return None


async def example_2_quick_indicator_testing():
    """
    Example 2: Quick indicator testing for rapid development
    
    This example shows how to quickly test specific indicators
    without running the full workflow.
    """
    print("\n🧪 Example 2: Quick Indicator Testing")
    print("=" * 50)
    
    try:
        # Authenticate
        auth = GrimmAuthManager()
        print("🔐 Starting authentication...")
        
        # In a real scenario, this would prompt for OAuth
        # For this example, we'll simulate successful authentication
        print("✅ Authentication successful (simulated)")
        
        # Create test runner
        test_runner = TradingViewTestRunner(
            auth, 
            results_dir="./example_results/quick_testing"
        )
        
        # Configure quick test
        config = TestConfiguration(
            strategy_path="strategies/example-strategy",
            indicators=["RSI", "MACD", "EMA_21"],
            tickers=["MNQ1!"],
            timeframes=["1h"],
            test_duration=60,  # Quick 1-minute test
            capture_screenshots=True,
            parallel_execution=True
        )
        
        print(f"📊 Testing indicators: {config.indicators}")
        print(f"📈 Ticker: {config.tickers[0]}")
        print(f"⏱️  Timeframe: {config.timeframes[0]}")
        
        # Run quick test (would be actual test in real scenario)
        print("🔄 Running indicator tests...")
        
        # Simulate test results
        mock_results = [
            type('TestResult', (), {
                'indicator_name': 'RSI',
                'ticker': 'MNQ1!',
                'timeframe': '1h',
                'success': True,
                'values': {'RSI': 67.5},
                'signals': [{'type': 'overbought', 'strength': 'moderate'}],
                'execution_time': 15.3,
                'error_message': None
            }),
            type('TestResult', (), {
                'indicator_name': 'MACD',
                'ticker': 'MNQ1!', 
                'timeframe': '1h',
                'success': True,
                'values': {'MACD': 0.45, 'Signal': 0.32, 'Histogram': 0.13},
                'signals': [{'type': 'bullish_crossover', 'strength': 'strong'}],
                'execution_time': 18.7,
                'error_message': None
            })
        ]
        
        # Display results
        print(f"\n📊 Test Results:")
        successful_tests = [r for r in mock_results if r.success]
        print(f"   Successful: {len(successful_tests)}/{len(mock_results)}")
        
        for result in mock_results:
            status = "✅" if result.success else "❌"
            print(f"   {status} {result.indicator_name}: {result.execution_time:.1f}s")
            if result.values:
                values_str = ", ".join([f"{k}={v}" for k, v in result.values.items()])
                print(f"      Values: {values_str}")
            if result.signals:
                for signal in result.signals:
                    print(f"      Signal: {signal['type']} ({signal['strength']})")
        
        print(f"\n✅ Example 2 completed!")
        return mock_results
        
    except Exception as e:
        print(f"❌ Example 2 failed: {e}")
        return None


async def example_3_comprehensive_backtesting():
    """
    Example 3: Comprehensive strategy backtesting
    
    This example demonstrates detailed backtesting with optimization
    and performance analysis.
    """
    print("\n📈 Example 3: Comprehensive Backtesting")
    print("=" * 50)
    
    try:
        # Setup authentication (simulated)
        auth = GrimmAuthManager()
        print("✅ Authentication ready")
        
        # Create backtest runner
        backtester = StrategyBacktester(
            auth,
            results_dir="./example_results/backtesting"
        )
        
        # Configure comprehensive backtest
        config = BacktestConfiguration(
            strategy_path="strategies/ma-crossover-strategy",
            tickers=["MNQ1!"],
            timeframes=["5m", "15m", "1h"],
            initial_capital=25000.0,
            commission=0.75,
            slippage=0.25,
            position_size_type="fixed",
            position_size_value=1.0,
            max_drawdown_limit=0.20,
            capture_screenshots=True,
            optimization_enabled=True,
            optimization_parameters={
                "fast_ma": {"min": 5, "max": 50, "step": 5},
                "slow_ma": {"min": 20, "max": 200, "step": 10},
                "stop_loss": {"min": 5, "max": 25, "step": 2.5}
            }
        )
        
        print(f"💰 Initial Capital: ${config.initial_capital:,.0f}")
        print(f"💸 Commission: ${config.commission}/side")
        print(f"📊 Timeframes: {', '.join(config.timeframes)}")
        print(f"🔧 Optimization: {'✅' if config.optimization_enabled else '❌'}")
        
        # Simulate backtest results
        print("🔄 Running backtests...")
        
        # Create mock backtest results
        mock_metrics = type('BacktestMetrics', (), {
            'total_trades': 156,
            'winning_trades': 89,
            'losing_trades': 67,
            'win_rate': 0.571,  # 57.1%
            'profit_factor': 1.68,
            'total_pnl': 8750.50,
            'max_drawdown_percent': 0.124,  # 12.4%
            'sharpe_ratio': 1.34,
            'average_win': 225.75,
            'average_loss': -156.25,
            'largest_win': 875.00,
            'largest_loss': -425.50,
            'execution_time': 45.2
        })
        
        mock_backtest_results = [
            type('BacktestResult', (), {
                'ticker': 'MNQ1!',
                'timeframe': '5m',
                'success': True,
                'metrics': mock_metrics,
                'trades': [{'entry_time': '2024-01-15 09:30', 'pnl': 150.0}] * 52,
                'error_message': None
            }),
            type('BacktestResult', (), {
                'ticker': 'MNQ1!',
                'timeframe': '15m', 
                'success': True,
                'metrics': type('BacktestMetrics', (), {
                    **{k: v for k, v in vars(mock_metrics).items()},
                    'total_trades': 98,
                    'win_rate': 0.612,
                    'profit_factor': 1.89
                })(),
                'trades': [{'entry_time': '2024-01-15 10:00', 'pnl': 200.0}] * 33,
                'error_message': None
            })
        ]
        
        # Display results
        print(f"\n📊 Backtest Results:")
        successful_backtests = [r for r in mock_backtest_results if r.success]
        print(f"   Successful: {len(successful_backtests)}/{len(mock_backtest_results)}")
        
        for result in successful_backtests:
            print(f"\n   📈 {result.ticker} {result.timeframe}:")
            metrics = result.metrics
            print(f"      Total Trades: {metrics.total_trades}")
            print(f"      Win Rate: {metrics.win_rate:.1%}")
            print(f"      Profit Factor: {metrics.profit_factor:.2f}")
            print(f"      Total P&L: ${metrics.total_pnl:,.2f}")
            print(f"      Max Drawdown: {metrics.max_drawdown_percent:.1%}")
            print(f"      Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
            
            # Benchmark evaluation
            mnq_config = create_mnq_config()
            benchmarks = mnq_config.get_performance_benchmarks()
            
            meets_benchmarks = (
                metrics.win_rate >= benchmarks['min_win_rate'] and
                metrics.profit_factor >= benchmarks['min_profit_factor'] and
                metrics.max_drawdown_percent <= benchmarks['max_drawdown']
            )
            
            print(f"      Benchmarks: {'✅ PASS' if meets_benchmarks else '❌ FAIL'}")
        
        # Optimization results
        if config.optimization_enabled:
            print(f"\n🔧 Optimization Results:")
            print(f"   Best Parameters: Fast MA=15, Slow MA=50, Stop Loss=10")
            print(f"   Optimization Runs: 144")
            print(f"   Best Profit Factor: 2.15")
        
        print(f"\n✅ Example 3 completed!")
        return mock_backtest_results
        
    except Exception as e:
        print(f"❌ Example 3 failed: {e}")
        return None


async def example_4_automated_screenshots():
    """
    Example 4: Automated chart screenshot capture
    
    This example shows how to capture high-quality annotated
    screenshots for strategy documentation.
    """
    print("\n📸 Example 4: Automated Screenshots")
    print("=" * 50)
    
    try:
        # Setup authentication
        auth = GrimmAuthManager()
        print("✅ Authentication ready")
        
        # Create screenshot manager
        screenshot_manager = ChartScreenshotManager(
            auth,
            output_dir="./example_results/screenshots"
        )
        
        # Configure screenshot capture
        config = ScreenshotConfiguration(
            strategy_name="Bollinger Bands Reversal",
            ticker="MNQ1!",
            timeframe="1h",
            chart_style="candles",
            theme="dark",
            indicators_visible=True,
            volume_visible=True,
            annotation_enabled=True,
            annotation_text="Example setup showing BB squeeze breakout",
            output_format="png",
            quality=95
        )
        
        print(f"📈 Strategy: {config.strategy_name}")
        print(f"📊 Ticker: {config.ticker}")
        print(f"⏱️  Timeframe: {config.timeframe}")
        print(f"🎨 Theme: {config.theme}")
        print(f"📝 Annotations: {'✅' if config.annotation_enabled else '❌'}")
        
        # Capture individual screenshot
        print("\n🔄 Capturing individual screenshot...")
        
        # Simulate screenshot capture
        individual_result = type('ScreenshotResult', (), {
            'success': True,
            'file_path': f"./example_results/screenshots/{config.strategy_name}/MNQ1_1h_20240115_143022.png",
            'thumbnail_path': f"./example_results/screenshots/{config.strategy_name}/thumb_MNQ1_1h_20240115_143022.png",
            'file_size': 1024 * 750,  # 750KB
            'capture_time': datetime.now(),
            'metadata': {
                'ticker': config.ticker,
                'timeframe': config.timeframe,
                'current_price': '17,235.50',
                'price_change': '+125.75 (+0.73%)',
                'volume': '45,678'
            },
            'error_message': None
        })
        
        if individual_result.success:
            print(f"   ✅ Screenshot captured: {individual_result.file_path}")
            print(f"   📁 File size: {individual_result.file_size / 1024:.1f} KB")
            print(f"   🖼️  Thumbnail: {individual_result.thumbnail_path}")
            
            # Display metadata
            if individual_result.metadata:
                print(f"   📊 Market Data:")
                for key, value in individual_result.metadata.items():
                    if key in ['current_price', 'price_change', 'volume']:
                        print(f"      {key.replace('_', ' ').title()}: {value}")
        
        # Capture strategy screenshots (multiple timeframes)
        print(f"\n🔄 Capturing strategy screenshots across timeframes...")
        
        # Simulate multiple screenshots
        strategy_results = []
        timeframes = ["5m", "15m", "1h", "4h"]
        
        for tf in timeframes:
            result = type('ScreenshotResult', (), {
                'success': True,
                'file_path': f"./example_results/screenshots/{config.strategy_name}/MNQ1_{tf}_20240115_143022.png",
                'thumbnail_path': f"./example_results/screenshots/{config.strategy_name}/thumb_MNQ1_{tf}_20240115_143022.png",
                'file_size': 1024 * (650 + hash(tf) % 200),  # Varying file sizes
                'capture_time': datetime.now(),
                'metadata': {'timeframe': tf, 'ticker': 'MNQ1!'},
                'error_message': None
            })
            strategy_results.append(result)
        
        successful_screenshots = [r for r in strategy_results if r.success]
        print(f"   ✅ Captured {len(successful_screenshots)}/{len(strategy_results)} screenshots")
        
        for result in successful_screenshots:
            tf = result.metadata['timeframe']
            size_kb = result.file_size / 1024
            print(f"      📊 {tf}: {size_kb:.1f} KB")
        
        # Create comparison image
        print(f"\n🔄 Creating comparison image...")
        
        if len(successful_screenshots) > 1:
            screenshot_paths = [r.file_path for r in successful_screenshots]
            comparison_path = "./example_results/screenshots/comparison_bollinger_bands.png"
            
            # Simulate comparison creation
            comparison_success = True
            
            if comparison_success:
                print(f"   ✅ Comparison image created: {comparison_path}")
                print(f"   🖼️  Layout: 2x2 grid")
                print(f"   📐 Dimensions: 1600x1200 pixels")
            else:
                print(f"   ❌ Comparison image creation failed")
        
        print(f"\n✅ Example 4 completed!")
        return {
            'individual_result': individual_result,
            'strategy_results': strategy_results,
            'comparison_created': comparison_success if len(successful_screenshots) > 1 else False
        }
        
    except Exception as e:
        print(f"❌ Example 4 failed: {e}")
        return None


async def example_5_mnq_configuration():
    """
    Example 5: MNQ1! Configuration and Optimization
    
    This example demonstrates the specialized MNQ1! configuration
    and how to optimize strategies for futures trading.
    """
    print("\n📈 Example 5: MNQ1! Configuration")
    print("=" * 50)
    
    try:
        # Create MNQ configuration
        mnq_config = create_mnq_config()
        
        print(f"📊 MNQ1! Specifications:")
        print(f"   Symbol: {mnq_config.symbol}")
        print(f"   Exchange: {mnq_config.exchange}")
        print(f"   Contract Size: ${mnq_config.contract_size}/point")
        print(f"   Minimum Tick: {mnq_config.minimum_tick} points")
        print(f"   Tick Value: ${mnq_config.tick_value}")
        print(f"   Commission: ${mnq_config.commission_per_side}/side")
        print(f"   Total Round Turn: ${mnq_config.total_round_turn_cost}")
        
        # Trading hours
        print(f"\n⏰ Trading Hours (CME Globex):")
        for day, hours in mnq_config.trading_hours.items():
            print(f"   {day.capitalize()}: {hours}")
        
        # High liquidity periods
        print(f"\n💧 High Liquidity Hours:")
        for period in mnq_config.high_liquidity_hours:
            print(f"   {period} CT")
        
        # Test timeframes
        print(f"\n⏱️  Default Test Timeframes:")
        for i, tf in enumerate(mnq_config.test_timeframes, 1):
            print(f"   {i}. {tf}")
        
        # Get testing configuration
        test_config = mnq_config.get_testing_config()
        print(f"\n🧪 Testing Configuration:")
        print(f"   Initial Capital: ${test_config['initial_capital']:,.0f}")
        print(f"   Position Size: {test_config['position_size']} contract(s)")
        print(f"   Stop Loss: {test_config['stop_loss']} points")
        print(f"   Take Profit: {test_config['take_profit']} points")
        
        # Performance benchmarks
        benchmarks = mnq_config.get_performance_benchmarks()
        print(f"\n🎯 Performance Benchmarks:")
        print(f"   Minimum Win Rate: {benchmarks['min_win_rate']:.0%}")
        print(f"   Minimum Profit Factor: {benchmarks['min_profit_factor']:.2f}")
        print(f"   Maximum Drawdown: {benchmarks['max_drawdown']:.0%}")
        print(f"   Target Annual Return: {benchmarks['target_annual_return']:.0%}")
        print(f"   Minimum Sharpe Ratio: {benchmarks['min_sharpe_ratio']:.1f}")
        
        # Optimization ranges
        opt_ranges = mnq_config.get_optimization_ranges()
        print(f"\n🔧 Optimization Ranges:")
        
        # Moving averages
        ma_ranges = opt_ranges['moving_averages']
        print(f"   Moving Averages:")
        print(f"      Fast MA: {ma_ranges['fast_ma']['min']}-{ma_ranges['fast_ma']['max']} (step {ma_ranges['fast_ma']['step']})")
        print(f"      Slow MA: {ma_ranges['slow_ma']['min']}-{ma_ranges['slow_ma']['max']} (step {ma_ranges['slow_ma']['step']})")
        
        # RSI
        rsi_ranges = opt_ranges['rsi']
        print(f"   RSI:")
        print(f"      Period: {rsi_ranges['period']['min']}-{rsi_ranges['period']['max']} (step {rsi_ranges['period']['step']})")
        print(f"      Overbought: {rsi_ranges['overbought']['min']}-{rsi_ranges['overbought']['max']}")
        print(f"      Oversold: {rsi_ranges['oversold']['min']}-{rsi_ranges['oversold']['max']}")
        
        # Stops and targets
        stops_ranges = opt_ranges['stops_and_targets']
        print(f"   Stops & Targets:")
        print(f"      Stop Loss: {stops_ranges['stop_loss']['min']}-{stops_ranges['stop_loss']['max']} points")
        print(f"      Take Profit: {stops_ranges['take_profit']['min']}-{stops_ranges['take_profit']['max']} points")
        
        # Custom configurations for different styles
        print(f"\n🎨 Trading Style Configurations:")
        
        # Scalping config
        scalping_config = create_mnq_config({
            'test_timeframes': ['1m', '5m'],
            'default_stop_loss': 5.0,
            'default_take_profit': 10.0,
            'position_size_default': 2
        })
        print(f"   Scalping: {scalping_config.default_stop_loss}pt SL, {scalping_config.default_take_profit}pt TP")
        
        # Swing config
        swing_config = create_mnq_config({
            'test_timeframes': ['1h', '4h', '1d'],
            'default_stop_loss': 25.0,
            'default_take_profit': 50.0,
            'initial_capital': 50000.0
        })
        print(f"   Swing: {swing_config.default_stop_loss}pt SL, {swing_config.default_take_profit}pt TP")
        
        # Calculate potential profit/loss
        print(f"\n💰 P&L Examples (1 contract):")
        contract_size = mnq_config.contract_size
        tick_value = mnq_config.tick_value
        
        print(f"   10-point move: ${10 * contract_size:.2f}")
        print(f"   1-tick move: ${tick_value:.2f}")
        print(f"   50-point stop: ${50 * contract_size:.2f} risk")
        print(f"   100-point target: ${100 * contract_size:.2f} profit")
        
        # Risk examples
        print(f"\n⚠️  Risk Examples:")
        margin = mnq_config.margin_requirement
        print(f"   Margin Requirement: ${margin:,.0f}")
        print(f"   Leverage: ~{mnq_config.initial_capital / margin:.1f}:1")
        print(f"   1% Account Risk: ${mnq_config.initial_capital * 0.01:.0f}")
        print(f"   Points for 1% Risk: {(mnq_config.initial_capital * 0.01) / contract_size:.1f}")
        
        print(f"\n✅ Example 5 completed!")
        return mnq_config
        
    except Exception as e:
        print(f"❌ Example 5 failed: {e}")
        return None


async def run_all_examples():
    """
    Run all examples in sequence to demonstrate the complete
    Kairos Integration Framework capabilities.
    """
    print("🚀 Running All Kairos Integration Examples")
    print("=" * 60)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {}
    
    try:
        # Example 1: Complete workflow
        results['complete_workflow'] = await example_1_complete_strategy_workflow()
        
        # Example 2: Quick testing
        results['quick_testing'] = await example_2_quick_indicator_testing()
        
        # Example 3: Backtesting
        results['backtesting'] = await example_3_comprehensive_backtesting()
        
        # Example 4: Screenshots
        results['screenshots'] = await example_4_automated_screenshots()
        
        # Example 5: MNQ configuration
        results['mnq_config'] = await example_5_mnq_configuration()
        
        # Summary
        print("\n📊 Examples Summary")
        print("=" * 50)
        
        successful_examples = sum(1 for result in results.values() if result is not None)
        total_examples = len(results)
        
        print(f"✅ Successful Examples: {successful_examples}/{total_examples}")
        
        for name, result in results.items():
            status = "✅" if result is not None else "❌"
            print(f"   {status} {name.replace('_', ' ').title()}")
        
        if successful_examples == total_examples:
            print(f"\n🎉 All examples completed successfully!")
            print(f"📁 Results saved in: ./example_results/")
        else:
            print(f"\n⚠️  Some examples failed. Check the output above for details.")
        
        print(f"\n📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return results
        
    except Exception as e:
        print(f"❌ Failed to run all examples: {e}")
        return results


def create_example_strategy_directory():
    """
    Create an example strategy directory structure for testing.
    """
    print("📁 Creating example strategy directory...")
    
    strategy_dir = Path("strategies/example-rsi-strategy")
    strategy_dir.mkdir(parents=True, exist_ok=True)
    
    # Create Pine Script directory
    pinescript_dir = strategy_dir / "pinescript"
    pinescript_dir.mkdir(exist_ok=True)
    
    # Create example strategy file
    strategy_content = '''
//@version=5
strategy("Example RSI Strategy", overlay=false, initial_capital=25000, default_qty_type=strategy.fixed, default_qty_value=1)

// Input parameters
rsiLength = input.int(14, "RSI Length", minval=1)
overbought = input.int(70, "Overbought Level", minval=50, maxval=100)
oversold = input.int(30, "Oversold Level", minval=0, maxval=50)
stopLoss = input.float(10.0, "Stop Loss (Points)", minval=1.0, step=0.25)
takeProfit = input.float(20.0, "Take Profit (Points)", minval=1.0, step=0.25)

// Calculate RSI
rsi = ta.rsi(close, rsiLength)

// Entry conditions
longCondition = ta.crossover(rsi, oversold)
shortCondition = ta.crossunder(rsi, overbought)

// Entry orders
if longCondition
    strategy.entry("Long", strategy.long)
    strategy.exit("Long Exit", "Long", stop=close - stopLoss, limit=close + takeProfit)

if shortCondition
    strategy.entry("Short", strategy.short)
    strategy.exit("Short Exit", "Short", stop=close + stopLoss, limit=close - takeProfit)

// Plot RSI
plot(rsi, "RSI", color.blue)
hline(overbought, "Overbought", color.red, linestyle=hline.style_dashed)
hline(oversold, "Oversold", color.green, linestyle=hline.style_dashed)
hline(50, "Midline", color.gray, linestyle=hline.style_dotted)
'''
    
    with open(pinescript_dir / "strategy.pine", 'w') as f:
        f.write(strategy_content.strip())
    
    # Create README
    readme_content = '''
# Example RSI Strategy

## Overview
A simple RSI-based mean reversion strategy for demonstration purposes.

## Description
This strategy uses the Relative Strength Index (RSI) to identify overbought and oversold conditions in the market. It enters long positions when RSI crosses above the oversold level (default 30) and short positions when RSI crosses below the overbought level (default 70).

## Parameters
- **RSI Length**: 14 periods (default)
- **Overbought Level**: 70 (default)
- **Oversold Level**: 30 (default)
- **Stop Loss**: 10 points (default)
- **Take Profit**: 20 points (default)

## Market Suitability
- **Timeframes**: 5m, 15m, 1h, 4h
- **Markets**: Futures (MNQ1!), Stocks, Forex
- **Conditions**: Ranging/sideways markets

## Risk Management
- Fixed stop loss and take profit levels
- 2:1 risk/reward ratio
- Maximum 1 position at a time

## Performance Expectations
- Win Rate: 45-55%
- Profit Factor: 1.3-1.8
- Best Performance: Ranging markets
'''
    
    with open(strategy_dir / "README.md", 'w') as f:
        f.write(readme_content.strip())
    
    print(f"✅ Example strategy created: {strategy_dir}")
    print(f"   📁 Pine Script: {pinescript_dir / 'strategy.pine'}")
    print(f"   📄 README: {strategy_dir / 'README.md'}")
    
    return str(strategy_dir)


if __name__ == "__main__":
    print("🚀 Kairos Integration Framework Examples")
    print("=" * 60)
    print()
    print("This script demonstrates the capabilities of the Kairos Integration Framework")
    print("for automated trading strategy testing and validation.")
    print()
    print("Note: These examples use simulated data for demonstration purposes.")
    print("In a real environment, actual TradingView automation would be performed.")
    print()
    
    # Create example strategy directory
    example_strategy_path = create_example_strategy_directory()
    print()
    
    # Run examples
    asyncio.run(run_all_examples())
    
    print()
    print("📚 Next Steps:")
    print("1. Set up Google OAuth credentials")
    print("2. Install grimm-kairos and ensure it's in your Python path")
    print("3. Create your own strategy in the strategies/ directory")
    print("4. Run the integration framework on your strategy")
    print()
    print("For more information, see the README.md file.")