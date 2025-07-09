"""
Performance Monitoring and Metrics for Kairos
Tracks system performance, browser operations, and automation metrics
"""

import time
import logging
import threading
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
from contextlib import contextmanager
from functools import wraps
import psutil
import os


@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'name': self.name,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp.isoformat(),
            'tags': self.tags
        }


@dataclass
class OperationStats:
    """Statistics for a specific operation"""
    name: str
    count: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    success_count: int = 0
    error_count: int = 0
    recent_times: deque = field(default_factory=lambda: deque(maxlen=100))
    
    def add_timing(self, duration: float, success: bool = True):
        """Add timing measurement"""
        self.count += 1
        self.total_time += duration
        self.min_time = min(self.min_time, duration)
        self.max_time = max(self.max_time, duration)
        self.recent_times.append(duration)
        
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
            
    @property
    def average_time(self) -> float:
        """Calculate average execution time"""
        return self.total_time / self.count if self.count > 0 else 0.0
        
    @property
    def recent_average(self) -> float:
        """Calculate recent average execution time"""
        return sum(self.recent_times) / len(self.recent_times) if self.recent_times else 0.0
        
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        return self.success_count / self.count if self.count > 0 else 0.0
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'name': self.name,
            'count': self.count,
            'total_time': self.total_time,
            'average_time': self.average_time,
            'min_time': self.min_time if self.min_time != float('inf') else 0,
            'max_time': self.max_time,
            'recent_average': self.recent_average,
            'success_count': self.success_count,
            'error_count': self.error_count,
            'success_rate': self.success_rate
        }


