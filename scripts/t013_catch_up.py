"""T-013: catch-up ingestion since the last successful run, per source.

HF: fetches everything since the hf watermark. YouTube: watermark is checked
but never acted on - no YouTube calls are made by this script, per explicit
instruction, until T-017's transcript-path decision lands.

Makes real network calls to the HF Daily Papers API; run it manually.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vg09.catchup import catch_up  # noqa: E402


def main() -> None:
    result = catch_up()
    hf = result["hf"]
    if hf is not None:
        print(f"\nHF catch-up done: {hf['fetched_days']} days fetched, {hf['skipped_days']} "
              f"skipped, {hf['total_papers']} papers written, new watermark {hf['watermark']}.")


if __name__ == "__main__":
    main()
