---
name: javascript-engineering
description: Develop and debug JavaScript applications and Node.js tooling. Use for tasks involving JS source, Node runtimes, package.json scripts, or browser behavior.
---

# JavaScript Engineering

## Overview
Handle JavaScript work in Node or browser contexts using the repo's existing tooling.

## Quick Start
- Detect the package manager and scripts in `package.json`.
- Use npm, yarn, or pnpm consistently with the repo.

## Workflow
1. Identify runtime target (Node vs browser) and module system (CJS vs ESM).
2. Make changes with attention to async flow and error handling.
3. Run lint, test, or build scripts relevant to the change.
4. Validate in the intended runtime.

## Common Tasks
- Add or update npm dependencies.
- Fix async bugs with `async` and `await` and proper error propagation.
- Improve performance by reducing repeated work and allocations.

## Guardrails
- Avoid breaking API changes without calling them out.
- Keep dependencies minimal and prefer existing utilities.
