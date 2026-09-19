"""T-020: build the frozen-eval-dataset archive and its manifest, once.

Zips data/raw/ (as it stands at T-014's frozen cutoff - HF through 2026-09-16, YouTube
through 2026-09-17) into an archive OUTSIDE the repo, and writes a SHA-256 manifest of
every file INSIDE the repo (small, text, safe to commit) so a later run of
t020_verify_eval_dataset.py can prove data/raw/ hasn't silently changed.

Run once, now, while data/raw/ matches the frozen cutoff. Do not re-run this after a
future catch-up run adds new documents - that would silently redefine what "frozen"
means. Re-freezing for a later eval round is a deliberate new decision, not a rerun of
this script.
"""

from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "data" / "raw"
ARCHIVE_DIR = Path(r"C:\AIProjects\VG-09-frozen")
ARCHIVE_PATH = ARCHIVE_DIR / "data-raw-frozen-hf20260916-yt20260917.zip"
MANIFEST_PATH = REPO_ROOT / "docs" / "eval-dataset-manifest.txt"


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    files = sorted(p for p in RAW_DIR.rglob("*") if p.is_file())
    print(f"{len(files)} files under {RAW_DIR}")

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ARCHIVE_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            zf.write(path, arcname=path.relative_to(RAW_DIR.parent))
    print(f"archive written: {ARCHIVE_PATH} ({ARCHIVE_PATH.stat().st_size} bytes)")

    real_docs = [p for p in files if not p.name.endswith(".pending.json") and p.name != "_done.json"]
    hf_docs = [p for p in real_docs if "hf" in p.relative_to(RAW_DIR).parts]
    yt_docs = [p for p in real_docs if "youtube" in p.relative_to(RAW_DIR).parts]
    done_markers = [p for p in files if p.name == "_done.json"]
    pending_markers = [p for p in files if p.name.endswith(".pending.json")]

    lines = [
        "# T-020 frozen eval dataset manifest",
        "# One line per file under data/raw/, at T-014's frozen cutoff",
        "# (HF through 2026-09-16, YouTube through 2026-09-17).",
        "# Format: <sha256>  <path relative to data/raw/>",
        "# Verify with: .venv/Scripts/python.exe scripts/t020_verify_eval_dataset.py",
        f"# total_files: {len(files)}",
        f"# real_documents: {len(real_docs)} (hf: {len(hf_docs)}, youtube: {len(yt_docs)})",
        f"# hf_done_markers: {len(done_markers)}",
        f"# youtube_pending_markers: {len(pending_markers)}",
        "",
    ]
    for path in files:
        rel = path.relative_to(RAW_DIR).as_posix()
        lines.append(f"{sha256_of(path)}  {rel}")

    MANIFEST_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"manifest written: {MANIFEST_PATH} ({len(files)} files)")


if __name__ == "__main__":
    main()
