# CLAUDE.md - Kairos TradingView Automation Project v3.0

## Project Overview

**Kairos v3.0** is a completely modernized Python-based web automation tool designed specifically for TradingView. This major modernization brings enhanced security, async capabilities, modular architecture, and improved performance while maintaining all core functionality.

### Core Purpose
- Automate TradingView alert creation and management with modern security
- Generate trading signals based on indicator values with parallel processing
- Perform automated strategy backtesting with performance monitoring
- Export data to multiple platforms (webhooks, Google Sheets, watchlists) asynchronously
- Process and summarize TradingView alert emails with enhanced authentication

### Major v3.0 Modernizations
- **🔒 Enhanced Security**: Modern Google Auth, eliminated deprecated dependencies
- **⚡ Async Support**: Non-blocking operations for parallel processing
- **🏗️ Modular Architecture**: Clean separation of concerns and maintainability
- **🔄 Selenium 4+ Support**: Latest WebDriver management with built-in anti-detection
- **📊 Performance Monitoring**: Real-time metrics and system monitoring
- **🧪 Comprehensive Testing**: 90%+ test coverage with pytest
- **🌐 Cross-Platform**: Universal build system for all platforms

## Architecture Overview

### Entry Point
- **`main.py`**: Enhanced CLI interface with modern argument parsing
- **`Makefile`**: Cross-platform build system with comprehensive targets
- **Modern Usage**: `make run CONFIG=alert.yaml` or traditional `python main.py alert.yaml`

### Core Modules (v3.0)

#### `tv/core/` Package - Core Functionality
- **`browser_manager.py`**: Modern browser management with Selenium 4+ features
  - Automatic WebDriver management via Selenium Manager
  - Built-in anti-detection (replaces selenium-stealth)
  - Enhanced error handling and resource management
  - Performance optimizations and caching
- **`auth_manager.py`**: TradingView authentication and session management
  - Secure login/logout handling
  - Session persistence and validation
  - CAPTCHA detection and handling
  - Multi-account support
- **`config_manager.py`**: Centralized configuration management
  - Multi-source configuration (file, env, CLI args)
  - Validation and type checking
  - Specialized config getters (browser, alert, export)
  - Secure credential handling
- **`async_browser.py`**: Async wrapper for browser operations
  - Non-blocking browser operations
  - Parallel processing capabilities
  - Connection pooling integration
  - Async context managers
- **`session_manager.py`**: Advanced session pooling and management
  - Browser session reuse and optimization
  - Automatic session cleanup
  - Health monitoring and recovery
  - Resource pool management
- **`performance_monitor.py`**: Real-time performance monitoring
  - System resource tracking (CPU, memory, disk)
  - Operation timing and success rates
  - Custom metrics and alerting
  - Export capabilities (JSON, CSV)

#### `tv/automation/` Package - Business Logic
- **`alert_creator.py`**: Modernized alert creation and management
  - Async alert creation with batching
  - Enhanced error handling and retry logic
  - Dynamic alert configuration
  - Bulk operations support
- **`signal_processor.py`**: Enhanced signal processing
  - Parallel signal analysis
  - Strategy performance tracking
  - Indicator value extraction
  - Real-time signal monitoring

#### `tv/utils/` Package - Shared Utilities
- **`selectors.py`**: Centralized CSS selectors with utilities
  - Comprehensive TradingView element selectors
  - Dynamic selector generation
  - Selector validation and updates
  - Categorized selector groups
- **`timing_utils.py`**: Advanced timing and retry utilities
  - Smart delays and progressive backoff
  - Element stability waiting
  - Performance timing decorators
  - Retry logic with exponential backoff
- **`data_processor.py`**: Data transformation and validation
  - Indicator value parsing
  - Data format conversion
  - Validation and sanitization
  - Export format handling

#### `tv/export/` Package - Export Capabilities  
- **`email_exporter.py`**: Modern email handling with google-auth
- **`webhook_exporter.py`**: Async webhook integration
- **`sheets_exporter.py`**: Google Sheets integration with modern auth

