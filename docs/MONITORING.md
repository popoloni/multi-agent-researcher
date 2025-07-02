# Production Monitoring System

The Multi-Agent Researcher includes a comprehensive production monitoring system that provides real-time insights into system performance, health checks, and optimization recommendations.

## Features

### 1. System Performance Monitoring
- **CPU Usage**: Real-time CPU utilization tracking
- **Memory Usage**: Memory consumption monitoring
- **Disk Usage**: Storage utilization tracking
- **Response Times**: API response time metrics
- **Throughput**: Requests per minute tracking
- **Error Rates**: Error percentage monitoring

### 2. Service Health Checks
- **Database Health**: Connection status and query performance
- **Vector Store Health**: Document indexing and search latency
- **AI Engine Health**: Model loading status and inference times
- **Overall System Health**: Comprehensive health status

### 3. RAG System Metrics
- **Query Performance**: Response time tracking
- **Relevance Scoring**: Quality metrics for search results
- **Context Retrieval**: Time spent retrieving relevant context
- **Vector Search**: Search operation performance
- **Generation Time**: AI response generation metrics

### 4. Optimization Recommendations
- **Performance Alerts**: Automatic detection of performance issues
- **Resource Optimization**: Recommendations for CPU, memory, and disk usage
- **Caching Strategies**: Suggestions for improving response times
- **Scaling Recommendations**: Guidance for horizontal and vertical scaling

## API Endpoints

### Health Check
```bash
GET /api/monitoring/health
```
Returns comprehensive health status of all system components.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-02T07:34:23.492012",
  "uptime": "0:02:37.135809",
  "checks": {
    "system": {
      "cpu_usage": {"value": 35.1, "status": "ok"},
      "memory_usage": {"value": 30.8, "status": "ok"},
      "disk_usage": {"value": 10.4, "status": "ok"}
    },
    "services": {
      "database": {"status": "ok", "response_time": 0.05},
      "vector_store": {"status": "ok", "search_latency": 0.1},
      "ai_engine": {"status": "ok", "model_loaded": true}
    }
  }
}
```

### System Metrics
```bash
GET /api/monitoring/metrics
```
Returns current system performance metrics.

**Response:**
```json
{
  "status": "success",
  "metrics": {
    "timestamp": "2025-07-02T07:34:35.314374",
    "cpu_usage": 32.8,
    "memory_usage": 30.8,
    "disk_usage": 10.4,
    "response_time": 0.0,
    "active_connections": 42,
    "error_rate": 0.0,
    "throughput": 0.0
  }
}
```

### Performance Summary
```bash
GET /api/monitoring/performance?hours=24
```
Returns performance summary for the specified time period.

**Parameters:**
- `hours` (optional): Time period in hours (default: 24)

### Optimization Recommendations
```bash
GET /api/monitoring/recommendations
```
Returns optimization recommendations based on current metrics.

**Response:**
```json
{
  "status": "success",
  "recommendations": [
    {
      "type": "performance",
      "priority": "medium",
      "title": "High CPU Usage Detected",
      "description": "CPU usage is at 85.2%",
      "recommendations": [
        "Consider scaling horizontally",
        "Optimize database queries",
        "Implement request caching"
      ]
    }
  ]
}
```

### Monitoring Dashboard
```bash
GET /api/monitoring/dashboard
```
Returns comprehensive monitoring dashboard data including current metrics, performance summary, health status, and recommendations.

## Alert Thresholds

The monitoring system uses the following default alert thresholds:

- **CPU Usage**: Warning at 80%, Critical at 90%
- **Memory Usage**: Warning at 85%, Critical at 95%
- **Disk Usage**: Warning at 90%, Critical at 95%
- **Response Time**: Warning at 5 seconds
- **Error Rate**: Warning at 5%

## Integration

### Programmatic Access
```python
from app.services.monitoring_service import monitoring_service

# Collect system metrics
metrics = await monitoring_service.collect_system_metrics()

# Check health status
health = monitoring_service.check_health()

# Get optimization recommendations
recommendations = monitoring_service.get_optimization_recommendations()

# Record custom metrics
monitoring_service.record_request(response_time=1.2, error=False)
monitoring_service.record_error("Database connection failed", {"query": "SELECT * FROM repos"})
```

### Custom Metrics
You can extend the monitoring system by adding custom metrics:

```python
# Record RAG metrics
await monitoring_service.collect_rag_metrics(
    query_time=2.1,
    relevance_score=0.85
)

# Record database metrics
await monitoring_service.collect_database_metrics(query_time=0.05)
```

## Production Deployment

### Monitoring Dashboard
For production deployments, consider integrating with external monitoring solutions:

- **Grafana**: Create dashboards using the monitoring API endpoints
- **Prometheus**: Export metrics in Prometheus format
- **DataDog**: Send metrics to DataDog for advanced analytics
- **New Relic**: Integrate with New Relic for APM monitoring

### Alerting
Set up alerting based on the health check endpoint:

```bash
# Example health check script for cron
#!/bin/bash
HEALTH=$(curl -s http://localhost:12000/api/monitoring/health | jq -r '.status')
if [ "$HEALTH" != "healthy" ]; then
    echo "System unhealthy: $HEALTH" | mail -s "Alert: System Health Issue" admin@example.com
fi
```

### Log Aggregation
The monitoring service logs important events. Configure log aggregation:

- **ELK Stack**: Elasticsearch, Logstash, and Kibana
- **Fluentd**: Log collection and forwarding
- **Splunk**: Enterprise log management

## Performance Optimization

Based on monitoring data, the system provides automatic optimization recommendations:

### CPU Optimization
- Horizontal scaling suggestions
- Database query optimization
- Caching implementation
- Async processing recommendations

### Memory Optimization
- Memory leak detection
- Caching strategy improvements
- Vector storage optimization
- Memory scaling recommendations

### Response Time Optimization
- Response caching
- Database index optimization
- CDN recommendations
- Async processing suggestions

## Troubleshooting

### Common Issues

1. **High CPU Usage**
   - Check for inefficient queries
   - Review vector search operations
   - Consider scaling resources

2. **High Memory Usage**
   - Monitor for memory leaks
   - Optimize vector storage
   - Review caching strategies

3. **Slow Response Times**
   - Check database performance
   - Review API endpoint efficiency
   - Consider caching implementation

### Debug Mode
Enable debug logging for detailed monitoring information:

```python
import logging
logging.getLogger('app.services.monitoring_service').setLevel(logging.DEBUG)
```

## Security Considerations

- Monitor access to monitoring endpoints
- Implement authentication for production deployments
- Sanitize sensitive data in metrics
- Use HTTPS for monitoring API access
- Regularly review monitoring logs for security events

## Future Enhancements

- Real-time alerting system
- Machine learning-based anomaly detection
- Predictive scaling recommendations
- Integration with cloud monitoring services
- Custom metric collection framework