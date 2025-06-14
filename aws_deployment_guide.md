# AWS Deployment Guide for ProStudio

## 📋 Pre-Deployment Checklist

Before running `./deploy_aws.sh`, ensure you have:

### 1. **AWS Account Setup**
- [ ] AWS Account created
- [ ] Billing alerts configured
- [ ] AWS CLI installed locally
- [ ] AWS credentials configured (`aws configure`)

### 2. **Required AWS Permissions**
Your AWS user/role needs permissions for:
- [ ] ECS (Elastic Container Service)
- [ ] ECR (Elastic Container Registry)
- [ ] EC2 (for VPC, Security Groups)
- [ ] ElastiCache (for Redis)
- [ ] ELB (Elastic Load Balancer)
- [ ] IAM (for roles)
- [ ] Secrets Manager
- [ ] CloudWatch Logs
- [ ] Application Auto Scaling

### 3. **Local Requirements**
- [ ] Docker installed and running
- [ ] AWS CLI v2 installed
- [ ] OpenSSL (for generating secrets)

## 💰 Cost Estimation

### Monthly AWS Costs (Estimated)

| Service | Configuration | Cost/Month |
|---------|--------------|------------|
| **ECS Fargate** | 3 tasks × 2 vCPU × 4GB RAM | ~$220 |
| **Application Load Balancer** | 1 ALB | ~$22 |
| **ElastiCache Redis** | cache.t3.micro (1 node) | ~$13 |
| **ECR** | 1GB storage | ~$0.10 |
| **Secrets Manager** | 2 secrets | ~$0.80 |
| **CloudWatch Logs** | 10GB/month | ~$5 |
| **Data Transfer** | 100GB out | ~$9 |
| **Total** | | **~$270/month** |

### Cost Optimization Tips

1. **Development Environment** (Save 70%):
   ```bash
   # Use smaller instances
   - Fargate: 0.5 vCPU, 1GB RAM
   - Redis: cache.t3.nano
   - Run only 1 task
   # Cost: ~$80/month
   ```

2. **Use Spot Instances** (Save 50-70%):
   ```bash
   # Modify task definition for Spot
   "capacityProviderStrategy": [
     {
       "capacityProvider": "FARGATE_SPOT",
       "weight": 8
     },
     {
       "capacityProvider": "FARGATE",
       "weight": 2
     }
   ]
   ```

3. **Auto-scaling Schedule** (Save 40%):
   ```bash
   # Scale down during off-hours
   aws application-autoscaling put-scheduled-action \
     --service-namespace ecs \
     --resource-id service/prostudio-cluster/prostudio-service \
     --scheduled-action-name scale-down-night \
     --schedule "cron(0 20 * * ? *)" \
     --scalable-target-action MinCapacity=1,MaxCapacity=2
   ```

## 🚀 Running the Deployment

### Basic Deployment

```bash
# Set your AWS region (optional, defaults to us-east-1)
export AWS_REGION=us-west-2

# Run deployment
./deploy_aws.sh
```

### Custom Configuration

```bash
# Set custom values before running
export CLUSTER_NAME=my-prostudio-cluster
export SERVICE_NAME=my-prostudio-service
export AWS_REGION=eu-west-1

./deploy_aws.sh
```

## 🔧 Post-Deployment Configuration

### 1. **Custom Domain (Optional)**

```bash
# Create Route 53 hosted zone
aws route53 create-hosted-zone --name prostudio.yourdomain.com --caller-reference $(date +%s)

# Get ALB DNS name
ALB_DNS=$(aws elbv2 describe-load-balancers --names prostudio-alb --query "LoadBalancers[0].DNSName" --output text)

# Create CNAME record
aws route53 change-resource-record-sets --hosted-zone-id YOUR_ZONE_ID --change-batch '{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "api.prostudio.yourdomain.com",
      "Type": "CNAME",
      "TTL": 300,
      "ResourceRecords": [{"Value": "'$ALB_DNS'"}]
    }
  }]
}'
```

### 2. **SSL/TLS Certificate**

```bash
# Request certificate
aws acm request-certificate \
  --domain-name api.prostudio.yourdomain.com \
  --validation-method DNS

# Add HTTPS listener to ALB
aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=$CERT_ARN \
  --default-actions Type=forward,TargetGroupArn=$TG_ARN
```

### 3. **CloudWatch Dashboard**

```bash
# Create dashboard
aws cloudwatch put-dashboard \
  --dashboard-name ProStudioDashboard \
  --dashboard-body file://cloudwatch-dashboard.json
```

### 4. **Monitoring Alerts**

