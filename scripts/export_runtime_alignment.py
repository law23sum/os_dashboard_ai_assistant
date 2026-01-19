#!/usr/bin/env python3
import json
import os
import re
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_RUNTIME = ROOT / 'agent_exports/runtime'

SEARCH_DIRS = [
    'frontend/src',
    'backend_api',
    'assistant_core',
    'assistant_hub',
    'assistant_hub_gui',
    'ai_os',
    'ai_agent',
    'orchestrator',
    'api_connectors',
    'python_os',
    'src',
    'utils',
    'config',
    'docs',
    'documentation',
    'workflows',
    'tools',
]

EXCLUDE_DIRS = {
    'node_modules', 'dist', 'build', '.git', 'venv', '__pycache__',
    'logs', 'coverage', 'playwright-report', 'test-results', 'htmlcov',
    'Omniverse',
}

INCLUDE_EXTS = {'.ts', '.tsx', '.js', '.jsx', '.py', '.md', '.yaml', '.yml', '.toml', '.txt', '.json'}

KEYWORDS = {
    'PEP_PDP': [r'\bPEP\b', r'\bPDP\b', 'policy enforcement', 'policy decision'],
    'LEDGER_AUDIT': ['ledger', 'audit log', 'audit trail', 'append-only', 'immutable'],
    'EVIDENCE_PACKS': ['evidence pack', 'evidence_pack', 'evidence', 'attestation'],
    'BREACH_MODE': ['breach mode', 'breach', 'incident mode', 'lockdown', 'emergency mode'],
    'TRACEABILITY': ['spec', 'specification', 'V9', 'traceability', 'requirements'],
}

SECRET_KEY_PATTERNS = re.compile(r'(secret|token|api[_-]?key|password|client_secret|private_key)', re.IGNORECASE)
ENV_LINE = re.compile(r'^\s*([A-Z0-9_]+)\s*=')


def iter_files() -> Iterable[Path]:
    for base in SEARCH_DIRS:
        base_path = (ROOT / base).resolve()
        if not base_path.exists():
            continue
        for root, dirs, files in os.walk(base_path):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for filename in files:
                path = Path(root) / filename
                if path.suffix.lower() not in INCLUDE_EXTS:
                    continue
                if any(part in EXCLUDE_DIRS for part in path.parts):
                    continue
                yield path

    # Root-level files (avoid full repo traversal)
    for path in ROOT.iterdir():
        if path.is_dir() or path.name in EXCLUDE_DIRS:
            continue
        if path.suffix.lower() not in INCLUDE_EXTS:
            continue
        yield path


def search_patterns(patterns: List[str]) -> Dict[str, List[int]]:
    hits: Dict[str, List[int]] = {}
    compiled = [re.compile(p, re.IGNORECASE) for p in patterns]
    for path in iter_files():
        try:
            text = path.read_text(encoding='utf-8')
        except Exception:
            continue
        lines = text.splitlines()
        line_numbers: List[int] = []
        for idx, line in enumerate(lines, start=1):
            if any(p.search(line) for p in compiled):
                line_numbers.append(idx)
        if line_numbers:
            hits[str(path.relative_to(ROOT))] = line_numbers
    return hits


def collect_secrets() -> Dict[str, List[str]]:
    secrets: Dict[str, List[str]] = {}
    for path in iter_files():
        try:
            text = path.read_text(encoding='utf-8')
        except Exception:
            continue
        # .env style
        if path.name.startswith('env') or path.suffix in {'.env', '.example'}:
            keys = []
            for line in text.splitlines():
                match = ENV_LINE.match(line)
                if not match:
                    continue
                key = match.group(1)
                if SECRET_KEY_PATTERNS.search(key):
                    keys.append(key)
            if keys:
                secrets[str(path.relative_to(ROOT))] = sorted(set(keys))
            continue

        # JSON style
        if path.suffix.lower() == '.json':
            keys = set()
            for match in re.finditer(r'"([^"]+)"\s*:', text):
                key = match.group(1)
                if SECRET_KEY_PATTERNS.search(key):
                    keys.add(key)
            if keys:
                secrets[str(path.relative_to(ROOT))] = sorted(keys)
            continue

        # Generic key=value in code
        keys = set()
        for match in re.finditer(r'\b([A-Z0-9_]{3,})\b', text):
            key = match.group(1)
            if SECRET_KEY_PATTERNS.search(key):
                keys.add(key)
        if keys:
            secrets[str(path.relative_to(ROOT))] = sorted(keys)

    return secrets


