#!/bin/bash
# ProStudio AWS Deployment Script
# ================================

set -e  # Exit on error

echo "🚀 ProStudio AWS Deployment"
echo "==========================="
echo

# Configuration
AWS_REGION=${AWS_REGION:-us-east-1}
AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID:-$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "YOUR_ACCOUNT_ID")}
CLUSTER_NAME="prostudio-cluster"
SERVICE_NAME="prostudio-service"
TASK_FAMILY="prostudio-task"
ECR_REPO="prostudio"
REDIS_CLUSTER_ID="prostudio-redis"
ALB_NAME="prostudio-alb"
TARGET_GROUP_NAME="prostudio-targets"
VPC_NAME="prostudio-vpc"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        echo -e "${RED}❌ AWS CLI not found${NC}"
        echo "Please install AWS CLI: https://aws.amazon.com/cli/"
        exit 1
    fi
    echo -e "${GREEN}✓ AWS CLI found${NC}"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker not found${NC}"
        echo "Please install Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker found${NC}"
}

check_aws_credentials() {
    if ! aws sts get-caller-identity &> /dev/null; then
        echo -e "${RED}❌ AWS credentials not configured${NC}"
        echo "Please run: aws configure"
        exit 1
    fi
    echo -e "${GREEN}✓ AWS credentials configured${NC}"
    echo "  Account ID: $AWS_ACCOUNT_ID"
    echo "  Region: $AWS_REGION"
}

# Main deployment steps
echo "🔍 Checking prerequisites..."
check_aws_cli
check_docker
check_aws_credentials

echo
echo "📋 Deployment Configuration:"
echo "  Cluster: $CLUSTER_NAME"
echo "  Service: $SERVICE_NAME"
echo "  Region: $AWS_REGION"
echo
read -p "Continue with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled"
    exit 0
fi

# Step 1: Create ECR Repository
echo
echo "1️⃣ Creating ECR Repository..."
aws ecr describe-repositories --repository-names $ECR_REPO --region $AWS_REGION 2>/dev/null || \
aws ecr create-repository \
    --repository-name $ECR_REPO \
    --region $AWS_REGION \
    --image-scanning-configuration scanOnPush=true \
    --encryption-configuration encryptionType=AES256

ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO"
echo -e "${GREEN}✓ ECR repository ready: $ECR_URI${NC}"

# Step 2: Build and Push Docker Image
echo
echo "2️⃣ Building and pushing Docker image..."

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URI

# Build image
echo "Building Docker image..."
docker build -t $ECR_REPO:latest .

# Tag and push
docker tag $ECR_REPO:latest $ECR_URI:latest
docker push $ECR_URI:latest

echo -e "${GREEN}✓ Docker image pushed to ECR${NC}"

# Step 3: Create VPC (if needed)
echo
echo "3️⃣ Setting up VPC..."
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=tag:Name,Values=$VPC_NAME" --query "Vpcs[0].VpcId" --output text 2>/dev/null)

if [ "$VPC_ID" == "None" ] || [ -z "$VPC_ID" ]; then
    echo "Creating new VPC..."
    VPC_ID=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 --query 'Vpc.VpcId' --output text)
    aws ec2 create-tags --resources $VPC_ID --tags Key=Name,Value=$VPC_NAME
    
    # Enable DNS
    aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-support
    aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-hostnames
    
    # Create subnets
    SUBNET1_ID=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.1.0/24 --availability-zone ${AWS_REGION}a --query 'Subnet.SubnetId' --output text)
    SUBNET2_ID=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.2.0/24 --availability-zone ${AWS_REGION}b --query 'Subnet.SubnetId' --output text)
    
    # Create Internet Gateway
    IGW_ID=$(aws ec2 create-internet-gateway --query 'InternetGateway.InternetGatewayId' --output text)
    aws ec2 attach-internet-gateway --vpc-id $VPC_ID --internet-gateway-id $IGW_ID
    
    # Create route table
    ROUTE_TABLE_ID=$(aws ec2 create-route-table --vpc-id $VPC_ID --query 'RouteTable.RouteTableId' --output text)
    aws ec2 create-route --route-table-id $ROUTE_TABLE_ID --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID
    aws ec2 associate-route-table --subnet-id $SUBNET1_ID --route-table-id $ROUTE_TABLE_ID
    aws ec2 associate-route-table --subnet-id $SUBNET2_ID --route-table-id $ROUTE_TABLE_ID
