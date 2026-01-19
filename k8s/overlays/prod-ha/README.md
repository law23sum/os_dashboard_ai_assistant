# Production HA Overlay (Postgres Required)

This overlay enables multi-replica backend + HPA/PDB.
Use it only after migrating persistence from SQLite to Postgres.

Prerequisites:
- App code reads `DATABASE_URL` and no longer relies on SQLite files
- `osdash-secrets` contains a valid `DATABASE_URL`
- Postgres is reachable from the cluster

Apply manually:
```bash
kubectl apply -k k8s/overlays/prod-ha
```