def write_md(path: Path, title: str, intro: str, hits: Dict[str, List[int]]):
    lines = [f"# {title}", '', intro, '']
    if not hits:
        lines.append('- No keyword matches found in scanned code paths.')
    else:
        for file_path, line_numbers in sorted(hits.items()):
            lines.append(f"- {file_path}: {', '.join(str(n) for n in line_numbers[:10])}{'...' if len(line_numbers) > 10 else ''}")
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main() -> int:
    OUTPUT_RUNTIME.mkdir(parents=True, exist_ok=True)

    pep_hits = search_patterns(KEYWORDS['PEP_PDP'])
    ledger_hits = search_patterns(KEYWORDS['LEDGER_AUDIT'])
    evidence_hits = search_patterns(KEYWORDS['EVIDENCE_PACKS'])
    breach_hits = search_patterns(KEYWORDS['BREACH_MODE'])
    trace_hits = search_patterns(KEYWORDS['TRACEABILITY'])

    write_md(
        OUTPUT_RUNTIME / 'GOV_PEPS.md',
        'Policy Enforcement Points (PEP/PDP)',
        'Note: V9 spec file not found in repo; evidence is based on keyword scan only.',
        pep_hits,
    )
    write_md(
        OUTPUT_RUNTIME / 'LEDGER_AUDIT.md',
        'Ledger + Audit Logging',
        'Note: V9 spec file not found in repo; evidence is based on keyword scan only.',
        ledger_hits,
    )
    write_md(
        OUTPUT_RUNTIME / 'EVIDENCE_PACKS.md',
        'Evidence Packs',
        'Note: V9 spec file not found in repo; evidence is based on keyword scan only.',
        evidence_hits,
    )
    write_md(
        OUTPUT_RUNTIME / 'BREACH_MODE.md',
        'Breach Mode',
        'Note: V9 spec file not found in repo; evidence is based on keyword scan only.',
        breach_hits,
    )

    secrets = collect_secrets()
    secrets_lines = [
        '# Secrets & Keys',
        '',
        'Note: Redacted output. Only file paths + key names are listed. V9 spec file not found in repo.',
        '',
    ]
    if not secrets:
        secrets_lines.append('- No secret-like keys detected in scanned files.')
    else:
        for file_path, keys in sorted(secrets.items()):
            key_list = ', '.join(keys)
            secrets_lines.append(f"- {file_path}: {key_list}")
    (OUTPUT_RUNTIME / 'SECRETS_AND_KEYS.md').write_text('\n'.join(secrets_lines) + '\n', encoding='utf-8')

    write_md(
        OUTPUT_RUNTIME / 'SPEC_TRACEABILITY.md',
        'Spec-to-Code Traceability',
        'Note: V9 spec file not found in repo; traceability is based on keyword scan only.',
        trace_hits,
    )

    def status_for(hits: Dict[str, List[int]]) -> str:
        return 'partial' if hits else 'no'

    gap_matrix = {
        'repo': {
            'branch': os.environ.get('GIT_BRANCH', 'unknown'),
            'commit': os.environ.get('GIT_COMMIT', 'unknown'),
        },
        'areas': [
            {
                'area': 'PEP/PDP',
                'implemented': status_for(pep_hits),
                'evidence_files': sorted(pep_hits.keys()),
                'notes': 'Keyword scan only; V9 spec missing.',
                'next_actions': ['Locate V9 spec file', 'Confirm PEP/PDP expectations vs code'],
            },
            {
                'area': 'Ledger + Audit Logging',
                'implemented': status_for(ledger_hits),
                'evidence_files': sorted(ledger_hits.keys()),
                'notes': 'Keyword scan only; V9 spec missing.',
                'next_actions': ['Locate V9 spec file', 'Verify audit/ledger requirements'],
            },
            {
                'area': 'Evidence Packs',
                'implemented': status_for(evidence_hits),
                'evidence_files': sorted(evidence_hits.keys()),
                'notes': 'Keyword scan only; V9 spec missing.',
                'next_actions': ['Locate V9 spec file', 'Define evidence pack artifacts'],
            },
            {
                'area': 'Breach Mode',
                'implemented': status_for(breach_hits),
                'evidence_files': sorted(breach_hits.keys()),
                'notes': 'Keyword scan only; V9 spec missing.',
                'next_actions': ['Locate V9 spec file', 'Define breach mode behaviors'],
            },
            {
                'area': 'Secrets Handling',
                'implemented': 'partial' if secrets else 'no',
                'evidence_files': sorted(secrets.keys()),
                'notes': 'Secret-like keys detected; values redacted.',
                'next_actions': ['Audit secrets storage/rotation vs V9 spec'],
            },
            {
                'area': 'Spec Traceability',
                'implemented': status_for(trace_hits),
                'evidence_files': sorted(trace_hits.keys()),
                'notes': 'Keyword scan only; V9 spec missing.',
                'next_actions': ['Locate V9 spec file', 'Add explicit traceability anchors'],
            },
        ],
    }

    (OUTPUT_RUNTIME / 'GAP_MATRIX.json').write_text(json.dumps(gap_matrix, indent=2), encoding='utf-8')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
