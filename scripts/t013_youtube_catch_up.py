"""T-013: real YouTube catch-up, isolated from HF's (which the ticket's HF
half already verified). Calls vg09.catchup.catch_up_youtube() directly
rather than the combined catch_up() so this doesn't also touch the real HF
watermark/data.

Makes real network calls (yt-dlp, youtube_transcript_api, and possibly a
real local Whisper transcription if captions are blocked, D-009); run it
manually.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vg09.catchup import catch_up_youtube  # noqa: E402


def main() -> None:
    result = catch_up_youtube()
    if result is None:
        print("No youtube watermark - nothing to catch up.")
        return
    print(f"\nYouTube catch-up done: captions={result.fetched_captions} "
          f"whisper={result.fetched_whisper} fallback={result.fetched_fallback} "
          f"already_done={result.already_done} attempts={result.attempts}")


if __name__ == "__main__":
    main()
