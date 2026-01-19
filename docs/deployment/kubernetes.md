# Kubernetes Deployment

This repo ships Kustomize overlays for dev, staging, and production. The base stack includes:
- FastAPI backend (`osdash-backend`, SQLite persistence)
- React frontend (`osdash-frontend`, Nginx)
- Shared data PVC (`osdash-data`) for SQLite + attachments

## Directory Layout
```
k8s/
  base/                 # Shared resources (Deployments, Services, PVCs)
  addons/               # Optional add-ons (cert-manager, external-secrets, postgres)
  overlays/
    dev/                # Dev namespace + ingress + overrides
    preview/            # PR preview namespace + overrides
    staging/            # Staging namespace + ingress + overrides
    prod/               # Production namespace + ingress
    prod-ha/            # Production HA overlay (Postgres required)
```

## Build and Push Images
Backend:
```
docker build -f Dockerfile.backend --target production -t ghcr.io/law23sum/os_dashboard_ai_assistant/backend:staging .
docker push ghcr.io/law23sum/os_dashboard_ai_assistant/backend:staging
```

Frontend:
```
docker build -f frontend/Dockerfile -t ghcr.io/law23sum/os_dashboard_ai_assistant/frontend:staging frontend
docker push ghcr.io/law23sum/os_dashboard_ai_assistant/frontend:staging
```

Update the `images` entries in each overlay `kustomization.yaml` if you use a different registry/repo.

## Configure Secrets
Secrets are not applied by default to avoid overwriting existing values.
Create `osdash-secrets` yourself (or use an external secrets manager). A template is available at `k8s/base/secrets.yaml`.

At minimum, set:
- `OPENAI_API_KEY` (optional)
- `SENTRY_DSN` (optional)

Add any provider credentials your deployment needs (Microsoft, Google, GitHub, etc.) as additional secret keys and wire them into the backend deployment if required.
CI deploy jobs re-sync `osdash-secrets` from GitHub Environment secrets when provided; if secrets are unset, the step is skipped.

## Optional Add-ons

### Cert-Manager (TLS)
If you use cert-manager, apply the addon templates:
```
kubectl apply -k k8s/addons/cert-manager
```
Update the issuer email and hostnames before applying.

### External Secrets Operator
If you use External Secrets, update the provider config and apply:
```
kubectl apply -k k8s/addons/external-secrets
```

### In-Cluster Postgres (non-prod only)
For non-production clusters, you can run Postgres inside the cluster:
```
kubectl apply -k k8s/addons/postgres
```
Create a `osdash-postgres` secret with `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD` first.

## Configure Ingress Hosts
Update the hosts in overlay ingress manifests:
- `k8s/overlays/dev/ingress.yaml`
- `k8s/overlays/staging/ingress.yaml`
- `k8s/overlays/prod/ingress.yaml`

The frontend expects `/api` to route to the backend on the same host.

Preview environments are created per PR by CI (`osdash-pr-<number>` namespaces) and do not create ingress by default. If you want per-PR URLs, configure a wildcard DNS entry and set `PREVIEW_HOST_SUFFIX` (and optional `PREVIEW_TLS_SECRET`) in CI secrets.

## Deploy
Dev:
```
kubectl apply -k k8s/overlays/dev
```

Staging:
```
kubectl apply -k k8s/overlays/staging
```

Production:
```
kubectl apply -k k8s/overlays/prod
```

Production HA (Postgres required):
```
kubectl apply -k k8s/overlays/prod-ha
```

See `docs/deployment/postgres-migration.md` for the migration plan.

## CI/CD Flow
- Pull Requests deploy to a preview namespace (`osdash-pr-<number>`).
- `develop` builds images, deploys to `dev`, and runs smoke checks.
- `main` builds images, deploys to `staging`, and runs smoke checks.
- Tag `v*` (release) builds images and deploys to `production`.

Use GitHub Environments to require approvals on `production` if you want a manual gate.

## Rollout and Rollback
Rollout status:
```
kubectl rollout status deployment/osdash-backend -n osdash-production
kubectl rollout status deployment/osdash-frontend -n osdash-production
```

Restart to pull new images on a fixed tag:
```
kubectl rollout restart deployment/osdash-backend -n osdash-production
kubectl rollout restart deployment/osdash-frontend -n osdash-production
```

Rollback:
```
kubectl rollout undo deployment/osdash-backend -n osdash-production
kubectl rollout undo deployment/osdash-frontend -n osdash-production
```

## Storage Notes
`osdash-data` uses `ReadWriteOnce` for SQLite persistence. The backend runs as a single replica with a `Recreate` rollout strategy to avoid concurrent writers.

If you need horizontal scale, move persistence to a real database (Postgres, etc.) and update the backend to use it before increasing replicas.
