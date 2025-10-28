"""
Performance monitoring and metrics collection
"""

import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
from functools import wraps
import structlog
from dataclasses import dataclass, asdict
import json

logger = structlog.get_logger()


@dataclass
class RequestMetric:
    """Request performance metric"""
    endpoint: str
    method: str
    status_code: int
    response_time: float
    timestamp: datetime
    user_id: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class SystemMetric:
    """System performance metric"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_usage_percent: float
    active_connections: int


class MetricsCollector:
    """Collect and store performance metrics"""
    
    def __init__(self, max_metrics: int = 10000):
        self.max_metrics = max_metrics
        self.request_metrics: deque = deque(maxlen=max_metrics)
        self.system_metrics: deque = deque(maxlen=1000)  # Keep last 1000 system metrics
        self.error_counts = defaultdict(int)
        self.endpoint_stats = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'min_time': float('inf'),
            'max_time': 0.0,
            'error_count': 0
        })
        self.active_requests = 0
        self.total_requests = 0
        self.start_time = datetime.utcnow()
        self._lock = threading.Lock()
    
    def add_request_metric(self, metric: RequestMetric):
        """Add a request metric"""
        with self._lock:
            self.request_metrics.append(metric)
            self.total_requests += 1
            
            # Update endpoint statistics
            stats = self.endpoint_stats[f"{metric.method} {metric.endpoint}"]
            stats['count'] += 1
            stats['total_time'] += metric.response_time
            stats['min_time'] = min(stats['min_time'], metric.response_time)
            stats['max_time'] = max(stats['max_time'], metric.response_time)
            
            if metric.status_code >= 400:
                stats['error_count'] += 1
                self.error_counts[metric.status_code] += 1
    
    def add_system_metric(self, metric: SystemMetric):
        """Add a system metric"""
        with self._lock:
            self.system_metrics.append(metric)
    
    def get_request_stats(self, minutes: int = 60) -> Dict[str, Any]:
        """Get request statistics for the last N minutes"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        with self._lock:
            recent_metrics = [
                m for m in self.request_metrics 
                if m.timestamp >= cutoff_time
            ]
            
            if not recent_metrics:
                return {
                    'total_requests': 0,
                    'avg_response_time': 0,
                    'error_rate': 0,
                    'requests_per_minute': 0
                }
            
            total_requests = len(recent_metrics)
            avg_response_time = sum(m.response_time for m in recent_metrics) / total_requests
            error_count = sum(1 for m in recent_metrics if m.status_code >= 400)
            error_rate = (error_count / total_requests) * 100
            requests_per_minute = total_requests / minutes
            
            return {
                'total_requests': total_requests,
                'avg_response_time': round(avg_response_time, 3),
                'error_rate': round(error_rate, 2),
                'requests_per_minute': round(requests_per_minute, 2),
                'error_count': error_count
            }
    
    def get_endpoint_stats(self) -> Dict[str, Any]:
        """Get statistics by endpoint"""
        with self._lock:
            stats = {}
            for endpoint, data in self.endpoint_stats.items():
                if data['count'] > 0:
                    avg_time = data['total_time'] / data['count']
                    error_rate = (data['error_count'] / data['count']) * 100
                    
                    stats[endpoint] = {
                        'count': data['count'],
                        'avg_response_time': round(avg_time, 3),
                        'min_response_time': round(data['min_time'], 3),
                        'max_response_time': round(data['max_time'], 3),
                        'error_rate': round(error_rate, 2),
                        'error_count': data['error_count']
                    }
            
            return stats
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system statistics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get network connections (approximate active connections)
            connections = len(psutil.net_connections(kind='inet'))
            
            current_metric = SystemMetric(
                timestamp=datetime.utcnow(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / (1024 * 1024),
                disk_usage_percent=disk.percent,
                active_connections=connections
            )
            
            self.add_system_metric(current_metric)
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_mb': round(memory.used / (1024 * 1024), 2),
                'memory_available_mb': round(memory.available / (1024 * 1024), 2),
                'disk_usage_percent': disk.percent,
                'active_connections': connections,
                'uptime_seconds': (datetime.utcnow() - self.start_time).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"Failed to get system stats: {e}")
            return {}
    
    def get_error_summary(self) -> Dict[str, int]:
        """Get error count summary"""
        with self._lock:
            return dict(self.error_counts)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        request_stats = self.get_request_stats(5)  # Last 5 minutes
        system_stats = self.get_system_stats()
        
        # Determine health status
        health_score = 100
        issues = []
        
        # Check error rate
        if request_stats.get('error_rate', 0) > 10:
            health_score -= 30
            issues.append(f"High error rate: {request_stats['error_rate']}%")
        
        # Check response time
        if request_stats.get('avg_response_time', 0) > 2.0:
            health_score -= 20
            issues.append(f"Slow response time: {request_stats['avg_response_time']}s")
        
        # Check system resources
        if system_stats.get('cpu_percent', 0) > 80:
            health_score -= 25
            issues.append(f"High CPU usage: {system_stats['cpu_percent']}%")
        
        if system_stats.get('memory_percent', 0) > 85:
            health_score -= 25
            issues.append(f"High memory usage: {system_stats['memory_percent']}%")
        
        # Determine status
        if health_score >= 90:
            status = "healthy"
        elif health_score >= 70:
            status = "warning"
        else:
            status = "critical"
        
        return {
            'status': status,
            'health_score': max(0, health_score),
            'issues': issues,
            'last_check': datetime.utcnow().isoformat()
        }


