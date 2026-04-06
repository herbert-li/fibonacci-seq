# Fibonacci REST API

A production-ready REST API service that computes and returns the nth number in the Fibonacci sequence.

## Overview

This service provides a simple HTTP API endpoint that accepts an integer `n` and returns the nth Fibonacci number, where:
- F(0) = 0
- F(1) = 1
- F(n) = F(n-1) + F(n-2) for n > 1

## API Specification

### Endpoints

#### GET /fibonacci

Computes the nth Fibonacci number.

**Parameters:**
- `n` (required): Non-negative integer (0 ≤ n ≤ 10000)

**Example Requests:**

```bash
# F(2) = 1
curl "http://localhost:5000/fibonacci?n=2"

# F(10) = 55
curl "http://localhost:5000/fibonacci?n=10"
```

**Success Response (200 OK):**

```json
{
  "n": 10,
  "result": 55,
  "computation_time_seconds": 0.0001
}
```

**Error Responses:**

```json
// Missing parameter (400 Bad Request)
{
  "error": "Missing parameter 'n'",
  "message": "Please provide a non-negative integer n as a query parameter"
}

// Invalid parameter (400 Bad Request)
{
  "error": "Invalid parameter",
  "message": "Parameter 'n' must be an integer"
}
```

#### GET /health

Health check endpoint for monitoring and load balancers.

**Response (200 OK):**

```json
{
  "status": "healthy"
}
```

## Local Development

### Prerequisites

- Python 3.11 or higher
- pip

### Setup and Run

1. **Clone the repository:**

```bash
cd fibonacci-seq
```

2. **Create a virtual environment:**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Run the application:**

```bash
# Development mode
python app.py

# Production mode with gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

The API will be available at `http://localhost:5000`

### Testing

Run the test suite:

```bash
pytest test_app.py -v
```

Run with coverage:

```bash
pytest --cov=app test_app.py
```

## Production Deployment

### Containerization with Docker

The service includes a Dockerfile for containerized deployments.

**Build the Docker image:**

```bash
docker build -t fibonacci-api:latest .
```

**Run the container:**

```bash
docker run -p 5000:5000 fibonacci-api:latest
```

**Run with environment variables:**

```bash
docker run -p 5000:5000 \
  -e WORKERS=4 \
  fibonacci-api:latest
```

### Docker Compose (Optional)

Create a `docker-compose.yml` for easy orchestration:

```yaml
version: '3.8'
services:
  fibonacci-api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - WORKERS=4
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Run with: `docker compose up -d`

### Kubernetes Deployment

For Kubernetes deployments, here's a basic configuration:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fibonacci-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fibonacci-api
  template:
    metadata:
      labels:
        app: fibonacci-api
    spec:
      containers:
      - name: fibonacci-api
        image: fibonacci-api:latest
        ports:
        - containerPort: 5000
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 10

---
apiVersion: v1
kind: Service
metadata:
  name: fibonacci-api
spec:
  selector:
    app: fibonacci-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  type: LoadBalancer
```

### GitOps with ArgoCD (OpenShift/Kubernetes)

