"""
Real-time Analytics Engine for Phase 4 Kenobi Code Analysis Agent
Provides real-time monitoring, performance tracking, and usage analytics
"""

import asyncio
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import threading
from pathlib import Path
import hashlib

from app.models.repository_schemas import CodeElement, Repository


class MetricType(str, Enum):
    """Types of metrics tracked by analytics engine"""
    PERFORMANCE = "performance"
    USAGE = "usage"
    QUALITY = "quality"
    SECURITY = "security"
    TREND = "trend"
    ALERT = "alert"


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Metric:
    """Individual metric data point"""
    timestamp: datetime
    metric_type: MetricType
    name: str
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class Alert:
    """Alert configuration and state"""
    id: str
    name: str
    metric_name: str
    condition: str  # e.g., "value > 100", "trend_direction == 'down'"
    severity: AlertSeverity
    threshold: float
    enabled: bool = True
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0


@dataclass
class PerformanceMetrics:
    """Performance tracking metrics"""
    response_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    throughput: deque = field(default_factory=lambda: deque(maxlen=1000))
    error_rates: deque = field(default_factory=lambda: deque(maxlen=1000))
    memory_usage: deque = field(default_factory=lambda: deque(maxlen=1000))
    cpu_usage: deque = field(default_factory=lambda: deque(maxlen=1000))


@dataclass
class UsageMetrics:
    """Usage analytics metrics"""
    api_calls: Dict[str, int] = field(default_factory=dict)
    user_sessions: Dict[str, datetime] = field(default_factory=dict)
    feature_usage: Dict[str, int] = field(default_factory=dict)
    repository_access: Dict[str, int] = field(default_factory=dict)


class RealTimeMonitor:
    """Real-time file system and code monitoring"""
    
    def __init__(self, analytics_engine):
        self.analytics_engine = analytics_engine
        self.watched_paths: Dict[str, float] = {}  # path -> last_modified
        self.monitoring_active = False
        self.monitor_thread = None
        
    def start_monitoring(self, paths: List[str]):
        """Start monitoring specified paths for changes"""
        self.watched_paths = {path: 0 for path in paths}
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop file system monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
            
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                for path_str in list(self.watched_paths.keys()):
                    path = Path(path_str)
                    if path.exists():
                        current_mtime = path.stat().st_mtime
                        if current_mtime > self.watched_paths[path_str]:
                            self.watched_paths[path_str] = current_mtime
                            asyncio.create_task(self._handle_file_change(path_str))
                            
                time.sleep(1)  # Check every second
            except Exception as e:
                print(f"Monitor error: {e}")
                time.sleep(5)
                
    async def _handle_file_change(self, file_path: str):
        """Handle detected file changes"""
        await self.analytics_engine.record_metric(
            MetricType.USAGE,
            "file_change",
            1,
            metadata={"file_path": file_path, "timestamp": datetime.now().isoformat()}
        )


class TrendAnalyzer:
    """Analyze trends in metrics data"""
    
    def __init__(self):
        self.trend_cache: Dict[str, Dict] = {}
        
    def analyze_trend(self, metrics: List[Metric], window_hours: int = 24) -> Dict[str, Any]:
        """Analyze trend for given metrics"""
        if len(metrics) < 2:
            return {"direction": "stable", "confidence": 0, "rate": 0}
            
        # Sort by timestamp
        sorted_metrics = sorted(metrics, key=lambda m: m.timestamp)
        
        # Calculate trend direction and rate
        values = [m.value for m in sorted_metrics]
        timestamps = [m.timestamp.timestamp() for m in sorted_metrics]
        
        # Simple linear regression for trend
        n = len(values)
        sum_x = sum(timestamps)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(timestamps, values))
        sum_x2 = sum(x * x for x in timestamps)
        
        if n * sum_x2 - sum_x * sum_x == 0:
            slope = 0
        else:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            
        # Determine direction
        if abs(slope) < 0.001:
            direction = "stable"
        elif slope > 0:
            direction = "up"
        else:
            direction = "down"
            
        # Calculate confidence based on R-squared
        if len(set(values)) == 1:
            confidence = 1.0 if direction == "stable" else 0.0
        else:
            mean_y = sum_y / n
            ss_tot = sum((y - mean_y) ** 2 for y in values)
            ss_res = sum((values[i] - (slope * timestamps[i])) ** 2 for i in range(n))
            confidence = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
        return {
            "direction": direction,
            "confidence": min(1.0, max(0.0, confidence)),
            "rate": slope,
            "data_points": n
        }


