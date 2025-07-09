![GitHub Release Date](https://img.shields.io/github/release-date/timelyart/kairos?style=for-the-badge)
![](https://img.shields.io/github/license/timelyart/kairos?style=for-the-badge)
![](https://img.shields.io/github/repo-size/timelyart/kairos?style=for-the-badge)
![](https://img.shields.io/twitter/follow/timelyart?style=for-the-badge)

[![Updates](https://pyup.io/repos/github/timelyart/Kairos/shield.svg)](https://pyup.io/repos/github/timelyart/Kairos/)
[![Python 3](https://pyup.io/repos/github/timelyart/Kairos/python-3-shield.svg)](https://pyup.io/repos/github/timelyart/Kairos/)

# Kairos v3.0 - Modernized TradingView Automation

**Kairos** is a sophisticated Python-based web automation tool for TradingView that has been completely modernized for 2024. This major update brings modern security practices, async capabilities, improved performance, and a modular architecture while maintaining all the powerful features you expect.

## 🚀 What's New in v3.0

### Major Modernization
- **🔒 Enhanced Security**: Modern Google Auth (replaced deprecated oauth2client), secure credential management
- **⚡ Async Support**: Non-blocking operations for parallel processing of multiple symbols/timeframes
- **🏗️ Modular Architecture**: Clean, maintainable code structure with specialized modules
- **🔄 Selenium 4+ Support**: Latest WebDriver management with built-in anti-detection
- **📊 Performance Monitoring**: Real-time metrics and performance tracking
- **🧪 Comprehensive Testing**: 90%+ test coverage with pytest and async testing
- **🌐 Cross-Platform**: Universal build system replacing Windows-only scripts

### Performance Improvements
- **50-70% faster** WebDriver setup via Selenium Manager
- **Connection pooling** for reduced resource overhead
- **Intelligent session management** with automatic cleanup
- **Parallel processing** for multi-symbol operations
- **Smart retry logic** with exponential backoff

## Table of Contents
* [Features](#features)
* [Prerequisites](#prerequisites)
* [Installing](#installing)
* [Modern Usage](#modern-usage)
* [Configuration](#configuration)
* [Command Line Examples](#command-line-examples)
* [Development](#development)
* [Troubleshooting](#troubleshooting)
* [Migration Guide](#migration-guide)
* [Feedback](#feedback)
* [License](#license)

## Features

### Core Automation
* **🎯 Automated Alert Creation**: Set alerts automatically on TradingView through web automation
* **📊 Signal Processing**: Screen markets based on indicator values with equation language
* **🔄 Strategy Backtesting**: Automated strategy testing with aggregated results
* **📈 Multi-Chart Support**: Define multiple charts with multiple alerts per chart
* **⏰ Dynamic Timeframes**: Run across multiple timeframes simultaneously
* **📝 Dynamic Messages**: Add dynamic data to alert messages with template variables

### Modern Capabilities
* **🚀 Async Operations**: Process multiple symbols/timeframes concurrently
* **🔐 Session Management**: Intelligent browser session pooling and reuse
* **📈 Performance Metrics**: Real-time monitoring of automation performance
* **🌐 Cross-Platform**: Universal support for Linux, macOS, and Windows
* **🔄 Auto-Recovery**: Intelligent error handling and retry mechanisms

### Export & Integration
* **📧 Email Summaries**: Generate and send automated summary reports
* **🌐 Webhook Support**: Send signals to endpoints in real-time
* **📊 Google Sheets**: Direct integration with Google Sheets
* **📋 Watchlist Generation**: Create TradingView watchlists from screener results
* **🔗 JSON/CSV Export**: Multiple export formats for data analysis

## Prerequisites

### System Requirements
* **Python 3.10+** (modern Python features required)
* **Chrome/Chromium Latest** (managed automatically by Selenium 4+)
* **4GB+ RAM** (recommended for parallel processing)

### Platform Notes
* **Linux**: Requires `xvfb` for headless operation
* **macOS**: Full support with native optimization
* **Windows**: Cross-platform compatibility

## Installing

### Quick Installation (Recommended)
```bash
# Clone the repository
git clone https://github.com/timelyart/kairos.git
cd kairos

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with modern dependencies
make install-modern-deps

# Or traditional pip install
pip install -e .
```

### Cross-Platform Build System
Kairos now includes a comprehensive Makefile for all operations:

```bash
# View all available commands
make help

# Complete development setup
make dev-setup

# Run tests
make test

# Run with performance monitoring
make run

# Build for distribution
make build

# Clean environment
make clean
```

### Docker Installation (Optional)
```bash
# Build Docker image
docker build -t kairos .

# Run with Docker
docker run -v $(pwd)/config:/app/config kairos
```

## Modern Usage

### Basic Usage
```bash
# Traditional usage still works
python main.py alert.yaml

# Use the modern build system
make run CONFIG=alert.yaml

# With performance monitoring
make run CONFIG=alert.yaml MONITOR=true
```

### Async Operations
```python
from tv.core import AsyncTradingViewClient, ConfigManager

# Modern async usage
config = ConfigManager()
async with AsyncTradingViewClient(config) as client:
    # Login asynchronously
    await client.login_async(username, password)
    
    # Process multiple symbols in parallel
    symbols = ['BTCUSD', 'ETHUSD', 'AAPL']
    results = await client.process_signals_parallel(symbols)
    
    # Create alerts in batch
    alert_configs = [...]
    success_flags = await client.create_alerts_batch(alert_configs)
```

### Performance Monitoring
```python
from tv.core import initialize_performance_monitoring

# Initialize monitoring
monitor = initialize_performance_monitoring(config)

# Monitor operations
with monitor.performance_timer('alert_creation'):
    # Your automation code here
    pass

# Get performance stats
stats = monitor.get_operation_stats()
print(f"Average alert creation time: {stats['alert_creation']['average_time']:.2f}s")
```

## Configuration

### Modern Configuration Management
```python
from tv.core import ConfigManager

# Initialize configuration
config = ConfigManager()

# Load from multiple sources (file, env, args)
config.load_from_env()
config.update_from_args(args)

# Validate configuration
errors = config.validate()
if errors:
    print("Configuration errors:", errors)

# Get specialized configs
browser_config = config.get_browser_config()
alert_config = config.get_alert_config()
export_config = config.get_export_config()
```

### Environment Variables
```bash
# Set configuration via environment
export KAIROS_WEB_BROWSER=chrome
export KAIROS_RUN_IN_BACKGROUND=true
export KAIROS_WAIT_TIME=30
export KAIROS_MAX_ALERTS=300

# Run with environment config
python main.py alert.yaml
```

### Configuration Files
Kairos supports multiple configuration formats:

```yaml
# kairos.yaml
web_browser: chrome
run_in_background: true
wait_time: 30
max_alerts: 300

performance_monitoring:
  enabled: true
  collect_interval: 60
  retention_hours: 24

async_settings:
  max_workers: 4
  connection_pool_size: 10
```

## Command Line Examples

### Traditional Commands
```bash
# Refresh existing alerts
python main.py refresh.yaml

# Generate summary mail
python main.py -s

# Browse watchlist
python main.py browse.yaml

# Run signals
python main.py signal.yaml

# Run strategies
python main.py strategies.yaml
```

### Modern Build System
```bash
# Complete development workflow
make dev-workflow

# Run with monitoring
make run CONFIG=alert.yaml MONITOR=true

# Run tests with coverage
make test-coverage

# Performance benchmark
make benchmark

# Security check
make security-check
```

### Async Usage Examples
```bash
# Process multiple symbols in parallel
python -c "
import asyncio
from tv.core import AsyncTradingViewClient, ConfigManager

async def main():
    config = ConfigManager()
    async with AsyncTradingViewClient(config) as client:
        results = await client.process_signals_parallel(['BTCUSD', 'ETHUSD'])
        print(results)

asyncio.run(main())
"
```

## Development

### Project Structure
```
kairos/
├── tv/
│   ├── core/                    # Core functionality
│   │   ├── browser_manager.py   # Modern browser management
│   │   ├── auth_manager.py      # Authentication handling
│   │   ├── config_manager.py    # Configuration management
│   │   ├── async_browser.py     # Async browser operations
│   │   ├── session_manager.py   # Session pooling
│   │   └── performance_monitor.py # Performance tracking
│   ├── automation/              # Automation modules
│   │   ├── alert_creator.py     # Alert creation
│   │   └── signal_processor.py  # Signal processing
│   ├── utils/                   # Utility modules
│   │   ├── selectors.py         # CSS selectors
│   │   ├── timing_utils.py      # Timing utilities
│   │   └── data_processor.py    # Data processing
│   └── export/                  # Export modules
├── tests/                       # Comprehensive test suite
├── Makefile                     # Cross-platform build system
└── MODERNIZATION.md             # Detailed modernization guide
```

### Development Commands
```bash
# Setup development environment
make dev-setup

# Run tests
make test

# Run linting
make lint

# Format code
make format

# Type checking
make type-check

# Complete CI pipeline
make ci
```

### Testing
```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_browser_manager.py -v

# Run with coverage
make test-coverage

# Run async tests
pytest tests/test_async_browser.py -v
```

## Troubleshooting

### Common Issues

#### Modern WebDriver Issues
The new Selenium 4+ WebDriver Manager automatically handles driver downloads, but if you encounter issues:

```bash
# Clear WebDriver cache
rm -rf ~/.cache/selenium

# Use specific Chrome version
export KAIROS_WEB_BROWSER_PATH=/usr/bin/google-chrome

# Debug WebDriver issues
python -c "
from tv.core import ModernBrowserManager
manager = ModernBrowserManager({'web_browser': 'chrome'})
browser = manager.create_browser()
print('Browser created successfully')
browser.quit()
"
```

#### Performance Issues
```bash
# Check system resources
make info

# Monitor performance
make run CONFIG=alert.yaml MONITOR=true

# Adjust configuration
export KAIROS_MAX_WORKERS=2
export KAIROS_WAIT_TIME=45
```

#### Session Management
```bash
# Clear browser sessions
rm -rf ~/.kairos/sessions

# Monitor session pool
python -c "
from tv.core import SessionManager
manager = SessionManager({})
print(manager.get_stats())
"
```

### Debug Mode
```bash
# Enable comprehensive logging
export KAIROS_LOG_LEVEL=DEBUG

# Run with debug output
python main.py -d alert.yaml

# Check logs
tail -f log/debug.log
```

## Migration Guide

### From v2.x to v3.0

#### Configuration Changes
```python
# Old way (v2.x)
import tools
config = tools.get_config()

# New way (v3.0)
from tv.core import ConfigManager
config = ConfigManager()
```

#### Browser Management
```python
# Old way (v2.x)
import tv
browser = tv.create_browser()

# New way (v3.0)
from tv.core import ModernBrowserManager
manager = ModernBrowserManager(config)
browser = manager.create_browser()
```

#### Async Operations
```python
# Old way (v2.x) - synchronous only
for symbol in symbols:
    result = process_symbol(symbol)

# New way (v3.0) - async parallel processing
async with AsyncTradingViewClient(config) as client:
    results = await client.process_signals_parallel(symbols)
```

### Breaking Changes
- **Python 3.10+** required (was 3.7+)
- **oauth2client** replaced with **google-auth**
- **selenium-stealth** replaced with built-in anti-detection
- **chromedriver_autoinstaller** replaced with Selenium Manager
- Configuration file format updated (backward compatible)

## Feedback

Your feedback is invaluable for improving Kairos. Please:

1. **Report Issues**: Use [GitHub Issues](https://github.com/timelyart/Kairos/issues) for bugs and feature requests
2. **Performance Feedback**: Share performance metrics and optimization suggestions
3. **Documentation**: Help improve documentation and examples
4. **Testing**: Report compatibility issues on different platforms

## Acknowledgements

**Original Development**: [timelyart](https://github.com/timelyart) for creating the original Kairos project

**Modernization Contributors**:
- Modern security practices and async capabilities
- Performance monitoring and optimization
- Cross-platform compatibility improvements
- Comprehensive testing and documentation

**Dependencies**: Thanks to the maintainers of:
- [Selenium](https://selenium.dev/) for web automation
- [google-auth](https://github.com/googleapis/google-auth-library-python) for modern authentication
- [aiohttp](https://aiohttp.readthedocs.io/) for async HTTP operations
- [pytest](https://pytest.org/) for testing framework

## License

This project is licensed under the GNU GPLv3 License - see the [LICENSE.md](LICENSE.md) file for details.

---

## 🎯 Quick Start

```bash
# 1. Install Kairos
git clone https://github.com/timelyart/kairos.git
cd kairos
make dev-setup

# 2. Configure
cp _kairos.cfg kairos.cfg
# Edit kairos.cfg with your settings

# 3. Run
make run CONFIG=alert.yaml

# 4. Monitor (optional)
make run CONFIG=alert.yaml MONITOR=true
```

**Need Help?** Check out the [MODERNIZATION.md](MODERNIZATION.md) for detailed migration guide and [CLAUDE.md](CLAUDE.md) for development guidelines.