"""T-020: verify data/raw/ still matches docs/eval-dataset-manifest.txt.

Recomputes SHA-256 for every file currently under data/raw/ and compares it against
the committed manifest - proves (or disproves) that the frozen eval dataset T-014's
questions were verified against hasn't changed, without needing the external zip
archive at all (the manifest alone is enough to detect drift; the archive is the
recovery copy if drift is ever found).

Exit code 0 = clean match. Exit code 1 = at least one mismatch, missing, or extra file.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "data" / "raw"
MANIFEST_PATH = REPO_ROOT / "docs" / "eval-dataset-manifest.txt"


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest() -> dict[str, str]:
    expected: dict[str, str] = {}
    for line in MANIFEST_PATH.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        digest, rel = line.split("  ", 1)
        expected[rel] = digest
    return expected


def main() -> int:
    expected = load_manifest()
    actual_paths = {p.relative_to(RAW_DIR).as_posix() for p in RAW_DIR.rglob("*") if p.is_file()}

    missing = sorted(set(expected) - actual_paths)
    extra = sorted(actual_paths - set(expected))
    mismatched = []
    for rel in sorted(set(expected) & actual_paths):
        actual_digest = sha256_of(RAW_DIR / rel)
        if actual_digest != expected[rel]:
            mismatched.append(rel)

    print(f"manifest entries: {len(expected)}")
    print(f"files on disk:    {len(actual_paths)}")

    if missing:
        print(f"\nMISSING ({len(missing)}) - in manifest, not on disk:")
        for rel in missing:
            print(f"  {rel}")
    if extra:
        print(f"\nEXTRA ({len(extra)}) - on disk, not in manifest:")
        for rel in extra:
            print(f"  {rel}")
    if mismatched:
        print(f"\nMISMATCHED ({len(mismatched)}) - content changed since freeze:")
        for rel in mismatched:
            print(f"  {rel}")

    if not (missing or extra or mismatched):
        print("\nOK - data/raw/ matches the frozen manifest exactly.")
        return 0

    print("\nFAILED - data/raw/ no longer matches the frozen manifest.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
