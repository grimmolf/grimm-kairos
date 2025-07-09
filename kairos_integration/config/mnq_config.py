"""
MNQ1! Configuration for Automated Testing

Provides specialized configuration for NQ Futures (MNQ1!) testing
with optimized settings for futures trading automation.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import json
from pathlib import Path


@dataclass
class MNQConfiguration:
    """
    Specialized configuration for MNQ1! (NQ Futures) testing.
    
    MNQ1! is the Micro E-mini Nasdaq-100 futures contract,
    ideal for testing due to high liquidity and 24-hour trading.
    """
    
    # Symbol Configuration
    symbol: str = "MNQ1!"
    symbol_description: str = "Micro E-mini Nasdaq-100 Futures"
    exchange: str = "CME"
    currency: str = "USD"
    contract_size: float = 2.0  # $2 per index point
    minimum_tick: float = 0.25  # 0.25 index points
    tick_value: float = 0.50   # $0.50 per tick
    
    # Trading Hours (CME Globex)
    trading_hours: Dict[str, str] = None
    
    # Default Timeframes for Testing
    test_timeframes: List[str] = None
    
    # Commission and Fees (typical for futures)
    commission_per_side: float = 0.75  # $0.75 per side
    exchange_fees: float = 0.25        # Exchange fees
    total_round_turn_cost: float = 2.00  # Total cost per round turn
    
    # Risk Management
    default_stop_loss: float = 10.0    # 10 points default stop
    default_take_profit: float = 20.0  # 20 points default target
    max_daily_loss: float = 500.0      # $500 max daily loss
    position_size_default: int = 1     # 1 contract default
    
    # Backtesting Configuration
    initial_capital: float = 25000.0   # $25k minimum for futures
    margin_requirement: float = 1320.0 # Typical intraday margin
    
    # Market Characteristics
    average_daily_volume: int = 500000  # Contracts per day
    average_spread: float = 0.25        # Typical bid-ask spread
    high_liquidity_hours: List[str] = None
    
    # Chart Configuration
    preferred_chart_style: str = "candles"
    default_theme: str = "dark"
    volume_profile_enabled: bool = True
    
    def __post_init__(self):
        """Initialize default values that require computation."""
        if self.trading_hours is None:
            self.trading_hours = {
                "sunday": "17:00-16:15+1",  # Sunday 5:00 PM - Monday 4:15 PM CT
                "monday": "00:00-16:15",    # Continuous
                "tuesday": "17:00-16:15+1", # Tuesday 5:00 PM - Wednesday 4:15 PM CT
                "wednesday": "17:00-16:15+1",
                "thursday": "17:00-16:15+1",
                "friday": "17:00-16:15+1",  # Friday 5:00 PM - Saturday 4:15 PM CT
                "saturday": "00:00-16:15"   # Ends Saturday 4:15 PM CT
            }
            
        if self.test_timeframes is None:
            self.test_timeframes = [
                "1m",   # 1 minute - scalping
                "5m",   # 5 minute - short-term
                "15m",  # 15 minute - intraday
                "1h",   # 1 hour - swing
                "4h",   # 4 hour - position
                "1d"    # Daily - trend
            ]
            
        if self.high_liquidity_hours is None:
            # Peak trading hours (US market open overlap)
            self.high_liquidity_hours = [
                "08:30-11:30",  # Market open (CT)
                "13:30-16:15"   # Afternoon session (CT)
            ]
    
    def get_testing_config(self) -> Dict[str, Any]:
        """Get configuration optimized for automated testing."""
        return {
            'symbol': self.symbol,
            'timeframes': self.test_timeframes,
            'commission': self.commission_per_side,
            'slippage': self.minimum_tick,
            'initial_capital': self.initial_capital,
            'position_size': self.position_size_default,
            'stop_loss': self.default_stop_loss,
            'take_profit': self.default_take_profit,
            'contract_specifications': {
                'contract_size': self.contract_size,
                'tick_size': self.minimum_tick,
                'tick_value': self.tick_value,
                'margin_requirement': self.margin_requirement
            }
        }
    
    def get_chart_config(self) -> Dict[str, Any]:
        """Get configuration for chart screenshot capture."""
        return {
            'symbol': self.symbol,
            'timeframes': self.test_timeframes,
            'chart_style': self.preferred_chart_style,
            'theme': self.default_theme,
            'volume_visible': True,
            'indicators_visible': True,
            'session_breaks': True  # Show session breaks for futures
        }
    
    def get_backtest_config(self) -> Dict[str, Any]:
        """Get configuration for strategy backtesting."""
        return {
            'symbol': self.symbol,
            'timeframes': self.test_timeframes,
            'initial_capital': self.initial_capital,
            'commission': self.total_round_turn_cost / 2,  # Per side
            'slippage': self.minimum_tick,
            'margin_requirement': self.margin_requirement,
            'currency': self.currency,
            'session_template': 'CME_GLOBEX',
            'use_bar_magnifier': True,  # For intraday data
            'calculate_on_every_tick': True  # Realistic fills
        }
    
    def get_risk_config(self) -> Dict[str, Any]:
        """Get risk management configuration."""
        return {
            'max_position_size': 5,  # Max 5 contracts
            'max_daily_loss': self.max_daily_loss,
            'max_drawdown': 0.20,  # 20% max drawdown
            'position_sizing': 'fixed',
            'default_stop_loss': self.default_stop_loss,
            'default_take_profit': self.default_take_profit,
            'risk_per_trade': 0.02,  # 2% risk per trade
            'max_correlated_positions': 2
        }
    
    def get_optimization_ranges(self) -> Dict[str, Dict[str, Any]]:
        """Get typical parameter optimization ranges for MNQ strategies."""
        return {
            'moving_averages': {
                'fast_ma': {'min': 5, 'max': 50, 'step': 5},
                'slow_ma': {'min': 20, 'max': 200, 'step': 10}
            },
            'rsi': {
                'period': {'min': 10, 'max': 30, 'step': 2},
                'overbought': {'min': 65, 'max': 85, 'step': 5},
                'oversold': {'min': 15, 'max': 35, 'step': 5}
            },
            'bollinger_bands': {
                'period': {'min': 15, 'max': 25, 'step': 2},
                'deviation': {'min': 1.5, 'max': 2.5, 'step': 0.1}
            },
            'stops_and_targets': {
                'stop_loss': {'min': 5, 'max': 25, 'step': 2.5},
                'take_profit': {'min': 10, 'max': 50, 'step': 5},
                'trailing_stop': {'min': 5, 'max': 20, 'step': 2.5}
            },
            'time_filters': {
                'start_hour': {'min': 6, 'max': 10, 'step': 1},
                'end_hour': {'min': 14, 'max': 18, 'step': 1}
            }
        }
    
    def get_performance_benchmarks(self) -> Dict[str, float]:
        """Get performance benchmarks for MNQ strategies."""
        return {
            'min_win_rate': 0.45,          # 45% minimum win rate
            'min_profit_factor': 1.25,     # 1.25 minimum profit factor
            'max_drawdown': 0.15,          # 15% maximum drawdown
            'min_sharpe_ratio': 1.0,       # Minimum Sharpe ratio
            'min_trades_per_month': 20,    # Minimum trade frequency
            'max_consecutive_losses': 10,   # Maximum consecutive losses
            'min_recovery_factor': 2.0,    # Minimum recovery factor
            'target_annual_return': 0.30   # 30% target annual return
        }
    
    def save_to_file(self, file_path: str) -> None:
        """Save configuration to JSON file."""
        config_data = asdict(self)
        with open(file_path, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'MNQConfiguration':
        """Load configuration from JSON file."""
        with open(file_path, 'r') as f:
            config_data = json.load(f)
        return cls(**config_data)


def create_mnq_config(custom_settings: Optional[Dict[str, Any]] = None) -> MNQConfiguration:
    """
    Create MNQ configuration with optional custom settings.
    
    Args:
        custom_settings: Dictionary of custom configuration overrides
        
    Returns:
        Configured MNQConfiguration instance
    """
    config = MNQConfiguration()
    
    if custom_settings:
        for key, value in custom_settings.items():
            if hasattr(config, key):
                setattr(config, key, value)
    
    return config


def get_mnq_kairos_yaml() -> str:
    """
    Generate Kairos YAML configuration optimized for MNQ1! testing.
    
    Returns:
        YAML configuration string for grimm-kairos
    """
    config = create_mnq_config()
    
    yaml_config = f"""