else
    echo "Using existing VPC: $VPC_ID"
    SUBNET1_ID=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query "Subnets[0].SubnetId" --output text)
    SUBNET2_ID=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query "Subnets[1].SubnetId" --output text)
fi

echo -e "${GREEN}✓ VPC configured${NC}"

# Step 4: Create Security Groups
echo
echo "4️⃣ Creating Security Groups..."

# ALB Security Group
ALB_SG_ID=$(aws ec2 create-security-group \
    --group-name prostudio-alb-sg \
    --description "ProStudio ALB Security Group" \
    --vpc-id $VPC_ID \
    --query 'GroupId' \
    --output text 2>/dev/null || \
    aws ec2 describe-security-groups --filters "Name=group-name,Values=prostudio-alb-sg" --query "SecurityGroups[0].GroupId" --output text)

aws ec2 authorize-security-group-ingress --group-id $ALB_SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0 2>/dev/null || true
aws ec2 authorize-security-group-ingress --group-id $ALB_SG_ID --protocol tcp --port 443 --cidr 0.0.0.0/0 2>/dev/null || true

# ECS Security Group
ECS_SG_ID=$(aws ec2 create-security-group \
    --group-name prostudio-ecs-sg \
    --description "ProStudio ECS Security Group" \
    --vpc-id $VPC_ID \
    --query 'GroupId' \
    --output text 2>/dev/null || \
    aws ec2 describe-security-groups --filters "Name=group-name,Values=prostudio-ecs-sg" --query "SecurityGroups[0].GroupId" --output text)

aws ec2 authorize-security-group-ingress --group-id $ECS_SG_ID --protocol tcp --port 8000 --source-group $ALB_SG_ID 2>/dev/null || true

echo -e "${GREEN}✓ Security groups configured${NC}"

# Step 5: Create ElastiCache Redis Cluster
echo
echo "5️⃣ Creating Redis Cluster..."

# Create subnet group for Redis
aws elasticache create-cache-subnet-group \
    --cache-subnet-group-name prostudio-redis-subnet \
    --cache-subnet-group-description "ProStudio Redis Subnet Group" \
    --subnet-ids $SUBNET1_ID $SUBNET2_ID 2>/dev/null || true

# Create Redis cluster
REDIS_ENDPOINT=$(aws elasticache describe-cache-clusters \
    --cache-cluster-id $REDIS_CLUSTER_ID \
    --query "CacheClusters[0].CacheNodes[0].Endpoint.Address" \
    --output text 2>/dev/null)

if [ "$REDIS_ENDPOINT" == "None" ] || [ -z "$REDIS_ENDPOINT" ]; then
    echo "Creating new Redis cluster..."
    aws elasticache create-cache-cluster \
        --cache-cluster-id $REDIS_CLUSTER_ID \
        --cache-node-type cache.t3.micro \
        --engine redis \
        --engine-version 7.0 \
        --num-cache-nodes 1 \
        --cache-subnet-group-name prostudio-redis-subnet \
        --security-group-ids $ECS_SG_ID
    
    echo "Waiting for Redis cluster to be available..."
    aws elasticache wait cache-cluster-available --cache-cluster-id $REDIS_CLUSTER_ID
    
    REDIS_ENDPOINT=$(aws elasticache describe-cache-clusters \
        --cache-cluster-id $REDIS_CLUSTER_ID \
        --query "CacheClusters[0].CacheNodes[0].Endpoint.Address" \
        --output text)
fi

echo -e "${GREEN}✓ Redis cluster endpoint: $REDIS_ENDPOINT${NC}"

# Step 6: Create ECS Cluster
echo
echo "6️⃣ Creating ECS Cluster..."

aws ecs create-cluster --cluster-name $CLUSTER_NAME --region $AWS_REGION 2>/dev/null || true

# Enable Container Insights
aws ecs put-cluster-settings \
    --cluster $CLUSTER_NAME \
    --name containerInsights \
    --value enabled

echo -e "${GREEN}✓ ECS cluster created${NC}"

# Step 7: Create Task Definition
echo
echo "7️⃣ Creating Task Definition..."

# Create CloudWatch log group
aws logs create-log-group --log-group-name /ecs/prostudio --region $AWS_REGION 2>/dev/null || true

