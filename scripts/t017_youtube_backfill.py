"""T-017/T-019: paced 4-week YouTube backfill.

Thin entry point over vg09.youtube_backfill.run() - see that module's
docstring for the pacing, ordering and three-tier fallback behaviour
(D-006/D-009). Re-runnable: already-fetched videos are skipped
(`document.exists()`), so running this again for @NateBJones/@ColeMedin
(T-019) does not re-fetch @theAIsearch/@mreflow's already-complete history.

Makes real network calls (and, when Whisper is needed, a real local GPU
transcription); run it manually.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vg09.youtube_backfill import run  # noqa: E402


def main() -> None:
    result = run()
    print("\n=== YouTube backfill summary ===")
    print(f"captions fetched: {result.fetched_captions}")
    print(f"whisper fetched (captions were blocked): {result.fetched_whisper}")
    print(f"fallback (title+description): {result.fetched_fallback}")
    print(f"already done (skipped): {result.already_done}")
    print(f"attempts this run: {result.attempts}")
    print(f"channels reached: {result.channels_reached}")
    print("Completed full window.")


if __name__ == "__main__":
    main()
