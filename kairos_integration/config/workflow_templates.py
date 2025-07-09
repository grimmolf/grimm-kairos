"""
Workflow Templates for Kairos Integration

Provides pre-configured workflow templates for common trading strategy
development and testing scenarios.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import yaml
import json
from pathlib import Path


@dataclass
class WorkflowTemplate:
    """Base class for workflow templates."""
    name: str
    description: str
    steps: List[Dict[str, Any]]
    config: Dict[str, Any]
    
    def to_yaml(self) -> str:
        """Convert template to YAML format."""
        data = {
            'name': self.name,
            'description': self.description,
            'steps': self.steps,
            'config': self.config
        }
        return yaml.dump(data, default_flow_style=False, indent=2)
    
    def save_to_file(self, file_path: str) -> None:
        """Save template to YAML file."""
        with open(file_path, 'w') as f:
            f.write(self.to_yaml())


class WorkflowTemplates:
    """Collection of workflow templates for different scenarios."""
    
    @staticmethod
    def get_complete_strategy_workflow() -> WorkflowTemplate:
        """Complete strategy development and testing workflow."""
        return WorkflowTemplate(
            name="Complete Strategy Development",
            description="Full end-to-end strategy development from idea to production",
            steps=[
                {
                    "step": "authenticate",
                    "description": "Authenticate with Google OAuth for grimm@greysson.com",
                    "action": "auth_manager.authenticate",
                    "required": True
                },
                {
                    "step": "load_strategy",
                    "description": "Load strategy from trading-setups directory",
                    "action": "load_strategy_files",
                    "config": {
                        "strategy_path": "strategies/{strategy_name}",
                        "validate_pine_script": True,
                        "validate_thinkscript": True
                    }
                },
                {
                    "step": "test_indicators",
                    "description": "Test strategy indicators on MNQ1!",
                    "action": "test_runner.test_strategy_indicators",
                    "config": {
                        "tickers": ["MNQ1!"],
                        "timeframes": ["5m", "15m", "1h", "4h"],
                        "indicators": ["RSI", "MACD", "EMA", "SMA"],
                        "capture_screenshots": True,
                        "test_duration": 300
                    }
                },
                {
                    "step": "run_backtest",
                    "description": "Run comprehensive backtest",
                    "action": "backtest_runner.backtest_strategy",
                    "config": {
                        "tickers": ["MNQ1!"],
                        "timeframes": ["5m", "15m", "1h"],
                        "initial_capital": 25000.0,
                        "commission": 0.75,
                        "slippage": 0.25,
                        "capture_screenshots": True,
                        "optimization_enabled": True
                    }
                },
                {
                    "step": "capture_charts",
                    "description": "Capture annotated chart screenshots",
                    "action": "screenshot_manager.capture_strategy_screenshots",
                    "config": {
                        "tickers": ["MNQ1!"],
                        "timeframes": ["5m", "1h", "4h", "1d"],
                        "annotation_enabled": True,
                        "theme": "dark",
                        "chart_style": "candles"
                    }
                },
                {
                    "step": "generate_report",
                    "description": "Generate comprehensive strategy report",
                    "action": "generate_strategy_report",
                    "config": {
                        "include_backtest_results": True,
                        "include_screenshots": True,
                        "include_optimization": True,
                        "output_format": "pdf"
                    }
                }
            ],
            config={
                "default_ticker": "MNQ1!",
                "auth_email": "grimm@greysson.com",
                "results_directory": "./results",
                "parallel_execution": True,
                "error_handling": "continue_on_error",
                "logging_level": "INFO"
            }
        )
    
    @staticmethod
    def get_quick_test_workflow() -> WorkflowTemplate:
        """Quick strategy testing workflow for rapid iteration."""
        return WorkflowTemplate(
            name="Quick Strategy Test",
            description="Fast strategy validation on MNQ1! 1h timeframe",
            steps=[
                {
                    "step": "authenticate",
                    "description": "Quick authentication check",
                    "action": "auth_manager.is_authenticated",
                    "timeout": 30
                },
                {
                    "step": "quick_indicator_test",
                    "description": "Test key indicators quickly",
                    "action": "test_runner.run_quick_test",
                    "config": {
                        "ticker": "MNQ1!",
                        "timeframe": "1h",
                        "indicators": ["RSI", "MACD"],
                        "test_duration": 60,
                        "capture_screenshots": True
                    }
                },
                {
                    "step": "quick_backtest",
                    "description": "Quick backtest validation",
                    "action": "backtest_runner.run_quick_backtest",
                    "config": {
                        "ticker": "MNQ1!",
                        "timeframe": "1h",
                        "test_period": "1M",  # 1 month
                        "capture_screenshots": True
                    }
                },
                {
                    "step": "capture_setup_chart",
                    "description": "Capture annotated setup chart",
                    "action": "screenshot_manager.capture_chart_screenshot",
                    "config": {
                        "ticker": "MNQ1!",
                        "timeframe": "1h",
                        "annotation_text": "Quick Test Setup"
                    }
                }
            ],
            config={
                "execution_timeout": 600,  # 10 minutes max
                "skip_optimization": True,
                "minimal_output": True,
                "auto_cleanup": True
            }
        )
    
    @staticmethod
    def get_indicator_research_workflow() -> WorkflowTemplate:
        """Workflow focused on indicator research and testing."""
        return WorkflowTemplate(
            name="Indicator Research",
            description="Comprehensive indicator testing and analysis",
            steps=[
                {
                    "step": "authenticate",
                    "description": "Authenticate for indicator testing",
                    "action": "auth_manager.authenticate"
                },
                {
                    "step": "multi_timeframe_test",
                    "description": "Test indicators across multiple timeframes",
                    "action": "test_runner.test_strategy_indicators",
                    "config": {
                        "tickers": ["MNQ1!"],
                        "timeframes": ["1m", "5m", "15m", "1h", "4h", "1d"],
                        "indicators": [
                            "RSI", "MACD", "Stochastic", "Williams %R",
                            "EMA_9", "EMA_21", "SMA_50", "SMA_200",
                            "Bollinger_Bands", "ATR", "ADX"
                        ],
                        "parallel_execution": True,
                        "capture_screenshots": True
                    }
                },
                {
                    "step": "indicator_correlation_analysis",
                    "description": "Analyze indicator correlations",
                    "action": "analyze_indicator_correlations",
                    "config": {
                        "correlation_threshold": 0.8,
                        "time_window": "3M",
                        "export_results": True
                    }
                },
                {
                    "step": "signal_strength_analysis",
                    "description": "Analyze signal strength across timeframes",
                    "action": "analyze_signal_strength",
                    "config": {
                        "signal_types": ["buy", "sell", "neutral"],
                        "strength_metrics": ["consistency", "frequency", "reliability"]
                    }
                },
                {
                    "step": "create_indicator_comparison",
                    "description": "Create visual indicator comparison",
                    "action": "screenshot_manager.create_comparison_image",
                    "config": {
                        "layout": "grid",
                        "timeframes": ["5m", "1h", "4h"],
                        "annotations": True
                    }
                }
            ],
            config={
                "research_mode": True,
                "detailed_logging": True,
                "export_data": True,
                "statistical_analysis": True
            }
        )
    
    @staticmethod
    def get_optimization_workflow() -> WorkflowTemplate:
        """Workflow for strategy optimization and parameter tuning."""
        return WorkflowTemplate(
            name="Strategy Optimization",
            description="Comprehensive strategy parameter optimization",
            steps=[
                {
                    "step": "authenticate",
                    "description": "Authenticate for optimization",
                    "action": "auth_manager.authenticate"
                },
                {
                    "step": "baseline_backtest",
                    "description": "Run baseline backtest with default parameters",
                    "action": "backtest_runner.backtest_strategy",
                    "config": {
                        "optimization_enabled": False,
                        "capture_baseline": True
                    }
                },
                {
                    "step": "parameter_optimization",
                    "description": "Optimize strategy parameters",
                    "action": "backtest_runner.backtest_strategy",
                    "config": {
                        "optimization_enabled": True,
                        "optimization_parameters": {
                            "rsi_period": {"min": 10, "max": 30, "step": 2},
                            "ma_fast": {"min": 5, "max": 50, "step": 5},
                            "ma_slow": {"min": 20, "max": 200, "step": 10},
                            "stop_loss": {"min": 5, "max": 25, "step": 2.5},
                            "take_profit": {"min": 10, "max": 50, "step": 5}
                        },
                        "optimization_metric": "profit_factor",
                        "validation_method": "walk_forward"
                    }
                },
                {
                    "step": "robustness_testing",
                    "description": "Test optimized parameters on different periods",
                    "action": "run_robustness_tests",
                    "config": {
                        "test_periods": [
                            "2023-01-01:2023-06-30",
                            "2023-07-01:2023-12-31",
                            "2024-01-01:2024-06-30"
                        ],
                        "statistical_tests": True
                    }
                },
                {
                    "step": "optimization_report",
                    "description": "Generate optimization analysis report",
                    "action": "generate_optimization_report",
                    "config": {
                        "include_parameter_maps": True,
                        "include_stability_analysis": True,
                        "include_recommendations": True
                    }
                }
            ],
            config={
                "optimization_iterations": 1000,
                "cpu_cores": 4,
                "memory_limit": "8GB",
                "overfitting_protection": True
            }
        )
    
    @staticmethod
    def get_production_validation_workflow() -> WorkflowTemplate:
        """Workflow for validating strategies before production deployment."""
        return WorkflowTemplate(
            name="Production Validation",
            description="Final validation before strategy goes live",
            steps=[
                {
                    "step": "authenticate",
                    "description": "Authenticate for production validation",
                    "action": "auth_manager.authenticate"
                },
                {
                    "step": "comprehensive_backtest",
                    "description": "Run comprehensive historical backtest",
                    "action": "backtest_runner.backtest_strategy",
                    "config": {
                        "test_period": "5Y",  # 5 years of data
                        "include_bear_markets": True,
                        "include_volatile_periods": True,
                        "realistic_fills": True,
                        "slippage_model": "aggressive"
                    }
                },
                {
                    "step": "stress_testing",
                    "description": "Stress test strategy under extreme conditions",
                    "action": "run_stress_tests",
                    "config": {
                        "scenarios": [
                            "market_crash",
                            "high_volatility",
                            "low_liquidity",
                            "trending_market",
                            "sideways_market"
                        ],
                        "commission_stress": 2.0,  # 2x normal commission
                        "slippage_stress": 3.0     # 3x normal slippage
                    }
                },
                {
                    "step": "risk_analysis",
                    "description": "Comprehensive risk analysis",
                    "action": "analyze_strategy_risks",
                    "config": {
                        "var_analysis": True,
                        "monte_carlo_simulation": True,
                        "correlation_analysis": True,
                        "tail_risk_analysis": True
                    }
                },
                {
                    "step": "paper_trading_preparation",
                    "description": "Prepare for paper trading phase",
                    "action": "setup_paper_trading",
                    "config": {
                        "paper_duration": "30D",
                        "real_time_monitoring": True,
                        "alert_setup": True
                    }
                },
                {
                    "step": "production_documentation",
                    "description": "Generate production-ready documentation",
                    "action": "generate_production_docs",
                    "config": {
                        "include_risk_disclosures": True,
                        "include_operating_procedures": True,
                        "include_monitoring_setup": True
                    }
                }
            ],
            config={
                "validation_criteria": {
                    "min_sharpe_ratio": 1.5,
                    "max_drawdown": 0.15,
                    "min_profit_factor": 1.5,
                    "min_win_rate": 0.45
                },
                "approval_required": True,
                "documentation_required": True
            }
        )
    
    @staticmethod
    def get_all_templates() -> Dict[str, WorkflowTemplate]:
        """Get all available workflow templates."""
        return {
            'complete_strategy': WorkflowTemplates.get_complete_strategy_workflow(),
            'quick_test': WorkflowTemplates.get_quick_test_workflow(),
            'indicator_research': WorkflowTemplates.get_indicator_research_workflow(),
            'optimization': WorkflowTemplates.get_optimization_workflow(),
            'production_validation': WorkflowTemplates.get_production_validation_workflow()
        }
    
    @staticmethod
    def save_all_templates(output_dir: str) -> None:
        """Save all templates to files."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        templates = WorkflowTemplates.get_all_templates()
        
        for name, template in templates.items():
            file_path = output_path / f"{name}_workflow.yaml"
            template.save_to_file(str(file_path))
            print(f"Saved template: {file_path}")
    
    @staticmethod
    def create_custom_workflow(name: str, 
                              description: str,
                              strategy_path: str,
                              test_config: Optional[Dict[str, Any]] = None) -> WorkflowTemplate:
        """Create a custom workflow template."""
        default_config = {
            "ticker": "MNQ1!",
            "timeframes": ["1h"],
            "capture_screenshots": True
        }
        
        if test_config:
            default_config.update(test_config)
        
        steps = [
            {
                "step": "authenticate",
                "description": "Authenticate with Google OAuth",
                "action": "auth_manager.authenticate"
            },
            {
                "step": "test_strategy",
                "description": f"Test strategy: {name}",
                "action": "test_runner.test_strategy_indicators",
                "config": {
                    "strategy_path": strategy_path,
                    **default_config
                }
            },
            {
                "step": "backtest_strategy",
                "description": f"Backtest strategy: {name}",
                "action": "backtest_runner.backtest_strategy",
                "config": {
                    "strategy_path": strategy_path,
                    **default_config
                }
            },
            {
                "step": "capture_screenshots",
                "description": f"Capture charts for: {name}",
                "action": "screenshot_manager.capture_strategy_screenshots",
                "config": {
                    "strategy_name": name,
                    **default_config
                }
            }
        ]
        
        return WorkflowTemplate(
            name=name,
            description=description,
            steps=steps,
            config={
                "strategy_path": strategy_path,
                "custom_workflow": True,
                **default_config
            }
        )