# Kairos Configuration for MNQ1! (Micro E-mini Nasdaq-100) Testing
# Optimized for futures trading automation

# Symbol Configuration
symbol: "{config.symbol}"
exchange: "{config.exchange}"
currency: "{config.currency}"

# Chart Configuration
charts:
  - url: "https://www.tradingview.com/chart/?symbol={config.symbol}"
    timeframes: {config.test_timeframes}
    
# Testing Configuration
testing:
  default_timeframes: {config.test_timeframes}
  commission_per_side: {config.commission_per_side}
  slippage: {config.minimum_tick}
  initial_capital: {config.initial_capital}
  position_size: {config.position_size_default}
  
# Risk Management
risk_management:
  max_position_size: 5
  max_daily_loss: {config.max_daily_loss}
  default_stop_loss: {config.default_stop_loss}
  default_take_profit: {config.default_take_profit}
  margin_requirement: {config.margin_requirement}

# Contract Specifications
contract_specs:
  contract_size: {config.contract_size}
  minimum_tick: {config.minimum_tick}
  tick_value: {config.tick_value}
  
# Trading Hours (CME Globex)
trading_hours:
  timezone: "America/Chicago"
  session_template: "CME_GLOBEX"
  high_liquidity_hours: {config.high_liquidity_hours}

