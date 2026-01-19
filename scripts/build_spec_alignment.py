#!/usr/bin/env python3
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "agent_exports" / "runtime"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SPEC_PATH = Path("/Users/sum/Desktop/Omniverse/OmniverseServicesTechnicalDesignSpecificationsVersion9.txt")

EXCLUDE_GLOBS = ["node_modules", "dist", "build", "coverage", ".git", "venv", "__pycache__"]


def git_info() -> Dict[str, str]:
    try:
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=REPO_ROOT).decode().strip()
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT).decode().strip()
    except Exception:
        branch = "unknown"
        commit = "unknown"
    return {"branch": branch, "commit": commit}


def read_spec() -> str:
    return SPEC_PATH.read_text(errors="ignore")


def extract_snippets(text: str, keywords: List[str], max_snippets: int = 5, context_lines: int = 2) -> List[str]:
    lines = text.splitlines()
    snippets: List[str] = []
    keyword_re = re.compile("|".join(re.escape(k) for k in keywords), re.IGNORECASE)
    for idx, line in enumerate(lines):
        if keyword_re.search(line):
            start = max(0, idx - context_lines)
            end = min(len(lines), idx + context_lines + 1)
            snippet = "\n".join(lines[start:end]).strip()
            if snippet and snippet not in snippets:
                snippets.append(snippet)
        if len(snippets) >= max_snippets:
            break
    return snippets


def rg_files(pattern: str, search_roots: List[str]) -> List[str]:
    cmd = ["rg", "--files-with-matches", "-i", pattern]
    for glob in EXCLUDE_GLOBS:
        cmd.extend(["-g", f"!{glob}/**"])
    cmd += search_roots
    try:
        output = subprocess.check_output(cmd, cwd=REPO_ROOT).decode().splitlines()
    except subprocess.CalledProcessError:
        return []
    return sorted(set(output))


def scan_evidence() -> Dict[str, List[str]]:
    roots = ["frontend/src", "backend_api", "backend", "src", "assistant_core", "assistant_hub", "ai_os", "utils", "services", "docs", "documentation"]

    evidence = {
        "pep_pdp": rg_files(r"policy\s+enforcement|pep\b|pdp\b|policy\s+decision|policy\s+engine|policy\s+simulator", roots),
        "ledger_audit": rg_files(r"ledger|audit\s+log|audit\b|append-only|immutab", roots),
        "evidence_packs": rg_files(r"evidence\s+pack|evidence\b|attestation|provenance", roots),
        "breach_mode": rg_files(r"breach\b|incident\s+mode|lockdown", roots),
        "traceability": rg_files(r"spec\b|technical\s+design|traceability|v9", roots),
    }
    return evidence


def find_secret_files() -> Set[Path]:
    candidates: Set[Path] = set()
    patterns = [
        ".env",
        "env.*",
        "*.pem",
        "*.key",
        "*secret*.json",
        "*credentials*.json",
        "*client_secret*.json",
    ]
    for pattern in patterns:
        cmd = ["rg", "--files", "-g", pattern]
        for glob in EXCLUDE_GLOBS:
            cmd.extend(["-g", f"!{glob}/**"])
        try:
            output = subprocess.check_output(cmd, cwd=REPO_ROOT).decode().splitlines()
        except subprocess.CalledProcessError:
            output = []
        for line in output:
            candidates.add(REPO_ROOT / line)
    return candidates


def redact_secrets(files: Set[Path]) -> List[Dict[str, str]]:
    findings: List[Dict[str, str]] = []
    key_pattern = re.compile(r"(secret|token|api_key|apikey|password|client_secret|private_key|access_key)", re.IGNORECASE)

    for path in sorted(files):
        try:
            if path.stat().st_size > 1_000_000:
                continue
        except FileNotFoundError:
            continue
        rel_path = str(path.relative_to(REPO_ROOT))
        if path.suffix.lower() == ".json":
            try:
                data = json.loads(path.read_text())
            except Exception:
                data = None
            if isinstance(data, dict):
                for key in data.keys():
                    if key_pattern.search(key):
                        findings.append({"path": rel_path, "key": key, "value": "***REDACTED***"})
        else:
            try:
                text = path.read_text(errors="ignore")
            except Exception:
                continue
            for line in text.splitlines():
                if line.strip().startswith("#") or "=" not in line:
                    continue
                key = line.split("=", 1)[0].strip()
                if key_pattern.search(key):
                    findings.append({"path": rel_path, "key": key, "value": "***REDACTED***"})
    return findings


def write_md(path: Path, content: str) -> None:
    path.write_text(content.strip() + "\n")