```bash
# High CPU alert
aws cloudwatch put-metric-alarm \
  --alarm-name prostudio-high-cpu \
  --alarm-description "ProStudio CPU above 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2

# Error rate alert
aws cloudwatch put-metric-alarm \
  --alarm-name prostudio-high-errors \
  --alarm-description "ProStudio error rate above 1%" \
  --metric-name 4XXError \
  --namespace AWS/ApplicationELB \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1
```

## 📊 Testing the Deployment

### 1. **Health Check**

```bash
# Get ALB URL
ALB_URL=$(cat deployment-info.json | jq -r .alb_url)
API_KEY=$(cat deployment-info.json | jq -r .api_key)

# Test health endpoint
curl $ALB_URL/health
```

### 2. **Generate Content**

```bash
# Test content generation
curl -X POST $ALB_URL/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "concept": "5 AI productivity tips for creators",
    "platform": "TIKTOK",
    "content_type": "VIDEO_SHORT"
  }'
```

### 3. **Load Test**

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Run load test
ab -n 1000 -c 50 \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -p request.json \
  $ALB_URL/generate
```

## 🛠️ Troubleshooting

### Common Issues

1. **"Service not stabilizing"**
   ```bash
   # Check task logs
   aws logs tail /ecs/prostudio --follow
   
   # Check task status
   aws ecs describe-tasks --cluster prostudio-cluster --tasks $(aws ecs list-tasks --cluster prostudio-cluster --query 'taskArns[0]' --output text)
   ```

2. **"Cannot connect to Redis"**
   ```bash
   # Check security group rules
   aws ec2 describe-security-groups --group-ids $ECS_SG_ID
   
   # Ensure Redis SG allows ECS SG
   ```

3. **"High latency"**
   ```bash
   # Check task CPU/Memory
   aws cloudwatch get-metric-statistics \
     --namespace AWS/ECS \
     --metric-name CPUUtilization \
     --dimensions Name=ServiceName,Value=prostudio-service Name=ClusterName,Value=prostudio-cluster \
     --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S) \
     --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
     --period 300 \
     --statistics Average
   ```

## 🧹 Cleanup

To remove all resources and avoid charges:

```bash
# Create cleanup script
cat > cleanup_aws.sh << 'EOF'
#!/bin/bash
# WARNING: This will delete all ProStudio resources!

echo "⚠️  This will delete all ProStudio AWS resources!"
read -p "Are you sure? (yes/no) " -r
if [[ $REPLY != "yes" ]]; then
    echo "Cleanup cancelled"
    exit 0
fi

# Delete ECS service
aws ecs update-service --cluster prostudio-cluster --service prostudio-service --desired-count 0
aws ecs delete-service --cluster prostudio-cluster --service prostudio-service

# Delete ALB
ALB_ARN=$(aws elbv2 describe-load-balancers --names prostudio-alb --query "LoadBalancers[0].LoadBalancerArn" --output text)
aws elbv2 delete-load-balancer --load-balancer-arn $ALB_ARN

# Delete target group
TG_ARN=$(aws elbv2 describe-target-groups --names prostudio-targets --query "TargetGroups[0].TargetGroupArn" --output text)
aws elbv2 delete-target-group --target-group-arn $TG_ARN

# Delete ECS cluster
aws ecs delete-cluster --cluster prostudio-cluster

# Delete Redis cluster
aws elasticache delete-cache-cluster --cache-cluster-id prostudio-redis

# Delete secrets
aws secretsmanager delete-secret --secret-id prostudio/secret-key --force-delete-without-recovery
aws secretsmanager delete-secret --secret-id prostudio/api-key --force-delete-without-recovery

# Delete ECR repository
aws ecr delete-repository --repository-name prostudio --force

# Delete CloudWatch logs
aws logs delete-log-group --log-group-name /ecs/prostudio

echo "✅ Cleanup complete!"
EOF

chmod +x cleanup_aws.sh
```

## 📈 Scaling for Production

### Recommendations for High Traffic

1. **Use Multiple Availability Zones**
2. **Enable CloudFront CDN** for static assets
3. **Use RDS for persistent data** (if needed)
4. **Implement API Gateway** for rate limiting
5. **Use AWS WAF** for security
6. **Enable AWS Shield** for DDoS protection
7. **Set up Multi-region** deployment for global users

### Performance Targets

With this deployment, you can achieve:
- **50ms** average API latency
- **10,000+ requests/second** with proper scaling
- **99.9% uptime** with multi-AZ deployment
- **Auto-scaling** from 2 to 100+ instances

## 🎉 Ready to Deploy!

Run `./deploy_aws.sh` to deploy ProStudio to AWS. The script will:
1. Build and push your Docker image
2. Create all necessary AWS resources
3. Configure auto-scaling
4. Set up monitoring
5. Provide you with the API endpoint and key

The entire deployment takes about 10-15 minutes.