# Deployment & Production Guide

## Development Deployment (Current)

### Local Development

```bash
# 1. Setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 2. Load real data
python setup.py

# 3. Run agent
python cssa_agent.py

# 4. Test
python test_agent.py
pytest -q
```

Agent runs on `http://127.0.0.1:5000` with Flask development server (debug mode enabled).

### Docker Development

```bash
# Build local image
docker build -t cssa-agent:dev .

# Run container
docker run -p 5000:5000 \
  -v %CD%:/app \
  -e FLASK_ENV=development \
  cssa-agent:dev

# Or with docker-compose
docker-compose up
```

## Production Deployment

### Configuration

Create `.env` or set environment variables:

```bash
FLASK_ENV=production
DEBUG=False
FLASK_APP=cssa_agent:app
WORKERS=4  # For Gunicorn
```

### Docker (Recommended)

```bash
# Build production image
docker build -t cssa-agent:1.0 .

# Run with Gunicorn (multi-worker)
docker run -d \
  --name cssa-agent \
  -p 5000:5000 \
  -e FLASK_ENV=production \
  -v cssa-memory:/app/data \
  cssa-agent:1.0

# Scale with docker-compose
docker-compose -f docker-compose.prod.yml up -d --scale web=3
```

### Kubernetes (Future)

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cssa-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cssa-agent
  template:
    metadata:
      labels:
        app: cssa-agent
    spec:
      containers:
      - name: agent
        image: cssa-agent:1.0
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: "production"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 10
```

### Cloud Deployment (AWS, GCP, Azure)

**AWS ECS:**
```bash
# Push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker tag cssa-agent:1.0 <account>.dkr.ecr.us-east-1.amazonaws.com/cssa-agent:1.0
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/cssa-agent:1.0

# Create ECS service with Fargate
```

**Google Cloud Run:**
```bash
gcloud run deploy cssa-agent \
  --source . \
  --platform managed \
  --region us-central1 \
  --memory 512Mi \
  --timeout 300
```

### WSGI Server (Gunicorn)

For production on Linux/Mac without Docker:

```bash
# Install gunicorn (already in requirements.txt)
pip install gunicorn

# Run with 4 worker processes
gunicorn -w 4 -b 0.0.0.0:5000 cssa_agent:app

# With environment
FLASK_ENV=production gunicorn \
  -w 4 \
  -b 0.0.0.0:5000 \
  --access-logfile - \
  --error-logfile - \
  cssa_agent:app
```

## Load Balancing & Reverse Proxy

### Nginx

```nginx
upstream cssa_backend {
  server localhost:5001;
  server localhost:5002;
  server localhost:5003;
}

server {
  listen 80;
  server_name api.example.com;

  location / {
    proxy_pass http://cssa_backend;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }

  location /health {
    proxy_pass http://cssa_backend;
  }
}
```

### HAProxy

```haproxy
global
  log stdout local0
  
frontend http_front
  bind *:80
  default_backend http_back

backend http_back
  balance roundrobin
  server agent1 127.0.0.1:5001 check
  server agent2 127.0.0.1:5002 check
  server agent3 127.0.0.1:5003 check
```

## Database Scaling (Future)

### PostgreSQL for Production

When migrating from JSON to PostgreSQL:

```bash
# Create database
createdb cssa_products

# Connect and migrate
python -c "
from cssa_agent import app
with app.app_context():
    # Run migration
    db.create_all()
"
```

### Redis Cache

For session caching and rate limiting:

```bash
# Docker
docker run -d -p 6379:6379 redis:7-alpine

# Configure in agent
REDIS_URL=redis://localhost:6379/0
```

## Monitoring & Logging

### Prometheus Metrics

Add to agent:

```python
from prometheus_client import Counter, Histogram
rec_counter = Counter('recommendations_total', 'Total recommendations')
rec_time = Histogram('recommendation_duration_seconds', 'Recommendation latency')
```

### ELK Stack (Elasticsearch, Logstash, Kibana)

Configure structured logging:

```python
import json_log_formatter
formatter = json_log_formatter.JSONFormatter()
```

### Application Performance Monitoring

Integrate APM:

```python
from elastic_apm import instrument
instrument()
```

## Health Checks & Monitoring

### Kubernetes Probes

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 5000
  initialDelaySeconds: 10
  periodSeconds: 10
  
readinessProbe:
  httpGet:
    path: /api/status
    port: 5000
  initialDelaySeconds: 5
  periodSeconds: 5
```

### Supervisor Integration

Supervisor polls agent regularly:

```
GET /health → returns 200 + agent metadata
GET /api/status → returns operational status + memory stats
GET /api/registry → returns capabilities
```

## Scaling Strategy

### Horizontal Scaling (Multiple Instances)

```
[Load Balancer]
  ↓
[Agent 1] [Agent 2] [Agent 3]
  ↓         ↓         ↓
[Shared Product Cache (PostgreSQL/Redis)]
[Shared LTM (PostgreSQL)]
```

### Vertical Scaling

- Increase worker processes (Gunicorn `-w` flag)
- Increase memory limits
- Use faster JSON parsing (e.g., `ujson`)

## Backup & Recovery

### Database Backups

```bash
# SQLite backup
cp cssa_memory.db cssa_memory.db.backup.$(date +%s)

# PostgreSQL backup
pg_dump cssa_products > backup_$(date +%Y%m%d).sql

# Automated daily backup
0 2 * * * pg_dump cssa_products | gzip > /backups/cssa_$(date +\%Y\%m\%d).sql.gz
```

### Data Recovery

```bash
# From SQLite backup
cp cssa_memory.db.backup.1234567890 cssa_memory.db

# From PostgreSQL backup
psql cssa_products < backup_20250101.sql
```

## Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Use HTTPS/TLS (reverse proxy)
- [ ] Add API authentication (API keys, OAuth)
- [ ] Rate limiting (Flask-Limiter)
- [ ] Input validation (already done with jsonschema)
- [ ] SQL injection prevention (use ORM)
- [ ] CORS configuration (if needed)
- [ ] Secrets management (not in code, use .env)
- [ ] Log rotation (already done with RotatingFileHandler)

## Deployment Checklist

- [ ] Environment variables configured
- [ ] Database migrations run
- [ ] Health check passes
- [ ] Integration tests pass
- [ ] Logging configured
- [ ] Monitoring alerts set up
- [ ] Backup strategy in place
- [ ] Load balancer routing configured
- [ ] SSL certificates installed
- [ ] Documentation updated

## Support

For issues:
1. Check logs: `docker logs cssa-agent`
2. Health check: `curl http://localhost:5000/health`
3. API docs: `http://localhost:5000/ui/swagger.html`
4. Memory stats: `curl http://localhost:5000/api/status`
