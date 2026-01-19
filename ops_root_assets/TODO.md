# AI OS – TODO

- [ ] Expand `config/repo_manifest.json` with every approved repository (include stack + owner tags).
- [ ] Harden `scripts/codex_sentinel.py` to dispatch actual lint/test/fix commands per repo and emit structured JSON logs to this folder.
- [ ] Install git hooks (pre-commit/pre-push) across all repos so Codex Sentinel runs automatically.
- [ ] Publish the shared frontend design system (tokens + components) and migrate dependent projects incrementally.
- [ ] Create backend service templates + data contracts, then refactor each repo to adopt them.
- [ ] Draft customer-facing documentation for the v1000 platform tiers and deployment modes.
- [ ] Launch follow-up Codex session with this TODO list as context before the next automation pass.

## Latest Sentinel run

- Timestamp: `20251211T233147Z`
- Repo health: dirty=18, missing=0
- Dirty repos (sample): os_dashboard_ai_assistant, portfolio_strategist, idea_trade_exchange, portfolio_ref_financia, trader_exchange, codenest, matlab_mathematica, research_papers_energy

- Reports:
  - `/Users/chrisdixon/OS_Dashboard_AI_Assistant/FEATURES_OVERVIEW.md`
  - `/Users/chrisdixon/OS_Dashboard_AI_Assistant/ARCHITECTURE_DEEP_DIVE.md`
  - `/Users/chrisdixon/OS_Dashboard_AI_Assistant/TODO_REMAINING_20251211T233147Z.md`

## Next execution TODOs

- [ ] Decide enforcement policy for git hooks (warn-only vs block-on-unhealthy).

- [ ] Add per-stack adapters to Sentinel: python (ruff/pytest), node (eslint/vitest), java (gradle/mvn), latex (latexmk).

- [ ] Add a safe hook installer that does not block commits on staged changes.

- [ ] Add a nightly scheduled run (launchd/cron) that writes logs + refreshed reports.
