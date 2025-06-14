# EC2 Deployment Guide for DevPrompt Studio

## Prerequisites Installed ✅
- Docker CE
- Node.js 18.x
- PowerShell
- Git

## Next Steps

### Step 1: Clone Your Repository
```bash
git clone <YOUR_PROJECT_GIT_URL> prostudio
cd prostudio/devprompt-studio
```

### Step 2: Set Up Database with Docker
```bash
# Create Docker network for better container communication
docker network create prostudio-network

# Run PostgreSQL with the same password from your local setup
docker run --name prostudio-db \
  --network prostudio-network \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=3odcx62izogEY1rH \
  -e POSTGRES_DB=devprompt-studio \
  -p 5432:5432 \
  -d \
  -v prostudio_db_data:/var/lib/postgresql/data \
  --restart always \
  postgres:15

# Verify it's running
docker ps
```

### Step 3: Configure Environment
```bash
# Copy environment example
cp .env.example .env

# Update .env with production values
cat > .env << 'EOF'
# Auth Secret (generate a new one for production)
AUTH_SECRET="$(openssl rand -base64 32)"

# Database (using Docker container)
DATABASE_URL="postgresql://postgres:3odcx62izogEY1rH@localhost:5432/devprompt-studio"

# NextAuth URL - Update with your EC2 public IP or domain
NEXTAUTH_URL="http://YOUR_EC2_PUBLIC_IP:3000"

# Tenxsom AI Integration (if applicable)
TENXSOM_API_URL="http://localhost:8000"
TENXSOM_API_KEY=""
TENXSOM_WS_URL="ws://localhost:8000"
EOF
```

### Step 4: Install Dependencies & Build
```bash
# Install dependencies
npm install

# Push database schema
npm run db:push

# Build for production
npm run build
```

### Step 5: Run with PM2 (Production Process Manager)
```bash
# Install PM2 globally
npm install -g pm2

# Start the application
pm2 start npm --name "devprompt-studio" -- start

# Save PM2 configuration
pm2 save
pm2 startup

# Monitor the app
pm2 monit
```

### Step 6: Configure Nginx (Optional but Recommended)
```bash
# Install Nginx
sudo apt-get install -y nginx

# Create Nginx configuration
sudo tee /etc/nginx/sites-available/devprompt-studio << 'EOF'
server {
    listen 80;
    server_name YOUR_EC2_PUBLIC_IP;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable the site
sudo ln -s /etc/nginx/sites-available/devprompt-studio /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 7: Configure EC2 Security Group
In AWS Console, ensure your security group allows:
- Port 80 (HTTP) - if using Nginx
- Port 3000 (Node.js) - if accessing directly
- Port 22 (SSH) - for management

### Step 8: Set Up SSL with Let's Encrypt (Optional)
```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get SSL certificate (replace with your domain)
sudo certbot --nginx -d your-domain.com
```

## Docker Compose Alternative (Recommended)

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    container_name: prostudio-db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: 3odcx62izogEY1rH
      POSTGRES_DB: devprompt-studio
    volumes:
      - prostudio_db_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: always
    networks:
      - prostudio-network

  app:
    build: .
    container_name: devprompt-studio
    environment:
      DATABASE_URL: postgresql://postgres:3odcx62izogEY1rH@db:5432/devprompt-studio
      NODE_ENV: production
    ports:
      - "3000:3000"
    depends_on:
      - db
    restart: always
    networks:
      - prostudio-network

volumes:
  prostudio_db_data:

networks:
  prostudio-network:
    driver: bridge
```

Create `Dockerfile`:
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy application files
COPY . .

# Build the application
RUN npm run build

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
```

Then run:
```bash
docker-compose up -d
```

## Monitoring & Maintenance

### View Logs
```bash
# PM2 logs
pm2 logs devprompt-studio

# Docker logs
docker logs prostudio-db
docker logs devprompt-studio
```

### Backup Database
```bash
# Create backup
docker exec prostudio-db pg_dump -U postgres devprompt-studio > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
docker exec -i prostudio-db psql -U postgres devprompt-studio < backup_file.sql
```

### Update Application
```bash
# Pull latest code
git pull

# Rebuild and restart
npm install
npm run build
pm2 restart devprompt-studio
```

## Troubleshooting

1. **Database Connection Issues**
   ```bash
   # Check if database is running
   docker ps
   
   # Test connection
   docker exec -it prostudio-db psql -U postgres -d devprompt-studio
   ```

2. **Port Already in Use**
   ```bash
   # Find process using port
   sudo lsof -i :3000
   
   # Kill if needed
   sudo kill -9 <PID>
   ```

3. **Memory Issues**
   ```bash
   # Check memory usage
   free -h
   
   # Increase swap if needed
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

## Security Checklist

- [ ] Change default database password
- [ ] Set strong AUTH_SECRET
- [ ] Configure firewall (ufw)
- [ ] Enable SSL/TLS
- [ ] Regular security updates
- [ ] Backup strategy in place
- [ ] Monitor logs for suspicious activity

## Performance Optimization

1. **Enable Node.js Cluster Mode**
   ```bash
   pm2 start npm --name "devprompt-studio" -i max -- start
   ```

2. **Configure Nginx Caching**
   Add to Nginx config:
   ```nginx
   location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
       expires 1y;
       add_header Cache-Control "public, immutable";
   }
   ```

3. **Database Optimization**
   ```bash
   # Connect to database
   docker exec -it prostudio-db psql -U postgres -d devprompt-studio
   
   # Run ANALYZE
   ANALYZE;
   ```

Your EC2 instance is now ready for deployment! Follow these steps to get DevPrompt Studio running in production.