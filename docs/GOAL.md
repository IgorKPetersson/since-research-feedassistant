# GOAL

## One sentence

A local-first, open-source (Apache-2) research-feed assistant that collects Hugging Face
Daily Papers and a handful of chosen YouTube channels, and lets one person ask in plain
language what's new, whether a topic came up, or how a topic has developed over the last
n weeks — running entirely on their own machine with a local model.

## The problem

Keeping up with AI research means checking the HF Daily Papers page and several YouTube
channels every day. Neither has memory across sources or time: you can't ask "did anyone
cover X this month?" or "has Q moved forward in the last four weeks?". Hosted tools that do
something similar cost money and send your interests to someone else's cloud. A small,
local, open-source alternative that runs on one machine — including machines without an
always-on server — doesn't exist in a form that's simple to install.

## The claim we're testing

Date-aware retrieval — filtering chunks by **feed date** before similarity search —
answers time-bound questions ("in the last n weeks") measurably better than plain
similarity search, on a hand-written question set of 15–20 questions.

**Feed date** is the date something appeared in the source we watch, not necessarily when
it was first published elsewhere: HF Daily Papers' `submittedOnDailyAt` for papers, a
video's YouTube upload date for videos. All date filtering and catch-up ingestion use feed
date. A paper's original arXiv `publishedAt` is stored as extra metadata and shown in
citations, but never used for filtering — see D-002. HF's daily selection includes papers
already published on arXiv earlier, so filtering on arXiv `publishedAt` would hide papers
that just appeared in the feed, which is exactly the "what's new" case the project cares
about.

If plain similarity search scores the same, the claim is wrong, and that is a valid result
to report.

## Success criteria

- After the PC has been off for up to 7 days, one catch-up run ingests everything missed
  from HF Daily Papers, with no duplicates when run again
- Every answer cites its sources: link, title, feed date, and — for papers — the arXiv
  publication date
- The three question types work end to end: "what's new", "did X come up", "has Q
  progressed in the last n weeks"
- The evaluation compares date-aware vs plain retrieval, and a large vs a small local model,
  and the results are in the repo
- A fresh clone reaches a first answer by following the README only

## Definition of done

1. Public GitHub repo with Apache-2 `LICENSE` and a README covering install, ingest and asking
2. An ingest command that catches up since the last successful run
3. A simple chat UI that answers with sources, including an empty state when no data exists
4. An evaluation script and a results table committed to the repo
5. Live demonstration and presentation for the course (no written report — I,
   2026-10-02)

Anything beyond this is bonus and belongs in § Parked.

## Non-goals — say no to these

- **Not** an always-on service: no scheduler, no server, no Raspberry Pi
- **Not** Docker, k3s or any deployment setup
- **Not** a graph database
- **Not** multi-user, accounts or authentication
- **Not** all of arXiv — only the HF Daily Papers selection
- **Not** audio transcription (Whisper) unless Phase 0 shows captions can't be fetched
  *and* time allows
- **Not** conversation history in version 1: each question is answered independently, with
  no memory of earlier turns in the session

## Known limitations — state these, don't hide them

1. Only ingests while the PC is on. "24/7" is interpreted as *always caught up when you
2. YouTube channel RSS lists only the latest ~15 videos, so a long absence from a very
   active channel can miss videos
3. YouTube may block caption requests; the fallback is title + description, which gives
   weaker answers for those videos
4. Answer quality depends on the local model; the small-model results show the budget case
5. Sources are mostly English; questions in Swedish may retrieve worse than questions in
   English unless a multilingual embedding model is used

## Parked

- Conversation history / multi-turn memory — asking a follow-up that depends on an earlier
  question is out of scope for version 1; revisit once the single-turn context budget
  (system prompt + question + reasoning/answer + retrieved chunks, see `docs/DESIGN.md`) is
  proven to have room for it under `num_ctx=16000`
- Scheduled ingest (Task Scheduler) or an always-on device
- Local audio transcription with Whisper for videos without captions
- A graph of papers, authors and topics (graph database + agent)
- A morning digest generated automatically
- More sources: blogs, specific arXiv categories
- An MCP API so other agents can query the knowledge base
