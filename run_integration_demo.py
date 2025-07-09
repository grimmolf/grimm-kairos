#!/usr/bin/env python3
"""
Kairos Integration Framework Demonstration

This script demonstrates the capabilities of the Kairos Integration Framework
without requiring the actual grimm-kairos installation. Perfect for understanding
the integration before setting up the full environment.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime


def create_example_strategy_directory():
    """Create an example strategy directory structure for testing."""
    print("📁 Creating example strategy directory...")
    
    strategy_dir = Path("strategies/example-rsi-strategy")
    strategy_dir.mkdir(parents=True, exist_ok=True)
    
    # Create Pine Script directory
    pinescript_dir = strategy_dir / "pinescript"
    pinescript_dir.mkdir(exist_ok=True)
    
    # Create example strategy file
    strategy_content = '''
//@version=5
strategy("Example RSI Strategy for MNQ1!", overlay=false, 
         initial_capital=25000, default_qty_type=strategy.fixed, default_qty_value=1,
         commission_type=strategy.commission.cash_per_contract, commission_value=0.75)

// Input parameters optimized for MNQ1!
rsiLength = input.int(14, "RSI Length", minval=1)
overbought = input.int(70, "Overbought Level", minval=50, maxval=100)
oversold = input.int(30, "Oversold Level", minval=0, maxval=50)
stopLoss = input.float(10.0, "Stop Loss (Points)", minval=1.0, step=0.25)
takeProfit = input.float(20.0, "Take Profit (Points)", minval=1.0, step=0.25)

// Time filter for MNQ high liquidity hours
startHour = input.int(8, "Start Hour (CT)", minval=0, maxval=23)
endHour = input.int(16, "End Hour (CT)", minval=0, maxval=23)
timeFilter = hour >= startHour and hour <= endHour

// Calculate RSI
rsi = ta.rsi(close, rsiLength)

// Entry conditions with time filter
longCondition = ta.crossover(rsi, oversold) and timeFilter
shortCondition = ta.crossunder(rsi, overbought) and timeFilter

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

// Table for performance info
if barstate.islast
    var table infoTable = table.new(position.top_right, 2, 4, bgcolor=color.white, border_width=1)
    table.cell(infoTable, 0, 0, "Strategy", text_color=color.black, bgcolor=color.gray)
    table.cell(infoTable, 1, 0, "RSI MNQ1!", text_color=color.black, bgcolor=color.white)
    table.cell(infoTable, 0, 1, "RSI", text_color=color.black, bgcolor=color.gray)
    table.cell(infoTable, 1, 1, str.tostring(rsi, "#.##"), text_color=color.black, bgcolor=color.white)
    table.cell(infoTable, 0, 2, "Signal", text_color=color.black, bgcolor=color.gray)
    signal_text = rsi > overbought ? "Overbought" : rsi < oversold ? "Oversold" : "Neutral"
    table.cell(infoTable, 1, 2, signal_text, text_color=color.black, bgcolor=color.white)
    table.cell(infoTable, 0, 3, "Time Filter", text_color=color.black, bgcolor=color.gray)
    table.cell(infoTable, 1, 3, timeFilter ? "Active" : "Inactive", 
               text_color=timeFilter ? color.green : color.red, bgcolor=color.white)
'''
    
    with open(pinescript_dir / "strategy.pine", 'w') as f:
        f.write(strategy_content.strip())
    
    # Create README
    readme_content = '''
# Example RSI Strategy for MNQ1!

## Overview
A simple RSI-based mean reversion strategy optimized for MNQ1! (Micro E-mini Nasdaq-100) futures trading.

## Description
This strategy uses the Relative Strength Index (RSI) to identify overbought and oversold conditions in MNQ1!. It includes time filters for high liquidity hours and is configured with appropriate commission and slippage for futures trading.

## MNQ1! Specifications
- **Symbol**: MNQ1! (Micro E-mini Nasdaq-100)
- **Exchange**: CME Globex
- **Contract Size**: $2 per index point
- **Minimum Tick**: 0.25 points ($0.50 value)
- **Commission**: $0.75 per side (configured in strategy)
- **Trading Hours**: Nearly 24 hours (Sunday 5 PM - Friday 4:15 PM CT)

## Strategy Parameters
- **RSI Length**: 14 periods (default)
- **Overbought Level**: 70 (default)
- **Oversold Level**: 30 (default)
- **Stop Loss**: 10 points (default) = $20 risk per contract
- **Take Profit**: 20 points (default) = $40 profit per contract
- **Time Filter**: 8 AM - 4 PM CT (high liquidity hours)

## Entry Conditions
- **Long Entry**: RSI crosses above 30 during market hours
- **Short Entry**: RSI crosses below 70 during market hours
- **Time Filter**: Only trade during high liquidity hours (8 AM - 4 PM CT)

## Risk Management
- **Risk/Reward**: 1:2 ratio (10pt stop, 20pt target)
- **Position Size**: 1 contract (default)
- **Maximum Risk per Trade**: $20 (10 points × $2/point)
- **Maximum Profit per Trade**: $40 (20 points × $2/point)

## Market Suitability
- **Primary Timeframes**: 5m, 15m, 1h
- **Market Conditions**: Ranging/sideways markets
- **Volatility**: Medium volatility periods

## Performance Expectations
- **Target Win Rate**: 45-55%
- **Target Profit Factor**: 1.3-1.8
- **Maximum Drawdown**: <15%
- **Best Performance**: During US market hours with good liquidity

## Kairos Integration
This strategy is configured for automated testing with the Kairos Integration Framework:
- Optimized for MNQ1! contract specifications
- Includes time filters for high-liquidity testing
- Configured with realistic commission and slippage
- Ready for multi-timeframe backtesting
'''
    
    with open(strategy_dir / "README.md", 'w') as f:
        f.write(readme_content.strip())
    
    # Create automation directory
    automation_dir = strategy_dir / "automation"
    automation_dir.mkdir(exist_ok=True)
    
    # Create workflow config
    workflow_config = '''
# Kairos Integration Workflow Configuration for RSI Strategy

strategy_name: "Example RSI Strategy"
description: "RSI mean reversion strategy optimized for MNQ1!"

# Testing Configuration
testing:
  primary_ticker: "MNQ1!"
  timeframes:
    - "5m"
    - "15m" 
    - "1h"
    - "4h"
  indicators:
    - "RSI"
    - "EMA_21"
    - "SMA_50"
  test_duration: 300  # 5 minutes
  capture_screenshots: true

# Backtesting Configuration  
backtesting:
  initial_capital: 25000.0
  commission: 0.75  # Per side
  slippage: 0.25    # Points
  position_size: 1  # Contracts
  optimization_enabled: true
  optimization_params:
    rsi_length: [10, 14, 18, 22]
    overbought: [65, 70, 75, 80]
    oversold: [20, 25, 30, 35]
    stop_loss: [5, 10, 15, 20]
    take_profit: [10, 20, 30, 40]

# Screenshot Configuration
screenshots:
  theme: "dark"
  chart_style: "candles"
  timeframes: ["5m", "1h", "4h"]
  annotations: true
  annotation_text: "RSI Strategy Setup on MNQ1!"

# Performance Benchmarks
benchmarks:
  min_win_rate: 0.45      # 45%
  min_profit_factor: 1.25  # 1.25
  max_drawdown: 0.15      # 15%
  min_trades: 50          # Minimum trades for validity
'''
    
    with open(automation_dir / "workflow_config.yaml", 'w') as f:
        f.write(workflow_config.strip())
    
    print(f"✅ Example strategy created: {strategy_dir}")
    print(f"   📄 Pine Script: {pinescript_dir / 'strategy.pine'}")
    print(f"   📖 README: {strategy_dir / 'README.md'}")
    print(f"   ⚙️  Workflow Config: {automation_dir / 'workflow_config.yaml'}")
    
    return str(strategy_dir)


async def simulate_workflow_execution(strategy_path):
    """Simulate the execution of the Kairos Integration Framework workflow."""
    print(f"🚀 Simulating Kairos Integration Workflow")
    print(f"📁 Strategy: {strategy_path}")
    print("=" * 60)
    
    # Step 1: Authentication simulation
    print("🔐 Step 1: Authentication")
    print("   📧 User: grimm@greysson.com")
    print("   🔑 OAuth Flow: Google authentication")
    print("   💾 Token Caching: Enabled")
    await asyncio.sleep(1)
    print("   ✅ Authentication successful")
    print()
    
    # Step 2: Strategy loading
    print("📁 Step 2: Strategy Loading")
    print("   📖 Reading strategy files...")
    print("   🧠 Analyzing Pine Script logic...")
    print("   ⚙️  Loading configuration...")
    await asyncio.sleep(1)
    print("   ✅ Strategy loaded successfully")
    print("      • Name: Example RSI Strategy")
    print("      • Type: Mean Reversion")
    print("      • Indicators: RSI, EMA, SMA")
    print()
    
    # Step 3: Indicator testing
    print("🧪 Step 3: Indicator Testing on MNQ1!")
    test_results = []
    
    indicators = ["RSI", "EMA_21", "SMA_50"]
    timeframes = ["5m", "15m", "1h", "4h"]
    
    for i, indicator in enumerate(indicators):
        for j, timeframe in enumerate(timeframes):
            print(f"   🔄 Testing {indicator} on {timeframe}...")
            await asyncio.sleep(0.5)
            
            # Simulate different results
            if indicator == "RSI" and timeframe == "1h":
                value = 67.5
                signal = "Approaching overbought"
            elif indicator == "EMA_21" and timeframe == "1h":
                value = 17234.25
                signal = "Price above EMA (bullish)"
            elif indicator == "SMA_50" and timeframe == "4h":
                value = 17198.50
                signal = "Price above SMA (bullish)"
            else:
                value = 17225.0 + (i * 10) + (j * 2)
                signal = "Neutral"
            
            result = {
                'indicator': indicator,
                'timeframe': timeframe,
                'value': value,
                'signal': signal,
                'success': True,
                'execution_time': 12.5 + (i * 2) + (j * 0.5)
            }
            test_results.append(result)
            print(f"      ✅ {indicator} ({timeframe}): {value:.2f} - {signal}")
    
    print(f"   📊 Test Summary: {len(test_results)}/{len(test_results)} successful")
    print(f"   ⏱️  Average execution time: {sum(r['execution_time'] for r in test_results) / len(test_results):.1f}s")
    print()
    
    # Step 4: Backtesting
    print("📈 Step 4: Strategy Backtesting")
    backtest_results = []
    
    for timeframe in ["5m", "15m", "1h"]:
        print(f"   🔄 Backtesting on {timeframe}...")
        await asyncio.sleep(1)
        
        # Simulate backtest results
        if timeframe == "5m":
            metrics = {
                'total_trades': 156,
                'win_rate': 0.571,
                'profit_factor': 1.68,
                'total_pnl': 4250.50,
                'max_drawdown': 0.124,
                'sharpe_ratio': 1.34
            }
        elif timeframe == "15m":
            metrics = {
                'total_trades': 98,
                'win_rate': 0.612,
                'profit_factor': 1.89,
                'total_pnl': 5180.75,
                'max_drawdown': 0.098,
                'sharpe_ratio': 1.67
            }
        else:  # 1h
            metrics = {
                'total_trades': 67,
                'win_rate': 0.582,
                'profit_factor': 1.76,
                'total_pnl': 3940.25,
                'max_drawdown': 0.102,
                'sharpe_ratio': 1.52
            }
        
        backtest_results.append({
            'timeframe': timeframe,
            'metrics': metrics,
            'success': True
        })
        
        print(f"      ✅ {timeframe}: {metrics['win_rate']:.1%} win rate, {metrics['profit_factor']:.2f} PF")
    
    print(f"   📊 Backtest Summary: {len(backtest_results)}/{len(backtest_results)} successful")
    print()
    
    # Step 5: Screenshot capture
    print("📸 Step 5: Chart Screenshot Capture")
    screenshot_results = []
    
    for timeframe in ["5m", "1h", "4h"]:
        print(f"   📷 Capturing {timeframe} chart...")
        await asyncio.sleep(0.5)
        
        screenshot_results.append({
            'timeframe': timeframe,
            'file_path': f"./screenshots/rsi_strategy_MNQ1_{timeframe}_20240115_143022.png",
            'file_size_kb': 650 + hash(timeframe) % 200,
            'success': True
        })
        
        print(f"      ✅ {timeframe}: Chart captured successfully")
    
    # Comparison image
    print("   🖼️  Creating comparison image...")
    await asyncio.sleep(0.5)
    print("      ✅ Comparison image created: ./screenshots/rsi_strategy_comparison.png")
    print()
    
    # Step 6: Performance analysis
    print("📊 Step 6: Performance Analysis")
    
    # Calculate aggregate metrics
    avg_win_rate = sum(r['metrics']['win_rate'] for r in backtest_results) / len(backtest_results)
    avg_profit_factor = sum(r['metrics']['profit_factor'] for r in backtest_results) / len(backtest_results)
    max_drawdown = max(r['metrics']['max_drawdown'] for r in backtest_results)
    total_pnl = sum(r['metrics']['total_pnl'] for r in backtest_results)
    
    print(f"   📈 Aggregate Performance:")
    print(f"      Average Win Rate: {avg_win_rate:.1%}")
    print(f"      Average Profit Factor: {avg_profit_factor:.2f}")
    print(f"      Maximum Drawdown: {max_drawdown:.1%}")
    print(f"      Total P&L: ${total_pnl:,.2f}")
    print()
    
    # Benchmark evaluation
    benchmarks = {
        'min_win_rate': 0.45,
        'min_profit_factor': 1.25,
        'max_drawdown': 0.15
    }
    
    win_rate_pass = avg_win_rate >= benchmarks['min_win_rate']
    pf_pass = avg_profit_factor >= benchmarks['min_profit_factor']
    dd_pass = max_drawdown <= benchmarks['max_drawdown']
    overall_pass = win_rate_pass and pf_pass and dd_pass
    
    print(f"   🎯 Benchmark Evaluation:")
    print(f"      Win Rate: {'✅ PASS' if win_rate_pass else '❌ FAIL'} ({avg_win_rate:.1%} vs {benchmarks['min_win_rate']:.0%} min)")
    print(f"      Profit Factor: {'✅ PASS' if pf_pass else '❌ FAIL'} ({avg_profit_factor:.2f} vs {benchmarks['min_profit_factor']:.2f} min)")
    print(f"      Max Drawdown: {'✅ PASS' if dd_pass else '❌ FAIL'} ({max_drawdown:.1%} vs {benchmarks['max_drawdown']:.0%} max)")
    print(f"      Overall: {'🎉 STRATEGY APPROVED' if overall_pass else '⚠️  NEEDS IMPROVEMENT'}")
    print()
    
    # Step 7: Report generation
    print("📋 Step 7: Report Generation")
    print("   📄 Creating detailed performance report...")
    print("   📊 Generating trade analysis...")
    print("   📈 Creating equity curve charts...")
    print("   📝 Compiling strategy documentation...")
    await asyncio.sleep(1)
    print("   ✅ Comprehensive report generated")
    print("      • Performance Summary: ./reports/rsi_strategy_performance.pdf")
    print("      • Trade Analysis: ./reports/rsi_strategy_trades.csv")
    print("      • Screenshots: ./screenshots/ (4 files)")
    print()
    
    return {
        'overall_success': overall_pass,
        'test_results': test_results,
        'backtest_results': backtest_results,
        'screenshot_results': screenshot_results,
        'performance_metrics': {
            'avg_win_rate': avg_win_rate,
            'avg_profit_factor': avg_profit_factor,
            'max_drawdown': max_drawdown,
            'total_pnl': total_pnl
        },
        'benchmark_evaluation': {
            'win_rate_pass': win_rate_pass,
            'profit_factor_pass': pf_pass,
            'drawdown_pass': dd_pass,
            'overall_pass': overall_pass
        }
    }


def show_integration_info():
    """Show detailed information about the integration framework."""
    print("📋 Kairos Integration Framework Information")
    print("=" * 60)
    print()
    
    print("🎯 Purpose:")
    print("   Automated testing and validation of trading strategies using TradingView")
    print("   and the grimm-kairos automation framework for grimm@greysson.com.")
    print()
    
    print("🔧 Core Components:")
    print("   • GrimmAuthManager - Google OAuth authentication")
    print("   • TradingViewTestRunner - Automated indicator testing")
    print("   • StrategyBacktester - Comprehensive backtesting") 
    print("   • ChartScreenshotManager - Automated chart capture")
    print("   • CompleteWorkflow - End-to-end automation orchestration")
    print()
    
    print("📈 MNQ1! Focus (Micro E-mini Nasdaq-100):")
    print("   • Symbol: MNQ1!")
    print("   • Exchange: CME Globex")
    print("   • Contract Size: $2 per index point")
    print("   • Minimum Tick: 0.25 points ($0.50 value)")
    print("   • Commission: $0.75 per side")
    print("   • Margin: ~$1,320 intraday")
    print("   • Trading Hours: Nearly 24 hours")
    print("   • High Liquidity: 8:30 AM - 4:15 PM CT")
    print()
    
    print("⏱️  Default Test Timeframes:")
    print("   • 1m - Ultra-short term/scalping")
    print("   • 5m - Short-term entries")
    print("   • 15m - Intraday trading")
    print("   • 1h - Swing trading")
    print("   • 4h - Position trading")
    print("   • 1d - Trend following")
    print()
    
    print("🎯 Performance Benchmarks:")
    print("   • Minimum Win Rate: 45%")
    print("   • Minimum Profit Factor: 1.25")
    print("   • Maximum Drawdown: 15%")
    print("   • Minimum Sharpe Ratio: 1.0")
    print("   • Target Annual Return: 30%")
    print()
    
    print("🔐 Authentication:")
    print("   • Google OAuth 2.0 for grimm@greysson.com")
    print("   • Automatic token caching and refresh")
    print("   • Secure session management")
    print("   • TradingView integration")
    print()
    
    print("📊 Automated Testing Features:")
    print("   • Multi-timeframe indicator testing")
    print("   • Real-time value extraction")
    print("   • Signal generation and analysis")
    print("   • Parallel processing for efficiency")
    print("   • Screenshot capture during testing")
    print()
    
    print("📈 Backtesting Capabilities:")
    print("   • Comprehensive performance metrics")
    print("   • Parameter optimization")
    print("   • Risk analysis and validation")
    print("   • Trade-by-trade analysis")
    print("   • Multi-timeframe backtesting")
    print()
    
    print("📸 Screenshot Features:")
    print("   • High-quality chart capture")
    print("   • Automatic annotation and labeling")
    print("   • Multiple themes (dark/light)")
    print("   • Thumbnail generation")
    print("   • Comparison image creation")
    print()
    
    print("💻 System Requirements:")
    print("   • Python 3.10+")
    print("   • grimm-kairos automation framework")
    print("   • Google OAuth credentials")
    print("   • Chrome/Chromium browser")
    print("   • TradingView account")
    print("   • Stable internet connection")
    print()
    
    print("📁 Integration Directory Structure:")
    print("   kairos_integration/")
    print("   ├── core/                     # Core automation classes")
    print("   │   ├── auth_manager.py       # Google OAuth authentication")
    print("   │   ├── test_runner.py        # Indicator testing automation")
    print("   │   ├── backtest_runner.py    # Strategy backtesting")
    print("   │   └── screenshot_manager.py # Chart screenshot capture")
    print("   ├── config/                   # Configuration management")
    print("   │   ├── mnq_config.py         # MNQ1! specific settings")
    print("   │   └── workflow_templates.py # Pre-configured workflows")
    print("   ├── workflows/                # Workflow orchestration")
    print("   │   └── complete_workflow.py  # End-to-end automation")
    print("   ├── tests/                    # Integration tests")
    print("   │   └── test_integration.py   # Comprehensive test suite")
    print("   └── examples/                 # Usage examples")
    print("       └── example_workflows.py  # Example implementations")
    print()


async def main():
    """Main demonstration function."""
    print("🚀 Kairos Integration Framework - Complete Demonstration")
    print("=" * 70)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("ℹ️  This demonstration shows the complete capabilities of the Kairos")
    print("   Integration Framework for automated trading strategy testing.")
    print()
    print("📋 What this demo includes:")
    print("   • Example strategy creation (RSI for MNQ1!)")
    print("   • Complete workflow simulation")
    print("   • Performance analysis and benchmarking")
    print("   • Real-world configuration examples")
    print()
    
    try:
        # Step 1: Create example strategy
        print("📁 Creating Example Strategy")
        print("-" * 40)
        strategy_path = create_example_strategy_directory()
        print()
        
        # Step 2: Show integration info
        print("📋 Integration Framework Overview")
        print("-" * 40)
        show_integration_info()
        
        # Step 3: Simulate workflow execution
        print("🚀 Workflow Simulation")
        print("-" * 40)
        results = await simulate_workflow_execution(strategy_path)
        
        # Step 4: Final summary
        print("🎉 Demonstration Summary")
        print("=" * 60)
        print(f"📊 Overall Success: {'✅ YES' if results['overall_success'] else '❌ NO'}")
        print(f"🧪 Indicator Tests: {len(results['test_results'])}/12 successful")
        print(f"📈 Backtests: {len(results['backtest_results'])}/3 successful")
        print(f"📸 Screenshots: {len(results['screenshot_results'])} captured")
        print()
        
        perf = results['performance_metrics']
        print(f"📊 Performance Summary:")
        print(f"   Average Win Rate: {perf['avg_win_rate']:.1%}")
        print(f"   Average Profit Factor: {perf['avg_profit_factor']:.2f}")
        print(f"   Maximum Drawdown: {perf['max_drawdown']:.1%}")
        print(f"   Total P&L: ${perf['total_pnl']:,.2f}")
        print()
        
        bench = results['benchmark_evaluation']
        if bench['overall_pass']:
            print("🎯 Benchmark Result: ✅ STRATEGY APPROVED FOR LIVE TRADING")
            print("   All performance benchmarks met!")
        else:
            print("🎯 Benchmark Result: ⚠️  STRATEGY NEEDS IMPROVEMENT")
            print("   Some benchmarks not met - requires optimization")
        print()
        
        print("📚 Next Steps for Real Implementation:")
        print("-" * 50)
        print("1. 🔐 Set up Google OAuth credentials")
        print("   • Download from Google Cloud Console")
        print("   • Save as 'credentials.json'")
        print()
        print("2. 🧪 Install grimm-kairos framework")
        print("   • Ensure it's in your Python path")
        print("   • Verify Chrome/Chromium installation")
        print()
        print("3. 🚀 Run real automation:")
        print("   from kairos_integration import CompleteWorkflow")
        print("   workflow = CompleteWorkflow()")
        print("   results = await workflow.run_complete_workflow('strategies/my-strategy')")
        print()
        print("4. 📊 Analyze real results")
        print("   • Review actual performance metrics")
        print("   • Examine captured screenshots")
        print("   • Validate against benchmarks")
        print()
        
        print("📁 Files Created in This Demo:")
        print(f"   • {strategy_path}/pinescript/strategy.pine")
        print(f"   • {strategy_path}/README.md")
        print(f"   • {strategy_path}/automation/workflow_config.yaml")
        print()
        
        print("📖 Documentation:")
        print("   • kairos_integration/README.md - Comprehensive guide")
        print("   • kairos_integration/examples/ - Usage examples")
        print("   • trading-setups/CLAUDE.md - Updated with integration info")
        print()
        
        print(f"📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🎉 Kairos Integration Framework demonstration complete!")
        
        return True
        
    except Exception as e:
        print(f"❌ Demonstration failed: {e}")
        return False


def quick_info():
    """Quick information display."""
    print("📋 Kairos Integration Framework - Quick Info")
    print("=" * 50)
    print()
    print("🎯 Purpose: Automated TradingView strategy testing for grimm@greysson.com")
    print("📈 Focus: MNQ1! (Micro E-mini Nasdaq-100) futures")
    print("🔐 Auth: Google OAuth integration")
    print("🧪 Testing: Multi-timeframe indicator validation")
    print("📊 Backtesting: Comprehensive performance analysis")
    print("📸 Screenshots: Automated chart documentation")
    print()
    print("🚀 Usage: python run_integration_demo.py")
    print("📖 Help: python run_integration_demo.py --help")
    print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("Kairos Integration Framework Demonstration")
            print()
            print("Usage:")
            print("   python run_integration_demo.py          # Full demonstration")
            print("   python run_integration_demo.py --info   # Quick information")
            print("   python run_integration_demo.py --help   # Show this help")
            print()
            print("This script demonstrates the complete Kairos Integration Framework")
            print("capabilities without requiring the actual grimm-kairos installation.")
            sys.exit(0)
        elif sys.argv[1] == "--info":
            quick_info()
            sys.exit(0)
    
    # Run full demonstration
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Demonstration interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)