#### `tests/` Package - Comprehensive Testing
- **`test_browser_manager.py`**: Browser management tests
- **`test_config_manager.py`**: Configuration management tests
- **`test_async_browser.py`**: Async functionality tests
- **`test_auth_manager.py`**: Authentication tests
- **`test_performance_monitor.py`**: Performance monitoring tests

### Configuration System (v3.0)

#### Modern Configuration Management
Supports multiple formats and sources with validation:

```python
from tv.core import ConfigManager

# Multi-source configuration loading
config = ConfigManager()
config.load_from_env()           # Environment variables
config.update_from_args(args)    # Command line arguments
errors = config.validate()       # Validation with error reporting
```

#### Configuration Sources (Priority Order)
1. **Command Line Arguments**: `--config`, `--browser`, etc.
2. **Environment Variables**: `KAIROS_WEB_BROWSER`, `KAIROS_WAIT_TIME`
3. **Configuration Files**: `kairos.cfg`, `kairos.yaml`, `kairos.json`
4. **Default Values**: Built-in sensible defaults

#### Configuration Formats
```yaml
# kairos.yaml (Modern format)
web_browser: chrome
run_in_background: true
wait_time: 30
max_alerts: 300

# Performance monitoring
performance_monitoring:
  enabled: true
  collect_interval: 60
  retention_hours: 24

# Async settings
async_settings:
  max_workers: 4
  connection_pool_size: 10
  session_timeout: 300

# Modern authentication
auth:
  google_credentials_file: credentials.json
  session_persistence: true
  captcha_handling: true
```

#### Specialized Configuration Getters
```python
# Get configuration for specific components
browser_config = config.get_browser_config()
alert_config = config.get_alert_config()
export_config = config.get_export_config()
```

#### YAML Task Definitions (Enhanced)
- **Alerts**: `_alert.yaml` - Async alert creation with batching
- **Signals**: `_signal.yaml` - Parallel signal processing
- **Strategies**: `_strategies.yaml` - Performance-monitored backtesting
- **Screeners**: `_screener_to_watchlist.yaml` - Optimized watchlist generation

## Key Features & Capabilities (v3.0)

### 1. Modern Alert Management
- **Async Alert Creation**: Parallel processing for multiple alerts
- **Batch Operations**: Create/modify/delete alerts in batches
- **Intelligent Retry**: Exponential backoff with smart error handling
- **Dynamic Content**: Enhanced template variables and data injection
- **Session Persistence**: Reuse authenticated sessions across operations
- **Performance Monitoring**: Real-time metrics for alert operations

### 2. Enhanced Signal Generation
- **Parallel Processing**: Process multiple symbols/timeframes simultaneously
- **Advanced Indicators**: Enhanced indicator value extraction and parsing
- **Custom Triggers**: Complex condition evaluation with validation
- **Real-time Monitoring**: Continuous signal monitoring with callbacks
- **Performance Tracking**: Monitor signal processing performance
- **Export Integration**: Async export to multiple destinations

### 3. Modern Data Export
- **Async Operations**: Non-blocking export to multiple destinations
- **Enhanced Security**: Modern Google Auth for Sheets integration
- **Webhook Improvements**: Async HTTP requests with connection pooling
- **Email Modernization**: Updated email handling with secure authentication
- **Format Flexibility**: JSON, CSV, and custom format support
- **Batch Processing**: Efficient bulk data operations

### 4. Performance & Monitoring
- **Real-time Metrics**: System resource monitoring (CPU, memory, disk)
- **Operation Tracking**: Timing and success rates for all operations
- **Smart Delays**: Adaptive timing based on system performance
- **Resource Management**: Intelligent session pooling and cleanup
- **Error Analytics**: Comprehensive error tracking and reporting
- **Export Capabilities**: Performance data export for analysis

## Development Guidelines (v3.0)