# Generate secrets
SECRET_KEY=$(openssl rand -hex 32)
API_KEY=$(openssl rand -hex 32)

# Store secrets in AWS Secrets Manager
aws secretsmanager create-secret \
    --name prostudio/secret-key \
    --secret-string $SECRET_KEY \
    --region $AWS_REGION 2>/dev/null || \
    aws secretsmanager update-secret \
    --secret-id prostudio/secret-key \
    --secret-string $SECRET_KEY \
    --region $AWS_REGION

aws secretsmanager create-secret \
    --name prostudio/api-key \
    --secret-string $API_KEY \
    --region $AWS_REGION 2>/dev/null || \
    aws secretsmanager update-secret \
    --secret-id prostudio/api-key \
    --secret-string $API_KEY \
    --region $AWS_REGION

# Create task definition
cat > task-definition.json << EOF
{
  "family": "$TASK_FAMILY",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "containerDefinitions": [
    {
      "name": "prostudio",
      "image": "$ECR_URI:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "PROSTUDIO_ENV", "value": "production"},
        {"name": "REDIS_HOST", "value": "$REDIS_ENDPOINT"},
        {"name": "ENABLE_GPU", "value": "false"},
        {"name": "ENABLE_METRICS", "value": "true"},
        {"name": "API_WORKERS", "value": "4"}
      ],
      "secrets": [
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:$AWS_REGION:$AWS_ACCOUNT_ID:secret:prostudio/secret-key"
        },
        {
          "name": "API_KEY",
          "valueFrom": "arn:aws:secretsmanager:$AWS_REGION:$AWS_ACCOUNT_ID:secret:prostudio/api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/prostudio",
          "awslogs-region": "$AWS_REGION",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ],
  "taskRoleArn": "arn:aws:iam::$AWS_ACCOUNT_ID:role/ecsTaskExecutionRole",
  "executionRoleArn": "arn:aws:iam::$AWS_ACCOUNT_ID:role/ecsTaskExecutionRole"
}
EOF

# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json --region $AWS_REGION

echo -e "${GREEN}✓ Task definition registered${NC}"

# Step 8: Create Application Load Balancer
echo
echo "8️⃣ Creating Load Balancer..."

# Create ALB
ALB_ARN=$(aws elbv2 describe-load-balancers --names $ALB_NAME --query "LoadBalancers[0].LoadBalancerArn" --output text 2>/dev/null)

if [ "$ALB_ARN" == "None" ] || [ -z "$ALB_ARN" ]; then
    ALB_ARN=$(aws elbv2 create-load-balancer \
        --name $ALB_NAME \
        --subnets $SUBNET1_ID $SUBNET2_ID \
        --security-groups $ALB_SG_ID \
        --scheme internet-facing \
        --type application \
        --query 'LoadBalancers[0].LoadBalancerArn' \
        --output text)
    
    echo "Waiting for ALB to be active..."
    aws elbv2 wait load-balancer-available --load-balancer-arns $ALB_ARN
fi

ALB_DNS=$(aws elbv2 describe-load-balancers --load-balancer-arns $ALB_ARN --query "LoadBalancers[0].DNSName" --output text)

# Create target group
TG_ARN=$(aws elbv2 create-target-group \
    --name $TARGET_GROUP_NAME \
    --protocol HTTP \
    --port 8000 \
    --vpc-id $VPC_ID \
    --target-type ip \
    --health-check-enabled \
    --health-check-path /health \
    --health-check-interval-seconds 30 \
    --health-check-timeout-seconds 5 \
    --healthy-threshold-count 2 \
    --unhealthy-threshold-count 3 \
    --query 'TargetGroups[0].TargetGroupArn' \
    --output text 2>/dev/null || \
    aws elbv2 describe-target-groups --names $TARGET_GROUP_NAME --query "TargetGroups[0].TargetGroupArn" --output text)

# Create listener
aws elbv2 create-listener \
    --load-balancer-arn $ALB_ARN \
    --protocol HTTP \
    --port 80 \
    --default-actions Type=forward,TargetGroupArn=$TG_ARN 2>/dev/null || true

echo -e "${GREEN}✓ Load balancer configured${NC}"
echo "  URL: http://$ALB_DNS"

# Step 9: Create ECS Service
echo
echo "9️⃣ Creating ECS Service..."

# Create service
aws ecs create-service \
    --cluster $CLUSTER_NAME \
    --service-name $SERVICE_NAME \
    --task-definition $TASK_FAMILY:1 \
    --desired-count 3 \
    --launch-type FARGATE \
    --platform-version LATEST \
    --network-configuration "awsvpcConfiguration={subnets=[$SUBNET1_ID,$SUBNET2_ID],securityGroups=[$ECS_SG_ID],assignPublicIp=ENABLED}" \
    --load-balancers targetGroupArn=$TG_ARN,containerName=prostudio,containerPort=8000 \
    --health-check-grace-period-seconds 60 \
    --deployment-configuration "maximumPercent=200,minimumHealthyPercent=100" 2>/dev/null || \
    aws ecs update-service \
        --cluster $CLUSTER_NAME \
        --service $SERVICE_NAME \
        --desired-count 3

echo -e "${GREEN}✓ ECS service created${NC}"

# Step 10: Configure Auto Scaling
echo
echo "🔟 Configuring Auto Scaling..."

# Register scalable target
aws application-autoscaling register-scalable-target \
    --service-namespace ecs \
    --resource-id service/$CLUSTER_NAME/$SERVICE_NAME \
    --scalable-dimension ecs:service:DesiredCount \
    --min-capacity 2 \
    --max-capacity 10

# Create scaling policy (CPU)
aws application-autoscaling put-scaling-policy \
    --policy-name prostudio-cpu-scaling \
    --service-namespace ecs \
    --resource-id service/$CLUSTER_NAME/$SERVICE_NAME \
    --scalable-dimension ecs:service:DesiredCount \
    --policy-type TargetTrackingScaling \
    --target-tracking-scaling-policy-configuration '{
        "TargetValue": 70.0,
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
        },
        "ScaleInCooldown": 300,
        "ScaleOutCooldown": 60
    }'

