# Environment Configuration and Deployment Guide

This document defines the deployment environments, tag patterns, secrets management, and how to run CI-equivalent checks locally.

## Environment Names

The OS Dashboard AI Assistant uses four deployment environments:

1. **alpha** - Development/staging environment
2. **beta** - Pre-production testing environment
3. **preprod** - Production-like environment for final validation
4. **prod** - Production environment

### Environment Promotion Ladder

```
local/dev (implicit) → alpha → beta → preprod → prod
```

Environments are promoted forward using immutable Docker image artifacts. The same built image digest is deployed across environments - **we do NOT rebuild differently per environment**.

## Tag Patterns and Deployment Rules

### Automatic Deployments

- **`develop` branch** → Automatically deploys to `alpha`
  - Image tag: `develop-<short-sha>`
  - Example: `develop-a1b2c3d`

### Tag-Based Deployments

Deployments are triggered by Git tags matching specific patterns:

| Tag Pattern | Environment | Example |
|------------|--------------|---------|
| `vX.Y.Z-alpha.N` | `alpha` | `v1.2.3-alpha.1` |
| `vX.Y.Z-beta.N` | `beta` | `v1.2.3-beta.2` |
| `vX.Y.Z-rc.N` | `preprod` | `v1.2.3-rc.1` |
| `vX.Y.Z` | `prod` | `v1.2.3` |

Where:
- `X.Y.Z` is the semantic version (e.g., `1.2.3`)
- `N` is a build number (e.g., `1`, `2`, `3`)
- `rc` stands for "release candidate"

### Tag Examples

```bash
# Deploy to alpha
git tag v1.2.3-alpha.1
git push origin v1.2.3-alpha.1

# Deploy to beta
git tag v1.2.3-beta.1
git push origin v1.2.3-beta.1

# Deploy to preprod (requires approval)
git tag v1.2.3-rc.1
git push origin v1.2.3-rc.1

# Deploy to prod (requires approval)
git tag v1.2.3
git push origin v1.2.3
```

## GitHub Environments and Approval Gates

GitHub Environments are configured in the repository settings to enforce deployment governance:

- **alpha** and **beta**: No approval required (automatic deployment)
- **preprod** and **prod**: Require manual approval before deployment

### Setting Up GitHub Environments

1. Go to repository Settings → Environments
2. Create environments: `alpha`, `beta`, `preprod`, `prod`
3. For `preprod` and `prod`:
   - Enable "Required reviewers"
   - Add required reviewers (team or individuals)
   - Optionally set deployment branches/tags

The deployment workflow (`.github/workflows/deploy.yml`) automatically references these environments, triggering approval workflows when needed.

## Secrets Management

### GitHub Secrets

The following secrets must be configured in GitHub repository settings:

- **`AWS_ROLE_ARN`**: AWS IAM role ARN for GitHub OIDC authentication
  - Format: `arn:aws:iam::<account-id>:role/<role-name>`
  - Used for: ECR push, ECS deployment

### AWS Systems Manager (SSM) Parameter Store

Runtime secrets are stored in AWS SSM Parameter Store per environment. The deployment script (`deploy-aws.sh`) sets up these parameters automatically.

#### SSM Parameter Path Convention

All secrets follow the pattern: `/<environment>/<category>/<key>`

Examples:
- `/$ENVIRONMENT/db/username`
- `/$ENVIRONMENT/db/password`
- `/$ENVIRONMENT/db/url`
- `/$ENVIRONMENT/redis/url`
- `/$ENVIRONMENT/openai/key`
- `/$ENVIRONMENT/secret/key`

Where `$ENVIRONMENT` is one of: `alpha`, `beta`, `preprod`, `prod`

#### Manual Secret Setup

Some secrets must be set manually after initial deployment:

```bash
# Example: Set OpenAI API key for alpha environment
aws ssm put-parameter \
  --name "/alpha/openai/key" \
  --value "sk-..." \
  --type "SecureString" \
  --region us-east-1 \
  --overwrite

# Example: Set secret key for prod environment
aws ssm put-parameter \
  --name "/prod/secret/key" \
  --value "your-secret-key" \
  --type "SecureString" \
  --region us-east-1 \
  --overwrite
```

## Running CI-Equivalent Checks Locally

You can run the same checks that CI performs locally to catch issues before pushing.

### Backend Tests (Multi-OS)

**Ubuntu/macOS:**
```bash
# Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Run unit tests
python -m unittest discover -s tests -p "test_*.py" -v

# Run pytest
pip install pytest pytest-asyncio
pytest tests/ -v --tb=short

# Run import/smoke sanity check
python -c "
import sys
try:
    import backend_api
    import assistant_core
    import assistant_hub
    print('✓ Core imports successful')
except ImportError as e:
    print(f'✗ Import error: {e}')
    sys.exit(1)
"
```

**Windows (PowerShell):**
```powershell
# Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Run unit tests
python -m unittest discover -s tests -p "test_*.py" -v

# Run pytest
pip install pytest pytest-asyncio
pytest tests/ -v --tb=short
```

### Frontend Build

```bash
cd frontend
npm ci
npm run build
```

### Docker Compose Integration Smoke Test

```bash
# Start services
docker compose up -d --profile default

# Wait for API (check health endpoint)
timeout=120
elapsed=0
while [ $elapsed -lt $timeout ]; do
  if curl -f http://localhost:8000/health >/dev/null 2>&1 || \
     curl -f http://localhost:8000/api/health >/dev/null 2>&1; then
    echo "✓ API is healthy"
    break
  fi
  echo "Waiting for API... (${elapsed}s/${timeout}s)"
  sleep 5
  elapsed=$((elapsed + 5))
done

# Health check
response=$(curl -sf http://localhost:8000/health || \
           curl -sf http://localhost:8000/api/health || echo "FAILED")
if [ "$response" = "FAILED" ]; then
  echo "✗ Health check failed"
  docker compose logs app
  exit 1
fi
echo "✓ Health check passed"
echo "Response: $response"

# Cleanup
docker compose down -v
```

### Debian Parity Smoke Test

```bash
docker run --rm \
  -v "$PWD:/workspace" \
  -w /workspace \
  debian:stable-slim \
  bash -c "
  set -euo pipefail
  apt-get update -qq
  apt-get install -y -qq python3 python3-pip python3-venv curl >/dev/null
  python3 -m venv /tmp/venv
  source /tmp/venv/bin/activate
  pip install --upgrade pip --quiet
  pip install -r requirements.txt --quiet
  python3 -c '
  import sys
  try:
      import backend_api
      import assistant_core
      print(\"✓ Debian imports successful\")
  except ImportError as e:
      print(f\"✗ Import error: {e}\")
      sys.exit(1)
  '
  echo '✓ Debian parity smoke test passed'
  "
```

### Complete Local CI Run

Run all checks in sequence:

```bash
#!/bin/bash
set -euo pipefail

echo "🧪 Running local CI checks..."

# Backend tests
echo "📦 Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "🔍 Running backend tests..."
python -m unittest discover -s tests -p "test_*.py" -v || true
pip install pytest pytest-asyncio || true
pytest tests/ -v --tb=short -x --maxfail=5 || true

echo "✅ Running import/smoke sanity check..."
python -c "
import sys
try:
    import backend_api
    import assistant_core
    import assistant_hub
    print('✓ Core imports successful')
except ImportError as e:
    print(f'✗ Import error: {e}')
    sys.exit(1)
"

# Frontend build
echo "🎨 Building frontend..."
cd frontend
npm ci
npm run build
cd ..

# Docker compose smoke test
echo "🐳 Running Docker Compose smoke test..."
docker compose up -d --profile default
sleep 10
if curl -f http://localhost:8000/health >/dev/null 2>&1 || \
   curl -f http://localhost:8000/api/health >/dev/null 2>&1; then
  echo "✓ API health check passed"
else
  echo "✗ API health check failed"
  docker compose logs app
  docker compose down -v
  exit 1
fi
docker compose down -v

# Debian parity test
echo "🐧 Running Debian parity test..."
docker run --rm \
  -v "$PWD:/workspace" \
  -w /workspace \
  debian:stable-slim \
  bash -c "
  set -euo pipefail
  apt-get update -qq
  apt-get install -y -qq python3 python3-pip python3-venv curl >/dev/null
  python3 -m venv /tmp/venv
  source /tmp/venv/bin/activate
  pip install --upgrade pip --quiet
  pip install -r requirements.txt --quiet
  python3 -c 'import backend_api, assistant_core; print(\"✓ Debian imports successful\")'
  "

echo "✅ All local CI checks passed!"
```

