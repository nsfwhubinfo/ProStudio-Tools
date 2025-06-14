#!/bin/bash
# EC2 Free Tier Setup Script for ProStudio
# ========================================
# This script provisions a t2.micro instance with everything needed
# to run ProStudio with zero initial cost

set -e

# Configuration
AWS_REGION=${AWS_REGION:-us-east-1}
INSTANCE_TYPE="t2.micro"
KEY_NAME=${KEY_NAME:-prostudio-key}
SECURITY_GROUP_NAME="prostudio-free-tier-sg"
INSTANCE_NAME="prostudio-free-tier"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🚀 ProStudio Zero-Cost EC2 Setup"
echo "================================"
echo

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found. Please install it first.${NC}"
    exit 1
fi

# Check if already deployed
EXISTING_INSTANCE=$(aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=$INSTANCE_NAME" \
              "Name=instance-state-name,Values=running" \
    --query "Reservations[0].Instances[0].InstanceId" \
    --output text 2>/dev/null || echo "None")

if [ "$EXISTING_INSTANCE" != "None" ] && [ -n "$EXISTING_INSTANCE" ]; then
    echo -e "${YELLOW}⚠️  Instance already exists: $EXISTING_INSTANCE${NC}"
    read -p "Do you want to continue with the existing instance? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
    INSTANCE_ID=$EXISTING_INSTANCE
else
    # Create key pair if it doesn't exist
    if ! aws ec2 describe-key-pairs --key-names $KEY_NAME &>/dev/null; then
        echo "Creating SSH key pair..."
        aws ec2 create-key-pair --key-name $KEY_NAME --query 'KeyMaterial' --output text > ${KEY_NAME}.pem
        chmod 400 ${KEY_NAME}.pem
        echo -e "${GREEN}✓ Key pair created: ${KEY_NAME}.pem${NC}"
    fi

    # Get default VPC
    VPC_ID=$(aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query "Vpcs[0].VpcId" --output text)
    echo "Using VPC: $VPC_ID"

    # Create security group
    SG_ID=$(aws ec2 describe-security-groups \
        --filters "Name=group-name,Values=$SECURITY_GROUP_NAME" \
        --query "SecurityGroups[0].GroupId" \
        --output text 2>/dev/null || echo "None")

    if [ "$SG_ID" == "None" ]; then
        echo "Creating security group..."
        SG_ID=$(aws ec2 create-security-group \
            --group-name $SECURITY_GROUP_NAME \
            --description "Security group for ProStudio free tier deployment" \
            --vpc-id $VPC_ID \
            --query 'GroupId' \
            --output text)
        
        # Add rules
        aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 22 --cidr 0.0.0.0/0
        aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0
        aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 443 --cidr 0.0.0.0/0
        
        echo -e "${GREEN}✓ Security group created: $SG_ID${NC}"
    fi

    # Get latest Ubuntu 22.04 AMI
    AMI_ID=$(aws ec2 describe-images \
        --owners 099720109477 \
        --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
                  "Name=state,Values=available" \
        --query "sort_by(Images, &CreationDate)[-1].ImageId" \
        --output text)
    
    echo "Using AMI: $AMI_ID"

    # Create user data script
    cat > user-data.sh << 'USERDATA'
#!/bin/bash
# EC2 User Data Script for ProStudio Setup

# Update system
apt-get update
apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker ubuntu

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install additional tools
apt-get install -y git htop ncdu jq aws-cli

# Create directory structure
mkdir -p /home/ubuntu/prostudio/{logs,cache,ssl}
cd /home/ubuntu/prostudio

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    container_name: prostudio-redis
    command: >
      redis-server
      --maxmemory 256mb
      --maxmemory-policy allkeys-lru
      --save 60 1
      --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  app:
    image: ghcr.io/YOUR_GITHUB_USERNAME/prostudio:latest
    container_name: prostudio-app
    environment:
      - PROSTUDIO_ENV=production
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - API_WORKERS=2
      - ENABLE_METRICS=true
    depends_on:
      redis:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
      - ./cache:/app/cache
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    container_name: prostudio-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - app
    restart: unless-stopped

volumes:
  redis_data:
EOF

# Create nginx.conf
cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server app:8000;
    }
    
    server {
        listen 80;
        server_name _;
        
        location /health {
            proxy_pass http://backend/health;
            access_log off;
        }
        
        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
EOF

# Set proper permissions
chown -R ubuntu:ubuntu /home/ubuntu/prostudio

# Create systemd service for auto-start
cat > /etc/systemd/system/prostudio.service << 'EOF'
[Unit]
Description=ProStudio Docker Compose Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ubuntu/prostudio
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0
User=ubuntu
Group=ubuntu

[Install]
WantedBy=multi-user.target
EOF

# Enable the service
systemctl daemon-reload
systemctl enable prostudio.service

# Setup swap (important for t2.micro with only 1GB RAM)
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab

# Configure system for better performance
cat >> /etc/sysctl.conf << 'EOF'
# Network optimizations
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.ip_local_port_range = 1024 65535
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 30

# Memory optimizations
vm.swappiness = 10
vm.overcommit_memory = 1
EOF

sysctl -p

# Install CloudWatch agent (optional, for monitoring)
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
dpkg -i -E ./amazon-cloudwatch-agent.deb
rm amazon-cloudwatch-agent.deb

# Signal completion
touch /home/ubuntu/prostudio/.setup-complete

echo "ProStudio setup complete!"
USERDATA

    # Launch instance
    echo "Launching EC2 instance..."
    INSTANCE_ID=$(aws ec2 run-instances \
        --image-id $AMI_ID \
        --instance-type $INSTANCE_TYPE \
        --key-name $KEY_NAME \
        --security-group-ids $SG_ID \
        --user-data file://user-data.sh \
        --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME},{Key=Project,Value=ProStudio},{Key=Environment,Value=free-tier}]" \
        --metadata-options "HttpTokens=optional,HttpPutResponseHopLimit=2,HttpEndpoint=enabled" \
        --monitoring Enabled=false \
        --instance-initiated-shutdown-behavior stop \
        --query 'Instances[0].InstanceId' \
        --output text)
    
    echo -e "${GREEN}✓ Instance launched: $INSTANCE_ID${NC}"
    
    # Wait for instance to be running
    echo "Waiting for instance to start..."
    aws ec2 wait instance-running --instance-ids $INSTANCE_ID
    
    # Wait for status checks
    echo "Waiting for instance to be ready..."
    aws ec2 wait instance-status-ok --instance-ids $INSTANCE_ID
