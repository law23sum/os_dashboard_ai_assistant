---
name: java-engineering
description: Build, debug, and maintain Java applications and services on the JVM. Use for tasks involving Java source code, Maven or Gradle builds, JUnit tests, JVM runtime options, or performance troubleshooting.
---

# Java Engineering

## Overview
Deliver Java changes end-to-end: understand project layout, build with Maven or Gradle, run tests, and validate runtime behavior.

## Quick Start
- Detect build tool and prefer the project wrapper when present.
- Confirm target JDK version and module system use.
- Run a minimal build and the smallest relevant test set.

## Workflow
1. Inspect `pom.xml` or `build.gradle` and identify modules and entry points.
2. Build and run tests using the project wrapper.
3. Apply code changes; keep API and binary compatibility in mind.
4. Re-run targeted tests, then expand if needed.
5. Note required JVM flags, env vars, and config files.

## Common Tasks
- Add or modify classes, interfaces, and annotations with consistent packages.
- Update dependencies and versions in build files.
- Diagnose runtime issues via logs and JVM options.
- Refactor with attention to nullability and concurrency.

## Guardrails
- Avoid breaking public APIs without calling it out.
- Prefer deterministic tests; avoid time-based flakiness.
- Match formatting and import style in the repo.
