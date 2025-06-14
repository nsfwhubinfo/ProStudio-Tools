# ProStudio Dynamic Memory Caching - Cloud Deployment Guide
=========================================================

## Overview

This guide covers deploying ProStudio's dynamic memory caching system to AWS and GCP, including:
- High-availability Redis clusters
- Auto-scaling container orchestration
- CI/CD pipelines
- Monitoring and observability

## Prerequisites

### Common Requirements
- Docker installed locally
- Git repository with ProStudio code
- Domain name for SSL certificates
- Monitoring solution (Datadog/New Relic/Prometheus)

### AWS Requirements
- AWS CLI configured with appropriate credentials
- Terraform >= 1.0
- AWS account with following service limits:
  - ECS Fargate tasks: 100
  - ElastiCache nodes: 20
  - Application Load Balancers: 20

### GCP Requirements
- Google Cloud SDK (gcloud) installed
- Terraform >= 1.0
- GCP project with billing enabled
- APIs enabled: GKE, Memorystore, Cloud Build

## AWS Deployment

### 1. Initial Setup

```bash
# Clone repository
git clone <your-repo>
cd prostudio

# Navigate to AWS deployment directory
cd deploy/aws

# Initialize Terraform
cd terraform
terraform init

# Create terraform.tfvars
cat > terraform.tfvars <<EOF
aws_region = "us-east-1"
environment = "production"
domain_name = "yourdomain.com"
EOF
```

### 2. Deploy Infrastructure

```bash
# Review planned changes
terraform plan

# Apply infrastructure
terraform apply

# Save outputs
terraform output -json > ../outputs.json
```

### 3. Build and Push Docker Image

```bash
# Get ECR login
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t prostudio:latest ../../

# Tag and push
docker tag prostudio:latest <ecr-uri>:latest
docker push <ecr-uri>:latest
```

### 4. Deploy Application

```bash
# Update ECS service with new image
aws ecs update-service \
  --cluster prostudio-cluster-production \
  --service prostudio-production \
  --force-new-deployment

# Monitor deployment
aws ecs wait services-stable \
  --cluster prostudio-cluster-production \
  --services prostudio-production
```

### 5. Verify Deployment

```bash
# Check health endpoint
curl https://prostudio.yourdomain.com/health

# Test API
curl -X POST https://prostudio.yourdomain.com/api/cache \
  -H "X-API-Key: <your-api-key>" \
  -H "Content-Type: application/json" \
  -d '{"key": "test", "value": "data"}'
```

## GCP Deployment

### 1. Initial Setup

```bash
# Set project
gcloud config set project <your-project-id>

# Navigate to GCP deployment directory
cd deploy/gcp

# Initialize Terraform
cd terraform
terraform init

# Create terraform.tfvars
cat > terraform.tfvars <<EOF
project_id = "your-project-id"
region = "us-central1"
environment = "production"
EOF
```

### 2. Deploy Infrastructure

```bash
# Review planned changes
terraform plan

# Apply infrastructure
terraform apply

# Get GKE credentials
gcloud container clusters get-credentials prostudio-gke-production --region us-central1
```

### 3. Configure Secrets

```bash
# Create Redis connection secret
kubectl create secret generic redis-connection \
  --from-literal=host=$(terraform output -raw redis_host) \
  --namespace prostudio-prod

# Update secrets in k8s/deployment.yaml with actual values
kubectl apply -f ../k8s/deployment.yaml
```

### 4. Build and Deploy

```bash
# Submit build to Cloud Build
gcloud builds submit --config=../cloudbuild.yaml ../../

# Verify deployment
kubectl get pods -n prostudio-prod
kubectl get svc -n prostudio-prod
```

### 5. Configure Ingress

```bash
# Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Apply ingress configuration
kubectl apply -f ../k8s/ingress.yaml
```

## Post-Deployment Configuration

### 1. SSL Certificates

#### AWS
- ACM certificate will be automatically validated if using Route53
- Otherwise, add DNS validation records manually

#### GCP
```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Apply certificate configuration
kubectl apply -f ../k8s/certificate.yaml
```

### 2. Monitoring Setup

