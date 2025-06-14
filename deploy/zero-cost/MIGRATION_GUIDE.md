# ProStudio Zero-Cost to Production Migration Guide
=================================================

## Overview

This guide details the seamless migration path from the zero-cost deployment to the full production architecture. The system is designed for linear scaling with minimal code changes.

## Current Architecture (Zero-Cost)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   NGINX     │────▶│  ProStudio  │────▶│    Redis    │
│  (Port 80)  │     │   (Gunicorn)│     │  (In-Memory)│
└─────────────┘     └─────────────┘     └─────────────┘
       │                    │                    │
       └────────────────────┴────────────────────┘
                    Single EC2 t2.micro
```

## Target Architecture (Production)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│     ALB     │────▶│  ECS Fargate │────▶│ ElastiCache │
│   (HTTPS)   │     │  (20 tasks)  │     │  (3 nodes)  │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Migration Phases

### Phase 1: Preparation (Current State)
- ✅ Containerized application
- ✅ Environment-based configuration
- ✅ Health check endpoints
- ✅ Structured logging
- ✅ Redis abstraction layer

### Phase 2: Incremental Improvements ($10-50/month)

#### Step 1: Separate Redis (Week 1)
```bash
# Launch ElastiCache Redis (single node, cache.t3.micro)
aws elasticache create-cache-cluster \
  --cache-cluster-id prostudio-redis-prod \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1

# Update application configuration
export REDIS_HOST=prostudio-redis-prod.abc123.cache.amazonaws.com
export REDIS_AUTH_TOKEN=<generated-token>
```

**Benefits:**
- Dedicated cache memory (500MB)
- Better performance isolation
- Automatic backups
- **Cost:** ~$13/month

#### Step 2: Add Load Balancer (Week 2)
```bash
# Create Application Load Balancer
aws elbv2 create-load-balancer \
  --name prostudio-alb \
  --subnets subnet-12345 subnet-67890

# Register EC2 instance as target
aws elbv2 register-targets \
  --target-group-arn arn:aws:elasticloadbalancing:... \
  --targets Id=i-1234567890abcdef0
```

**Benefits:**
- SSL termination
- Health checks
- Path-based routing
- **Cost:** ~$25/month

#### Step 3: Multi-Instance Setup (Week 3)
```bash
# Launch second t2.micro instance
./setup-ec2.sh  # Modified to create instance #2

# Both instances connect to same Redis
# ALB distributes traffic between them
```

**Benefits:**
- High availability
- Rolling deployments
- 2x capacity
- **Cost:** $0 (still within free tier)

### Phase 3: Production Migration ($625+/month)

#### Step 1: Terraform Infrastructure
```bash
cd deploy/aws/terraform

# Update terraform.tfvars
cat > terraform.tfvars <<EOF
environment = "production"
domain_name = "prostudio.com"
redis_node_type = "cache.r7g.large"
ecs_task_count = 3
EOF

# Deploy infrastructure
terraform init
terraform plan
terraform apply
```

#### Step 2: Data Migration
```python
# Migration script (run from EC2 instance)
import redis

# Connect to both Redis instances
source = redis.Redis(host='localhost', port=6379)
target = redis.Redis(
    host='elasticache-endpoint.amazonaws.com',
    port=6379,
    password='auth-token',
    ssl=True
)

# Migrate data
for key in source.scan_iter("*"):
    ttl = source.ttl(key)
    value = source.get(key)
    if ttl > 0:
        target.setex(key, ttl, value)
    else:
        target.set(key, value)

print(f"Migrated {source.dbsize()} keys")
```

#### Step 3: DNS Cutover
```bash
# Update Route53 to point to ALB
aws route53 change-resource-record-sets \
  --hosted-zone-id Z123456 \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "api.prostudio.com",
        "Type": "CNAME",
        "TTL": 60,
        "ResourceRecords": [{"Value": "prostudio-alb-123456.us-east-1.elb.amazonaws.com"}]
      }
    }]
  }'
