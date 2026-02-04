# Production Best Practices - Stone Prover Integration
## Deployment and Operations Guide

**Date**: January 27, 2026  
**Author**: Obsqra Labs Research Team  
**Status**: Production-Validated  
**Category**: Best Practices Guide

---

## Executive Summary

This document provides comprehensive best practices for deploying and operating Stone Prover integration in production. Based on Obsqra Labs' production system with 100+ proofs and 100% success rate, this guide covers infrastructure setup, monitoring, error handling, security, performance optimization, and scaling strategies.

**Target Audience**: Teams deploying Stone Prover integration to production  
**Difficulty**: Advanced  
**Time to Implement**: 1-2 weeks

---

## Table of Contents

1. [Infrastructure Setup](#infrastructure-setup)
2. [Monitoring and Alerting](#monitoring-and-alerting)
3. [Error Handling](#error-handling)
4. [Retry Strategies](#retry-strategies)
5. [Rate Limiting](#rate-limiting)
6. [Security Considerations](#security-considerations)
7. [Performance Optimization](#performance-optimization)
8. [Cost Optimization](#cost-optimization)
9. [Disaster Recovery](#disaster-recovery)
10. [Scaling Strategies](#scaling-strategies)

---

## Infrastructure Setup

### Server Requirements

**Minimum** (for testing):
- CPU: 4 cores
- RAM: 8GB
- Storage: 50GB SSD
- Network: Basic

**Recommended** (for production):
- CPU: 8+ cores
- RAM: 16GB+
- Storage: 100GB+ SSD
- Network: Low latency to Starknet RPC

**High Throughput** (for scale):
- CPU: 16+ cores
- RAM: 32GB+
- Storage: 500GB+ SSD
- Network: Dedicated connection

### Deployment Architecture

**Single Instance**:
```
Application Server
    ├─ Stone Prover Binary
    ├─ Integrity Integration
    ├─ API Endpoints
    └─ Database
```

**Scaled Architecture**:
```
Load Balancer
    ↓
Application Servers (multiple)
    ├─ Stone Prover Binary
    ├─ Integrity Integration
    └─ API Endpoints
    ↓
Shared Database
    ↓
Queue System (optional)
```

### Container Deployment

**Docker Setup**:
```dockerfile
FROM ubuntu:20.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    build-essential

# Copy Stone binary
COPY stone-prover/bazel-bin/.../cpu_air_prover /usr/local/bin/

# Copy application
COPY . /app
WORKDIR /app

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Run application
CMD ["python3", "main.py"]
```

**Kubernetes Deployment**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: stone-prover-service
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: stone-prover
        image: obsqra/stone-prover-service:latest
        resources:
          requests:
            cpu: "4"
            memory: "8Gi"
          limits:
            cpu: "8"
            memory: "16Gi"
```

---

## Monitoring and Alerting

### Key Metrics

**Performance Metrics**:
- Proof generation time (P50, P95, P99)
- Success rate
- Error rate
- Throughput (proofs/minute)

**Resource Metrics**:
- CPU usage
- Memory usage
- Disk I/O
- Network I/O

**Business Metrics**:
- Proofs generated/day
- Cost per proof
- Customer usage
- Error distribution

### Monitoring Setup

**Prometheus + Grafana**:
```python
from prometheus_client import Counter, Histogram

proof_generation_time = Histogram(
    'proof_generation_seconds',
    'Time spent generating proofs'
)

proofs_generated = Counter(
    'proofs_generated_total',
    'Total proofs generated'
)

# In code
with proof_generation_time.time():
    result = await stone_service.generate_proof(...)
    if result.success:
        proofs_generated.inc()
```

### Alerting Rules

**Critical Alerts**:
- Proof generation failure rate > 5%
- Proof generation time P95 > 10s
- System CPU > 90%
- System memory > 90%
- RPC errors > 10%

**Warning Alerts**:
- Proof generation time P95 > 5s
- Success rate < 95%
- System CPU > 70%
- System memory > 70%

---

## Error Handling

### Error Categories

**Retryable Errors**:
- Network timeouts
- RPC temporary failures
- System resource constraints

**Non-Retryable Errors**:
- Invalid inputs
- FRI parameter errors
- Version mismatches

### Error Handling Pattern

```python
async def generate_proof_with_retry(inputs, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = await stone_service.generate_proof(**inputs)
            
            if result.success:
                return result
            
            # Check if error is retryable
            if is_retryable_error(result.error):
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
            
            # Non-retryable or max retries
            raise Exception(f"Proof generation failed: {result.error}")
        
        except subprocess.TimeoutExpired:
            if attempt < max_retries - 1:
                # Increase timeout and retry
                inputs["timeout_seconds"] = inputs.get("timeout_seconds", 300) * 2
                await asyncio.sleep(2 ** attempt)
                continue
            raise
        
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)
    
    raise Exception("Max retries exceeded")
```

### Error Logging

```python
import logging
import traceback

logger = logging.getLogger(__name__)

try:
    result = await generate_proof(...)
except Exception as e:
    logger.error(
        f"Proof generation failed: {type(e).__name__}: {str(e)}",
        exc_info=True,
        extra={
            "n_steps": n_steps,
            "trace_file": trace_file,
            "attempt": attempt
        }
    )
    # Handle error
```

---

## Retry Strategies

### Exponential Backoff

```python
import asyncio

async def retry_with_backoff(func, max_retries=3, base_delay=1):
    for attempt in range(max_retries):
        try:
            return await func()
        except RetryableError as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            await asyncio.sleep(delay)
    raise Exception("Max retries exceeded")
```

### Circuit Breaker

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    async def call(self, func):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half-open"
            else:
                raise CircuitBreakerOpenError()
        
        try:
            result = await func()
            self.failure_count = 0
            self.state = "closed"
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            
            raise
```

---

## Rate Limiting

### API Rate Limiting

```python
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self, max_requests=100, window=60):
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)
    
    async def acquire(self, key):
        now = time.time()
        requests = self.requests[key]
        
        # Remove old requests
        requests[:] = [r for r in requests if now - r < self.window]
        
        if len(requests) >= self.max_requests:
            raise RateLimitError("Rate limit exceeded")
        
        requests.append(now)
```

### Proof Generation Rate Limiting

```python
# Limit concurrent proof generation
semaphore = asyncio.Semaphore(4)  # Max 4 concurrent

async def generate_proof_with_limit(inputs):
    async with semaphore:
        return await stone_service.generate_proof(**inputs)
```

---

## Security Considerations

### Private Key Management

**Best Practices**:
- Never commit private keys to git
- Use environment variables
- Use secret management services
- Rotate keys regularly
- Limit key access

**Implementation**:
```python
import os
from pathlib import Path

# Load from environment
private_key = os.getenv("BACKEND_WALLET_PRIVATE_KEY")
if not private_key:
    raise ValueError("Private key not configured")

# Validate format
try:
    int(private_key, 16)
except ValueError:
    raise ValueError("Invalid private key format")
```

### API Security

**Authentication**:
```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    valid_keys = os.getenv("API_KEYS", "").split(",")
    if api_key not in valid_keys:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key
```

**Input Validation**:
```python
from pydantic import BaseModel, validator

class ProofRequest(BaseModel):
    n_steps: int
    
    @validator('n_steps')
    def validate_n_steps(cls, v):
        if v & (v - 1) != 0:
            raise ValueError("n_steps must be power of 2")
        if v < 512:
            raise ValueError("n_steps must be >= 512")
        return v
```

### Audit Logging

```python
import logging

audit_logger = logging.getLogger("audit")

def log_proof_generation(request, result):
    audit_logger.info(
        "Proof generated",
        extra={
            "request_id": request.id,
            "n_steps": request.n_steps,
            "success": result.success,
            "proof_hash": result.proof_hash if result.success else None,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

---

## Performance Optimization

### Trace Size Optimization

**Minimize n_steps**:
```python
# Calculate actual steps needed
actual_steps = calculate_required_steps(computation)

# Round to next power of 2
n_steps_log = math.ceil(math.log2(actual_steps))
n_steps = 2 ** n_steps_log

# Don't over-allocate
if n_steps > actual_steps * 2:
    n_steps = n_steps // 2
```

### Parallel Processing

**Generate Multiple Proofs**:
```python
async def generate_proofs_parallel(inputs_list, max_concurrent=4):
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def generate_with_limit(inputs):
        async with semaphore:
            return await stone_service.generate_proof(**inputs)
    
    tasks = [generate_with_limit(inp) for inp in inputs_list]
    return await asyncio.gather(*tasks)
```

### Caching

**Cache FRI Parameters**:
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_fri_steps(n_steps: int, last_layer: int) -> tuple:
    return tuple(calculate_fri_step_list(n_steps, last_layer))
```

**Cache Proof Results** (if deterministic):
```python
proof_cache = {}

def get_cache_key(inputs):
    return hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()

async def generate_proof_cached(inputs):
    cache_key = get_cache_key(inputs)
    if cache_key in proof_cache:
        return proof_cache[cache_key]
    
    result = await generate_proof(inputs)
    proof_cache[cache_key] = result
    return result
```

---

## Cost Optimization

### Infrastructure Optimization

**Right-Sizing**:
- Start with minimum requirements
- Scale based on actual usage
- Monitor resource utilization
- Adjust as needed

**Resource Pooling**:
- Share infrastructure across customers
- Efficient resource allocation
- Auto-scaling based on demand

### Proof Generation Optimization

**Batch Processing**:
- Process multiple proofs together
- Share common computation
- Reduce overhead

**Optimize Trace Sizes**:
- Minimize n_steps
- Reduce proof size
- Lower generation time

---

## Disaster Recovery

### Backup Strategy

**What to Backup**:
- Stone Prover binary
- Configuration files
- Proof data (if needed)
- Database (if applicable)

**Backup Frequency**:
- Daily backups
- Before major changes
- Before deployments

### Recovery Procedures

**Stone Binary Recovery**:
```bash
# Rebuild if needed
cd stone-prover
git checkout 1414a545e4fb38a85391289abe91dd4467d268e1
bazel build //src/starkware/main/cpu:cpu_air_prover
```

**Service Recovery**:
- Health checks
- Automatic restart
- Failover to backup
- Manual intervention procedures

---

## Scaling Strategies

### Vertical Scaling

**More Resources**:
- More CPU cores → more parallel proofs
- More RAM → larger traces
- Faster storage → faster I/O

**Limits**:
- Diminishing returns after 16 cores
- Memory becomes bottleneck
- Cost increases linearly

### Horizontal Scaling

**Multiple Instances**:
- Deploy multiple instances
- Load balancing
- Shared state (if needed)
- Queue system (optional)

**Benefits**:
- Linear scaling
- Fault tolerance
- Geographic distribution

### Auto-Scaling

**Kubernetes HPA**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: stone-prover-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: stone-prover-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## Conclusion

Production deployment requires:

**Infrastructure**:
- ✅ Proper server setup
- ✅ Monitoring and alerting
- ✅ Backup and recovery

**Operations**:
- ✅ Error handling
- ✅ Retry strategies
- ✅ Rate limiting
- ✅ Security

**Optimization**:
- ✅ Performance tuning
- ✅ Cost optimization
- ✅ Scaling strategies

**Next Steps**:
1. Set up infrastructure
2. Implement monitoring
3. Deploy to production
4. Monitor and optimize

**Related Documents**:
- `Guides/COMPLETE_INTEGRATION_TUTORIAL.md` - Integration guide
- `Guides/TROUBLESHOOTING_GUIDE.md` - Troubleshooting
- `Benchmarks/STONE_PROVER_PERFORMANCE_BENCHMARKS.md` - Performance data

---

**This guide enables production-ready deployment of Stone Prover integration.**
