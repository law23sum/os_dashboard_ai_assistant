---
name: deployment-engineering
description: Plan, implement, and troubleshoot deployment pipelines and release processes. Use for CI/CD workflows, environment promotion, rollback strategies, and feature deployment operations.
---

# Deployment Engineering

## Overview
Deliver reliable deployments with automated pipelines, safe rollouts, and clear rollback paths.

## Quick Start
- Identify target environments and release cadence.
- Inspect existing CI/CD configuration and secrets handling.
- Verify how feature flags and migrations are handled.

## Workflow
1. Map environments (dev, staging, prod) and promotion rules.
2. Validate build steps, tests, and artifact creation.
3. Define deployment strategy (blue/green, canary, rolling).
4. Ensure migrations, config, and secrets are safe and repeatable.
5. Add monitoring, rollback steps, and post-deploy verification.

## Common Tasks
- Add pipeline steps for lint, test, build, and deploy.
- Configure environment variables and secrets securely.
- Implement feature-flagged releases and gradual rollouts.
- Add health checks and smoke tests post-deploy.

## Guardrails
- Avoid irreversible migrations without a rollback plan.
- Keep production changes auditable and repeatable.
- Prefer least-privilege credentials and secret rotation.
