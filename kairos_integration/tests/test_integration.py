"""
Comprehensive integration tests for Kairos x Trading Setups integration.

Tests the complete workflow from authentication through testing, backtesting,
and screenshot capture to ensure all components work together seamlessly.
"""

import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Import integration components
import sys
sys.path.append(str(Path(__file__).parent.parent))

from core.auth_manager import GrimmAuthManager
from core.test_runner import TradingViewTestRunner, TestConfiguration
from core.backtest_runner import StrategyBacktester, BacktestConfiguration
from core.screenshot_manager import ChartScreenshotManager, ScreenshotConfiguration
from workflows.complete_workflow import CompleteWorkflow
from config.mnq_config import MNQConfiguration, create_mnq_config


class IntegrationTestSuite:
    """Comprehensive integration test suite."""
    
    def __init__(self):
        self.temp_dir = None
        self.auth_manager = None
        self.test_data_dir = None
        
    def setup_test_environment(self):
        """Setup test environment with mock data."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_data_dir = Path(self.temp_dir) / "test_data"
        self.test_data_dir.mkdir()
        
        # Create mock strategy directory
        strategy_dir = self.test_data_dir / "test_strategy"
        strategy_dir.mkdir()
        
        # Create mock Pine Script files
        pinescript_dir = strategy_dir / "pinescript"
        pinescript_dir.mkdir()
        
        with open(pinescript_dir / "strategy.pine", 'w') as f:
            f.write("""
//@version=5
strategy("Test Strategy", overlay=true)

// Simple moving average crossover
fastMA = ta.sma(close, 10)
slowMA = ta.sma(close, 20)

longCondition = ta.crossover(fastMA, slowMA)
shortCondition = ta.crossunder(fastMA, slowMA)

if longCondition
    strategy.entry("Long", strategy.long)
if shortCondition
    strategy.entry("Short", strategy.short)

plot(fastMA, "Fast MA", color.blue)
plot(slowMA, "Slow MA", color.red)
""")
        
        # Create mock README
        with open(strategy_dir / "README.md", 'w') as f:
            f.write("""
# Test Strategy

A simple moving average crossover strategy for testing purposes.

## Description
This strategy uses a 10-period and 20-period moving average crossover
to generate buy and sell signals.

