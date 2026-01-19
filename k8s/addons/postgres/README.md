# Postgres Add-on (Optional)

This provides an in-cluster Postgres instance for non-production use.
For production, use a managed Postgres service instead.

Prerequisites:
- Create a secret named `osdash-postgres` with:
  - `POSTGRES_DB`
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`

Apply:
```bash
kubectl apply -k k8s/addons/postgres
```
