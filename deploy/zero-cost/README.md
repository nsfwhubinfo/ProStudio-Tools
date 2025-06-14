# ProStudio Zero-Cost Deployment
================================

Launch ProStudio's dynamic memory caching system with **$0 initial investment** using AWS Free Tier or local Docker.

## Quick Start (5 minutes)

### Option 1: Local Development
```bash
cd deploy/zero-cost
chmod +x local-start.sh
./local-start.sh
```

Access at: http://localhost

### Option 2: AWS Free Tier
```bash
cd deploy/zero-cost
chmod +x setup-ec2.sh
./setup-ec2.sh
```

Access at: http://<ec2-public-ip>

## Architecture

```
┌─────────────────────────────────────────────────┐
│                   nginx (Port 80)               │
├─────────────────────────────────────────────────┤
│                ProStudio App (Gunicorn)         │
│                    - 2 workers                  │
│                    - Health checks              │
│                    - Metrics endpoint           │
├─────────────────────────────────────────────────┤
│               Redis 7.0 (In-Memory Cache)       │
│                    - 512MB limit                │
│                    - LRU eviction               │
│                    - Persistence                │
└─────────────────────────────────────────────────┘
```

## What's Included

### Phase 1: Local Simulation
- **docker-compose.yml**: Complete multi-service setup
- **Nginx**: Load balancer with rate limiting
- **Redis**: Production-configured caching
- **Monitoring**: Optional Prometheus + Grafana

### Phase 2: Cloud Deployment  
- **EC2 Setup**: Automated t2.micro provisioning
- **GitHub Actions**: CI/CD pipeline
- **Health Checks**: Automated monitoring
- **SSL Ready**: Nginx configured for HTTPS

### Phase 3: Migration Path
- **Seamless scaling**: Same code, bigger infrastructure
- **Terraform ready**: One command to production
- **Zero downtime**: Gradual traffic migration

## File Structure

```
deploy/zero-cost/
├── docker-compose.yml      # Local development environment
├── Dockerfile             # Optimized container image
├── nginx.conf            # Load balancer configuration
├── start.sh              # Container startup script
├── local-start.sh        # Local development launcher
├── setup-ec2.sh          # AWS Free Tier provisioning
├── MIGRATION_GUIDE.md    # Path to production
└── README.md            # This file
```

## Features

### Performance
- ✅ Redis caching with compression
- ✅ Connection pooling
- ✅ Batch operations
- ✅ Gunicorn with gevent workers

### Reliability
- ✅ Health check endpoints
- ✅ Automatic restarts
- ✅ Graceful shutdowns
- ✅ Swap space (for t2.micro)

### Security
- ✅ Non-root containers
- ✅ Environment-based secrets
- ✅ Rate limiting
- ✅ Security headers

### Monitoring
- ✅ Prometheus metrics
- ✅ JSON structured logging
- ✅ Health endpoints
- ✅ Performance tracking

## Commands

### Local Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# With monitoring
docker-compose --profile monitoring up -d
```

### Testing

```bash
# Health check
curl http://localhost/health

# Set cache value
curl -X POST http://localhost/api/cache/set \
  -H 'X-API-Key: local_dev_api_key_change_in_prod' \
  -H 'Content-Type: application/json' \
  -d '{"key": "test", "value": "Hello World"}'

# Get cache value  
curl http://localhost/api/cache/get/test \
  -H 'X-API-Key: local_dev_api_key_change_in_prod'
```

### AWS Deployment

```bash
# Check instance status
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=prostudio-free-tier" \
  --query "Reservations[*].Instances[*].[InstanceId,State.Name,PublicIpAddress]" \
  --output table

# SSH to instance
ssh -i prostudio-key.pem ubuntu@<public-ip>

# View container logs
ssh -i prostudio-key.pem ubuntu@<public-ip> \
  'docker-compose -f /home/ubuntu/prostudio/docker-compose.yml logs -f'
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_HOST` | redis | Redis hostname |
| `REDIS_PASSWORD` | (generated) | Redis authentication |
| `API_KEY` | (generated) | API authentication |
| `SECRET_KEY` | (generated) | App secret key |
| `API_WORKERS` | 2 | Gunicorn workers |
| `MAX_MEMORY_MB` | 1024 | Cache memory limit |

## Cost Breakdown

### Local (Phase 1)
- **Cost**: $0
- **Requirements**: Docker Desktop

### AWS Free Tier (Phase 2)
- **Cost**: $0 for 12 months
- **Includes**:
  - 750 hours EC2 t2.micro
  - 30 GB EBS storage
  - 15 GB data transfer

### Production (Phase 3)
- **Cost**: ~$625/month
- **Includes**:
  - ECS Fargate (3-20 tasks)
  - ElastiCache Redis HA
  - Application Load Balancer

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs app

# Verify Redis connection
docker-compose exec app redis-cli -h redis ping
```

### High memory usage
```bash
# Check Redis memory
docker-compose exec redis redis-cli info memory

# Flush cache if needed
docker-compose exec redis redis-cli FLUSHDB
```

### EC2 setup fails
```bash
# Check CloudFormation events
aws cloudformation describe-stack-events \
  --stack-name prostudio-free-tier

# Manual instance check
aws ec2 describe-instance-status \
  --instance-ids <instance-id>
```

## Next Steps

1. **Test Locally**: Run `./local-start.sh`
2. **Deploy to AWS**: Run `./setup-ec2.sh`
3. **Configure GitHub**: Add AWS credentials as secrets
4. **Push Code**: Trigger automatic deployment
5. **Monitor**: Check health endpoints
6. **Scale**: Follow MIGRATION_GUIDE.md

## Support

- GitHub Issues: [your-repo]/issues
- Documentation: [your-docs-site]
- Email: support@prostudio.io

---

Built with ❤️ for zero-cost cloud deployment