def main() -> None:
    repo = git_info()
    spec_text = read_spec()
    evidence = scan_evidence()

    pep_snips = extract_snippets(spec_text, ["policy enforcement", "PEP", "PDP", "policy decision"])
    ledger_snips = extract_snippets(spec_text, ["ledger", "audit log", "audit"])
    evidence_snips = extract_snippets(spec_text, ["evidence pack", "evidence"])
    breach_snips = extract_snippets(spec_text, ["breach mode", "breach", "incident mode"])
    secrets_snips = extract_snippets(spec_text, ["secrets", "keys", "credential", "vault"])
    trace_snips = extract_snippets(spec_text, ["traceability", "spec", "version 9", "v9"])

    def md_block(title: str, snippets: List[str], files: List[str]) -> str:
        lines = [f"# {title}", "", "Spec references:"]
        if snippets:
            for snip in snippets:
                cleaned = snip.replace("\n", " / ")
                lines.append(f"- {cleaned}")
        else:
            lines.append("- Not found in spec (keyword scan).")
        lines.append("")
        lines.append("Evidence in repo:")
        if files:
            for f in files[:25]:
                lines.append(f"- `{f}`")
            if len(files) > 25:
                lines.append(f"- ... {len(files) - 25} more")
        else:
            lines.append("- None found via keyword scan.")
        return "\n".join(lines)

    write_md(OUT_DIR / "GOV_PEPS.md", md_block("Policy Enforcement Points (PEP/PDP)", pep_snips, evidence["pep_pdp"]))
    write_md(OUT_DIR / "LEDGER_AUDIT.md", md_block("Ledger + Audit Logging", ledger_snips, evidence["ledger_audit"]))
    write_md(OUT_DIR / "EVIDENCE_PACKS.md", md_block("Evidence Packs", evidence_snips, evidence["evidence_packs"]))
    write_md(OUT_DIR / "BREACH_MODE.md", md_block("Breach Mode", breach_snips, evidence["breach_mode"]))
    write_md(OUT_DIR / "SECRETS_AND_KEYS.md", md_block("Secrets Handling", secrets_snips, []))

    # Secrets findings (redacted)
    secret_findings = redact_secrets(find_secret_files())
    if secret_findings:
        lines = ["", "Detected secret/key references (values redacted):"]
        for item in secret_findings:
            lines.append(f"- `{item['path']}`: `{item['key']}` = {item['value']}")
        with (OUT_DIR / "SECRETS_AND_KEYS.md").open("a") as f:
            f.write("\n".join(lines) + "\n")

    write_md(OUT_DIR / "SPEC_TRACEABILITY.md", md_block("Spec-to-Code Traceability", trace_snips, evidence["traceability"]))

    def status_for(files: List[str]) -> str:
        return "partial" if files else "no"

    gap_matrix = {
        "repo": repo,
        "areas": [
            {
                "area": "Policy Enforcement Points (PEP/PDP)",
                "implemented": status_for(evidence["pep_pdp"]),
                "evidence_files": evidence["pep_pdp"],
                "notes": "Keyword scan only; verify runtime wiring and PDP/PEP enforcement paths.",
                "next_actions": ["Confirm runtime policy enforcement flow", "Map PEP/PDP boundaries to services"],
            },
            {
                "area": "Ledger + Audit Logging",
                "implemented": status_for(evidence["ledger_audit"]),
                "evidence_files": evidence["ledger_audit"],
                "notes": "Audit references found; confirm append-only ledger storage and tamper controls.",
                "next_actions": ["Identify ledger storage backend", "Verify audit event schema"],
            },
            {
                "area": "Evidence Packs",
                "implemented": status_for(evidence["evidence_packs"]),
                "evidence_files": evidence["evidence_packs"],
                "notes": "Evidence references found; confirm pack assembly, signing, and export.",
                "next_actions": ["Locate evidence pack builder", "Document pack lifecycle"],
            },
            {
                "area": "Breach Mode",
                "implemented": status_for(evidence["breach_mode"]),
                "evidence_files": evidence["breach_mode"],
                "notes": "No explicit breach mode enforcement located via keyword scan.",
                "next_actions": ["Search for incident response toggles", "Add breach mode control plane"],
            },
            {
                "area": "Secrets Handling",
                "implemented": "partial" if secret_findings else "no",
                "evidence_files": [item["path"] for item in secret_findings],
                "notes": "Secrets appear in config files; confirm centralized secret management integration.",
                "next_actions": ["Inventory secret sources", "Adopt vault or KMS integration"],
            },
            {
                "area": "Spec Traceability",
                "implemented": status_for(evidence["traceability"]),
                "evidence_files": evidence["traceability"],
                "notes": "Spec references located; ensure mapping from V9 requirements to code anchors.",
                "next_actions": ["Create requirement-to-code index", "Tag features with spec IDs"],
            },
        ],
    }

    (OUT_DIR / "GAP_MATRIX.json").write_text(json.dumps(gap_matrix, indent=2))


if __name__ == "__main__":
    main()