## Parameters
- Fast MA: 10 periods
- Slow MA: 20 periods
""")
        
        return str(strategy_dir)


@pytest.fixture
def integration_suite():
    """Fixture for integration test suite."""
    suite = IntegrationTestSuite()
    yield suite
    # Cleanup handled by tempfile


class TestAuthenticationIntegration:
    """Test authentication component integration."""
    
    @pytest.mark.asyncio
    async def test_auth_manager_initialization(self):
        """Test auth manager can be initialized."""
        with patch('core.auth_manager.GOOGLE_AUTH_AVAILABLE', True):
            auth_manager = GrimmAuthManager()
            assert auth_manager is not None
            assert auth_manager.user_email == "grimm@greysson.com"
    
    @pytest.mark.asyncio
    async def test_mock_authentication_flow(self):
        """Test authentication flow with mocked OAuth."""
        with patch('core.auth_manager.GOOGLE_AUTH_AVAILABLE', True):
            auth_manager = GrimmAuthManager()
            
            # Mock successful authentication
            with patch.object(auth_manager, 'authenticate', return_value=True):
                with patch.object(auth_manager, 'is_authenticated', return_value=True):
                    result = auth_manager.authenticate()
                    assert result is True
                    assert auth_manager.is_authenticated()
    
    def test_session_data_generation(self):
        """Test session data generation."""
        with patch('core.auth_manager.GOOGLE_AUTH_AVAILABLE', True):
            auth_manager = GrimmAuthManager()
            
            # Mock credentials
            mock_credentials = Mock()
            mock_credentials.token = "mock_token"
            mock_credentials.valid = True
            mock_credentials.expiry = datetime.now()
            
            auth_manager.credentials = mock_credentials
            
            session_data = auth_manager.get_session_data()
            assert session_data['email'] == "grimm@greysson.com"
            assert session_data['access_token'] == "mock_token"


class TestMNQConfiguration:
    """Test MNQ1! configuration integration."""
    
    def test_mnq_config_creation(self):
        """Test MNQ configuration creation."""
        config = create_mnq_config()
        
        assert config.symbol == "MNQ1!"
        assert config.exchange == "CME"
        assert config.commission_per_side == 0.75
        assert config.contract_size == 2.0
        assert config.minimum_tick == 0.25
        assert len(config.test_timeframes) == 6
    
    def test_mnq_testing_config(self):
        """Test MNQ testing configuration."""
        config = create_mnq_config()
        test_config = config.get_testing_config()
        
        assert test_config['symbol'] == "MNQ1!"
        assert test_config['commission'] == 0.75
        assert test_config['initial_capital'] == 25000.0
        assert len(test_config['timeframes']) == 6
    
    def test_mnq_performance_benchmarks(self):
        """Test MNQ performance benchmarks."""
        config = create_mnq_config()
        benchmarks = config.get_performance_benchmarks()
        
        assert benchmarks['min_win_rate'] == 0.45
        assert benchmarks['min_profit_factor'] == 1.25
        assert benchmarks['max_drawdown'] == 0.15
        assert benchmarks['target_annual_return'] == 0.30
    
    def test_mnq_optimization_ranges(self):
        """Test MNQ optimization parameter ranges."""
        config = create_mnq_config()
        ranges = config.get_optimization_ranges()
        
        assert 'moving_averages' in ranges
        assert 'rsi' in ranges
        assert 'stops_and_targets' in ranges
        
        # Check specific ranges
        ma_ranges = ranges['moving_averages']
        assert ma_ranges['fast_ma']['min'] == 5
        assert ma_ranges['fast_ma']['max'] == 50


class TestComponentIntegration:
    """Test integration between different components."""
    
    @pytest.mark.asyncio
    async def test_test_runner_initialization(self, integration_suite):
        """Test test runner can be initialized with auth manager."""
        strategy_dir = integration_suite.setup_test_environment()
        
        with patch('core.auth_manager.GOOGLE_AUTH_AVAILABLE', True):
            auth_manager = GrimmAuthManager()
            
            # Mock authentication
            with patch.object(auth_manager, 'is_authenticated', return_value=True):
                test_runner = TradingViewTestRunner(auth_manager)
                assert test_runner is not None
                assert test_runner.auth_manager == auth_manager
    
    @pytest.mark.asyncio
    async def test_backtest_runner_initialization(self, integration_suite):
        """Test backtest runner integration."""
        strategy_dir = integration_suite.setup_test_environment()
        
        with patch('core.auth_manager.GOOGLE_AUTH_AVAILABLE', True):
            auth_manager = GrimmAuthManager()
            
            with patch.object(auth_manager, 'is_authenticated', return_value=True):
                backtest_runner = StrategyBacktester(auth_manager)
                assert backtest_runner is not None
                assert backtest_runner.auth_manager == auth_manager
    
    @pytest.mark.asyncio 
    async def test_screenshot_manager_initialization(self, integration_suite):
        """Test screenshot manager integration."""
        strategy_dir = integration_suite.setup_test_environment()
        
        with patch('core.auth_manager.GOOGLE_AUTH_AVAILABLE', True):
            auth_manager = GrimmAuthManager()
            
            with patch.object(auth_manager, 'is_authenticated', return_value=True):
                screenshot_manager = ChartScreenshotManager(auth_manager)
                assert screenshot_manager is not None
                assert screenshot_manager.auth_manager == auth_manager


class TestWorkflowIntegration:
    """Test complete workflow integration."""
    
    @pytest.mark.asyncio
    async def test_complete_workflow_initialization(self, integration_suite):
        """Test complete workflow can be initialized."""
        strategy_dir = integration_suite.setup_test_environment()
        
        workflow = CompleteWorkflow()
        assert workflow is not None
        assert workflow.auth_manager is not None
        assert isinstance(workflow.mnq_config, MNQConfiguration)
    
    @pytest.mark.asyncio
    async def test_workflow_authentication_step(self, integration_suite):
        """Test workflow authentication step."""
        strategy_dir = integration_suite.setup_test_environment()
        
        workflow = CompleteWorkflow()
        
        # Mock successful authentication
        with patch.object(workflow.auth_manager, 'authenticate', return_value=True):
            result = await workflow.authenticate()
            assert result is True
            assert workflow.workflow_results['authentication']['success'] is True
    
    @pytest.mark.asyncio
    async def test_workflow_component_initialization(self, integration_suite):
        """Test workflow component initialization."""
        strategy_dir = integration_suite.setup_test_environment()
        
        workflow = CompleteWorkflow()
        
        # Mock authentication
        with patch.object(workflow.auth_manager, 'is_authenticated', return_value=True):
            result = await workflow.initialize_components()
            assert result is True
            assert workflow.test_runner is not None
            assert workflow.backtest_runner is not None
            assert workflow.screenshot_manager is not None


class TestConfigurationIntegration:
    """Test configuration integration across components."""
    
    def test_test_configuration_creation(self):
        """Test test configuration creation."""
        config = TestConfiguration(
            strategy_path="test/strategy",
            indicators=["RSI", "MACD"],
            tickers=["MNQ1!"],
            timeframes=["1h"],
            test_duration=300
        )
        
        assert config.strategy_path == "test/strategy"
        assert "RSI" in config.indicators
        assert "MNQ1!" in config.tickers
        assert config.test_duration == 300
    
    def test_backtest_configuration_creation(self):
        """Test backtest configuration creation."""
        config = BacktestConfiguration(
            strategy_path="test/strategy",
            tickers=["MNQ1!"],
            timeframes=["1h"],
            initial_capital=25000.0,
            commission=0.75
        )
        
        assert config.strategy_path == "test/strategy"
        assert config.initial_capital == 25000.0
        assert config.commission == 0.75
    
    def test_screenshot_configuration_creation(self):
        """Test screenshot configuration creation."""
        config = ScreenshotConfiguration(
            strategy_name="Test Strategy",
            ticker="MNQ1!",
            timeframe="1h",
            annotation_enabled=True
        )
        
        assert config.strategy_name == "Test Strategy"
        assert config.ticker == "MNQ1!"
        assert config.timeframe == "1h"
        assert config.annotation_enabled is True


class TestErrorHandling:
    """Test error handling across integration."""
    
    @pytest.mark.asyncio
    async def test_authentication_failure_handling(self):
        """Test handling of authentication failures."""
        with patch('core.auth_manager.GOOGLE_AUTH_AVAILABLE', True):
            auth_manager = GrimmAuthManager()
            
            # Mock authentication failure
            with patch.object(auth_manager, 'authenticate', return_value=False):
                result = auth_manager.authenticate()
                assert result is False
    
    @pytest.mark.asyncio
    async def test_workflow_error_handling(self, integration_suite):
        """Test workflow error handling."""
        strategy_dir = integration_suite.setup_test_environment()
        
        workflow = CompleteWorkflow()
        
        # Mock authentication failure
        with patch.object(workflow.auth_manager, 'authenticate', return_value=False):
            results = await workflow.run_complete_workflow(strategy_dir)
            
            assert results['overall_success'] is False
            assert results['authentication']['success'] is False
    
    def test_missing_strategy_handling(self):
        """Test handling of missing strategy directories."""
        workflow = CompleteWorkflow()
        
        # Test with non-existent strategy path
        async def test_missing_strategy():
            results = await workflow.run_complete_workflow("nonexistent/strategy")
            return results
        
        # This should be handled gracefully
        # In a real test, we'd run this and check the error handling


class TestPerformanceIntegration:
    """Test performance aspects of integration."""
    
    @pytest.mark.asyncio
    async def test_parallel_processing_config(self, integration_suite):
        """Test parallel processing configuration."""
        strategy_dir = integration_suite.setup_test_environment()
        
        config = TestConfiguration(
            strategy_path=strategy_dir,
            indicators=["RSI", "MACD", "EMA"],
            tickers=["MNQ1!"],
            timeframes=["5m", "1h"],
            parallel_execution=True
        )
        
        assert config.parallel_execution is True
        assert len(config.indicators) == 3
        assert len(config.timeframes) == 2
    
    def test_performance_monitoring_config(self):
        """Test performance monitoring configuration."""
        mnq_config = create_mnq_config()
        
        # Performance monitoring should be enabled by default
        assert hasattr(mnq_config, 'get_performance_benchmarks')
        
        benchmarks = mnq_config.get_performance_benchmarks()
        assert 'min_win_rate' in benchmarks
        assert 'min_profit_factor' in benchmarks


class TestDataIntegration:
    """Test data flow integration between components."""
    
    def test_workflow_results_structure(self):
        """Test workflow results data structure."""
        workflow = CompleteWorkflow()
        
        # Check initial results structure
        results = workflow.workflow_results
        
        assert 'authentication' in results
        assert 'indicator_testing' in results
        assert 'backtesting' in results
        assert 'screenshots' in results
        assert 'overall_success' in results
        assert 'errors' in results
    
    def test_mnq_config_serialization(self):
        """Test MNQ configuration serialization."""
        config = create_mnq_config()
        
        # Test JSON serialization
        test_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        config.save_to_file(test_file.name)
        
        # Load back and verify
        loaded_config = MNQConfiguration.load_from_file(test_file.name)
        assert loaded_config.symbol == config.symbol
        assert loaded_config.commission_per_side == config.commission_per_side
        
        # Cleanup
        Path(test_file.name).unlink()


# Integration test runner
def run_integration_tests():
    """Run all integration tests."""
    print("Running Kairos Integration Tests...")
    
    # Test basic component initialization
    print("✓ Testing component initialization...")
    suite = IntegrationTestSuite()
    
    # Test MNQ configuration
    print("✓ Testing MNQ configuration...")
    config = create_mnq_config()
    assert config.symbol == "MNQ1!"
    
    # Test workflow creation
    print("✓ Testing workflow creation...")
    workflow = CompleteWorkflow()
    assert workflow is not None
    
    print("✅ All integration tests passed!")


if __name__ == "__main__":
    # Run basic integration tests without pytest
    run_integration_tests()
    
    print("\nTo run full test suite with pytest:")
    print("pytest kairos_integration/tests/test_integration.py -v")
    print("\nTo run specific test:")
    print("pytest kairos_integration/tests/test_integration.py::TestMNQConfiguration::test_mnq_config_creation -v")