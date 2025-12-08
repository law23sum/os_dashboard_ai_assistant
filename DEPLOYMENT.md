# Deployment Guide

This guide covers deploying the OS Dashboard AI Assistant to various platforms.

## Table of Contents

- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Heroku Deployment](#heroku-deployment)
- [Other Platform Options](#other-platform-options)

## Local Development

### Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd os_dashboard_ai_assistant
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Start development environment**
   ```bash
   # Basic development setup
   docker-compose up -d

   # Or full production stack
   docker-compose --profile full up -d

   # Or GUI desktop mode
   docker-compose --profile gui up -d
   ```

4. **View logs**
   ```bash
   docker-compose logs -f app
   ```

5. **Access the services**
   - Web API: http://localhost:8000
   - Database: localhost:5432
   - Redis: localhost:6379
   - Grafana (full profile): http://localhost:3000
   - Prometheus (full profile): http://localhost:9090
   - File Browser (full profile): http://localhost:8080

### Manual Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL and Redis**
   ```bash
   # Install PostgreSQL and Redis locally
   # Configure DATABASE_URL and REDIS_URL in your environment
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

## Docker Deployment

### Basic Development Setup

```bash
# Start basic development environment (app, postgres, redis, celery)
docker-compose up -d

# View logs
docker-compose logs -f app
```

### Full Production Stack

```bash
# Start complete production environment with monitoring
docker-compose --profile full up -d

# This includes: app, postgres, redis, elasticsearch, nginx, prometheus, grafana, filebrowser
```

### GUI Desktop Mode

```bash
# Run desktop GUI (requires X11 forwarding on Linux/Mac)
docker-compose --profile gui up -d
```

### Build Custom Image

```bash
# Build the image
docker build -t os-dashboard .

# Run with environment variables
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://postgres:osdashboard123@host:5432/osdashboard \
  -e REDIS_URL=redis://host:6379 \
  -e OPENAI_API_KEY=your-key \
  os-dashboard
```

### Available Profiles

The docker-compose.yml includes multiple profiles for different use cases:

- **default**: Basic development (app, postgres, redis, celery-worker)
- **full**: Complete production stack (+ elasticsearch, nginx, prometheus, grafana, filebrowser)
- **gui**: Desktop GUI mode (requires X11 display forwarding)

## Heroku Deployment

### Prerequisites

1. **Heroku CLI installed**
   ```bash
   # Install Heroku CLI
   # https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Heroku account and app created**
   ```bash
   heroku create your-app-name
   ```

### Database Setup

1. **Add PostgreSQL add-on**
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

2. **Add Redis add-on**
   ```bash
   heroku addons:create heroku-redis:hobby-dev
   ```

### Configuration

1. **Set environment variables**
   ```bash
   heroku config:set OPENAI_API_KEY=your-openai-key
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set LOG_LEVEL=INFO
   heroku config:set ENVIRONMENT=production

   # Database and Redis URLs are automatically set by add-ons
   ```

2. **Deploy to Heroku**
   ```bash
   git push heroku main
   ```

3. **Scale the application**
   ```bash
   heroku ps:scale web=1
   ```

4. **Add worker processes (if using Celery)**
   ```bash
   heroku ps:scale worker=1
   ```

### Monitoring

```bash
# View logs
heroku logs --tail

# Check app status
heroku ps

# View config
heroku config
```

## AWS Deployment (Recommended for Production)

### Prerequisites

1. **AWS CLI installed and configured**
   ```bash
   aws configure
   ```

2. **Docker installed**

3. **AWS Account with appropriate permissions**

### Infrastructure Components

- **ECS Fargate** - Container orchestration
- **RDS PostgreSQL** - Primary database
- **ElastiCache Redis** - Caching and background jobs
- **ECR** - Container registry
- **CloudFormation** - Infrastructure as code
- **VPC** - Network isolation
- **Application Load Balancer** - Traffic distribution
- **SSM Parameter Store** - Secrets management

### Quick Start Deployment

```bash
# Make deployment script executable
chmod +x deploy-aws.sh

# Full deployment (infrastructure + application)
./deploy-aws.sh prod deploy
```

### Step-by-Step Deployment

1. **Set AWS Region**
   ```bash
   export AWS_REGION=us-east-1
   ```

2. **Build and push Docker image**
   ```bash
   ./deploy-aws.sh prod build
   ```

3. **Deploy infrastructure**
   ```bash
   ./deploy-aws.sh prod infra
   ```

4. **Setup secrets**
   ```bash
   ./deploy-aws.sh prod secrets
   ```

5. **Register task definition**
   ```bash
   ./deploy-aws.sh prod task
   ```

6. **Update service**
   ```bash
   ./deploy-aws.sh prod service
   ```

### Environment Variables Setup

Store sensitive configuration in SSM Parameter Store:

```bash
# OpenAI API Key
aws ssm put-parameter --name "/prod/openai/key" --value "your-openai-key" --type "SecureString"

# Application Secret Key
aws ssm put-parameter --name "/prod/secret/key" --value "$(openssl rand -base64 32)" --type "SecureString"
```

### Scaling

**Horizontal Scaling:**
```bash
aws ecs update-service --cluster prod-cluster --service os-dashboard-service --desired-count 3
```

**Vertical Scaling:**
Update the task definition with higher CPU/memory values and redeploy.

### Monitoring

**CloudWatch Logs:**
```bash
aws logs tail /ecs/prod-os-dashboard --follow
```

**ECS Service Status:**
```bash
./deploy-aws.sh prod status
```

**Application Metrics:**
- Enable CloudWatch Container Insights
- Set up CloudWatch alarms for CPU/memory usage

### Cost Optimization

1. **Use Spot Instances** for non-critical workloads
2. **Auto Scaling** based on CPU utilization
3. **RDS Reserved Instances** for predictable database usage
4. **ElastiCache Reserved Nodes** for Redis

### Backup and Recovery

- **RDS Automated Backups** (enabled by default)
- **ElastiCache Snapshots** for Redis data
- **ECS Task Definition Versions** for rollbacks

## Other Platform Options

### Render

1. **Create Render account**
2. **Connect GitHub repository**
3. **Configure build settings:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn ai_os.app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
4. **Add PostgreSQL and Redis databases**
5. **Set environment variables**

### Railway

1. **Create Railway account**
2. **Deploy from GitHub**
3. **Configure environment variables**
4. **Add PostgreSQL and Redis plugins**

## Environment Variables

See `env.example` for all required environment variables.

## Troubleshooting

### Common Issues

1. **Port binding errors**
   - Ensure `$PORT` environment variable is used in production

2. **Database connection issues**
   - Verify DATABASE_URL format
   - Check database credentials

3. **Memory issues**
   - Increase dyno size on Heroku
   - Optimize Docker memory limits

4. **GUI not working**
   - GUI components require desktop environment
   - Use separate deployment for GUI vs web API

### Logs

```bash
# Docker logs
docker-compose logs

# Heroku logs
heroku logs --tail

# Application logs (inside container)
tail -f /app/logs/application.log
```

## Security Considerations

1. **Use HTTPS in production**
2. **Rotate API keys regularly**
3. **Use environment variables for secrets**
4. **Enable database backups**
5. **Configure proper CORS settings**
6. **Use secure headers**

## Performance Optimization

1. **Use gunicorn with multiple workers**
2. **Enable connection pooling**
3. **Configure proper caching**
4. **Optimize database queries**
5. **Use CDN for static assets**
6. **Enable compression**
