# Troubleshooting Guide

Common issues and solutions for the Multi-Agent Research System.

## 🚨 Quick Diagnostics

### System Health Check
```bash
# Check if server is running
curl http://localhost:8080/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-06-27T12:00:00Z",
  "components": {
    "api": "healthy",
    "cache": "healthy",
    "ai": "healthy"
  }
}
```

### Component Status
```bash
# Check all system components
curl http://localhost:8080/api/v1/dashboard/system-health

# Test specific endpoints
python test_api_endpoints.py
```

## 🔧 Installation Issues

### Python Version Problems

**Issue**: `Python version not supported`
```bash
# Check Python version
python --version

# Should be 3.8 or higher
# Install correct version:
sudo apt update
sudo apt install python3.11 python3.11-pip
python3.11 -m pip install -r requirements.txt
```

### Dependency Installation Failures

**Issue**: `pip install fails`
```bash
# Clear pip cache
pip cache purge

# Upgrade pip
python -m pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v

# Alternative: Use conda
conda create -n multi-agent python=3.11
conda activate multi-agent
pip install -r requirements.txt
```

### Permission Issues

**Issue**: `Permission denied`
```bash
# Fix file permissions
chmod +x setup.sh
chmod +x run.py

# Fix directory permissions
sudo chown -R $USER:$USER .

# Use virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🚀 Server Startup Issues

### Port Already in Use

**Issue**: `Address already in use`
```bash
# Find process using port 8080
lsof -i :8080

# Kill the process
kill -9 <PID>

# Or use different port
API_PORT=8081 python run.py
```

### Environment Variables Not Set

**Issue**: `Environment variable not found`
```bash
# Check current environment
env | grep API

# Create .env file
cp .env.example .env

# Edit .env file
nano .env

# Source environment
source .env
```

### Import Errors

**Issue**: `ModuleNotFoundError`
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Install missing dependencies
pip install -r requirements.txt

# Check for conflicting packages
pip list | grep -E "(fastapi|uvicorn|pydantic)"

# Reinstall if needed
pip uninstall fastapi uvicorn pydantic
pip install fastapi uvicorn pydantic
```

## 📡 API Issues

### 404 Not Found

**Issue**: `Endpoint not found`
```bash
# Check available endpoints
curl http://localhost:8080/docs

# Verify correct URL format
curl http://localhost:8080/api/v1/repositories/list

# Check server logs
tail -f server.log
```

### 422 Validation Error

**Issue**: `Request validation failed`
```bash
# Check request format
curl -X POST http://localhost:8080/api/v1/repositories/analyze \
  -H "Content-Type: application/json" \
  -d '{"path": "/valid/path/to/repository"}'

# Validate JSON format
echo '{"path": "/test"}' | jq .

# Check API documentation
open http://localhost:8080/docs
```

### 500 Internal Server Error

**Issue**: `Server error`
```bash
# Check server logs
tail -f server.log

# Enable debug mode
LOG_LEVEL=DEBUG python run.py

# Check system resources
free -h
df -h
```

## 🤖 AI Analysis Issues

### API Key Problems

**Issue**: `Invalid API key`
```bash
# Check API key format
echo $ANTHROPIC_API_KEY | wc -c
# Should be around 100 characters

# Test API key
curl -H "Authorization: Bearer $ANTHROPIC_API_KEY" \
  https://api.anthropic.com/v1/messages

# Use demo mode for testing
python demo_working_features.py
```

### Model Not Available

**Issue**: `Model not found`
```bash
# Check available models
curl http://localhost:8080/api/v1/models/available

# Test with different model
curl -X POST http://localhost:8080/api/v1/ai/analyze-code \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(\"hello\")",
    "language": "python",
    "model": "claude-3-haiku-20240307"
  }'
```

### Rate Limiting

**Issue**: `Rate limit exceeded`
```bash
# Check rate limit status
curl -I http://localhost:8080/api/v1/ai/analyze-code

# Wait and retry
sleep 60

# Use batch processing
curl -X POST http://localhost:8080/api/v1/repositories/batch-analyze
```

## 💾 Cache Issues

### Redis Connection Problems

**Issue**: `Redis connection failed`
```bash
# Check Redis status
redis-cli ping

# Start Redis
docker run -d -p 6379:6379 redis:alpine

# Test without Redis
ENABLE_REDIS=false python run.py

# Check Redis logs
docker logs <redis-container-id>
```

### Cache Performance Issues

**Issue**: `Slow cache responses`
```bash
# Check cache statistics
curl http://localhost:8080/api/v1/cache/stats

# Clear cache
curl -X DELETE http://localhost:8080/api/v1/cache/clear

# Optimize cache settings
CACHE_TTL=1800  # 30 minutes
MAX_CACHE_SIZE=1000
```

## 📊 Performance Issues