class PerformanceMonitor:
    """
    Main performance monitoring system
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Monitoring configuration
        self.enabled = config.get('performance_monitoring', True)
        self.collect_interval = config.get('collect_interval', 60)  # seconds
        self.retention_hours = config.get('retention_hours', 24)
        self.max_metrics = config.get('max_metrics', 10000)
        
        # Data storage
        self.metrics: deque = deque(maxlen=self.max_metrics)
        self.operation_stats: Dict[str, OperationStats] = {}
        self.system_metrics: Dict[str, Any] = {}
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Background collection
        self._collection_thread = None
        self._stop_collection = threading.Event()
        
        if self.enabled:
            self._start_collection()
            
    def _start_collection(self):
        """Start background metrics collection"""
        self._collection_thread = threading.Thread(
            target=self._collection_loop,
            daemon=True
        )
        self._collection_thread.start()
        self.logger.info("Performance monitoring started")
        
    def _collection_loop(self):
        """Background collection loop"""
        while not self._stop_collection.is_set():
            try:
                self._collect_system_metrics()
                self._cleanup_old_metrics()
                
                # Wait for next collection
                self._stop_collection.wait(self.collect_interval)
                
            except Exception as e:
                self.logger.error(f"Error in performance collection: {e}")
                
    def _collect_system_metrics(self):
        """Collect system-level metrics"""
        if not self.enabled:
            return
            
        now = datetime.now()
        
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            self.add_metric('system.cpu.usage', cpu_percent, 'percent')
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self.add_metric('system.memory.usage', memory.percent, 'percent')
            self.add_metric('system.memory.available', memory.available, 'bytes')
            self.add_metric('system.memory.total', memory.total, 'bytes')
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            self.add_metric('system.disk.usage', disk.percent, 'percent')
            self.add_metric('system.disk.free', disk.free, 'bytes')
            
            # Process metrics
            process = psutil.Process()
            self.add_metric('process.cpu.usage', process.cpu_percent(), 'percent')
            self.add_metric('process.memory.usage', process.memory_percent(), 'percent')
            self.add_metric('process.memory.rss', process.memory_info().rss, 'bytes')
            
            # Network metrics (if available)
            try:
                net_io = psutil.net_io_counters()
                self.add_metric('system.network.bytes_sent', net_io.bytes_sent, 'bytes')
                self.add_metric('system.network.bytes_recv', net_io.bytes_recv, 'bytes')
            except:
                pass
                
        except Exception as e:
            self.logger.warning(f"Error collecting system metrics: {e}")
            
    def _cleanup_old_metrics(self):
        """Clean up old metrics"""
        if not self.metrics:
            return
            
        cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)
        
        with self._lock:
            # Remove old metrics
            while self.metrics and self.metrics[0].timestamp < cutoff_time:
                self.metrics.popleft()
                
    def add_metric(self, name: str, value: float, unit: str, tags: Optional[Dict[str, str]] = None):
        """
        Add a performance metric
        
        Args:
            name: Metric name
            value: Metric value
            unit: Unit of measurement
            tags: Optional tags for filtering
        """
        if not self.enabled:
            return
            
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            tags=tags or {}
        )
        
        with self._lock:
            self.metrics.append(metric)
            
    def record_operation(self, operation_name: str, duration: float, success: bool = True):
        """
        Record operation timing
        
        Args:
            operation_name: Name of the operation
            duration: Duration in seconds
            success: Whether operation was successful
        """
        if not self.enabled:
            return
            
        with self._lock:
            if operation_name not in self.operation_stats:
                self.operation_stats[operation_name] = OperationStats(operation_name)
                
            self.operation_stats[operation_name].add_timing(duration, success)
            
        # Also add as metric
        self.add_metric(
            f'operation.{operation_name}.duration',
            duration,
            'seconds',
            {'success': str(success)}
        )
        
    def get_operation_stats(self, operation_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get operation statistics
        
        Args:
            operation_name: Specific operation name, or None for all
            
        Returns:
            Dictionary of operation statistics
        """
        with self._lock:
            if operation_name:
                stats = self.operation_stats.get(operation_name)
                return stats.to_dict() if stats else {}
            else:
                return {
                    name: stats.to_dict() 
                    for name, stats in self.operation_stats.items()
                }
                
    def get_metrics(
        self, 
        name_filter: Optional[str] = None,
        time_range: Optional[timedelta] = None
    ) -> List[Dict[str, Any]]:
        """
        Get metrics with optional filtering
        
        Args:
            name_filter: Filter by metric name (substring match)
            time_range: Time range from now
            
        Returns:
            List of metric dictionaries
        """
        with self._lock:
            metrics = list(self.metrics)
            
        # Apply time filter
        if time_range:
            cutoff_time = datetime.now() - time_range
            metrics = [m for m in metrics if m.timestamp >= cutoff_time]
            
        # Apply name filter
        if name_filter:
            metrics = [m for m in metrics if name_filter in m.name]
            
        return [m.to_dict() for m in metrics]
        
    def get_system_summary(self) -> Dict[str, Any]:
        """Get system performance summary"""
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'memory_available': memory.available,
                'disk_usage': disk.percent,
                'disk_free': disk.free,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting system summary: {e}")
            return {}
            
    def get_browser_metrics(self) -> Dict[str, Any]:
        """Get browser-specific metrics"""
        browser_ops = {
            name: stats for name, stats in self.operation_stats.items()
            if 'browser' in name.lower() or 'selenium' in name.lower()
        }
        
        return {
            'operations': {name: stats.to_dict() for name, stats in browser_ops.items()},
            'total_operations': sum(stats.count for stats in browser_ops.values()),
            'average_success_rate': sum(stats.success_rate for stats in browser_ops.values()) / len(browser_ops) if browser_ops else 0
        }
        
    def export_metrics(self, format: str = 'json', filename: Optional[str] = None) -> str:
        """
        Export metrics to file or string
        
        Args:
            format: Export format ('json' or 'csv')
            filename: Optional filename to save to
            
        Returns:
            Exported data as string
        """
        data = {
            'metrics': self.get_metrics(),
            'operations': self.get_operation_stats(),
            'system_summary': self.get_system_summary(),
            'export_timestamp': datetime.now().isoformat()
        }
        
        if format == 'json':
            output = json.dumps(data, indent=2)
        elif format == 'csv':
            # Convert to CSV format
            lines = ['timestamp,name,value,unit,tags']
            for metric in data['metrics']:
                tags_str = json.dumps(metric['tags'])
                lines.append(f"{metric['timestamp']},{metric['name']},{metric['value']},{metric['unit']},{tags_str}")
            output = '\n'.join(lines)
        else:
            raise ValueError(f"Unsupported format: {format}")
            
        if filename:
            with open(filename, 'w') as f:
                f.write(output)
                
        return output
        
    def reset_stats(self):
        """Reset all statistics"""
        with self._lock:
            self.metrics.clear()
            self.operation_stats.clear()
            
        self.logger.info("Performance statistics reset")
        
    def stop(self):
        """Stop performance monitoring"""
        self._stop_collection.set()
        
        if self._collection_thread:
            self._collection_thread.join(timeout=5)
            
        self.logger.info("Performance monitoring stopped")
        
    def __del__(self):
        """Cleanup on destruction"""
        self.stop()


