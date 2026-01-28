---
name: software-standards
description: Apply industry-standard software engineering practices. Use for tasks involving Git workflows, testing strategy, CI or CD, security hygiene, documentation, or code review standards.
---

# Software Standards

## Overview
Apply consistent engineering practices across codebases: git hygiene, testing, CI or CD, docs, and security basics.

## Workflow
1. Keep changes small, focused, and clearly described.
2. Add or update tests that cover behavior changes.
3. Ensure CI steps are updated or respected.
4. Document behavior changes in relevant docs.

## Key Practices
- Git: branch per change, clear commit messages, avoid force-push unless requested.
- Testing: unit before integration when possible; avoid flaky timing.
- CI or CD: keep pipelines green; prefer incremental updates.
- Security: avoid hard-coded secrets; validate inputs; use least privilege.

## Guardrails
- Do not remove tests without explicit reason.
- Prefer backward-compatible changes unless asked otherwise.
