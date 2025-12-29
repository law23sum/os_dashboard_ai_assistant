---
name: typescript-engineering
description: Build and maintain TypeScript codebases. Use for tasks involving TS types, tsconfig, strictness issues, or TS build pipelines.
---

# TypeScript Engineering

## Overview
Apply typed changes with minimal type escape and align with the repo's TS configuration.

## Quick Start
- Inspect `tsconfig.json` for strictness and module settings.
- Use the repo's build and test scripts.

## Workflow
1. Understand type boundaries and public interfaces.
2. Implement changes with proper types and minimal `any`.
3. Update type tests or API docs if needed.
4. Run `tsc` or the repo build to validate.

## Common Tasks
- Define shared types and interfaces.
- Narrow types with guards and discriminated unions.
- Migrate JS to TS with incremental strictness.

## Guardrails
- Avoid `// @ts-ignore` unless absolutely necessary.
- Keep runtime behavior aligned with types.