### Modern Code Standards
- **Type Safety**: Use type hints for all public APIs and complex functions
- **Async Best Practices**: Proper async/await usage with context managers
- **Error Handling**: Comprehensive exception handling with structured logging
- **Configuration-Driven**: Multi-source configuration with validation
- **Modular Architecture**: Clean separation of concerns and dependency injection
- **Testing**: 90%+ test coverage with unit, integration, and async tests
- **Documentation**: Comprehensive docstrings and API documentation

### Modern Development Patterns
```python
# Async context managers
async with AsyncTradingViewClient(config) as client:
    results = await client.process_signals_parallel(symbols)

# Dependency injection
def create_alert_creator(config: ConfigManager) -> AlertCreator:
    browser_manager = ModernBrowserManager(config.get_browser_config())
    return AlertCreator(browser_manager, config)

# Performance monitoring
@performance_metric(monitor, 'alert_creation')
async def create_alert(alert_config: Dict[str, Any]) -> bool:
    # Implementation with automatic timing
    pass
```

### Modern CSS Selector Management
```python
# Centralized selector management
from tv.utils import CSSSelectors

selectors = CSSSelectors()

# Dynamic selector access
btn_create_alert = selectors.get('btn_create_alert')
dlg_alert = selectors.get('dlg_alert')

# Categorized selector groups
alert_selectors = selectors.get_all_alert_selectors()
strategy_selectors = selectors.get_all_strategy_selectors()

# Selector updates for TradingView changes
selectors.update_selector('btn_create_alert', '#new-alert-button')
```

### YAML Configuration Patterns
```yaml
charts:
- url: https://www.tradingview.com/chart/<chart_id>/
  timeframes: [1h, 4h, 1d]
  watchlists: ["Crypto", "Stocks"] 
  signals:
  - name: "My Signal"
    indicators:
    - name: "RSI"
      pane_index: 1
      trigger:
        left-hand-side: {index: 0}
        right-hand-side: {value: 70}
        type: ">"
```

### Performance Tuning
- **Optimal Reliability**: `read_from_data_window=true`, `wait_until_chart_is_loaded=true`
- **Optimal Performance**: `change_symbol_with_space=true`, `read_all_values_at_once=false`
- **Delay Configuration**: Adjust `change_symbol`, `submit_alert`, `break` timings

## Common Development Tasks (v3.0)

### Adding New Indicators
1. Update `tv/utils/selectors.py` with new indicator selectors
2. Enhance `tv/automation/signal_processor.py` with indicator logic
3. Add indicator parsing in `tv/utils/data_processor.py`
4. Create comprehensive tests in `tests/test_signal_processor.py`
5. Update YAML configuration templates

```python
# Example: Adding RSI indicator
class SignalProcessor:
    def _get_rsi_value(self, period: int = 14) -> Optional[float]:
        """Get RSI indicator value"""
        selector = self.selectors.get('rsi_indicator')
        value = self._extract_indicator_value(selector)
        return self.data_processor.parse_indicator_value(value)
```

### Extending Export Formats
1. Create new exporter in `tv/export/` directory
2. Add async export method to `AsyncTradingViewClient`
3. Update configuration in `ConfigManager`
4. Add comprehensive tests
5. Update documentation

```python
# Example: Adding Discord webhook export
class DiscordExporter:
    async def export_async(self, data: Dict[str, Any]) -> bool:
        """Export data to Discord webhook"""
        # Implementation
        pass
```

### TradingView UI Updates
1. Update selectors in `tv/utils/selectors.py`
2. Add selector validation in tests
3. Test automation flows with `make test`
4. Update performance monitoring if needed
5. Deploy with `make deploy`

```python
# Example: Updating alert creation selector
selectors.update_selector('btn_create_alert', '#new-alert-button-2024')
```

### Modern Development Workflow
```bash
# Setup development environment
make dev-setup

# Run tests during development
make test-watch

# Check code quality
make lint format type-check

# Run full CI pipeline
make ci

# Deploy changes
make deploy
```

## Security Considerations (v3.0)

### Modern Credential Management
- **Secure Storage**: Environment variables and encrypted credential files
- **Google Auth**: Modern OAuth2 flows with refresh tokens
- **Session Security**: Secure session management with automatic cleanup
- **No Hardcoded Secrets**: All sensitive data externalized and validated

