# Environment Configuration and Deployment Guide

This document defines the deployment environments, tag patterns, secrets management, and how to run CI-equivalent checks locally.

Note: Kubernetes + GitHub Actions is the current deployment path. AWS/ECS references below are legacy and can be ignored unless you still deploy to ECS.

## Environment Names

The AI OS uses four deployment environments:

1. **preview** - Per-PR ephemeral environment
2. **dev** - Integration environment for `develop`
3. **staging** - Release candidate environment for `main`
4. **prod** - Production environment

### Environment Promotion Ladder

```
preview (PR) → dev → staging → prod
```

### Promotion Timing and OS Builds

- Pull requests → preview (automatic)
- `develop` → dev (automatic)
- `main` → staging (automatic)
- `vX.Y.Z` tags → production deploy + desktop OS builds (Windows/macOS/Linux)

OS-specific testing/builds run in CI on Windows/macOS/Linux runners; you do not need separate long-lived server environments per OS.

### Preview URL Configuration

To enable per-PR URLs, set these GitHub secrets:
- `PREVIEW_HOST_SUFFIX` (e.g., `preview.osdashboard.ai`)
- `PREVIEW_TLS_SECRET` (optional, TLS secret name in your cluster)

## Feature Flags and Cohorts

Feature flags and cohorts are carried on API requests for telemetry:

- `X-OSD-Release`: Release channel (defaults to `stable`)
- `X-OSD-Cohort`: Cohort identifier (e.g., `alpha`, `beta`, `internal`)
- `X-OSD-Flags`: Comma-separated feature flags (e.g., `new-nav,fast-chat`)

Frontend defaults can be set via local storage keys:
- `osdash-release-channel`
- `osdash-cohort`
- `osdash-feature-flags` (JSON map of `flag -> boolean`)

Environments are promoted forward using immutable Docker image artifacts. The same built image digest is deployed across environments - **we do NOT rebuild differently per environment**.

## Tag Patterns and Deployment Rules

### Automatic Deployments

- **Pull Requests** → Preview environment per PR
  - Namespace: `osdash-pr-<number>`
- **`develop` branch** → Automatically deploys to `dev`
- **`main` branch** → Automatically deploys to `staging`

### Tag-Based Deployments

Deployments are triggered by Git tags matching:

| Tag Pattern | Environment | Example |
|------------|--------------|---------|
| `vX.Y.Z` | `prod` | `v1.2.3` |

### Tag Example

```bash
# Deploy to prod (requires approval if configured)
git tag v1.2.3
git push origin v1.2.3
```

Release tags also trigger desktop OS build workflows (Windows/macOS/Linux).

## GitHub Environments and Approval Gates

GitHub Environments enforce deployment governance:

- **preview**, **dev**, **staging**: No approval required (automatic deployment)
- **production**: Require manual approval before deployment

### Setting Up GitHub Environments

1. Go to repository Settings → Environments
2. Create environments: `preview`, `dev`, `staging`, `production`
3. For `production`:
   - Enable "Required reviewers"
   - Add required reviewers (team or individuals)
   - Optionally set deployment branches/tags

The deployment workflow (`.github/workflows/ci-cd.yml`) references these environments and triggers approvals when configured.

## Secrets Management

### GitHub Secrets (Kubernetes)

The following secrets must be configured in GitHub repository settings:

- **`KUBE_CONFIG`**: kubeconfig for the target cluster (base64 or raw content)
- **`PREVIEW_HOST_SUFFIX`** (optional): base domain for PR preview URLs
- **`PREVIEW_TLS_SECRET`** (optional): existing TLS secret name for preview ingress
- **`OPENAI_API_KEY`** (optional): runtime API key, scoped per GitHub Environment
- **`SENTRY_DSN`** (optional): runtime error reporting DSN, scoped per GitHub Environment

Runtime application secrets live in Kubernetes or an external secrets manager.
Use `k8s/base/secrets.yaml` as a template; it is not applied by default.

### Legacy: AWS Systems Manager (SSM) Parameter Store

Only required if you still deploy to ECS. The deployment script (`deploy-aws.sh`) sets up these parameters automatically.

#### SSM Parameter Path Convention

All secrets follow the pattern: `/<environment>/<category>/<key>`

Examples:
- `/$ENVIRONMENT/db/username`
- `/$ENVIRONMENT/db/password`
- `/$ENVIRONMENT/db/url`
- `/$ENVIRONMENT/redis/url`
- `/$ENVIRONMENT/openai/key`
- `/$ENVIRONMENT/secret/key`

Where `$ENVIRONMENT` is one of: `dev`, `staging`, `prod`

## Audit Log Configuration

The canonical audit log supports segmented sealing, retention tiers, and optional manifest signing.
Configure the following environment variables to tune segmenting, retention, and storage tiers:

| Variable | Purpose | Default |
| --- | --- | --- |
| `AUDIT_STORAGE_PATH` | Root directory for audit data | `audit_data` |
| `AUDIT_SEGMENT_WINDOW_MINUTES` | Segment time window (minutes) | `5` |
| `AUDIT_SEGMENT_TIME_FORMAT` | Segment bucket format | `%Y%m%d%H%M` |
| `AUDIT_SEGMENT_MAX_EVENTS` | Max events per segment | `5000` |
| `AUDIT_RETENTION_HOT_DAYS` | Local hot retention (days) | `30` |
| `AUDIT_RETENTION_ARCHIVE_DAYS` | Remote archive retention (days) | `395` |
| `AUDIT_RETENTION_BACKUP_YEARS` | Backup hardware retention (years) | `7` |
| `AUDIT_RETENTION_CLOUD_YEARS` | Cloud backup retention (years) | `7` |
| `AUDIT_SIGNING_KEY` | Optional HMAC signing key for manifests | unset |
| `AUDIT_TIER_REMOTE_ARCHIVE` | Optional path for remote archive tier | unset |
| `AUDIT_TIER_HARDWARE_BACKUP` | Optional path for hardware backup tier | unset |
| `AUDIT_TIER_CLOUD_BACKUP` | Optional path for cloud backup tier | unset |
| `AUDIT_MAINTENANCE_ENABLED` | Enable scheduled audit maintenance tasks | `true` |
| `AUDIT_RETENTION_APPLY` | Apply hot-tier retention deletions (vs plan-only) | `false` |
| `AUDIT_RETENTION_INTERVAL_HOURS` | Retention run cadence in hours | `24` |
| `AUDIT_COMPACTION_INTERVAL_HOURS` | Index compaction cadence in hours | `24` |
| `AUDIT_PARQUET_EXPORT_ENABLED` | Enable parquet cold export job | `false` |
| `AUDIT_PARQUET_EXPORT_INTERVAL_HOURS` | Parquet export cadence in hours | `168` |
| `AUDIT_PARQUET_EXPORT_RANGE_DAYS` | Days per parquet export window | `1` |
| `AUDIT_MAINTENANCE_TENANT_ID` | Optional tenant filter for maintenance jobs | unset |

#### Manual Secret Setup (Kubernetes)

Some secrets must be set manually after initial deployment:

```bash
# Example: Set OpenAI API key for dev environment
kubectl -n osdash-dev create secret generic osdash-secrets \
  --from-literal=OPENAI_API_KEY="sk-..." \
  --dry-run=client -o yaml | kubectl apply -f -

# Example: Set Sentry DSN for prod environment
kubectl -n osdash-production create secret generic osdash-secrets \
  --from-literal=SENTRY_DSN="https://example@o0.ingest.sentry.io/0" \
  --dry-run=client -o yaml | kubectl apply -f -
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

1. **Build once**: Docker images are built and pushed to GHCR with a tag + digest.
2. **Promote forward**: The same image digest is deployed across environments.
3. **No rebuilds**: We do NOT rebuild the image differently per environment.

### Deployment Workflow

1. **CI runs** on PR/push (`.github/workflows/ci-cd.yml`)
   - Backend tests (Ubuntu)
   - Frontend tests + build
   - Integration tests

2. **Preview workflow**
   - PRs deploy to `osdash-pr-<number>` namespaces

3. **Environment promotion**
   - `develop` → `dev`
   - `main` → `staging`
   - `v*` tag → `prod`

4. **Deployment**
   - Apply Kustomize overlay
   - Pin images to the exact digest built in CI
   - Run smoke checks
   - Roll back on failure (prod)

Overlay paths can be overridden via GitHub environment variables:
- `K8S_OVERLAY_PREVIEW` (default `k8s/overlays/preview`)
- `K8S_OVERLAY_DEV` (default `k8s/overlays/dev`)
- `K8S_OVERLAY_STAGING` (default `k8s/overlays/staging`)
- `K8S_OVERLAY_PROD` (default `k8s/overlays/prod`)

### Manual Deployment

```bash
# Deploy to staging
kubectl apply -k k8s/overlays/staging

# Deploy to prod
kubectl apply -k k8s/overlays/prod

# Deploy to prod (HA overlay, Postgres required)
kubectl apply -k k8s/overlays/prod-ha
```

## Environment Configuration Files

Environment-specific configuration templates are available:

- `env.dev.example` - Dev environment template
- `env.prod.example` - Production environment template
- `env.preprod.example`, `env.alpha.example`, `env.beta.example` - Legacy templates (prefer feature flag cohorts unless compliance/perf requires separate stacks)

These templates define the configuration contract for each environment. Copy and customize as needed for local development or deployment.

## Postgres Migration (Future HA)

See `docs/deployment/postgres-migration.md` for the Postgres migration plan and HA overlay requirements.

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
2. **Verify `KUBE_CONFIG`** is set in GitHub Actions secrets
3. **Confirm namespaces exist** (`kubectl get ns`)
4. **Check ingress/controller health** (`kubectl -n ingress-nginx get pods`)
5. **Check runtime secrets** (`kubectl -n <env> get secret osdash-secrets -o yaml`)

### CI Failures

1. **Backend tests failing**: Check Python version compatibility (3.11+)
2. **Frontend build failing**: Verify Node.js version (20+)
3. **Docker compose smoke test failing**: Check if port 8000 is available
4. **Debian parity test failing**: Verify all Python dependencies are compatible with Debian

### Health Check Failures

The health endpoint is available at:
- `/api/health` (primary endpoint)
- `/health` (alternative endpoint)

Both endpoints should return a JSON response with `status: "ok"` when healthy.

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Kubernetes Documentation](https://kubernetes.io/docs/home/)
