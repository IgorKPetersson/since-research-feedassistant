# research-feed-assistant

A local-first research-feed assistant for Hugging Face Daily Papers and a handful of
YouTube channels. Ask it in plain language what's new, whether a topic came up, or how a
topic has developed over the last few weeks — it answers with real citations (link, title,
feed date), and runs entirely on your own machine against a local model. No account, no
cloud service, no server process.

## The problem this solves

Keeping up with AI research means checking the [HF Daily Papers](https://huggingface.co/papers)
page and a few YouTube channels every day by hand. Neither has memory across sources or
time — you can't ask "did anyone cover X this month?" or "has Q moved forward in the last
four weeks?". Hosted tools that do something like this cost money and send your interests
to someone else's cloud. This is a small, local, open-source alternative: point it at a
handful of sources, run it on one machine (no always-on server required), and ask it
questions instead of re-reading everything yourself.

It ingests two kinds of sources — HF Daily Papers and YouTube video transcripts — chunks
and embeds them locally, and answers questions against a local Ollama model, with every
claim tied back to a real, clickable source.

## Requirements

- **Python 3.12** (tested with 3.12.10)
- **[Ollama](https://ollama.com/)**, installed and running (`ollama serve`), tested against
  version 0.34.0
- Three Ollama models pulled:
  ```
  ollama pull qwen3:30b-a3b
  ollama pull bge-m3
  ```
  `qwen3:30b-a3b` is the chat model that answers questions; `bge-m3` embeds every document
  chunk and every question (multilingual — see "Asking a question" below). A third model,
  `qwen3:8b`, is only needed for the optional model-size evaluation comparison
  (`docs/eval-results/`, `docs/TICKETS.md` T-033) and isn't required to use the chat UI.
- **A CUDA-capable GPU with real headroom.** Tested on an RTX 4090 (24GB VRAM):
  `qwen3:30b-a3b` (~20GB) and `bge-m3` loaded into Ollama at once leave roughly 2.4GB of
  headroom at this project's context-window settings. A GPU with meaningfully less VRAM
  likely can't hold both models simultaneously. Ollama also runs on CPU only, but that
  configuration hasn't been tested here and will be considerably slower.
- Developed and tested on **Windows**. The stack itself (Python, Ollama, Streamlit) is
  cross-platform, but only the Windows path has actually been run.

## Install

```
git clone https://github.com/IgorKPetersson/research-feed-assistant.git
cd research-feed-assistant
python -m venv .venv
.venv\Scripts\activate        # Windows;  on macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

### Configuring which sources it watches

HF Daily Papers is watched in full — no configuration needed. The YouTube channels are
currently a hardcoded list in [`vg09/channels.py`](vg09/channels.py); there's no config
file or UI for this yet, so changing the channel list means editing that file directly
before running the YouTube backfill below.

## Running ingest

Ingest is a manual, offline step — there's no scheduler or background service (a
deliberate choice; see "Known limitations" below). Run it, then ask questions; run it again
whenever you want to catch up.

**First time (initial backfill — HF: last 8 weeks, YouTube: latest ~4 weeks):**

```
python scripts/t015_hf_backfill.py
python scripts/t017_youtube_backfill.py
python scripts/t012_build_store.py
```

The first two fetch and write raw documents to `data/raw/` (not committed to git — this is
your own local dataset). The YouTube step tries real captions first; if a channel's captions
are blocked, it falls back to local Whisper transcription, and if that also fails, to the
video's title and description alone (weaker, but never a hard failure). The last step
chunks, embeds (via `bge-m3`) and writes everything currently in `data/raw/` into a local
Chroma vector store at `data/chroma_store/` — this is the step that actually makes newly
fetched documents answerable; running the first two without it leaves the assistant unable
to see what was just fetched.

**Catching up after time offline** (the PC being off for a few days is expected and
supported — this is what "no duplicates when run again" and "catches up since the last
successful run" mean in practice):

```
python scripts/t013_catch_up.py
python scripts/t013_youtube_catch_up.py
python scripts/t012_build_store.py
```

All three steps are safe to re-run — nothing is re-fetched or re-embedded twice.

## Asking a question

```
streamlit run app.py
```

opens the chat UI in your browser. Type a question and press "Fråga" (Ask). If nothing has
been ingested yet, the UI shows an explicit empty-state message instead of an empty or
broken screen.

A few things worth knowing before you use it:

- **The interface labels are in Swedish** (sidebar captions, buttons, status messages) —
  this was built for a single Swedish-speaking user. You can still **ask your question in
  any language**; `bge-m3`'s embedding is multilingual and retrieves correctly across
  languages. **Answers are always generated in English**, regardless of what language the
  question was asked in — a deliberate, explicit decision (see `docs/DECISIONS.md`, D-013),
  not something left to the model's default behavior.
- A sidebar lets you override the automatically-interpreted date window (e.g. "last week")
  with an explicit start/end date — the manual override always wins when set.
- Every answer lists its real sources underneath: title, feed date, and a clickable link
  (a YouTube source links to the exact timestamp it was drawn from). If the model's answer
  contains a citation-shaped bracket that couldn't be resolved to a real source, that's
  shown too, not hidden.

## Evaluation

`docs/eval-questions.md` holds the 15 hand-written evaluation questions, each with its own
expected answer and sources. `docs/eval-results/` holds the real, hand-graded comparison
runs against the actual pipeline — currently the date-aware-vs-plain-retrieval comparison
this project's central claim rests on (the model-size comparison is still pending). See
`docs/PLAN.md` and `docs/TICKETS.md` for what's done and what's left.

## Known limitations

- **Ingest only happens while your machine is on and you run it.** There's no scheduler and
  no always-on service by design (see "Non-goals" in `docs/GOAL.md`) — "always caught up"
  means the next time you run ingest, not continuous background updates.
- **YouTube's channel listing only exposes the latest ~15 videos per channel.** A long gap
  between catch-up runs on a very active channel can miss older videos that scrolled off
  that list before you caught up.
- **YouTube may block caption requests outright.** The fallback chain is real captions →
  local Whisper transcription → title and description only — the last of these gives
  noticeably weaker answers for the videos it applies to.
- **Answer quality depends on the local chat model.** Only `qwen3:30b-a3b` is wired into
  the chat UI today; the smaller `qwen3:8b` is evaluated separately (see "Evaluation"
  above) but isn't a model you can currently switch to in the UI itself.
- **Sources are in English.** `bge-m3`'s embedding is genuinely multilingual and retrieves
  correctly across languages, but a question asked in Swedish may still retrieve somewhat
  differently than the same question asked in English, since the text it's being matched
  against is English throughout.

## License

Apache License 2.0 — see [`LICENSE`](LICENSE).

## More

This started as a course project; the full design rationale, the decisions made along the
way (and why), and session-by-session history all live under [`docs/`](docs/) — start with
[`docs/GOAL.md`](docs/GOAL.md) for what this is trying to prove, or
[`docs/DESIGN.md`](docs/DESIGN.md) for how the pipeline actually works.