class PerformanceTimer:
    """
    Context manager for timing operations
    """
    
    def __init__(self, monitor: PerformanceMonitor, operation_name: str):
        self.monitor = monitor
        self.operation_name = operation_name
        self.start_time = None
        self.success = True
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.success = exc_type is None
            self.monitor.record_operation(self.operation_name, duration, self.success)
            
    def mark_error(self):
        """Mark operation as failed"""
        self.success = False


def performance_metric(monitor: PerformanceMonitor, operation_name: Optional[str] = None):
    """
    Decorator for automatically timing function calls
    
    Args:
        monitor: Performance monitor instance
        operation_name: Optional operation name (defaults to function name)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            with PerformanceTimer(monitor, op_name) as timer:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    timer.mark_error()
                    raise
                    
        return wrapper
    return decorator


class AlertPerformanceTracker:
    """
    Specialized tracker for alert creation performance
    """
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
        self.alert_metrics = defaultdict(list)
        
    def track_alert_creation(self, symbol: str, timeframe: str, duration: float, success: bool):
        """Track alert creation performance"""
        self.monitor.record_operation(
            'alert.creation',
            duration,
            success
        )
        
        # Add specific metrics
        self.monitor.add_metric(
            'alert.creation.duration',
            duration,
            'seconds',
            {'symbol': symbol, 'timeframe': timeframe, 'success': str(success)}
        )
        
    def track_alert_deletion(self, count: int, duration: float):
        """Track alert deletion performance"""
        self.monitor.record_operation('alert.deletion', duration, True)
        self.monitor.add_metric(
            'alert.deletion.count',
            count,
            'alerts',
            {'duration': str(duration)}
        )
        
    def get_alert_stats(self) -> Dict[str, Any]:
        """Get alert-specific statistics"""
        return {
            'creation': self.monitor.get_operation_stats('alert.creation'),
            'deletion': self.monitor.get_operation_stats('alert.deletion'),
            'recent_metrics': self.monitor.get_metrics(
                'alert.',
                timedelta(hours=1)
            )
        }


class BrowserPerformanceTracker:
    """
    Specialized tracker for browser operation performance
    """
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
        
    def track_page_load(self, url: str, duration: float, success: bool):
        """Track page load performance"""
        self.monitor.record_operation('browser.page_load', duration, success)
        self.monitor.add_metric(
            'browser.page_load.duration',
            duration,
            'seconds',
            {'url': url, 'success': str(success)}
        )
        
    def track_element_interaction(self, action: str, selector: str, duration: float, success: bool):
        """Track element interaction performance"""
        self.monitor.record_operation(f'browser.{action}', duration, success)
        self.monitor.add_metric(
            f'browser.{action}.duration',
            duration,
            'seconds',
            {'selector': selector, 'success': str(success)}
        )
        
    def track_browser_lifecycle(self, action: str, duration: float):
        """Track browser lifecycle events"""
        self.monitor.record_operation(f'browser.{action}', duration, True)
        self.monitor.add_metric(
            f'browser.{action}.duration',
            duration,
            'seconds'
        )
        
    def get_browser_stats(self) -> Dict[str, Any]:
        """Get browser-specific statistics"""
        return self.monitor.get_browser_metrics()


# Global performance monitor instance
_global_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> Optional[PerformanceMonitor]:
    """Get global performance monitor instance"""
    return _global_monitor


def initialize_performance_monitoring(config: Dict[str, Any]) -> PerformanceMonitor:
    """Initialize global performance monitoring"""
    global _global_monitor
    
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor(config)
        
    return _global_monitor


def cleanup_performance_monitoring():
    """Cleanup global performance monitoring"""
    global _global_monitor
    
    if _global_monitor:
        _global_monitor.stop()
        _global_monitor = None