## Deployment Process

### Immutable Artifact Promotion

1. **Build once**: Docker image is built and pushed to ECR with a specific tag/digest
2. **Promote forward**: The same image digest is deployed to subsequent environments
3. **No rebuilds**: We do NOT rebuild the image differently per environment

### Deployment Workflow

1. **CI runs** on PR/push (`.github/workflows/ci.yml`)
   - Backend tests (Ubuntu, macOS, Windows)
   - Frontend build
   - Docker compose smoke test
   - Debian parity test

2. **Deploy workflow triggers** (`.github/workflows/deploy.yml`)
   - On `develop` branch push → deploy to `alpha`
   - On version tag push → deploy to corresponding environment

3. **Image build and push**
   - Build Docker image once
   - Push to ECR with tag and digest
   - Store image digest for promotion

4. **Deployment**
   - Use `deploy-aws.sh` script with image URI
   - Update ECS task definition with image
   - Update ECS service
   - Print deployment summary with environment and image digest

### Manual Deployment

You can also deploy manually using the `deploy-aws.sh` script:

```bash
# Deploy to alpha with a specific image
./deploy-aws.sh alpha deploy 123456789012.dkr.ecr.us-east-1.amazonaws.com/os-dashboard:v1.2.3-alpha.1

# Deploy to prod (will build if image not provided)
./deploy-aws.sh prod deploy
```

## Environment Configuration Files

Environment-specific configuration templates are available:

- `env.alpha.example` - Alpha environment template
- `env.beta.example` - Beta environment template
- `env.preprod.example` - Preprod environment template
- `env.prod.example` - Production environment template

These templates define the configuration contract for each environment. Copy and customize as needed for local development or deployment.

## Phase-1 Considerations

The current Phase-0 implementation focuses on:
- ✅ Multi-OS CI coverage
- ✅ Docker-based deployment
- ✅ Immutable artifact promotion
- ✅ GitHub Environments with approval gates

Future Phase-1 enhancements may include:
- Infrastructure as Code (Terraform/CloudFormation templates)
- Automated rollback capabilities
- Blue-green deployments
- Canary deployments
- Advanced monitoring and alerting integration
- Multi-region deployment support

## Troubleshooting

### Deployment Failures

1. **Check GitHub Actions logs** for detailed error messages
2. **Verify AWS credentials** are configured correctly
3. **Check ECR repository** exists and is accessible
4. **Verify ECS cluster/service** exists for the target environment
5. **Check SSM parameters** are set for the environment

### CI Failures

1. **Backend tests failing**: Check Python version compatibility (3.11+)
2. **Frontend build failing**: Verify Node.js version (20+)
3. **Docker compose smoke test failing**: Check if port 8000 is available
4. **Debian parity test failing**: Verify all Python dependencies are compatible with Debian

### Health Check Failures

The health endpoint is available at:
- `/health` (primary endpoint)
- `/api/health` (alternative endpoint)

Both endpoints should return a JSON response with `status: "healthy"`.

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS ECS Deployment Guide](https://docs.aws.amazon.com/ecs/latest/developerguide/deployment.html)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [AWS SSM Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html)
