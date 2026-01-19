# Cert-Manager Add-on (Optional)

Prerequisites:
- cert-manager installed in the cluster
- DNS for `staging.osdashboard.ai` and `app.osdashboard.ai` pointing to your ingress

What this provides:
- ClusterIssuers for Let's Encrypt (staging + production)
- TLS Certificates for staging/prod ingresses

Before applying:
- Replace `you@example.com` in the ClusterIssuer manifests.
- Update hostnames if you use different domains.

Apply:
```bash
kubectl apply -k k8s/addons/cert-manager
```