For production-grade GitOps deployments using ArgoCD on OpenShift or Kubernetes, a complete deployment configuration is available in a separate repository: [fibonacci-seq-deploy](https://github.com/herbert-li/fibonacci-seq-deploy)

**What's included:**
- Kustomize-based multi-environment configurations (dev, staging, prod)
- ArgoCD Application manifests with automated sync policies
- Environment-specific resource configurations and overlays
- Health checks and monitoring integration
- Automated image tag updates via CI/CD

**Key Benefits:**
- **Declarative GitOps**: All Kubernetes resources versioned in Git
- **Automated Deployments**: Push to Git triggers automatic synchronization
- **Drift Detection**: Auto-healing when cluster state diverges from Git
- **Multi-Environment**: Consistent deployments across dev/staging/prod
- **Rollback Capability**: Easy rollback to any previous Git commit

**Quick Start:**

```bash
# Install ArgoCD (if not already installed)
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Deploy the application
kubectl apply -f https://raw.githubusercontent.com/herbert-li/fibonacci-seq-deploy/main/argocd/application.yaml

# Monitor deployment status
argocd app get fibonacci-api
```

See the [deployment repository](https://github.com/herbert-li/fibonacci-seq-deploy) for detailed setup instructions, architecture diagrams, and advanced configuration options.

## CI/CD Pipeline

### GitHub Actions

A sample CI/CD workflow is provided in `.github/workflows/ci.yml` that:

1. Runs tests on every push and pull request
2. Builds and pushes Docker images on successful tests

**Setup required:**
- Add `DOCKER_USERNAME` and `DOCKER_PASSWORD` to GitHub Secrets

### GitLab CI/CD

Example `.gitlab-ci.yml`:

```yaml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - pytest test_app.py -v

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t fibonacci-api:$CI_COMMIT_SHA .
    - docker push fibonacci-api:$CI_COMMIT_SHA
  only:
    - main

deploy:
  stage: deploy
  script:
    - kubectl set image deployment/fibonacci-api fibonacci-api=fibonacci-api:$CI_COMMIT_SHA
  only:
    - main

```

### ArgoCD GitOps Integration

ArgoCD provides continuous deployment with Git as the single source of truth. The workflow integrates seamlessly with the CI/CD pipeline:

**Deployment Flow:**

1. **CI Stage**: GitHub Actions builds and pushes Docker image with tag (e.g., `prod-abc123`)
2. **CD Stage**: Image tag is updated in the [deployment repository](https://github.com/herbert-li/fibonacci-seq-deploy)
3. **GitOps Sync**: ArgoCD detects Git changes and automatically syncs to Kubernetes cluster
4. **Health Check**: ArgoCD monitors application health via `/health` endpoint
5. **Notifications**: Deployment status sent to configured channels (Slack, email)

**Example CI/CD Integration:**

Add this step to `.github/workflows/ci.yml` after Docker image push:

```yaml
- name: Update ArgoCD deployment
  run: |
    # Clone deployment repo
    git clone https://github.com/herbert-li/fibonacci-seq-deploy.git
    cd fibonacci-seq-deploy
    
    # Update image tag in Kustomize overlay
    cd overlays/prod
    kustomize edit set image fibonacci-api:prod-${{ github.sha }}
    
    # Commit and push to trigger ArgoCD sync
    git config user.name "GitHub Actions"
    git config user.email "actions@github.com"
    git commit -am "Deploy prod-${{ github.sha }}"
    git push
```

**Monitoring Deployments:**

```bash
# Watch real-time sync status
argocd app watch fibonacci-api

# View deployment history
argocd app history fibonacci-api

# Rollback to previous version
argocd app rollback fibonacci-api <revision>
```

For complete ArgoCD setup, manifests, and advanced configurations (progressive delivery, sync waves, health checks), see: [fibonacci-seq-deploy](https://github.com/herbert-li/fibonacci-seq-deploy)

## Monitoring and Logging

### Logging Strategy

The application uses Python's built-in logging module with the following features:

- **Structured logging**: Timestamp, logger name, level, and message
- **Request logging**: Every Fibonacci computation is logged with input, output, and computation time
- **Error tracking**: Exceptions are logged with full stack traces

**Log aggregation recommendations:**
- Send logs to centralized logging (e.g., ELK Stack, Splunk, CloudWatch)
- Use structured JSON logging for production (e.g., python-json-logger)
- Configure log retention policies

### Monitoring

**Key metrics to monitor:**

1. **Application metrics:**
   - Request rate (requests/second)
   - Response time (p50, p95, p99)
   - Error rate (4xx, 5xx responses)
   - Computation time per request

2. **Infrastructure metrics:**
   - CPU usage
   - Memory usage
   - Network I/O
   - Container restarts

**Recommended tools:**

- **Prometheus + Grafana**: Metrics collection and visualization
- **Datadog/New Relic**: Application Performance Monitoring (APM)
- **CloudWatch/Stackdriver**: Cloud-native monitoring

**Example Prometheus instrumentation:**

Install prometheus-flask-exporter:
```bash
pip install prometheus-flask-exporter
```

Add to `app.py`:
```python
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)
```

### Alerting

Set up alerts for:
- Error rate > 5% over 5 minutes
- Response time p99 > 1 second
- Health check failures
- High memory/CPU usage

## Scaling Strategies

### Horizontal Scaling

**Auto-scaling with Kubernetes HPA (Horizontal Pod Autoscaler):**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fibonacci-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fibonacci-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### High Availability with PodDisruptionBudget

To ensure high availability during voluntary disruptions (node drains, cluster upgrades, scaling operations), configure a PodDisruptionBudget (PDB):

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: fibonacci-api-pdb
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: fibonacci-api
```

**Alternative configuration using maxUnavailable:**

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: fibonacci-api-pdb
spec:
  maxUnavailable: 1
  selector:
    matchLabels:
      app: fibonacci-api
```

**PDB Configuration Guidelines:**

- **minAvailable: 1** - Ensures at least 1 pod is always running during disruptions
- **maxUnavailable: 1** - Allows only 1 pod to be unavailable at a time (useful when you have multiple replicas)
- For production with 3+ replicas: Use `minAvailable: 2` or `maxUnavailable: 1` to maintain service availability
- For high-traffic production: Consider `minAvailable: "50%"` to always keep half your pods available

**Important Notes:**

- PDB only protects against *voluntary* disruptions (kubectl drain, cluster autoscaler, node maintenance)
- Does NOT protect against involuntary disruptions (node failures, hardware issues)
- Requires minReplicas ≥ 2 in your Deployment for effective HA
- Works in conjunction with HPA - ensure HPA minReplicas is sufficient for your PDB constraints

**Verifying PDB Status:**

```bash
# Check PDB status
kubectl get pdb fibonacci-api-pdb

# See detailed disruption information
kubectl describe pdb fibonacci-api-pdb
```

### Caching Strategy

For high-traffic scenarios, implement caching:

**Redis caching example:**

```python
import redis
from functools import lru_cache

# In-memory caching
@lru_cache(maxsize=1000)
def fibonacci_cached(n):
    return fibonacci(n)

# Distributed caching with Redis
redis_client = redis.Redis(host='redis', port=6379)

def get_fibonacci_redis(n):
    cached = redis_client.get(f'fib:{n}')
    if cached:
        return int(cached)
    result = fibonacci(n)
    redis_client.setex(f'fib:{n}', 3600, result)
    return result
```

### Load Balancing

- Use NGINX or HAProxy as reverse proxy
- Cloud load balancers (AWS ALB, GCP Load Balancer)
- Kubernetes Ingress controllers

### Performance Optimizations

1. **Connection pooling**: Use gunicorn with appropriate worker count
2. **Rate limiting**: Prevent abuse with Flask-Limiter
3. **CDN**: Cache responses for common inputs
4. **Database**: Store precomputed values for large n

## Security Considerations

1. **Input validation**: Strict validation of input parameters (already implemented)
2. **Rate limiting**: Implement rate limiting to prevent abuse
3. **HTTPS**: Always use TLS in production
4. **Non-root user**: Docker container runs as non-root user
5. **Dependencies**: Regularly update dependencies for security patches
6. **CORS**: Configure CORS headers if needed for web clients

## Performance Characteristics

- **Time complexity**: O(n) for computing F(n)
- **Space complexity**: O(1)
- **Max input**: n ≤ 10,000 (configurable in code)
- **Typical response time**: < 10ms for n < 1000

## License

MIT License

## Support

For issues or questions, please open an issue in the repository.
