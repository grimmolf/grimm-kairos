"""
Data processing utilities for TradingView automation
Handles data transformation, validation, and formatting
"""

import json
import re
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation


class DataProcessor:
    """
    Processes and transforms data from TradingView
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def parse_indicator_value(self, raw_value: str) -> Optional[Union[float, str]]:
        """
        Parse indicator value from TradingView display
        
        Args:
            raw_value: Raw text from TradingView indicator
            
        Returns:
            Parsed numeric value or original string if unparseable
        """
        if not raw_value:
            return None
            
        # Clean the value
        cleaned = raw_value.strip()
        
        # Handle special values
        if cleaned.lower() in ['n/a', 'na', '—', '-', '']:
            return None
            
        # Handle percentage values
        if cleaned.endswith('%'):
            try:
                return float(cleaned[:-1]) / 100
            except ValueError:
                return cleaned
                
        # Handle currency symbols
        cleaned = re.sub(r'[,$€£¥₹]', '', cleaned)
        
        # Handle parentheses for negative values
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
            
        # Handle scientific notation
        if 'e' in cleaned.lower():
            try:
                return float(cleaned)
            except ValueError:
                return cleaned
                
        # Handle K, M, B suffixes
        multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
        for suffix, multiplier in multipliers.items():
            if cleaned.upper().endswith(suffix):
                try:
                    return float(cleaned[:-1]) * multiplier
                except ValueError:
                    return cleaned
                    
        # Try to parse as number
        try:
            # Use Decimal for precise calculations
            decimal_value = Decimal(cleaned)
            # Convert to float for JSON serialization
            return float(decimal_value)
        except (InvalidOperation, ValueError):
            return cleaned
            
    def parse_price_value(self, raw_price: str) -> Optional[float]:
        """
        Parse price value from TradingView
        
        Args:
            raw_price: Raw price text
            
        Returns:
            Parsed price as float or None
        """
        if not raw_price:
            return None
            
        # Remove currency symbols and commas
        cleaned = re.sub(r'[,$€£¥₹\s]', '', raw_price.strip())
        
        try:
            return float(cleaned)
        except ValueError:
            return None
            
    def parse_volume_value(self, raw_volume: str) -> Optional[float]:
        """
        Parse volume value with K/M/B suffixes
        
        Args:
            raw_volume: Raw volume text
            
        Returns:
            Parsed volume as float or None
        """
        if not raw_volume:
            return None
            
        cleaned = raw_volume.strip().upper()
        
        # Handle suffixes
        multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}
        
        for suffix, multiplier in multipliers.items():
            if cleaned.endswith(suffix):
                try:
                    return float(cleaned[:-1]) * multiplier
                except ValueError:
                    return None
                    
        try:
            return float(cleaned)
        except ValueError:
            return None
            
    def parse_percentage(self, raw_percentage: str) -> Optional[float]:
        """
        Parse percentage value
        
        Args:
            raw_percentage: Raw percentage text
            
        Returns:
            Parsed percentage as decimal (0.05 for 5%)
        """
        if not raw_percentage:
            return None
            
        cleaned = raw_percentage.strip()
        
        # Remove % symbol
        if cleaned.endswith('%'):
            cleaned = cleaned[:-1]
            
        # Handle parentheses for negative values
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
            
        try:
            return float(cleaned) / 100
        except ValueError:
            return None
            
    def parse_datetime(self, raw_datetime: str) -> Optional[datetime]:
        """
        Parse datetime from TradingView format
        
        Args:
            raw_datetime: Raw datetime string
            
        Returns:
            Parsed datetime object or None
        """
        if not raw_datetime:
            return None
            
        # Common TradingView datetime formats
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%m/%d/%Y %H:%M',
            '%d/%m/%Y %H:%M',
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%H:%M:%S',
            '%H:%M'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(raw_datetime.strip(), fmt)
            except ValueError:
                continue
                
        return None
        
    def normalize_symbol(self, symbol: str) -> str:
        """
        Normalize symbol format
        
        Args:
            symbol: Raw symbol string
            
        Returns:
            Normalized symbol
        """
        if not symbol:
            return ""
            
        # Remove extra spaces and convert to uppercase
        normalized = symbol.strip().upper()
        
        # Handle exchange prefixes
        if ':' in normalized:
            exchange, symbol_part = normalized.split(':', 1)
            return f"{exchange}:{symbol_part}"
            
        return normalized
        
    def extract_numbers(self, text: str) -> List[float]:
        """
        Extract all numbers from text
        
        Args:
            text: Input text
            
        Returns:
            List of extracted numbers
        """
        if not text:
            return []
            
        # Pattern to match numbers (including decimals and negative)
        pattern = r'-?\d+(?:\.\d+)?'
        matches = re.findall(pattern, text)
        
        numbers = []
        for match in matches:
            try:
                numbers.append(float(match))
            except ValueError:
                continue
                
        return numbers
        
    def validate_alert_data(self, alert_data: Dict[str, Any]) -> List[str]:
        """
        Validate alert data structure
        
        Args:
            alert_data: Alert configuration data
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Required fields
        required_fields = ['name', 'condition_type']
        for field in required_fields:
            if field not in alert_data:
                errors.append(f"Missing required field: {field}")
                
        # Validate condition type
        valid_types = ['Price', 'Indicator', 'Strategy', 'Drawing']
        if alert_data.get('condition_type') not in valid_types:
            errors.append(f"Invalid condition_type. Must be one of: {valid_types}")
            
        # Validate expiration
        if 'expiration_minutes' in alert_data:
            try:
                minutes = int(alert_data['expiration_minutes'])
                if minutes < 0:
                    errors.append("expiration_minutes must be non-negative")
            except (ValueError, TypeError):
                errors.append("expiration_minutes must be a valid integer")
                
        return errors
        
    def clean_html(self, html_text: str) -> str:
        """
        Clean HTML from text
        
        Args:
            html_text: Text with HTML tags
            
        Returns:
            Cleaned text
        """
        if not html_text:
            return ""
            
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', html_text)
        
        # Decode HTML entities
        html_entities = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&#39;': "'",
            '&nbsp;': ' '
        }
        
        for entity, replacement in html_entities.items():
            clean_text = clean_text.replace(entity, replacement)
            
        return clean_text.strip()
        
    def format_number(self, value: Union[int, float], decimals: int = 2) -> str:
        """
        Format number for display
        
        Args:
            value: Numeric value
            decimals: Number of decimal places
            
        Returns:
            Formatted string
        """
        if value is None:
            return "N/A"
            
        try:
            if abs(value) >= 1000000000:
                return f"{value/1000000000:.{decimals}f}B"
            elif abs(value) >= 1000000:
                return f"{value/1000000:.{decimals}f}M"
            elif abs(value) >= 1000:
                return f"{value/1000:.{decimals}f}K"
            else:
                return f"{value:.{decimals}f}"
        except (TypeError, ValueError):
            return str(value)
            
    def format_percentage(self, value: Union[int, float], decimals: int = 2) -> str:
        """
        Format percentage for display
        
        Args:
            value: Decimal percentage (0.05 for 5%)
            decimals: Number of decimal places
            
        Returns:
            Formatted percentage string
        """
        if value is None:
            return "N/A"
            
        try:
            return f"{value * 100:.{decimals}f}%"
        except (TypeError, ValueError):
            return str(value)
            
    def create_summary_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create summary report from raw data
        
        Args:
            data: Raw data dictionary
            
        Returns:
            Formatted summary report
        """
        summary = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'summary': {},
            'details': data
        }
        
        # Process different data types
        if 'performance' in data:
            summary['summary']['performance'] = self._summarize_performance(data['performance'])
            
        if 'indicators' in data:
            summary['summary']['indicators'] = self._summarize_indicators(data['indicators'])
            
        if 'alerts' in data:
            summary['summary']['alerts'] = self._summarize_alerts(data['alerts'])
            
        return summary
        
    def _summarize_performance(self, performance: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize performance data"""
        return {
            'net_profit': self.format_number(performance.get('net_profit', 0)),
            'total_trades': performance.get('total_trades', 0),
            'win_rate': self.format_percentage(performance.get('percent_profitable', 0) / 100),
            'profit_factor': self.format_number(performance.get('profit_factor', 0)),
            'max_drawdown': self.format_percentage(performance.get('max_drawdown_percent', 0) / 100)
        }
        
    def _summarize_indicators(self, indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize indicator data"""
        summary = {}
        for name, value in indicators.items():
            if isinstance(value, (int, float)):
                summary[name] = self.format_number(value)
            else:
                summary[name] = str(value)
        return summary
        
    def _summarize_alerts(self, alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize alert data"""
        return {
            'total_alerts': len(alerts),
            'active_alerts': sum(1 for alert in alerts if alert.get('status') == 'active'),
            'recent_alerts': [alert for alert in alerts[-5:]]  # Last 5 alerts
        }
        
    def export_to_json(self, data: Dict[str, Any], pretty: bool = True) -> str:
        """
        Export data to JSON format
        
        Args:
            data: Data to export
            pretty: Whether to format JSON nicely
            
        Returns:
            JSON string
        """
        try:
            if pretty:
                return json.dumps(data, indent=2, default=str)
            else:
                return json.dumps(data, default=str)
        except Exception as e:
            self.logger.error(f"Failed to export to JSON: {e}")
            return "{}"
            
    def export_to_csv(self, data: List[Dict[str, Any]], headers: Optional[List[str]] = None) -> str:
        """
        Export data to CSV format
        
        Args:
            data: List of data dictionaries
            headers: Optional list of headers
            
        Returns:
            CSV string
        """
        if not data:
            return ""
            
        # Get headers from first row if not provided
        if headers is None:
            headers = list(data[0].keys())
            
        csv_lines = [','.join(headers)]
        
        for row in data:
            csv_row = []
            for header in headers:
                value = row.get(header, '')
                # Escape commas and quotes in CSV
                if isinstance(value, str):
                    if ',' in value or '"' in value:
                        value = f'"{value.replace('"', '""')}"'
                csv_row.append(str(value))
            csv_lines.append(','.join(csv_row))
            
        return '\n'.join(csv_lines)