class AlertManager:
    """Manage alerts and notifications"""
    
    def __init__(self):
        self.alerts: Dict[str, Alert] = {}
        self.alert_callbacks: List[Callable] = []
        
    def add_alert(self, alert: Alert):
        """Add new alert configuration"""
        self.alerts[alert.id] = alert
        
    def remove_alert(self, alert_id: str):
        """Remove alert configuration"""
        self.alerts.pop(alert_id, None)
        
    def add_callback(self, callback: Callable):
        """Add alert callback function"""
        self.alert_callbacks.append(callback)
        
    async def check_alerts(self, metric: Metric):
        """Check if metric triggers any alerts"""
        for alert in self.alerts.values():
            if not alert.enabled:
                continue
                
            if alert.metric_name == metric.name:
                if self._evaluate_condition(alert, metric):
                    await self._trigger_alert(alert, metric)
                    
    def _evaluate_condition(self, alert: Alert, metric: Metric) -> bool:
        """Evaluate alert condition"""
        try:
            # Simple condition evaluation
            if ">" in alert.condition:
                threshold = float(alert.condition.split(">")[1].strip())
                return metric.value > threshold
            elif "<" in alert.condition:
                threshold = float(alert.condition.split("<")[1].strip())
                return metric.value < threshold
            elif "==" in alert.condition:
                threshold = float(alert.condition.split("==")[1].strip())
                return abs(metric.value - threshold) < 0.001
            return False
        except:
            return False
            
    async def _trigger_alert(self, alert: Alert, metric: Metric):
        """Trigger alert and notify callbacks"""
        alert.last_triggered = datetime.now()
        alert.trigger_count += 1
        
        alert_data = {
            "alert_id": alert.id,
            "alert_name": alert.name,
            "severity": alert.severity.value,
            "metric": metric.name,
            "value": metric.value,
            "threshold": alert.threshold,
            "timestamp": metric.timestamp.isoformat()
        }
        
        for callback in self.alert_callbacks:
            try:
                await callback(alert_data)
            except Exception as e:
                print(f"Alert callback error: {e}")


