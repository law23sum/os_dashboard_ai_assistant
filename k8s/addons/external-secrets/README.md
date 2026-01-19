# External Secrets Add-on (Optional)

Prerequisites:
- External Secrets Operator installed in the cluster
- A configured SecretStore or ClusterSecretStore provider

What this provides:
- ClusterSecretStore template (AWS Secrets Manager example)
- ExternalSecret manifests that create `osdash-secrets` in dev/staging/prod

Before applying:
- Update `cluster-secret-store.yaml` for your provider (AWS, GCP, Vault, etc.).
- Adjust the remote secret keys to match your naming scheme.

Apply:
```bash
kubectl apply -k k8s/addons/external-secrets
```
