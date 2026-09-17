"""T-018: Whisper feasibility test for one video (YTG0rdHPTDE) - D-009's
required check before wiring yt-dlp audio + faster-whisper into the collector.

No youtube_transcript_api / caption call anywhere in this script - only
yt-dlp audio download, then local faster-whisper transcription. If the audio
download itself fails with a blocking-type signal, this script stops and
reports without attempting transcription, per explicit instruction.

Makes real network + GPU calls; run it manually.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yt_dlp  # noqa: E402

VIDEO_ID = "YTG0rdHPTDE"  # the video T-017 was blocked on (KB-008, 2026-09-17)
OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "t018_whisper"
BLOCK_SIGNALS = (
    "403", "429", "sign in to confirm", "not a bot", "too many requests",
    "http error 403", "http error 429",
)


def download_audio(video_id: str) -> Path | None:
    """Downloads bestaudio only, no postprocessing (no ffmpeg re-encode needed
    - faster-whisper/PyAV can decode the native container directly). Returns
    the downloaded file path, or None if the download failed for a reason
    that looks like a block rather than a one-off glitch."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outtmpl = str(OUT_DIR / f"{video_id}.%(ext)s")
    opts = {
        "format": "bestaudio/best",
        "outtmpl": outtmpl,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }
    url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return Path(ydl.prepare_filename(info))
    except Exception as exc:  # noqa: BLE001 - inspecting the message, not routing around it
        message = str(exc).lower()
        looks_blocked = any(sig in message for sig in BLOCK_SIGNALS)
        print(f"\nAudio download failed: {exc!r}")
        if looks_blocked:
            print("This looks like a blocking signal (403/429/bot-check), not a one-off "
                  "glitch - per instruction, STOPPING here. Do not proceed to transcription; "
                  "report only.")
        else:
            print("Does not obviously look like a block (no 403/429/bot-check text matched) "
                  "- still stopping and reporting per the acceptance criteria, since this "
                  "script's job is to report either way, not to retry or guess.")
        return None


def _add_cuda_dll_dirs() -> None:
    """ctranslate2 (faster-whisper's backend) needs cuBLAS/cuDNN on the DLL
    search path. Nothing on this machine's system PATH provides them -
    Ollama uses its own private copies, invisible to other processes
    (KB-012). The pip-installed nvidia-cublas-cu12/nvidia-cudnn-cu12 wheels
    provide them instead, but `os.add_dll_directory()` alone did NOT work -
    ctranslate2's own CUDA loading does not honor it, only a real PATH
    prepend does (KB-012, verified the hard way after add_dll_directory
    loaded the DLL fine standalone via ctypes but ctranslate2 still failed)."""
    import os
    site_packages = Path(__file__).resolve().parent.parent / ".venv" / "Lib" / "site-packages"
    dirs = [str(site_packages / "nvidia" / pkg / "bin") for pkg in ("cublas", "cudnn", "cuda_nvrtc")]
    dirs = [d for d in dirs if os.path.isdir(d)]
    os.environ["PATH"] = os.pathsep.join(dirs) + os.pathsep + os.environ["PATH"]


def transcribe(audio_path: Path) -> None:
    _add_cuda_dll_dirs()
    from faster_whisper import WhisperModel  # imported here so a download-only
    # failure above never even imports faster-whisper/ctranslate2

    print(f"\nLoading faster-whisper (GPU) ...")
    t0 = time.time()
    model = WhisperModel("small", device="cuda", compute_type="float16")
    load_s = time.time() - t0
    print(f"Model loaded in {load_s:.1f}s")

    print(f"Transcribing {audio_path.name} ...")
    t0 = time.time()
    segments, info = model.transcribe(str(audio_path), beam_size=5)
    segments = list(segments)  # the generator is where the real work happens
    transcribe_s = time.time() - t0

    print(f"\nTranscription took {transcribe_s:.1f}s (load {load_s:.1f}s separately)")
    print(f"Detected language: {info.language} (p={info.language_probability:.2f})")
    print(f"Segment count: {len(segments)}")
    print(f"\nFirst 5 segments (real shape faster-whisper returns):")
    for seg in segments[:5]:
        print(f"  start={seg.start:.2f} end={seg.end:.2f} text={seg.text!r}")

    joined = " ".join(s.text.strip() for s in segments)
    print(f"\nFirst 400 chars of joined transcript:\n{joined[:400]}")

    out_json = OUT_DIR / f"{VIDEO_ID}_transcript.txt"
    out_json.write_text(joined, encoding="utf-8")
    print(f"\nFull transcript written to {out_json}")


def main() -> None:
    print(f"T-018: downloading audio for {VIDEO_ID} (no caption call)")
    audio_path = download_audio(VIDEO_ID)
    if audio_path is None:
        print("\n=== STOPPED: audio download did not succeed. No transcription attempted. ===")
        return
    print(f"Audio downloaded: {audio_path} ({audio_path.stat().st_size / 1_000_000:.1f} MB)")
    transcribe(audio_path)


if __name__ == "__main__":
    main()