# Create scaling policy (Memory)
aws application-autoscaling put-scaling-policy \
    --policy-name prostudio-memory-scaling \
    --service-namespace ecs \
    --resource-id service/$CLUSTER_NAME/$SERVICE_NAME \
    --scalable-dimension ecs:service:DesiredCount \
    --policy-type TargetTrackingScaling \
    --target-tracking-scaling-policy-configuration '{
        "TargetValue": 80.0,
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "ECSServiceAverageMemoryUtilization"
        },
        "ScaleInCooldown": 300,
        "ScaleOutCooldown": 60
    }'

echo -e "${GREEN}✓ Auto scaling configured${NC}"

# Final output
echo
echo "✅ DEPLOYMENT COMPLETE!"
echo "======================="
echo
echo "📋 Deployment Summary:"
echo "  • ECS Cluster: $CLUSTER_NAME"
echo "  • Service: $SERVICE_NAME"
echo "  • Load Balancer URL: http://$ALB_DNS"
echo "  • Redis Endpoint: $REDIS_ENDPOINT"
echo "  • API Key: $API_KEY"
echo
echo "📊 Next Steps:"
echo "1. Wait 2-3 minutes for service to stabilize"
echo "2. Test the API:"
echo "   curl http://$ALB_DNS/health"
echo
echo "3. Test content generation:"
echo "   curl -X POST http://$ALB_DNS/generate \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -H 'X-API-Key: $API_KEY' \\"
echo "     -d '{\"concept\": \"AI productivity tips\", \"platform\": \"TIKTOK\"}'"
echo
echo "4. View logs:"
echo "   aws logs tail /ecs/prostudio --follow"
echo
echo "5. Monitor service:"
echo "   aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICE_NAME"
echo
echo "⚠️  IMPORTANT: Save your API key for future use!"
echo "   API Key: $API_KEY"
echo
echo "🎉 ProStudio is now running on AWS!"

# Save deployment info
cat > deployment-info.json << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "region": "$AWS_REGION",
  "cluster": "$CLUSTER_NAME",
  "service": "$SERVICE_NAME",
  "alb_url": "http://$ALB_DNS",
  "api_key": "$API_KEY",
  "redis_endpoint": "$REDIS_ENDPOINT",
  "ecr_uri": "$ECR_URI"
}
EOF

echo
echo "Deployment info saved to: deployment-info.json"