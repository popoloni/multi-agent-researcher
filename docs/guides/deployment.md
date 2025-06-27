# Deployment Guide

Complete guide for deploying the Multi-Agent Research System in production environments.

## 🐳 Docker Deployment (Recommended)

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY .env.example .env

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  multi-agent-researcher:
    build: .
    ports:
      - "8080:8080"
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

### Build and Deploy
```bash
# Build the image
docker build -t multi-agent-researcher .

# Run with Docker Compose
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f multi-agent-researcher
```

## 🖥️ Traditional Server Deployment

### System Requirements
- **OS**: Ubuntu 20.04+ / CentOS 8+ / RHEL 8+
- **CPU**: 4+ cores
- **RAM**: 8GB+ (16GB recommended)
- **Storage**: 50GB+ SSD
- **Network**: 1Gbps+ connection

### Installation Script
```bash
#!/bin/bash
# production-install.sh

set -e

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Install system dependencies
sudo apt install -y \
    git \
    nginx \
    redis-server \
    build-essential \
    curl \
    supervisor

# Create application user
sudo useradd -m -s /bin/bash research
sudo usermod -aG sudo research

# Clone repository
sudo -u research git clone https://github.com/popoloni/multi-agent-researcher.git /home/research/app
cd /home/research/app

# Create virtual environment
sudo -u research python3.11 -m venv venv
sudo -u research ./venv/bin/pip install -r requirements.txt

# Configure environment
sudo -u research cp .env.example .env
sudo -u research sed -i 's/REDIS_URL=.*/REDIS_URL=redis:\/\/localhost:6379/' .env

# Set up systemd service
sudo tee /etc/systemd/system/multi-agent-researcher.service > /dev/null <<EOF
[Unit]
Description=Multi-Agent Research System
After=network.target redis.service

[Service]
Type=exec
User=research
Group=research
WorkingDirectory=/home/research/app
Environment=PATH=/home/research/app/venv/bin
ExecStart=/home/research/app/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8080
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable multi-agent-researcher
sudo systemctl start multi-agent-researcher
sudo systemctl enable redis-server
sudo systemctl start redis-server

echo "Installation complete! Service running on port 8080"
```

## ☁️ Cloud Platform Deployment

### AWS ECS
```yaml
# ecs-task-definition.json
{
  "family": "multi-agent-researcher",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "multi-agent-researcher",
      "image": "your-account.dkr.ecr.region.amazonaws.com/multi-agent-researcher:latest",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "REDIS_URL",
          "value": "redis://your-elasticache-endpoint:6379"
        }
      ]
    }
  ]
}
```

### Google Cloud Run
```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/multi-agent-researcher', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/multi-agent-researcher']
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'multi-agent-researcher'
      - '--image'
      - 'gcr.io/$PROJECT_ID/multi-agent-researcher'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
```

## ⚙️ Kubernetes Deployment

### Deployment Manifest
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: multi-agent-researcher
spec:
  replicas: 3
  selector:
    matchLabels:
      app: multi-agent-researcher
  template:
    metadata:
      labels:
        app: multi-agent-researcher
    spec:
      containers:
      - name: multi-agent-researcher
        image: multi-agent-researcher:latest
        ports:
        - containerPort: 8080
        env:
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
```

### Service Manifest
```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: multi-agent-researcher-service
spec:
  selector:
    app: multi-agent-researcher
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: ClusterIP
```

### Deploy to Kubernetes
```bash
# Apply manifests
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# Check deployment status
kubectl get pods
kubectl get services

# View logs
kubectl logs -f deployment/multi-agent-researcher
```

## 🔧 Production Configuration

### Environment Variables
```bash
# Production environment variables
export REDIS_URL="redis://redis-host:6379"
export SECRET_KEY="your-super-secret-key"
export ENVIRONMENT="production"
export LOG_LEVEL="INFO"
export WORKERS=4
export MAX_CONNECTIONS=100
export CACHE_TTL=1800
```

## 📊 Monitoring and Health Checks

### Health Check Endpoint
```bash
# Check system health
curl http://localhost:8080/health

# Expected response
{
  "status": "healthy",
  "timestamp": "2025-06-27T12:00:00Z",
  "version": "1.0.0"
}
```

### Performance Monitoring
```bash
# System metrics
curl http://localhost:8080/kenobi/analytics/metrics

# Cache statistics
curl http://localhost:8080/kenobi/cache/stats
```

## 🔄 Backup and Recovery

### Database Backup
```bash
#!/bin/bash
# backup-redis.sh

BACKUP_DIR="/backups/redis"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Save Redis data
redis-cli BGSAVE

# Copy dump file
cp /var/lib/redis/dump.rdb $BACKUP_DIR/dump_$DATE.rdb

echo "Redis backup completed: $BACKUP_DIR/dump_$DATE.rdb"
```

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Environment variables configured
- [ ] SSL certificates installed (if applicable)
- [ ] Firewall rules configured
- [ ] Monitoring setup complete
- [ ] Backup procedures tested

### Post-Deployment
- [ ] Health checks passing
- [ ] Performance metrics baseline established
- [ ] Log aggregation working
- [ ] Security scan completed
- [ ] Documentation updated

## 🔗 Related Documentation

- [Quick Start Guide](./quick-start.md)
- [API Documentation](../api/README.md)
- [Architecture Overview](../architecture/README.md)