#!/bin/bash
#
# Simplified EC2 Setup for ProStudio
# 

echo "🚀 ProStudio Simple EC2 Setup"
echo "============================="

# Get the existing instance ID
INSTANCE_ID="i-0474aef21e74f44a9"

# Terminate the stuck instance
echo "Terminating stuck instance..."
aws ec2 terminate-instances --instance-ids $INSTANCE_ID
echo "✓ Instance termination initiated"

# Wait for termination
echo "Waiting for instance to terminate..."
aws ec2 wait instance-terminated --instance-ids $INSTANCE_ID
echo "✓ Instance terminated"

# Use existing key pair
KEY_NAME="prostudio-key"
echo "Using existing key pair: $KEY_NAME"

# Get default VPC
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query "Vpcs[0].VpcId" --output text)
echo "Using VPC: $VPC_ID"

# Use existing security group or create new one
SG_NAME="prostudio-sg-simple"
SG_ID=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=$SG_NAME" --query "SecurityGroups[0].GroupId" --output text 2>/dev/null)

if [ "$SG_ID" == "None" ] || [ -z "$SG_ID" ]; then
    echo "Creating security group..."
    SG_ID=$(aws ec2 create-security-group \
        --group-name $SG_NAME \
        --description "ProStudio Simple Security Group" \
        --vpc-id $VPC_ID \
        --query 'GroupId' \
        --output text)
    
    # Add rules
    aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 22 --cidr 0.0.0.0/0
    aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0
    echo "✓ Security group created: $SG_ID"
else
    echo "Using existing security group: $SG_ID"
fi

# Get latest Ubuntu 22.04 AMI
AMI_ID=$(aws ec2 describe-images \
    --owners 099720109477 \
    --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
    --query 'Images[0].ImageId' \
    --output text)
echo "Using AMI: $AMI_ID"

# Simplified user data - just install Docker
cat > user-data.sh << 'EOF'
#!/bin/bash
apt-get update
apt-get install -y docker.io docker-compose git
systemctl start docker
systemctl enable docker

# Add ubuntu user to docker group
usermod -aG docker ubuntu

# Create simple test
mkdir -p /home/ubuntu/prostudio
cat > /home/ubuntu/prostudio/docker-compose.yml << 'COMPOSE'
version: '3.8'
services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./index.html:/usr/share/nginx/html/index.html
COMPOSE

cat > /home/ubuntu/prostudio/index.html << 'HTML'
<!DOCTYPE html>
<html>
<head><title>ProStudio</title></head>
<body>
<h1>ProStudio EC2 Deployment</h1>
<p>Docker is ready! Now deploy the full ProStudio stack.</p>
</body>
</html>
HTML

cd /home/ubuntu/prostudio
docker-compose up -d
EOF

# Launch instance
echo "Launching EC2 instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type t2.micro \
    --key-name $KEY_NAME \
    --security-group-ids $SG_ID \
    --user-data file://user-data.sh \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=prostudio-simple}]" \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "✓ Instance launched: $INSTANCE_ID"

# Wait for instance
echo "Waiting for instance to start..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo ""
echo "✅ EC2 Instance Ready!"
echo "===================="
echo "Instance ID: $INSTANCE_ID"
echo "Public IP: $PUBLIC_IP"
echo ""
echo "SSH: ssh -i ${KEY_NAME}.pem ubuntu@$PUBLIC_IP"
echo "Web: http://$PUBLIC_IP"
echo ""
echo "Wait 2-3 minutes for Docker installation, then deploy ProStudio manually."

# Clean up
rm -f user-data.sh