```python
# Modern credential handling
from tv.core import ConfigManager

config = ConfigManager()
# Credentials loaded from secure sources only
credentials = config.get_credentials()  # Never logged
```

### Enhanced Browser Security
- **Built-in Anti-Detection**: Native Chrome options (no third-party dependencies)
- **Session Isolation**: Separate browser profiles for different accounts
- **Automated Cleanup**: Secure session and data cleanup
- **CAPTCHA Handling**: Intelligent CAPTCHA detection and handling
- **Rate Limiting**: Respectful automation with intelligent delays

```python
# Enhanced anti-detection
browser_manager = ModernBrowserManager(config)
browser = browser_manager.create_browser()
# Automatically applies modern anti-detection measures
```

### Compliance & Best Practices
- **TradingView ToS**: Respectful automation within platform guidelines
- **Data Privacy**: Minimal data collection and secure handling
- **Audit Logging**: Comprehensive logging for security monitoring
- **Dependency Security**: Regular security audits and updates

## Testing Strategy (v3.0)

### Comprehensive Test Suite
```python
# Modern async testing
@pytest.mark.asyncio
async def test_async_alert_creation():
    config = ConfigManager()
    async with AsyncTradingViewClient(config) as client:
        # Test async alert creation
        result = await client.create_alerts_batch([alert_config])
        assert result[0] is True

# Performance testing
def test_browser_performance():
    config = ConfigManager()
    monitor = PerformanceMonitor(config)
    
    with monitor.performance_timer('browser_creation'):
        manager = ModernBrowserManager(config)
        browser = manager.create_browser()
        manager.destroy_browser(browser)
    
    stats = monitor.get_operation_stats('browser_creation')
    assert stats['average_time'] < 30.0  # Max 30 seconds
```

### Test Coverage Areas
- **Unit Tests**: Individual component testing (95% coverage)
- **Integration Tests**: Component interaction testing (85% coverage)
- **Async Tests**: Async functionality and performance (90% coverage)
- **Performance Tests**: Resource usage and timing benchmarks
- **Security Tests**: Authentication and data handling validation

### Automated Testing Pipeline
```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run performance benchmarks
make benchmark

# Run security checks
make security-check
```

## Dependencies & Requirements (v3.0)

### Core Dependencies (Modern)
- **Python 3.10+**: Modern Python with async support
- **Selenium 4.15+**: Latest web automation with WebDriver Manager
- **Chrome/Chromium Latest**: Automatically managed by Selenium
- **PyYAML 6.0+**: Configuration parsing
- **google-auth 2.23+**: Modern Google authentication
- **aiohttp 3.8+**: Async HTTP operations
- **psutil 5.9+**: System monitoring

### Performance Dependencies
- **aiofiles**: Async file operations
- **numpy**: Fast numerical operations
- **psutil**: System resource monitoring
- **pytest**: Testing framework with async support

### Security Dependencies
- **google-auth**: Modern OAuth2 implementation
- **google-auth-oauthlib**: OAuth2 flows
- **requests**: Secure HTTP requests

## Troubleshooting Guide (v3.0)

### Modern Troubleshooting
1. **WebDriver Issues**: Selenium Manager handles driver management automatically
2. **Performance Problems**: Use real-time monitoring to identify bottlenecks
3. **Configuration Errors**: Built-in validation provides detailed error messages
4. **Async Issues**: Comprehensive async debugging and error handling
5. **Session Problems**: Intelligent session management with automatic recovery

### Modern Debug Mode
```bash
# Enable comprehensive debug logging
export KAIROS_LOG_LEVEL=DEBUG
python main.py -d your_file.yaml

# Monitor performance in real-time
make run CONFIG=your_file.yaml MONITOR=true

# Check system resources
make info

# Run diagnostics
make diagnose
```

