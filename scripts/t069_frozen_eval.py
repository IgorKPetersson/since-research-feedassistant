"""T-069: re-run T-032's date-aware vs plain comparison against the frozen eval dataset.

The answer key (docs/eval-questions.md) was written for the dataset as it stood at
HF 2026-09-16 / YouTube 2026-09-17. The live store has moved on - later data, and 5 papers
on or before 2026-09-16 that a later catch-up added - so the comparison is run on a store
built from the frozen archive instead, in data/eval_frozen/ (gitignored, like data/).
The live data/raw/ and data/chroma_store/ are never read or written here.

Steps: unpack the archive (once), check it against docs/eval-dataset-manifest.txt (stop
on any difference), build its own store (once), then run T-032's comparison with every
vg09 path pointed at the frozen copy. Makes real Ollama calls: ~30 answers, ~10 minutes.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

ARCHIVE = Path(r"C:\AIProjects\VG-09-frozen\data-raw-frozen-hf20260916-yt20260917.zip")
FROZEN_DIR = REPO_ROOT / "data" / "eval_frozen"
FROZEN_RAW = FROZEN_DIR / "raw"
FROZEN_STORE = FROZEN_DIR / "chroma_store"


def unpack() -> None:
    if FROZEN_RAW.exists():
        return
    with zipfile.ZipFile(ARCHIVE) as z:
        z.extractall(FROZEN_DIR)  # the archive's own paths start with raw/


def verify() -> None:
    import t020_verify_eval_dataset as t020

    t020.RAW_DIR = FROZEN_RAW
    if t020.main() != 0:
        sys.exit("The unpacked archive does not match the manifest - stopping.")


def point_vg09_at_frozen_copy() -> None:
    import vg09.document
    import vg09.store

    vg09.document.RAW_DIR = FROZEN_RAW
    vg09.store.RAW_DIR = FROZEN_RAW  # imported by value in vg09.store
    vg09.store.STORE_PATH = FROZEN_STORE


def build() -> None:
    from vg09.store import build_store, get_collection

    if FROZEN_STORE.exists() and get_collection().count() > 0:
        print(f"frozen store already built: {get_collection().count()} chunks")
        return
    result = build_store()
    print(f"frozen store built: {result}")


def main() -> None:
    unpack()
    verify()
    point_vg09_at_frozen_copy()
    build()

    import t032_date_aware_vs_plain_comparison as t032

    t032.main(
        file_label="t069-frozen-date-aware-vs-plain",
        title_note=(
            "**T-069:** körd mot en egen store byggd från det frysta arkivet "
            "(`data/eval_frozen/`, verifierad mot `docs/eval-dataset-manifest.txt`), med "
            "produktionens beteende efter T-061–T-068: datumraden med veckodagar, utökade "
            "datumfraser, 200 kandidater och källfilter (papers/videor) i Läge A. Båda "
            "lägena får ankaret som \"idag\" i prompten."
        ),
    )


if __name__ == "__main__":
    main()