```

## Configuration Changes

### Environment Variables Migration

| Zero-Cost | Production | Notes |
|-----------|------------|-------|
| `REDIS_HOST=redis` | `REDIS_HOST=<elasticache-endpoint>` | From Secrets Manager |
| `REDIS_PASSWORD=<plain>` | `REDIS_AUTH_TOKEN=<encrypted>` | Encrypted in transit |
| `API_WORKERS=2` | `API_WORKERS=4` | More CPU available |
| `MAX_MEMORY_MB=1024` | `MAX_MEMORY_MB=3072` | More RAM available |

### Code Changes Required

```python
# redis_cache.py - Already supports both modes!
if self.config['enable_sentinel']:
    # Production mode with HA
    sentinel = Sentinel(self.config['sentinel_hosts'])
    self.redis = sentinel.master_for('mymaster')
else:
    # Development/zero-cost mode
    self.redis = redis.Redis(
        host=self.config['host'],
        port=self.config['port']
    )
```

## Rollback Plan

Each phase can be rolled back independently:

1. **Redis Rollback**: Update `REDIS_HOST` to point back to local Redis
2. **ALB Rollback**: Update DNS to point directly to EC2 Elastic IP
3. **ECS Rollback**: Keep EC2 instances running while debugging

## Cost Optimization Tips

### Gradual Scaling
Start with minimal production resources:
- ElastiCache: 1 node → 3 nodes
- ECS Tasks: 2 → 5 → 20
- Instance types: t3.small → t3.medium → t3.large

### Reserved Instances
After 3 months of stable usage:
- ElastiCache Reserved Nodes: 35% savings
- ECS Fargate Savings Plans: 20% savings

### Monitoring Costs
Use AWS Cost Explorer to track:
- Daily spend by service
- Cost anomalies
- Optimization recommendations

## Performance Expectations

| Metric | Zero-Cost | Production | Improvement |
|--------|-----------|------------|-------------|
| Redis Ops/sec | 10,000 | 100,000+ | 10x |
| Concurrent Users | 100 | 10,000+ | 100x |
| Response Time (p99) | 200ms | 50ms | 4x |
| Availability | 95% | 99.9% | Better SLA |

## Automation Scripts

### Health Check During Migration
```bash
#!/bin/bash
# monitor-migration.sh

while true; do
    echo "=== Health Check $(date) ==="
    
    # Check old infrastructure
    curl -s http://ec2-ip/health | jq .
    
    # Check new infrastructure  
    curl -s https://api.prostudio.com/health | jq .
    
    # Compare Redis stats
    echo "Old Redis keys: $(redis-cli -h localhost dbsize)"
    echo "New Redis keys: $(redis-cli -h elasticache-endpoint dbsize)"
    
    sleep 10
done
```

### Traffic Shifting
```python
# Gradual traffic migration using Route53 weighted routing
import boto3

route53 = boto3.client('route53')

for old_weight in range(100, -1, -10):
    new_weight = 100 - old_weight
    
    print(f"Shifting traffic: {old_weight}% old, {new_weight}% new")
    
    # Update Route53 weights
    route53.change_resource_record_sets(
        HostedZoneId='Z123456',
        ChangeBatch={
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': 'api.prostudio.com',
                        'Type': 'A',
                        'SetIdentifier': 'Old',
                        'Weight': old_weight,
                        'AliasTarget': {'HostedZoneId': 'Z1', 'DNSName': 'old-ec2.com'}
                    }
                },
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': 'api.prostudio.com',
                        'Type': 'A',
                        'SetIdentifier': 'New',
                        'Weight': new_weight,
                        'AliasTarget': {'HostedZoneId': 'Z2', 'DNSName': 'new-alb.com'}
                    }
                }
            ]
        }
    )
    
    time.sleep(300)  # Wait 5 minutes between shifts
```

## Success Criteria

Before considering migration complete:

- [ ] Zero errors in CloudWatch Logs for 24 hours
- [ ] Response time p99 < 100ms
- [ ] Redis hit rate > 90%
- [ ] Auto-scaling tested (scale up and down)
- [ ] Backup/restore procedure tested
- [ ] Monitoring dashboards operational
- [ ] Runbook documented
- [ ] Team trained on new infrastructure

## Support Resources

- **AWS Support**: Basic (free) → Developer ($29/month) recommended during migration
- **Monitoring**: CloudWatch (included) + Datadog free tier
- **Documentation**: Update README with new architecture
- **Slack Channel**: #prostudio-migration for team coordination

---

*Remember: The beauty of this architecture is that the application code remains largely unchanged. The infrastructure scales around it.*