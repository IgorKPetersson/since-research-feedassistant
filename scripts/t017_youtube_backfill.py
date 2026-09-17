"""T-017: paced 4-week YouTube backfill.

Thin entry point over vg09.youtube_backfill.run() - see that module's
docstring for the pacing, ordering and stop-on-block behaviour (D-006/D-008).

Makes real network calls; run it manually.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vg09.youtube_backfill import run  # noqa: E402


def main() -> None:
    result = run()
    print("\n=== T-017 backfill summary ===")
    print(f"captions fetched: {result.fetched_captions}")
    print(f"fallback (title+description): {result.fetched_fallback}")
    print(f"already done (skipped): {result.already_done}")
    print(f"attempts this run: {result.attempts}")
    print(f"channels reached: {result.channels_reached}")
    if result.blocked:
        print(f"ABORTED - blocked on {result.blocked_video} ({result.blocked_reason})")
    else:
        print("Completed full window - no block hit.")


if __name__ == "__main__":
    main()