# Global metrics collector
metrics_collector = MetricsCollector()


def monitor_performance(endpoint_name: str = None):
    """
    Decorator to monitor endpoint performance
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            metrics_collector.active_requests += 1
            
            try:
                # Extract request info if available
                request = None
                for arg in args:
                    if hasattr(arg, 'method') and hasattr(arg, 'url'):
                        request = arg
                        break
                
                result = await func(*args, **kwargs)
                
                # Record successful request
                response_time = time.time() - start_time
                endpoint = endpoint_name or (request.url.path if request else func.__name__)
                method = request.method if request else "UNKNOWN"
                
                metric = RequestMetric(
                    endpoint=endpoint,
                    method=method,
                    status_code=200,
                    response_time=response_time,
                    timestamp=datetime.utcnow()
                )
                
                metrics_collector.add_request_metric(metric)
                return result
                
            except Exception as e:
                # Record failed request
                response_time = time.time() - start_time
                endpoint = endpoint_name or (request.url.path if request else func.__name__)
                method = request.method if request else "UNKNOWN"
                
                metric = RequestMetric(
                    endpoint=endpoint,
                    method=method,
                    status_code=500,
                    response_time=response_time,
                    timestamp=datetime.utcnow(),
                    error_message=str(e)
                )
                
                metrics_collector.add_request_metric(metric)
                raise
                
            finally:
                metrics_collector.active_requests -= 1
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            metrics_collector.active_requests += 1
            
            try:
                result = func(*args, **kwargs)
                
                # Record successful request
                response_time = time.time() - start_time
                endpoint = endpoint_name or func.__name__
                
                metric = RequestMetric(
                    endpoint=endpoint,
                    method="SYNC",
                    status_code=200,
                    response_time=response_time,
                    timestamp=datetime.utcnow()
                )
                
                metrics_collector.add_request_metric(metric)
                return result
                
            except Exception as e:
                # Record failed request
                response_time = time.time() - start_time
                endpoint = endpoint_name or func.__name__
                
                metric = RequestMetric(
                    endpoint=endpoint,
                    method="SYNC",
                    status_code=500,
                    response_time=response_time,
                    timestamp=datetime.utcnow(),
                    error_message=str(e)
                )
                
                metrics_collector.add_request_metric(metric)
                raise
                
            finally:
                metrics_collector.active_requests -= 1
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class PerformanceLogger:
    """Log performance metrics periodically"""
    
    def __init__(self, interval: int = 300):  # 5 minutes
        self.interval = interval
        self.running = False
        self.thread = None
    
    def start(self):
        """Start performance logging"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._log_loop, daemon=True)
            self.thread.start()
            logger.info("Performance logging started")
    
    def stop(self):
        """Stop performance logging"""
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("Performance logging stopped")
    
    def _log_loop(self):
        """Main logging loop"""
        while self.running:
            try:
                # Log request statistics
                request_stats = metrics_collector.get_request_stats(self.interval // 60)
                system_stats = metrics_collector.get_system_stats()
                health_status = metrics_collector.get_health_status()
                
                logger.info(
                    "Performance metrics",
                    request_stats=request_stats,
                    system_stats=system_stats,
                    health_status=health_status
                )
                
                # Log top endpoints by request count
                endpoint_stats = metrics_collector.get_endpoint_stats()
                if endpoint_stats:
                    top_endpoints = sorted(
                        endpoint_stats.items(),
                        key=lambda x: x[1]['count'],
                        reverse=True
                    )[:5]
                    
                    logger.info(
                        "Top endpoints by request count",
                        endpoints=dict(top_endpoints)
                    )
                
            except Exception as e:
                logger.error(f"Performance logging error: {e}")
            
            time.sleep(self.interval)


# Global performance logger
performance_logger = PerformanceLogger()


def start_monitoring():
    """Start performance monitoring"""
    performance_logger.start()


def stop_monitoring():
    """Stop performance monitoring"""
    performance_logger.stop()


def get_metrics_summary() -> Dict[str, Any]:
    """Get comprehensive metrics summary"""
    return {
        'request_stats': metrics_collector.get_request_stats(),
        'system_stats': metrics_collector.get_system_stats(),
        'endpoint_stats': metrics_collector.get_endpoint_stats(),
        'error_summary': metrics_collector.get_error_summary(),
        'health_status': metrics_collector.get_health_status(),
        'active_requests': metrics_collector.active_requests,
        'total_requests': metrics_collector.total_requests
    }