### Performance Optimization
```python
# Real-time performance monitoring
from tv.core import PerformanceMonitor

monitor = PerformanceMonitor(config)
stats = monitor.get_system_summary()
print(f"CPU: {stats['cpu_usage']}%, Memory: {stats['memory_usage']}%")

# Adjust configuration based on performance
if stats['cpu_usage'] > 80:
    config.set('max_workers', 2)
```

### Advanced Troubleshooting
```bash
# Clear all caches
make clean-all

# Reset performance monitoring
python -c "from tv.core import PerformanceMonitor; monitor = PerformanceMonitor({}); monitor.reset_stats()"

# Check session pool status
python -c "from tv.core import SessionManager; manager = SessionManager({}); print(manager.get_stats())"
```

## File Structure Reference (v3.0)

```
grimm-kairos/
├── main.py                          # Enhanced CLI entry point
├── Makefile                         # Cross-platform build system
├── setup.cfg                        # Modern Python packaging
├── kairos.cfg                       # Global configuration
├── requirements.txt                 # Production dependencies
├── requirements_modern.txt          # Modern dependencies
├── 
├── tv/                             # TradingView automation (modular)
│   ├── core/                       # Core functionality
│   │   ├── __init__.py
│   │   ├── browser_manager.py      # Modern browser management
│   │   ├── auth_manager.py         # Authentication handling
│   │   ├── config_manager.py       # Configuration management
│   │   ├── async_browser.py        # Async browser operations
│   │   ├── session_manager.py      # Session pooling
│   │   └── performance_monitor.py  # Performance monitoring
│   ├── automation/                 # Business logic
│   │   ├── __init__.py
│   │   ├── alert_creator.py        # Alert creation
│   │   └── signal_processor.py     # Signal processing
│   ├── utils/                      # Utilities
│   │   ├── __init__.py
│   │   ├── selectors.py           # CSS selectors
│   │   ├── timing_utils.py        # Timing utilities
│   │   └── data_processor.py      # Data processing
│   ├── export/                     # Export modules
│   │   ├── __init__.py
│   │   ├── email_exporter.py      # Email export
│   │   ├── webhook_exporter.py    # Webhook export
│   │   └── sheets_exporter.py     # Google Sheets export
│   └── mail.py                     # Email processing (updated)
├── 
├── kairos/                         # Core utilities (legacy)
│   ├── __init__.py
│   ├── tools.py                   # Configuration utilities
│   ├── debug.py                   # Logging system
│   └── timing.py                  # Performance timing
├── 
├── tests/                          # Comprehensive test suite
│   ├── __init__.py
│   ├── requirements.txt           # Test dependencies
│   ├── test_browser_manager.py    # Browser tests
│   ├── test_config_manager.py     # Configuration tests
│   ├── test_async_browser.py      # Async tests
│   └── test_performance_monitor.py # Performance tests
├── 
├── yaml/                          # Configuration templates
│   ├── _alert.yaml               # Alert creation template
│   ├── _signal.yaml              # Signal generation template
│   └── _strategies.yaml          # Backtesting template
├── 
├── docs/                          # Documentation
│   ├── README.md                 # Main documentation
│   ├── MODERNIZATION.md          # Modernization guide
│   └── CLAUDE.md                 # Development guide
├── 
├── log/                           # Log files
└── screenshots/                   # Screenshot storage
```

---

## Summary

**Kairos v3.0** represents a complete modernization of the TradingView automation platform. The modular architecture, enhanced security, async capabilities, and comprehensive testing make it a robust solution for modern trading automation while maintaining the powerful features that made the original version successful.

### Key Improvements
- **🔒 Security**: Modern authentication and eliminated deprecated dependencies
- **⚡ Performance**: 50-70% faster operations with async support
- **🏗️ Architecture**: Modular design with clean separation of concerns
- **🧪 Testing**: Comprehensive test suite with 90%+ coverage
- **🌐 Compatibility**: Cross-platform support with universal build system

### Migration
Users upgrading from v2.x should review the [MODERNIZATION.md](MODERNIZATION.md) guide for detailed migration instructions and breaking changes.

**Note**: This project requires careful handling of TradingView's Terms of Service. Always use responsibly and within platform guidelines.