# Example usage functions
def create_example_workflow_configs():
    """Create example workflow configuration files."""
    
    # Example 1: Simple strategy test
    simple_workflow = WorkflowTemplates.create_custom_workflow(
        name="Simple RSI Strategy Test",
        description="Test a simple RSI strategy on MNQ1!",
        strategy_path="strategies/rsi-strategy",
        test_config={
            "timeframes": ["5m", "1h"],
            "indicators": ["RSI"],
            "test_duration": 300
        }
    )
    
    # Example 2: Moving average strategy
    ma_workflow = WorkflowTemplates.create_custom_workflow(
        name="Moving Average Crossover",
        description="Test moving average crossover strategy",
        strategy_path="strategies/ma-crossover",
        test_config={
            "timeframes": ["15m", "1h", "4h"],
            "indicators": ["EMA_9", "EMA_21"],
            "optimization_enabled": True
        }
    )
    
    return {
        'simple_rsi': simple_workflow,
        'ma_crossover': ma_workflow
    }


if __name__ == "__main__":
    # Save all templates
    print("Creating workflow templates...")
    
    output_dir = Path("./workflow_templates")
    WorkflowTemplates.save_all_templates(str(output_dir))
    
    # Create example custom workflows
    custom_workflows = create_example_workflow_configs()
    
    for name, workflow in custom_workflows.items():
        file_path = output_dir / f"custom_{name}_workflow.yaml"
        workflow.save_to_file(str(file_path))
        print(f"Saved custom workflow: {file_path}")
    
    print("All workflow templates created successfully!")
    print(f"Templates saved in: {output_dir.absolute()}")