fi

# Get instance details
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

PUBLIC_DNS=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicDnsName' \
    --output text)

# Clean up
rm -f user-data.sh

# Output summary
echo
echo "✅ EC2 Setup Complete!"
echo "====================="
echo
echo "Instance Details:"
echo "  ID: $INSTANCE_ID"
echo "  Type: $INSTANCE_TYPE (Free Tier)"
echo "  Public IP: $PUBLIC_IP"
echo "  Public DNS: $PUBLIC_DNS"
echo
echo "SSH Access:"
echo "  ssh -i ${KEY_NAME}.pem ubuntu@$PUBLIC_IP"
echo
echo "Web Access:"
echo "  http://$PUBLIC_IP"
echo
echo "Next Steps:"
echo "1. Wait 3-5 minutes for initial setup to complete"
echo "2. Update docker-compose.yml with your GitHub container registry"
echo "3. Pull and start your containers"
echo
echo "To check setup progress:"
echo "  ssh -i ${KEY_NAME}.pem ubuntu@$PUBLIC_IP 'tail -f /var/log/cloud-init-output.log'"
echo
echo "To start services manually:"
echo "  ssh -i ${KEY_NAME}.pem ubuntu@$PUBLIC_IP"
echo "  cd /home/ubuntu/prostudio"
echo "  docker-compose up -d"
echo
echo "Monthly Cost: \$0 (within AWS Free Tier limits)"
echo "  - EC2 t2.micro: 750 hours/month free"
echo "  - EBS storage: 30 GB free"
echo "  - Data transfer: 15 GB free"

# Save instance info
cat > instance-info.json << EOF
{
  "instance_id": "$INSTANCE_ID",
  "public_ip": "$PUBLIC_IP",
  "public_dns": "$PUBLIC_DNS",
  "key_name": "$KEY_NAME",
  "security_group": "$SG_ID",
  "region": "$AWS_REGION",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

echo
echo "Instance info saved to: instance-info.json"