#### CloudWatch (AWS)
```bash
# Create dashboard
aws cloudwatch put-dashboard \
  --dashboard-name ProStudio-Production \
  --dashboard-body file://monitoring/cloudwatch-dashboard.json
```

#### Stackdriver (GCP)
```bash
# Create uptime checks
gcloud monitoring uptime-checks create \
  --display-name="ProStudio Health Check" \
  --resource-type="k8s-service" \
  --service="prostudio-service" \
  --namespace="prostudio-prod"
```

### 3. Cache Warming

```bash
# SSH into a container
# AWS
aws ecs execute-command \
  --cluster prostudio-cluster-production \
  --task <task-id> \
  --container prostudio \
  --interactive \
  --command "/bin/bash"

# GCP
kubectl exec -it <pod-name> -n prostudio-prod -- /bin/bash

# Run cache warming script
python -m core.cache_warmer --concepts "AI,ML,productivity" --platforms "TIKTOK,INSTAGRAM"
```

## Scaling Configuration

### AWS Auto Scaling
- CPU threshold: 70%
- Memory threshold: 80%
- Min instances: 2
- Max instances: 20
- Scale-out cooldown: 60s
- Scale-in cooldown: 300s

### GCP Auto Scaling
- Cluster autoscaler: 2-20 nodes
- HPA: 3-20 pods
- Node pool distribution: 20% spot instances

## Cost Optimization

### Estimated Monthly Costs

#### AWS
- ECS Fargate (3 tasks): ~$100
- ElastiCache (3 nodes, r7g.large): ~$450
- Application Load Balancer: ~$25
- Data transfer: ~$50
- **Total: ~$625/month**

#### GCP
- GKE nodes (n2-standard-4): ~$300
- Memorystore Redis (13GB, HA): ~$400
- Load Balancer: ~$25
- Data transfer: ~$50
- **Total: ~$775/month**

### Cost Reduction Strategies
1. Use spot/preemptible instances for non-critical workloads
2. Implement aggressive cache expiration policies
3. Use Redis memory optimization settings
4. Schedule scale-down during off-peak hours

## Troubleshooting

### Common Issues

1. **Redis Connection Failures**
   ```bash
   # Check Redis connectivity
   redis-cli -h <redis-host> -a <auth-token> ping
   ```

2. **High Memory Usage**
   ```bash
   # Check Redis memory
   redis-cli -h <redis-host> -a <auth-token> info memory
   
   # Flush cache if needed
   redis-cli -h <redis-host> -a <auth-token> FLUSHDB
   ```

3. **Deployment Failures**
   ```bash
   # AWS: Check ECS events
   aws ecs describe-services --cluster <cluster> --services <service>
   
   # GCP: Check pod events
   kubectl describe pod <pod-name> -n prostudio-prod
   ```

## Security Checklist

- [ ] All secrets stored in Secret Manager/Secrets Manager
- [ ] Redis authentication enabled
- [ ] SSL/TLS encryption for all traffic
- [ ] Network policies restricting pod-to-pod communication
- [ ] Regular security scanning of container images
- [ ] API rate limiting implemented
- [ ] WAF rules configured
- [ ] Audit logging enabled

## Backup and Recovery

### Redis Backup
```bash
# AWS: Create manual snapshot
aws elasticache create-snapshot \
  --replication-group-id prostudio-redis \
  --snapshot-name prostudio-backup-$(date +%Y%m%d)

# GCP: Export to GCS
gcloud redis instances export \
  prostudio-redis-production \
  gs://prostudio-backups/redis-$(date +%Y%m%d).rdb
```

### Disaster Recovery
1. Multi-region replication available (additional configuration required)
2. Point-in-time recovery: Last 5 days (AWS) / 7 days (GCP)
3. RTO: 30 minutes
4. RPO: 1 hour

## Next Steps

1. Set up monitoring dashboards
2. Configure alerting rules
3. Implement cache warming strategies
4. Load test the deployment
5. Set up CI/CD pipelines
6. Configure backup automation

For questions or issues, please refer to the [ProStudio documentation](https://docs.prostudio.io) or contact the infrastructure team.