# Screenshot Configuration
screenshots:
  chart_style: "{config.preferred_chart_style}"
  theme: "{config.default_theme}"
  volume_visible: {str(config.volume_profile_enabled).lower()}
  capture_session_breaks: true
  
# Performance Benchmarks
benchmarks:
  min_win_rate: 0.45
  min_profit_factor: 1.25
  max_drawdown: 0.15
  min_sharpe_ratio: 1.0
  target_annual_return: 0.30

# Browser Configuration
browser:
  wait_time: 45  # Longer wait for futures data
  read_from_data_window: true
  wait_until_chart_is_loaded: true
  
# Kairos Integration
kairos_integration:
  auth_manager: "grimm@greysson.com"
  test_runner_enabled: true
  backtest_runner_enabled: true
  screenshot_manager_enabled: true
  parallel_processing: true
  max_workers: 4
"""
    
    return yaml_config.strip()


def get_mnq_strategy_template() -> str:
    """
    Get Pine Script strategy template optimized for MNQ1!.
    
    Returns:
        Pine Script template string
    """
    config = create_mnq_config()
    
    template = f'''
//@version=5
strategy("MNQ Strategy Template", 
         overlay=true, 
         margin_long=100, 
         margin_short=100,
         initial_capital={int(config.initial_capital)},
         default_qty_type=strategy.fixed,
         default_qty_value={config.position_size_default},
         commission_type=strategy.commission.cash_per_contract,
         commission_value={config.commission_per_side},
         slippage={int(config.minimum_tick * 4)})  // 1 tick slippage

// Input Parameters
stopLoss = input.float({config.default_stop_loss}, "Stop Loss (Points)", minval=1, step=0.25)
takeProfit = input.float({config.default_take_profit}, "Take Profit (Points)", minval=1, step=0.25)
maxDailyLoss = input.float({config.max_daily_loss}, "Max Daily Loss ($)", minval=100)

// Time Filter for MNQ High Liquidity Hours
startHour = input.int(8, "Start Hour (CT)", minval=0, maxval=23)
endHour = input.int(16, "End Hour (CT)", minval=0, maxval=23)
timeFilter = hour >= startHour and hour <= endHour

// Daily Loss Tracking
var float dailyPnL = 0.0
if ta.change(time('1D'))
    dailyPnL := 0.0
dailyPnL += strategy.closed_trade_profit

// Risk Management
dailyLossExceeded = dailyPnL <= -maxDailyLoss

// Strategy Logic (Replace with your strategy)
// Example: Simple moving average crossover
fastMA = ta.sma(close, 20)
slowMA = ta.sma(close, 50)

longCondition = ta.crossover(fastMA, slowMA) and timeFilter and not dailyLossExceeded
shortCondition = ta.crossunder(fastMA, slowMA) and timeFilter and not dailyLossExceeded

// Entry Orders
if longCondition
    strategy.entry("Long", strategy.long)
    strategy.exit("Long Exit", "Long", 
                  stop=close - stopLoss, 
                  limit=close + takeProfit)

if shortCondition
    strategy.entry("Short", strategy.short)
    strategy.exit("Short Exit", "Short", 
                  stop=close + stopLoss, 
                  limit=close - takeProfit)

// Close all positions if daily loss exceeded
if dailyLossExceeded
    strategy.close_all("Daily Loss Limit")

// Plotting
plot(fastMA, "Fast MA", color.blue)
plot(slowMA, "Slow MA", color.red)
plotshape(longCondition, "Long Signal", shape.triangleup, location.belowbar, color.green, size=size.small)
plotshape(shortCondition, "Short Signal", shape.triangledown, location.abovebar, color.red, size=size.small)

// Table for Daily P&L
if barstate.islast
    var table pnlTable = table.new(position.top_right, 2, 2, bgcolor=color.white, border_width=1)
    table.cell(pnlTable, 0, 0, "Daily P&L", text_color=color.black, bgcolor=color.gray)
    table.cell(pnlTable, 1, 0, str.tostring(dailyPnL, "#.##"), 
               text_color=dailyPnL >= 0 ? color.green : color.red, bgcolor=color.white)
    table.cell(pnlTable, 0, 1, "Max Loss", text_color=color.black, bgcolor=color.gray)
    table.cell(pnlTable, 1, 1, str.tostring(maxDailyLoss, "#.##"), text_color=color.black, bgcolor=color.white)
'''
    
    return template.strip()


# Example usage and configuration presets
MNQ_SCALPING_CONFIG = {
    'test_timeframes': ['1m', '5m'],
    'default_stop_loss': 5.0,
    'default_take_profit': 10.0,
    'position_size_default': 2
}

MNQ_SWING_CONFIG = {
    'test_timeframes': ['1h', '4h', '1d'], 
    'default_stop_loss': 25.0,
    'default_take_profit': 50.0,
    'initial_capital': 50000.0
}

MNQ_DAYTRADING_CONFIG = {
    'test_timeframes': ['5m', '15m', '1h'],
    'default_stop_loss': 15.0,
    'default_take_profit': 30.0,
    'max_daily_loss': 1000.0
}


if __name__ == "__main__":
    # Example usage
    print("MNQ Configuration Examples:")
    print("=" * 50)
    
    # Default configuration
    config = create_mnq_config()
    print(f"Default Symbol: {config.symbol}")
    print(f"Default Timeframes: {config.test_timeframes}")
    print(f"Commission per side: ${config.commission_per_side}")
    print(f"Contract size: ${config.contract_size} per point")
    
    # Generate Kairos YAML
    print("\nKairos YAML Configuration:")
    print("-" * 30)
    yaml_config = get_mnq_kairos_yaml()
    print(yaml_config[:500] + "...")  # First 500 characters
    
    # Save configurations
    config.save_to_file("mnq_default_config.json")
    print("\nConfiguration saved to: mnq_default_config.json")
    
    with open("mnq_kairos_config.yaml", "w") as f:
        f.write(yaml_config)
    print("Kairos YAML saved to: mnq_kairos_config.yaml")
'''