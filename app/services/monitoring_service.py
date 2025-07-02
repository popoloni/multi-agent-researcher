"""
Production Monitoring Service

Provides comprehensive monitoring and optimization for the Multi-Agent Researcher system.
Includes performance metrics, health checks, and optimization recommendations.
"""

import time
import psutil
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    response_time: float
    active_connections: int
    error_rate: float
    throughput: float

@dataclass
class RAGMetrics:
    """RAG system quality metrics"""
    timestamp: datetime
    query_count: int
    avg_response_time: float
    relevance_score: float
    context_retrieval_time: float
    vector_search_time: float
    generation_time: float

@dataclass
class DatabaseMetrics:
    """Database performance metrics"""
    timestamp: datetime
    query_count: int
    avg_query_time: float
    connection_pool_usage: float
    cache_hit_rate: float
    index_efficiency: float

class MonitoringService:
    """Production monitoring and optimization service"""
    
    def __init__(self):
        self.performance_history: deque = deque(maxlen=1000)
        self.rag_history: deque = deque(maxlen=1000)
        self.database_history: deque = deque(maxlen=1000)
        self.error_log: deque = deque(maxlen=500)
        self.alert_thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'disk_usage': 90.0,
            'response_time': 5.0,
            'error_rate': 5.0
        }
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
        
    async def collect_system_metrics(self) -> PerformanceMetrics:
        """Collect system performance metrics"""
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Calculate response time (mock for now, should be integrated with actual requests)
            response_time = self._calculate_avg_response_time()
            
            # Calculate error rate
            error_rate = (self.error_count / max(self.request_count, 1)) * 100
            
            # Calculate throughput (requests per minute)
            uptime_minutes = (datetime.now() - self.start_time).total_seconds() / 60
            throughput = self.request_count / max(uptime_minutes, 1)
            
            metrics = PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                disk_usage=disk.percent,
                response_time=response_time,
                active_connections=self._get_active_connections(),
                error_rate=error_rate,
                throughput=throughput
            )
            
            self.performance_history.append(metrics)
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            raise
    
    async def collect_rag_metrics(self, query_time: float, relevance_score: float = 0.8) -> RAGMetrics:
        """Collect RAG system metrics"""
        try:
            metrics = RAGMetrics(
                timestamp=datetime.now(),
                query_count=1,
                avg_response_time=query_time,
                relevance_score=relevance_score,
                context_retrieval_time=query_time * 0.3,  # Estimated
                vector_search_time=query_time * 0.2,      # Estimated
                generation_time=query_time * 0.5          # Estimated
            )
            
            self.rag_history.append(metrics)
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting RAG metrics: {e}")
            raise
    
    async def collect_database_metrics(self, query_time: float) -> DatabaseMetrics:
        """Collect database performance metrics"""
        try:
            metrics = DatabaseMetrics(
                timestamp=datetime.now(),
                query_count=1,
                avg_query_time=query_time,
                connection_pool_usage=self._get_connection_pool_usage(),
                cache_hit_rate=self._get_cache_hit_rate(),
                index_efficiency=self._get_index_efficiency()
            )
            
            self.database_history.append(metrics)
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting database metrics: {e}")
            raise
    
    def check_health(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        try:
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'uptime': str(datetime.now() - self.start_time),
                'checks': {}
            }
            
            # System health checks
            latest_metrics = self.performance_history[-1] if self.performance_history else None
            if latest_metrics:
                health_status['checks']['system'] = {
                    'cpu_usage': {
                        'value': latest_metrics.cpu_usage,
                        'status': 'ok' if latest_metrics.cpu_usage < self.alert_thresholds['cpu_usage'] else 'warning'
                    },
                    'memory_usage': {
                        'value': latest_metrics.memory_usage,
                        'status': 'ok' if latest_metrics.memory_usage < self.alert_thresholds['memory_usage'] else 'warning'
                    },
                    'disk_usage': {
                        'value': latest_metrics.disk_usage,
                        'status': 'ok' if latest_metrics.disk_usage < self.alert_thresholds['disk_usage'] else 'warning'
                    }
                }
            
            # Service health checks
            health_status['checks']['services'] = {
                'database': self._check_database_health(),
                'vector_store': self._check_vector_store_health(),
                'ai_engine': self._check_ai_engine_health()
            }
            
            # Determine overall status
            if any(check.get('status') == 'error' for check in health_status['checks'].get('services', {}).values()):
                health_status['status'] = 'unhealthy'
            elif any(check.get('status') == 'warning' for check in health_status['checks'].get('system', {}).values()):
                health_status['status'] = 'degraded'
            
            return health_status
            
        except Exception as e:
            logger.error(f"Error during health check: {e}")
            return {
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for the specified time period"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_metrics = [m for m in self.performance_history if m.timestamp > cutoff_time]
            
            if not recent_metrics:
                return {'error': 'No metrics available for the specified period'}
            
            return {
                'period_hours': hours,
                'total_requests': self.request_count,
                'total_errors': self.error_count,
                'avg_cpu_usage': sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics),
                'avg_memory_usage': sum(m.memory_usage for m in recent_metrics) / len(recent_metrics),
                'avg_response_time': sum(m.response_time for m in recent_metrics) / len(recent_metrics),
                'peak_cpu_usage': max(m.cpu_usage for m in recent_metrics),
                'peak_memory_usage': max(m.memory_usage for m in recent_metrics),
                'error_rate': (self.error_count / max(self.request_count, 1)) * 100,
                'throughput': sum(m.throughput for m in recent_metrics) / len(recent_metrics)
            }
            
        except Exception as e:
            logger.error(f"Error generating performance summary: {e}")
            return {'error': str(e)}
    
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Generate optimization recommendations based on metrics"""
        recommendations = []
        
        try:
            if not self.performance_history:
                return recommendations
            
            latest_metrics = self.performance_history[-1]
            
            # CPU optimization
            if latest_metrics.cpu_usage > 70:
                recommendations.append({
                    'type': 'performance',
                    'priority': 'high' if latest_metrics.cpu_usage > 85 else 'medium',
                    'title': 'High CPU Usage Detected',
                    'description': f'CPU usage is at {latest_metrics.cpu_usage:.1f}%',
                    'recommendations': [
                        'Consider scaling horizontally',
                        'Optimize database queries',
                        'Implement request caching',
                        'Review CPU-intensive operations'
                    ]
                })
            
            # Memory optimization
            if latest_metrics.memory_usage > 75:
                recommendations.append({
                    'type': 'performance',
                    'priority': 'high' if latest_metrics.memory_usage > 90 else 'medium',
                    'title': 'High Memory Usage Detected',
                    'description': f'Memory usage is at {latest_metrics.memory_usage:.1f}%',
                    'recommendations': [
                        'Implement memory caching strategies',
                        'Review memory leaks',
                        'Optimize vector storage',
                        'Consider memory scaling'
                    ]
                })
            
            # Response time optimization
            if latest_metrics.response_time > 3.0:
                recommendations.append({
                    'type': 'performance',
                    'priority': 'medium',
                    'title': 'Slow Response Times',
                    'description': f'Average response time is {latest_metrics.response_time:.2f}s',
                    'recommendations': [
                        'Implement response caching',
                        'Optimize database indexes',
                        'Use async processing for heavy operations',
                        'Consider CDN for static content'
                    ]
                })
            
            # RAG optimization
            if self.rag_history:
                avg_rag_time = sum(m.avg_response_time for m in list(self.rag_history)[-10:]) / min(len(self.rag_history), 10)
                if avg_rag_time > 2.0:
                    recommendations.append({
                        'type': 'rag',
                        'priority': 'medium',
                        'title': 'RAG Performance Optimization',
                        'description': f'RAG response time is {avg_rag_time:.2f}s',
                        'recommendations': [
                            'Optimize vector search parameters',
                            'Implement semantic caching',
                            'Fine-tune embedding models',
                            'Optimize context retrieval'
                        ]
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating optimization recommendations: {e}")
            return []
    
    def record_request(self, response_time: float, error: bool = False):
        """Record a request for metrics tracking"""
        self.request_count += 1
        if error:
            self.error_count += 1
    
    def record_error(self, error: str, context: Dict[str, Any] = None):
        """Record an error for monitoring"""
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'error': error,
            'context': context or {}
        }
        self.error_log.append(error_entry)
    
    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time from recent metrics"""
        if not self.performance_history:
            return 0.0
        recent = list(self.performance_history)[-10:]
        return sum(m.response_time for m in recent) / len(recent) if recent else 0.0
    
    def _get_active_connections(self) -> int:
        """Get number of active connections (mock implementation)"""
        return len(psutil.net_connections())
    
    def _get_connection_pool_usage(self) -> float:
        """Get database connection pool usage (mock implementation)"""
        return 45.0  # Mock value
    
    def _get_cache_hit_rate(self) -> float:
        """Get cache hit rate (mock implementation)"""
        return 85.0  # Mock value
    
    def _get_index_efficiency(self) -> float:
        """Get database index efficiency (mock implementation)"""
        return 92.0  # Mock value
    
    def _check_database_health(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            # Mock database health check
            return {
                'status': 'ok',
                'response_time': 0.05,
                'connections': 5
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _check_vector_store_health(self) -> Dict[str, Any]:
        """Check vector store health"""
        try:
            # Mock vector store health check
            return {
                'status': 'ok',
                'indexed_documents': 1000,
                'search_latency': 0.1
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _check_ai_engine_health(self) -> Dict[str, Any]:
        """Check AI engine health"""
        try:
            # Mock AI engine health check
            return {
                'status': 'ok',
                'model_loaded': True,
                'avg_inference_time': 1.2
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

# Global monitoring service instance
monitoring_service = MonitoringService()