class AnalyticsEngine:
    """Main analytics engine for real-time monitoring and analysis"""
    
    def __init__(self):
        self.metrics_store: Dict[str, List[Metric]] = defaultdict(list)
        self.performance_metrics = PerformanceMetrics()
        self.usage_metrics = UsageMetrics()
        self.real_time_monitor = RealTimeMonitor(self)
        self.trend_analyzer = TrendAnalyzer()
        self.alert_manager = AlertManager()
        self.session_data: Dict[str, Dict] = {}
        self.start_time = datetime.now()
        
        # Setup default alerts
        self._setup_default_alerts()
        
    def _setup_default_alerts(self):
        """Setup default alert configurations"""
        default_alerts = [
            Alert(
                id="high_response_time",
                name="High Response Time",
                metric_name="response_time",
                condition="value > 5000",  # 5 seconds
                severity=AlertSeverity.HIGH,
                threshold=5000
            ),
            Alert(
                id="low_quality_score",
                name="Low Quality Score",
                metric_name="quality_score",
                condition="value < 0.6",
                severity=AlertSeverity.MEDIUM,
                threshold=0.6
            ),
            Alert(
                id="high_error_rate",
                name="High Error Rate",
                metric_name="error_rate",
                condition="value > 0.05",  # 5%
                severity=AlertSeverity.CRITICAL,
                threshold=0.05
            )
        ]
        
        for alert in default_alerts:
            self.alert_manager.add_alert(alert)
    
    async def record_metric(self, metric_type: MetricType, name: str, value: float, 
                          metadata: Dict[str, Any] = None, tags: Dict[str, str] = None):
        """Record a new metric"""
        metric = Metric(
            timestamp=datetime.now(),
            metric_type=metric_type,
            name=name,
            value=value,
            metadata=metadata or {},
            tags=tags or {}
        )
        
        # Store metric
        self.metrics_store[name].append(metric)
        
        # Keep only recent metrics (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.metrics_store[name] = [
            m for m in self.metrics_store[name] 
            if m.timestamp > cutoff_time
        ]
        
        # Check alerts
        await self.alert_manager.check_alerts(metric)
        
        # Update specific metric stores
        if metric_type == MetricType.PERFORMANCE:
            await self._update_performance_metrics(metric)
        elif metric_type == MetricType.USAGE:
            await self._update_usage_metrics(metric)
    
    async def _update_performance_metrics(self, metric: Metric):
        """Update performance-specific metrics"""
        if metric.name == "response_time":
            self.performance_metrics.response_times.append(metric.value)
        elif metric.name == "throughput":
            self.performance_metrics.throughput.append(metric.value)
        elif metric.name == "error_rate":
            self.performance_metrics.error_rates.append(metric.value)
        elif metric.name == "memory_usage":
            self.performance_metrics.memory_usage.append(metric.value)
        elif metric.name == "cpu_usage":
            self.performance_metrics.cpu_usage.append(metric.value)
    
    async def _update_usage_metrics(self, metric: Metric):
        """Update usage-specific metrics"""
        if metric.name == "api_call":
            endpoint = metric.metadata.get("endpoint", "unknown")
            self.usage_metrics.api_calls[endpoint] = self.usage_metrics.api_calls.get(endpoint, 0) + 1
        elif metric.name == "feature_usage":
            feature = metric.metadata.get("feature", "unknown")
            self.usage_metrics.feature_usage[feature] = self.usage_metrics.feature_usage.get(feature, 0) + 1
        elif metric.name == "repository_access":
            repo_id = metric.metadata.get("repository_id", "unknown")
            self.usage_metrics.repository_access[repo_id] = self.usage_metrics.repository_access.get(repo_id, 0) + 1
    
    async def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        summary = {
            "time_range": {
                "start": cutoff_time.isoformat(),
                "end": datetime.now().isoformat(),
                "hours": hours
            },
            "performance": await self._get_performance_summary(),
            "usage": await self._get_usage_summary(),
            "quality": await self._get_quality_summary(),
            "trends": await self._get_trends_summary(hours),
            "alerts": await self._get_alerts_summary(),
            "system": await self._get_system_summary()
        }
        
        return summary
    
    async def _get_performance_summary(self) -> Dict[str, Any]:
        """Get performance metrics summary"""
        response_times = list(self.performance_metrics.response_times)
        throughput = list(self.performance_metrics.throughput)
        error_rates = list(self.performance_metrics.error_rates)
        
        return {
            "response_time": {
                "avg": sum(response_times) / len(response_times) if response_times else 0,
                "min": min(response_times) if response_times else 0,
                "max": max(response_times) if response_times else 0,
                "p95": self._percentile(response_times, 95) if response_times else 0
            },
            "throughput": {
                "avg": sum(throughput) / len(throughput) if throughput else 0,
                "total": sum(throughput) if throughput else 0
            },
            "error_rate": {
                "avg": sum(error_rates) / len(error_rates) if error_rates else 0,
                "max": max(error_rates) if error_rates else 0
            }
        }
    
    async def _get_usage_summary(self) -> Dict[str, Any]:
        """Get usage metrics summary"""
        return {
            "api_calls": dict(self.usage_metrics.api_calls),
            "feature_usage": dict(self.usage_metrics.feature_usage),
            "repository_access": dict(self.usage_metrics.repository_access),
            "active_sessions": len(self.usage_metrics.user_sessions),
            "total_api_calls": sum(self.usage_metrics.api_calls.values())
        }
    
    async def _get_quality_summary(self) -> Dict[str, Any]:
        """Get quality metrics summary"""
        quality_metrics = self.metrics_store.get("quality_score", [])
        
        if not quality_metrics:
            return {"avg_score": 0, "trend": "stable", "data_points": 0}
            
        scores = [m.value for m in quality_metrics]
        trend = self.trend_analyzer.analyze_trend(quality_metrics)
        
        return {
            "avg_score": sum(scores) / len(scores),
            "min_score": min(scores),
            "max_score": max(scores),
            "trend": trend["direction"],
            "trend_confidence": trend["confidence"],
            "data_points": len(scores)
        }
    
    async def _get_trends_summary(self, hours: int) -> Dict[str, Any]:
        """Get trends analysis summary"""
        trends = {}
        
        for metric_name, metrics in self.metrics_store.items():
            if len(metrics) >= 2:
                trend = self.trend_analyzer.analyze_trend(metrics, hours)
                trends[metric_name] = trend
                
        return trends
    
    async def _get_alerts_summary(self) -> Dict[str, Any]:
        """Get alerts summary"""
        active_alerts = [a for a in self.alert_manager.alerts.values() if a.enabled]
        triggered_alerts = [a for a in active_alerts if a.last_triggered]
        
        return {
            "total_alerts": len(self.alert_manager.alerts),
            "active_alerts": len(active_alerts),
            "triggered_alerts": len(triggered_alerts),
            "recent_triggers": [
                {
                    "alert_id": a.id,
                    "name": a.name,
                    "severity": a.severity.value,
                    "last_triggered": a.last_triggered.isoformat() if a.last_triggered else None,
                    "trigger_count": a.trigger_count
                }
                for a in sorted(triggered_alerts, key=lambda x: x.last_triggered or datetime.min, reverse=True)[:10]
            ]
        }
    
    async def _get_system_summary(self) -> Dict[str, Any]:
        """Get system metrics summary"""
        uptime = datetime.now() - self.start_time
        
        return {
            "uptime_seconds": uptime.total_seconds(),
            "uptime_hours": uptime.total_seconds() / 3600,
            "start_time": self.start_time.isoformat(),
            "metrics_stored": sum(len(metrics) for metrics in self.metrics_store.values()),
            "monitoring_active": self.real_time_monitor.monitoring_active,
            "watched_paths": len(self.real_time_monitor.watched_paths)
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    async def start_real_time_monitoring(self, repository_paths: List[str]):
        """Start real-time monitoring for repositories"""
        self.real_time_monitor.start_monitoring(repository_paths)
        await self.record_metric(
            MetricType.USAGE,
            "monitoring_started",
            len(repository_paths),
            metadata={"paths": repository_paths}
        )
    
    async def stop_real_time_monitoring(self):
        """Stop real-time monitoring"""
        self.real_time_monitor.stop_monitoring()
        await self.record_metric(MetricType.USAGE, "monitoring_stopped", 1)
    
    async def track_api_call(self, endpoint: str, response_time: float, status_code: int):
        """Track API call metrics"""
        await self.record_metric(
            MetricType.PERFORMANCE,
            "response_time",
            response_time,
            metadata={"endpoint": endpoint, "status_code": status_code}
        )
        
        await self.record_metric(
            MetricType.USAGE,
            "api_call",
            1,
            metadata={"endpoint": endpoint, "status_code": status_code}
        )
        
        # Track error rate
        is_error = status_code >= 400
        await self.record_metric(
            MetricType.PERFORMANCE,
            "error_rate",
            1 if is_error else 0,
            metadata={"endpoint": endpoint, "status_code": status_code}
        )
    
    async def get_real_time_data(self) -> Dict[str, Any]:
        """Get current real-time analytics data"""
        now = datetime.now()
        
        # Get recent metrics (last 5 minutes)
        recent_cutoff = now - timedelta(minutes=5)
        recent_metrics = {}
        
        for name, metrics in self.metrics_store.items():
            recent = [m for m in metrics if m.timestamp > recent_cutoff]
            if recent:
                recent_metrics[name] = {
                    "count": len(recent),
                    "avg_value": sum(m.value for m in recent) / len(recent),
                    "latest_value": recent[-1].value,
                    "latest_timestamp": recent[-1].timestamp.isoformat()
                }
        
        return {
            "timestamp": now.isoformat(),
            "recent_metrics": recent_metrics,
            "performance": {
                "avg_response_time": sum(self.performance_metrics.response_times) / len(self.performance_metrics.response_times) if self.performance_metrics.response_times else 0,
                "current_throughput": list(self.performance_metrics.throughput)[-1] if self.performance_metrics.throughput else 0,
                "error_rate": sum(self.performance_metrics.error_rates) / len(self.performance_metrics.error_rates) if self.performance_metrics.error_rates else 0
            },
            "usage": {
                "active_sessions": len(self.usage_metrics.user_sessions),
                "total_api_calls": sum(self.usage_metrics.api_calls.values()),
                "top_endpoints": sorted(self.usage_metrics.api_calls.items(), key=lambda x: x[1], reverse=True)[:5]
            },
            "system": {
                "uptime_hours": (now - self.start_time).total_seconds() / 3600,
                "monitoring_active": self.real_time_monitor.monitoring_active,
                "metrics_count": sum(len(metrics) for metrics in self.metrics_store.values())
            }
        }


# Global analytics engine instance
analytics_engine = AnalyticsEngine()