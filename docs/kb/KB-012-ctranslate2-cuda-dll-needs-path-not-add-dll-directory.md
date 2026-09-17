# KB-012 — ctranslate2's CUDA loading on Windows ignores `os.add_dll_directory()`; only a real `PATH` prepend works

**Area:** Local model (faster-whisper / ctranslate2) — GPU setup on Windows
**Status:** verified
**Date:** 2026-09-17  ·  **From:** T-018

## Claim
On this machine, `faster-whisper`'s CUDA backend (`ctranslate2`) fails to load `cublas64_12.dll`
even when the DLL's directory has been registered via `os.add_dll_directory()` before any
`ctranslate2`/`faster_whisper` import - the exact mechanism Python's own docs recommend for
this situation. Only prepending the same directory to the process's `PATH` environment
variable actually fixes it.

## Evidence
This machine has no system-wide CUDA/cuDNN install - Ollama runs the RTX 4090 fine (D-005,
KB-007) using its own private, non-shared copies of these libraries. Installing
`faster-whisper` and calling `WhisperModel(..., device="cuda", ...).transcribe(...)` failed
with `RuntimeError: Library cublas64_12.dll is not found or cannot be loaded`, even after:

1. `pip install nvidia-cublas-cu12 nvidia-cudnn-cu12` (provides `cublas64_12.dll`,
   `cudnn64_9.dll`, etc. under `.venv/Lib/site-packages/nvidia/<pkg>/bin/`)
2. Calling `os.add_dll_directory(<that path>)` for each of `cublas`, `cudnn`, `cuda_nvrtc`
   before importing `faster_whisper` - still failed, identical error

Isolated check: loading the same DLL directly via
`ctypes.WinDLL(r".venv\Lib\site-packages\nvidia\cublas\bin\cublas64_12.dll")` **succeeded**
with the exact same `add_dll_directory()` calls in place - proving the DLL and its own
dependency chain (nvJitLink, etc.) resolve correctly through that mechanism in general.
`ctranslate2`'s internal CUDA loader specifically does not use it.

Fix: prepend the three `nvidia/*/bin` directories to `os.environ["PATH"]` (not
`add_dll_directory`) before importing `faster_whisper`. Confirmed working:
`scripts/t018_whisper_feasibility.py::_add_cuda_dll_dirs()` - model loads and transcribes
successfully with this in place, identical environment otherwise.

## Consequences
Any code in this project that loads `faster-whisper`/`ctranslate2` on this machine (or any
machine set up the same way - CUDA present only via pip wheels, not a system install) must
prepend those `nvidia/*/bin` directories to `PATH` at process start, not rely on
`add_dll_directory`. If T-017/T-018's Whisper path is ever wired into the real collector,
this setup step needs to run before the first `faster_whisper` import in that code path too,
not just in the standalone feasibility script.

## Confidence and limits
One machine, one `ctranslate2` version (4.8.2 via `faster-whisper==1.2.1`), one Windows
build. Not confirmed whether this is a `ctranslate2`-specific loader quirk, a Windows
DLL-search-order interaction with `LOAD_LIBRARY_SEARCH_*` flags, or something particular to
this Python 3.12 build. Not tested on Linux (where `LD_LIBRARY_PATH` is the analogous
mechanism and may or may not have the same gap). If a future `ctranslate2` version fixes
this, the `PATH`-prepend workaround should be harmless to leave in place regardless.
