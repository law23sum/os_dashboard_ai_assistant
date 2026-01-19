"""Create compressed and remote-aware backups for the activity log database."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from backend_api.utils.activity_logger import (
    ACTIVITY_BACKUP_DIR,
    copy_activity_db,
    create_zipped_backup,
    get_activity_db_path,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backup the activity log database.")
    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=ACTIVITY_BACKUP_DIR,
        help="Local directory to store the ZIP snapshot.",
    )
    parser.add_argument(
        "--remote-db-path",
        type=Path,
        help="Optional destination for a raw activity log DB copy (simulating a remote server).",
    )
    parser.add_argument(
        "--remote-zip-path",
        type=Path,
        help="Optional destination for the ZIP archive (e.g., remote share or server drop).",
    )
    parser.add_argument(
        "--include-main-db",
        action="store_true",
        help="Include the main assistant_hub.db in the ZIP alongside the activity log.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    activity_db = get_activity_db_path()
    if not activity_db.exists():
        print(f"[warning] Activity DB not found at {activity_db}. Nothing to back up.")
        return 1

    zip_path = create_zipped_backup(
        backup_root=args.backup_dir,
        include_main_db=args.include_main_db,
    )
    print(f"Created local archive: {zip_path}")

    if args.remote_db_path:
        remote_path = args.remote_db_path.expanduser()
        remote_path.parent.mkdir(parents=True, exist_ok=True)
        copy_activity_db(remote_path)
        print(f"Copied raw activity DB to remote path: {remote_path}")

    if args.remote_zip_path:
        target_zip = args.remote_zip_path.expanduser()
        target_zip.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(zip_path, target_zip)
        print(f"Copied ZIP archive to remote path: {target_zip}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
