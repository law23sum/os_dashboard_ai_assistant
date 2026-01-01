#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from PyPDF2 import PdfReader

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from assistant_hub_gui.assistant_hub import db as hub_db  # noqa: E402


def extract_pdf_text(pdf_path: Path) -> str:
    pdftotext = shutil.which("pdftotext")
    if not pdftotext:
        fallback = Path("/opt/homebrew/bin/pdftotext")
        if fallback.exists():
            pdftotext = str(fallback)
    if pdftotext:
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_path = Path(tmp_dir) / "deliverables.txt"
            subprocess.run(
                [pdftotext, "-layout", str(pdf_path), str(out_path)],
                check=True,
            )
            return out_path.read_text(errors="ignore")
    reader = PdfReader(str(pdf_path))
    parts: List[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text:
            parts.append(text)
    return "\n".join(parts)


def find_layers(text: str) -> List[Tuple[int, str]]:
    return [
        (match.start(), match.group(0).strip())
        for match in re.finditer(r"^LAYER\s+\d+[^\n]*", text, re.MULTILINE)
    ]


def layer_for_position(layers: List[Tuple[int, str]], position: int) -> str:
    layer = ""
    for layer_pos, label in layers:
        if layer_pos <= position:
            layer = label
        else:
            break
    return layer


def parse_deliverables(text: str) -> List[Dict[str, str]]:
    normalized = text.replace("\r", "\n").replace("\t", " ")
    normalized = re.sub(r" +", " ", normalized)
    layers = find_layers(normalized)

    pattern = re.compile(r"(\d{1,2})\.\s+(.+?)\s*(?:\n\s*)?Reason\b", re.MULTILINE)
    matches = list(pattern.finditer(normalized))
    items: List[Dict[str, str]] = []

    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(normalized)
        raw_block = normalized[start:end].strip()
        item_number = int(match.group(1))
        title = match.group(2).strip()
        layer = layer_for_position(layers, start)

        content = raw_block
        prefix = f"{item_number}. {title}"
        if content.startswith(prefix):
            content = content[len(prefix) :].lstrip()

        items.append(
            {
                "item_number": item_number,
                "title": title,
                "layer": layer,
                "content": content,
            }
        )

    deduped: Dict[Tuple[int, str], Dict[str, str]] = {}
    for item in items:
        key = (item["item_number"], item["title"])
        if key not in deduped or len(item["content"]) > len(deduped[key]["content"]):
            deduped[key] = item

    return [deduped[key] for key in sorted(deduped.keys(), key=lambda k: k[0])]


def resolve_user_id(conn, user_id: str | None) -> str:
    if user_id:
        return user_id
    admin_id = os.getenv("OSDASH_ADMIN_ID", "admin").strip() or "admin"
    admin_email = os.getenv("OSDASH_ADMIN_EMAIL", "admin@osdash.local").strip().lower()
    row = conn.execute(
        "SELECT id FROM users WHERE id = ? OR email = ? LIMIT 1", (admin_id, admin_email)
    ).fetchone()
    return row["id"] if row else admin_id


def replace_deliverables(conn, *, user_id: str, source: str, items: List[Dict[str, str]]) -> int:
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM deliverables WHERE user_id = ? AND source = ?",
        (user_id, source),
    )
    now = datetime.now().isoformat(timespec="seconds")
    rows = [
        (
            item["item_number"],
            item["title"],
            item.get("layer") or "",
            item["content"],
            source,
            now,
            user_id,
        )
        for item in items
    ]
    cursor.executemany(
        """
        INSERT INTO deliverables (
            item_number, title, layer, content, source, created_at, user_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()
    return len(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed project deliverables from a PDF into SQLite.")
    parser.add_argument("--pdf", required=True, help="Path to the deliverables PDF.")
    parser.add_argument("--user-id", default=None, help="User id to associate with the deliverables.")
    parser.add_argument("--source", default=None, help="Source label for the deliverables.")
    parser.add_argument("--dry-run", action="store_true", help="Parse and print summary without writing.")
    args = parser.parse_args()

    pdf_path = Path(args.pdf).expanduser()
    if not pdf_path.exists():
        raise SystemExit(f"PDF not found: {pdf_path}")

    text = extract_pdf_text(pdf_path)
    items = parse_deliverables(text)

    if not items:
        raise SystemExit("No deliverables found in the PDF.")

    if args.dry_run:
        print(f"Parsed {len(items)} deliverables from {pdf_path}")
        print("Sample:")
        for item in items[:3]:
            print(f"- {item['item_number']}. {item['title']}")
        return 0

    conn = hub_db.init_db()
    user_id = resolve_user_id(conn, args.user_id)
    source = args.source or pdf_path.name
    inserted = replace_deliverables(conn, user_id=user_id, source=source, items=items)
    conn.close()

    print(f"Inserted {inserted} deliverables for user_id={user_id} source={source}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
