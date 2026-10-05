# <img src="docs/assets/since-mark.svg" alt="" width="32" height="32"> Since

*What's happened since you last looked.* Since is the app in this repository
(`research-feed-assistant`): a local-first research-feed assistant for Hugging Face
Daily Papers and a handful of YouTube channels. Ask it in plain language what's new, whether a topic came up, or how a
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

## Start the app

```
streamlit run app.py
```

opens Since in your browser. It has two pages, listed in the sidebar: **Ask** and
**Sources**. The first time, with nothing fetched yet, it opens on Sources.

## Choosing sources and fetching them

Everything about what is watched, and fetching it, is on the **Sources** page.

- **Hugging Face Daily Papers** can be switched on or off, and you choose how many weeks
  of history to fetch the first time (8 by default). The whole daily selection is
  fetched; there is no topic filter.
- **YouTube channels** are added by pasting a channel's address or `@handle`. The address
  is checked against YouTube before it is saved. Up to 5 channels: each one adds a few
  minutes to every update, because videos are fetched slowly on purpose. Four channels
  are suggested on a first start; remove the ones you don't want.
- **Removing a channel** also removes the videos already fetched from it, so answers stop
  using them.
- **Update now** fetches everything new and makes it searchable. It runs in the
  background and shows its progress, and keeps going if you close the browser tab. The
  first update takes the longest (tens of minutes); later ones fetch only what is new.
  Your choices are saved in `data/sources.json`, which is not committed to git — a clone
  of this repository never carries someone else's channels or data.

For each video, real captions are tried first. If YouTube blocks them, the audio is
transcribed locally with Whisper, and if that fails too, the video's title and
description are used alone (weaker, but never a hard failure).

**The app updates itself when you open it.** The first time you open it each day, the
update starts in the background on its own; the header says "Updating…" until it has
finished, and you can ask questions meanwhile. Turn this off on the Sources page ("Update
when the app opens") if you'd rather update only with Update now. There is no scheduler,
so nothing is fetched while the app is closed (see "Known limitations" below). The
header shows how far the data reaches, marks it when it is more than two days old, and
says so in plain words if the last update failed.

### From the terminal instead

The same ingest can be run without the app. First time (Hugging Face: last 8 weeks,
YouTube: latest 4 weeks, using the channels in `data/sources.json`, or the four defaults
in [`vg09/channels.py`](vg09/channels.py) if that file doesn't exist):

```
python scripts/t015_hf_backfill.py
python scripts/t017_youtube_backfill.py
python scripts/t012_build_store.py
```

Catching up afterwards (both sources, then the search index):

```
python scripts/t013_catch_up.py
python scripts/t012_build_store.py
```

All of these are safe to re-run — nothing is fetched twice. The last step is the one that
makes newly fetched documents answerable. Don't run it while the app is answering
questions: the embedded vector store can't be read by one process while another writes it.

## Asking a question

On the **Ask** page, type a question and press Enter or "Ask".

A few things worth knowing before you use it:

- **The interface is in English** (D-016). You can **ask your question in any
  language**; `bge-m3`'s embedding is multilingual and retrieves correctly across
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
runs against the actual pipeline: the date-aware-vs-plain-retrieval comparison this
project's central claim rests on, and the `qwen3:30b-a3b`-vs-`qwen3:8b` model-size
comparison (T-033). See
`docs/PLAN.md` and `docs/TICKETS.md` for what's done and what's left.

## Known limitations

- **Fetching only happens while the app is open.** There's no scheduler and no always-on
  service by design (see "Non-goals" in `docs/GOAL.md`, D-018) — "always caught up" means
  caught up shortly after you open the app, not continuous background updates. After a
  long break the first update can take 10+ minutes.
- **Questions are refused for a few seconds at the end of an update**, while the new
  content is written to the search index. The app says so and you ask again.
- **At most 5 YouTube channels**, a deliberate limit to keep updates short.
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
