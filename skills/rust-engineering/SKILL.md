---
name: rust-engineering
description: Build, refactor, and debug Rust crates. Use for tasks involving Cargo, ownership and borrowing, lifetimes, async, or Rust testing.
---

# Rust Engineering

## Overview
Deliver Rust changes using Cargo with attention to ownership, lifetimes, and safe abstractions.

## Quick Start
- Use `cargo build` and `cargo test` and prefer workspace-aware commands.
- Run `cargo fmt` and `cargo clippy` when available.

## Workflow
1. Inspect `Cargo.toml` and workspace layout.
2. Implement changes with minimal public API disruption.
3. Resolve borrow and lifetime issues by tightening scopes and ownership.
4. Add targeted tests and run relevant suites.
5. Document unsafe blocks and invariants.

## Common Tasks
- Add crates and feature flags.
- Refactor modules and visibility (`pub`, `crate`).
- Optimize with iterators and zero-cost abstractions.

## Guardrails
- Avoid unnecessary `clone`; prefer borrowing.
- Keep unsafe code small and justified.
- Maintain MSRV if the project specifies one.
