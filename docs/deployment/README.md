# Deployment Documentation

Production deployment guides and operational procedures for the Multi-Agent Researcher system.

## 📋 Deployment Overview

The Multi-Agent Researcher is production-ready with comprehensive deployment options including local development, containerized deployment, and cloud-native solutions.

## 📚 Documentation Files

### [Deployment Instructions](./DEPLOYMENT_INSTRUCTIONS.md)
Complete deployment guide with step-by-step instructions for various environments.

**Covers:**
- **Local Development**: Quick setup for development
- **Docker Deployment**: Containerized deployment
- **Production Setup**: Production-ready configuration
- **Environment Configuration**: Environment variables and settings
- **Monitoring Setup**: Health checks and monitoring
- **Troubleshooting**: Common issues and solutions

## 🚀 Quick Deployment

### Local Development
```bash
# Clone repository
git clone https://github.com/popoloni/multi-agent-researcher.git
cd multi-agent-researcher

# Install dependencies
pip install -r requirements.txt

# Start services
python main.py
```

### Docker Deployment
```bash
# Build image
docker build -t multi-agent-researcher .

# Run container
docker run -p 8080:8080 multi-agent-researcher
```

### Production Deployment
```bash
# Environment setup
export ENVIRONMENT=production
export REDIS_URL=redis://localhost:6379
export OLLAMA_HOST=http://localhost:11434

# Start with production settings
python main.py --host 0.0.0.0 --port 8080
```

## 🔧 Configuration

### Environment Variables
```bash
# Core Settings
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8080

# AI Services
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2

# Database
REDIS_URL=redis://localhost:6379
CHROMA_PERSIST_DIRECTORY=./chroma_db

# Monitoring
LOG_LEVEL=INFO
METRICS_ENABLED=true
```

### Service Dependencies
- **Ollama**: AI model service (port 11434)
- **Redis**: Caching service (port 6379)
- **ChromaDB**: Vector database (embedded)

## 📊 Production Architecture

### High Availability Setup
```
Load Balancer
├── Multi-Agent Researcher Instance 1
├── Multi-Agent Researcher Instance 2
└── Multi-Agent Researcher Instance 3

Shared Services
├── Redis Cluster
├── Ollama Service
└── Monitoring Stack
```

### Scalability Considerations
- **Horizontal Scaling**: Multiple application instances
- **Database Scaling**: Redis clustering
- **Load Balancing**: Nginx or cloud load balancer
- **Monitoring**: Prometheus + Grafana

## 🔍 Monitoring & Health Checks

### Health Endpoints
- **System Health**: `GET /kenobi/status`
- **Ollama Status**: `GET /ollama/status`
- **Cache Stats**: `GET /kenobi/cache/stats`
- **Analytics**: `GET /kenobi/analytics/metrics`

### Monitoring Metrics
- **Response Times**: API endpoint performance
- **Error Rates**: System reliability metrics
- **Cache Performance**: Hit rates and efficiency
- **Resource Usage**: CPU, memory, disk usage

## 🔒 Security Configuration

### Production Security
- **HTTPS Only**: SSL/TLS encryption
- **API Authentication**: JWT or API key authentication
- **Rate Limiting**: Request throttling
- **Input Validation**: Comprehensive input sanitization
- **CORS Configuration**: Proper cross-origin settings

### Security Headers
```python
# Security middleware configuration
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000"
}
```

## 🐛 Troubleshooting

### Common Issues

#### Service Connection Issues
```bash
# Check Ollama service
curl http://localhost:11434/api/tags

# Check Redis connection
redis-cli ping

# Check application health
curl http://localhost:8080/kenobi/status
```

#### Performance Issues
```bash
# Check cache performance
curl http://localhost:8080/kenobi/cache/stats

# Monitor analytics
curl http://localhost:8080/kenobi/analytics/metrics

# Check system resources
htop
```

### Log Analysis
```bash
# Application logs
tail -f logs/application.log

# Error logs
grep ERROR logs/application.log

# Performance logs
grep "slow query" logs/application.log
```

## 📋 Operational Procedures

### Backup & Recovery
- **Database Backup**: Regular Redis snapshots
- **Vector Database**: ChromaDB persistence backup
- **Configuration Backup**: Environment and config files
- **Code Repository**: Git repository backup

### Updates & Maintenance
- **Rolling Updates**: Zero-downtime deployment
- **Database Migrations**: Schema update procedures
- **Dependency Updates**: Regular security updates
- **Performance Tuning**: Optimization procedures

### Disaster Recovery
- **Service Recovery**: Automated service restart
- **Data Recovery**: Backup restoration procedures
- **Failover**: Multi-region deployment
- **Monitoring**: Automated alerting

---

**Deployment Status**: Production Ready  
**Documentation Version**: v1.0.0  
**Last Updated**: June 27, 2025