### High Memory Usage

**Issue**: `Out of memory errors`
```bash
# Check memory usage
free -h
ps aux | grep python

# Optimize settings
MAX_BATCH_SIZE=5
CACHE_TTL=900
ENABLE_MONITORING=false

# Use memory profiling
pip install memory-profiler
python -m memory_profiler run.py
```

### Slow Analysis

**Issue**: `Analysis takes too long`
```bash
# Check system resources
top
htop

# Enable caching
ENABLE_REDIS=true
REDIS_URL=redis://localhost:6379

# Reduce analysis scope
curl -X POST http://localhost:8080/api/v1/repositories/analyze \
  -d '{"path": "/repo", "analysis_types": ["basic"]}'
```

### Database Connection Issues

**Issue**: `Database connection timeout`
```bash
# Check connection pool
curl http://localhost:8080/api/v1/dashboard/system-health

# Restart application
pkill -f "python run.py"
python run.py

# Check disk space
df -h
```

## 🔒 Security Issues

### CORS Errors

**Issue**: `CORS policy blocked`
```bash
# Check CORS configuration
curl -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: X-Requested-With" \
  -X OPTIONS http://localhost:8080/api/v1/repositories/list

# Configure CORS in .env
ALLOWED_ORIGINS=http://localhost:3000,https://your-domain.com
```

### SSL Certificate Issues

**Issue**: `SSL certificate verification failed`
```bash
# Check certificate
openssl x509 -in cert.pem -text -noout

# Test without SSL verification (development only)
curl -k https://localhost:8080/health

# Update certificates
certbot renew
```

## 🐳 Docker Issues

### Container Won't Start

**Issue**: `Docker container exits immediately`
```bash
# Check container logs
docker logs <container-id>

# Run interactively
docker run -it multi-agent-researcher /bin/bash

# Check Dockerfile
docker build -t multi-agent-researcher . --no-cache
```

### Volume Mount Issues

**Issue**: `File not found in container`
```bash
# Check volume mounts
docker inspect <container-id> | grep Mounts

# Fix volume paths
docker run -v $(pwd):/app multi-agent-researcher

# Check file permissions
ls -la /path/to/mounted/files
```

## 🔍 Debugging Tools

### Enable Debug Logging

```bash
# Set debug level
LOG_LEVEL=DEBUG python run.py

# Check specific component
curl http://localhost:8080/api/v1/debug/logs?component=ai

# Enable verbose output
VERBOSE=true python run.py
```

### Performance Profiling

```bash
# Install profiling tools
pip install py-spy

# Profile running application
py-spy top --pid <python-pid>

# Generate flame graph
py-spy record -o profile.svg --pid <python-pid>
```

### Network Debugging

```bash
# Check network connectivity
curl -v http://localhost:8080/health

# Test DNS resolution
nslookup api.anthropic.com

# Check firewall rules
sudo ufw status
```

## 📋 Diagnostic Commands

### System Information
```bash
# System info
uname -a
python --version
pip list

# Resource usage
free -h
df -h
ps aux | grep python
```

### Application Status
```bash
# Health check
curl http://localhost:8080/health

# System metrics
curl http://localhost:8080/api/v1/dashboard/system-health

# Component status
python test_api_endpoints.py
```

### Log Analysis
```bash
# View recent logs
tail -f server.log

# Search for errors
grep -i error server.log

# Filter by timestamp
grep "2025-06-27" server.log
```

## 🆘 Getting Help

### Self-Service Resources

1. **Check Documentation**: [Complete Documentation](../README.md)
2. **API Reference**: [API Documentation](../api/complete-reference.md)
3. **Run Diagnostics**: `python test_api_endpoints.py`
4. **Demo Mode**: `python demo_working_features.py`

### Community Support

1. **GitHub Issues**: [Report bugs and issues](https://github.com/popoloni/multi-agent-researcher/issues)
2. **GitHub Discussions**: [Ask questions and share ideas](https://github.com/popoloni/multi-agent-researcher/discussions)
3. **Documentation**: [Browse guides and tutorials](../guides/)

### Issue Reporting

When reporting issues, please include:

```bash
# System information
python --version
pip list | grep -E "(fastapi|uvicorn|anthropic)"
uname -a

# Error logs
tail -n 50 server.log

# Configuration (remove sensitive data)
cat .env | grep -v "API_KEY"

# Test results
python test_api_endpoints.py
```

### Emergency Recovery

**Complete System Reset:**
```bash
# Stop all services
pkill -f "python run.py"
docker-compose down

# Clear cache and temporary files
rm -rf __pycache__/
rm -rf .pytest_cache/
rm -f server.log

# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Restart system
python run.py
```

---

**Still having issues?** Open an issue on [GitHub](https://github.com/popoloni/multi-agent-researcher/issues) with detailed information about your problem.