"""T-019: does faster-whisper fit in VRAM alongside qwen3:30b-a3b + bge-m3
(D-005's pair), both already loaded via Ollama? Reuses T-018's downloaded
audio file rather than re-downloading.
"""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

AUDIO = Path(__file__).resolve().parent.parent / "data" / "t018_whisper" / "YTG0rdHPTDE.webm"


def add_cuda_dll_dirs() -> None:
    site_packages = Path(__file__).resolve().parent.parent / ".venv" / "Lib" / "site-packages"
    dirs = [str(site_packages / "nvidia" / pkg / "bin") for pkg in ("cublas", "cudnn", "cuda_nvrtc")]
    dirs = [d for d in dirs if os.path.isdir(d)]
    os.environ["PATH"] = os.pathsep.join(dirs) + os.pathsep + os.environ["PATH"]


def main() -> None:
    add_cuda_dll_dirs()
    from faster_whisper import WhisperModel

    print("Loading faster-whisper (small, GPU) alongside qwen3:30b-a3b + bge-m3 ...")
    t0 = time.time()
    try:
        model = WhisperModel("small", device="cuda", compute_type="float16")
        print(f"Whisper model loaded OK in {time.time() - t0:.1f}s")
    except Exception as exc:
        print(f"Whisper model FAILED TO LOAD: {exc!r}")
        return

    print("Transcribing ...")
    t0 = time.time()
    try:
        segments, info = model.transcribe(str(AUDIO), beam_size=5)
        segments = list(segments)
        print(f"Transcription OK in {time.time() - t0:.1f}s, {len(segments)} segments")
    except Exception as exc:
        print(f"Transcription FAILED: {exc!r}")


if __name__ == "__main__":
    main()
