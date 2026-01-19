# Agent Registry Guardrails

`Agent.registry.yaml` is the single source of truth for agent routing, decision rights, and
lane separation. Do not edit, move, or rename it unless the repo owner explicitly instructs
you to do so.

If implementation or design conflicts with the registry, treat the registry as canonical and
flag the mismatch before making changes.

Change control:
- Only update with explicit, written instruction from the owner/admin.
- Keep `schema_version` and `last_updated_local` in sync with approved edits.
- Record the reason for the change in the request that authorized the edit.
