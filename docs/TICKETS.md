# TICKETS

The backlog. `docs/PLAN.md` holds phases and exit criteria; this file holds the work.

IDs are `T-001`, `T-002`, … assigned in order, never reused, never renumbered. Use the
`ticket-write` skill to add one and the `ticket-done` skill to close one.

**Statuses:** `todo` · `in-progress` · `blocked` · `review` · `done`

**Git linkage:** branch `t/T-0NN-slug` · commit `T-0NN: imperative summary` ·
PR title `T-0NN — Title`. One ticket ID per commit.

---

## Open

### T-080 — Hide Streamlit's "Press Enter to submit form" hint

**Status:** done
**Size:** S  ·  **Branch:** `t/T-080-hide-enter-hint`  ·  **Phase:** 3

**Goal:** no leftover hint under the question field after a question is sent.

**Why:** I (2026-10-05): after typing and pressing Enter, "Press Enter to submit
form" stays. Measured: Streamlit shows it while focus is in the field, and after Enter
focus stays there, so it stood for 40 s and counting, long after the answer. Not a change
of the day; it has been so since T-051 made Enter submit. I chose to hide it
(over blurring the field with page script, which is fragile across Streamlit versions).

**Acceptance criteria**
- [x] `[data-testid="InputInstructions"]` is hidden by `CUSTOM_CSS` → test
- [x] In a real browser: the hint is not visible while typing or after Enter; Enter
  answered (10 chips); a second question sent with the Ask button ran
- [x] Full suite passes → 351/351

**Out of scope:** the placeholder text (unchanged: "What's happened since…").
**Depends on:** T-051.

---

### T-079 — Understand "over the 5 days", "the previous 5 days" and "de 5 senaste dagarna"

**Status:** done
**Size:** S  ·  **Branch:** `t/T-079-date-phrases`  ·  **Phase:** 3

**Goal:** these phrasings get the same date filter as "the last 5 days".

**Why:** my test (2026-10-05): "How has research on coding agents developed over
the 5 days?" got "No date filter"; the model then made up its own window and said no
source fell inside it. Adding "last" worked.

**Acceptance criteria**
- [x] "over/during/in/within/for the N days/weeks/months" and "previous N …" give the last-N
  window; "the 5 days before/after X" does not → tests (`T079PhrasesFromTheHumansTestTests`),
  failing first
- [x] Swedish "de N senaste dagarna/veckorna/månaderna" works like "senaste N …" → tests
- [x] Full suite passes → 335/335

**Out of scope:** any phrase not seen in a real question.
**Depends on:** T-066.

---

### T-078 — "research" is a topic, not a source: it no longer narrows the search to papers

**Status:** done
**Size:** S  ·  **Branch:** `t/T-078-research-is-a-topic`  ·  **Phase:** 3

**Goal:** a question about research searches papers and videos, and the caption never
claims the question mentions papers when it does not.

**Why:** my test (2026-10-05): "What's new in AI agent research this week?" and
"How has research on coding agents developed over the last month?" both showed "Papers
only (the question mentions papers)", though neither question mentions papers. T-068 put
"research"/"forskning" among the paper words (its notes say so).

**Acceptance criteria**
- [x] `detect_source()` returns None for "research", "forskning", "forskningen" alone;
  "papers", "arXiv", "artiklar" etc. still mean papers → tests, including both of my
  questions; the new test failed first ("'hf' is not None")
- [x] Real run: "What's new in AI agent research this week?" retrieves both papers and
  videos, and the caption has no "Papers only" → 23 papers + 10 videos, caption "Date
  filter (interpreted from the question): 2026-09-29 – 2026-10-05"; "How has research on
  coding agents developed…": 19 papers + 12 videos
- [x] Full suite passes → 326/326

**Out of scope:** re-running the graded evaluation (me, 2026-10-05).
**Depends on:** T-068.
**Notes:** eval questions 7 and 11 ("forskningen") were searched in papers only in
T-069's arm A; after this they search both sources. T-069's numbers describe the app
before this change; `docs/OVERVIEW.md` (T-076) says so.

---

### T-077 — Deck: slides for RAG and the stack, security, and testing

**Status:** todo
**Size:** S  ·  **Branch:** `t/T-048-slidev-deck` (the deck's branch)  ·  **Phase:** 3

**Goal:** the deck shows how Since is built and protected, not only what it does.

**Why:** I (2026-10-05): the deck never says RAG, the stack, the security or the

**Acceptance criteria**
- [ ] One slide names the pipeline as RAG and splits it into retrieval (date filter, then
  vector search), augmentation (excerpts inside a fixed token budget) and generation
- [ ] One slide lists the stack with a one-line reason each, citing its D-0NN in the notes
- [ ] One slide on security states only what T-071–T-074 verified, including the
  injection runs' real outcome
- [ ] One slide on testing: the unit test count from a real run, the graded evaluation,
  the frozen dataset, the fresh-clone test; no CI claimed
- [ ] Swedish without dashes (my standing preference); `npm run build` passes;
  every slide checked by screenshot

**Out of scope:** the overview document (T-076).
**Depends on:** T-071–T-075.
**Notes:** may replace the current "Allt körs på min dator" slide rather than add to it.

---

### T-076 — `docs/OVERVIEW.md`: purpose, design, security, tests and results in English

**Status:** todo
**Size:** M  ·  **Branch:** `t/T-076-overview`  ·  **Phase:** 3

how it works, how it is protected, how it was tested and what the results were.

**Why:** a code repo alone does not explain purpose and results; one document should be
the starting point and walk-through. English, because the app is international.

**Acceptance criteria**
- [ ] `docs/OVERVIEW.md` has: purpose and problem, the claim tested, how it works (RAG,
  with a diagram), stack with reasons, security (threat model and measures, D-020),
  testing, results (the three graded runs and the model comparison), limitations, how to
  try it, and a map of where to read more in the repo
- [ ] Every number links to the file it comes from
- [ ] It states that the graded evaluation predates the T-073 prompt change
- [ ] README links to it in its first lines
- [ ] Read through by me

**Out of scope:** rewriting README's install steps.
**Depends on:** T-071–T-075 (its security section reports their results).
**Notes:** reverses the 2026-10-02 "no written report" only in part: there is still no
separate report, but the overview plays that role in the repo (see GOAL item 5 note).

---

### T-075 — Record D-020 and show that the model has no tools

**Status:** done
**Size:** S  ·  **Branch:** `t/T-075-no-tools`  ·  **Phase:** 3

**Goal:** the "no tools" guarantee is written down and checked, not just true by accident.

**Why:** D-020; it is the main bound on what a prompt injection can do.

**Acceptance criteria**
- [x] A unit test asserts that every Ollama request the app builds (`answer.py`,
  `retrieval.py`, `store.py`) has no `tools`/`functions` field and uses only the
  `/api/chat`, `/api/generate` or `/api/embed` endpoints → `tests/test_no_tools.py`: the
  three real calls captured and checked (127.0.0.1, allowed endpoint, no tool keys, no
  "tool" role), plus a scan of `vg09/*.py` for tool keys. Shown to bite: a request with
  `tools`, and one to another host, both fail the check
- [x] `CLAUDE.md` gains a hard rule citing D-020
- [x] Full suite passes → 350/350

**Out of scope:** —
**Depends on:** —
**Notes:** D-020 itself was written with the spec (2026-10-05).

---

### T-074 — Fetching reaches only the source hosts; ids cannot write outside `data/`

**Status:** done
**Size:** S  ·  **Branch:** `t/T-074-reach`  ·  **Phase:** 3

**Goal:** fetched data cannot make the app contact other hosts or write elsewhere on disk.

**Why:** `docs/DESIGN.md` § Security baseline, behaviour 4.

**Acceptance criteria**
- [x] Every outgoing request in ingest is listed with its host, in the ticket; any host
  outside Hugging Face, arXiv, YouTube and Ollama on 127.0.0.1 is removed or explained →
  read from the code 2026-10-05:
  - `huggingface.co/api/daily_papers` (`hf_papers.fetch_day`)
  - `www.youtube.com` channel listings and video pages via yt-dlp (`youtube.py`,
    `youtube_backfill.py`); audio for Whisper comes from YouTube's own video servers
    (googlevideo.com), which yt-dlp is sent to by YouTube
  - YouTube captions via youtube-transcript-api
  - Ollama on `127.0.0.1:11434` (`answer.py`, `retrieval.py`, `store.py`)
  - **Removed:** Streamlit's usage statistics, on by default (`gatherUsageStats = true`),
    now `false` in `.streamlit/config.toml`, confirmed with `streamlit config show`
  - **Explained, kept:** the browser loads the Instrument Sans font from
    fonts.googleapis.com. Google sees the machine's address and that the page loaded,
    nothing about questions or sources. Self-hosting the font would remove it; not done
- [x] arXiv and video ids are validated against their real formats before they become
  file names; tests show `../`, absolute paths and odd characters are rejected →
  `tests/test_reach.py`, 6 tests, failing first (the Whisper one tried a real download of
  `../evil`). Also found: the HF feed date became a folder name unchecked; it must now be
  YYYY-MM-DD. Every id and date in `data/raw/` already matched; a real day (2026-10-02,
  50 papers) normalizes 50 of 50. Test fixtures `vid1`/`1000.1` got well-formed ids
- [x] Full suite passes → 346/346

**Out of scope:** limiting what the Python process itself may do (no sandbox, D-020).
**Depends on:** —

---

### T-073 — Mark source excerpts as untrusted data, and measure injection attempts

**Status:** done
**Size:** M  ·  **Branch:** `t/T-073-prompt-injection`  ·  **Phase:** 3

**Goal:** instructions hidden in a paper or a transcript are less likely to steer the
answer, and how often they still do is known.

**Why:** I (2026-10-05): prompt injection must be mitigated. D-020.

**Acceptance criteria**
- [x] Each excerpt in the prompt sits between explicit begin/end markers with its number;
  marker look-alikes inside source text are neutralised; tests cover both → **changed in
  the work:** the markers are `<<<BEGIN>>>`/`<<<END>>>` without a number, which stays on
  the `[N]` line inside; numbered `<<<SOURCE N …>>>` markers made the model cite "Source
  N" (93 and 103 times per measurement), which never becomes a chip
- [x] The system prompt says the excerpts are untrusted data, never instructions, and that
  the answer contains no HTML and no links; the extra tokens are measured and taken off
  the chunk budget (as T-061 did); `docs/DESIGN.md`'s budget arithmetic matches → 179 →
  327 tokens for the first version, 304 shipped; 330 reserved; budget 11717 → 11560
- [x] A script plants at least 4 fake documents with different injection attempts
  (ignore instructions, write HTML, add a link, claim a false fact) next to real ones and
  runs each question 5 times through the real pipeline, before and after the change; the
  results are committed, failures included → 6 attacks × 5 runs; steered 2/30 before,
  4/30 and 1/30 for two rejected prompt versions, 0/30 shipped:
  `docs/eval-results/2026-10-05-t073-prompt-injection.md`
- [x] The demo questions still answer with citations after the change (real run) → all
  four `done=stop`, no retries, generation 12.6–21.1 s
- [x] The system prompt asks for a citation in every list item and every paragraph, not
  only "every claim"; measured with the citation-placement script (3 questions × 4 runs,
  before and after, same data) as the share of answers with all citations in the last
  unit — baseline 2026-10-05: 3/12 on the 2026-10-02 code, 2/12 on main → fresh
  baseline on the branch's main 1/12; shipped 0/12, and 0 of 42 answers without any [N]
- [x] Every cited source gets a short sentence on what it says, not a bare "Yes" with one
  link; checked on my "Has Anthropic been mentioned in the last 8 days?", which
  answered "Yes" alone once on 2026-10-05 → 4 of 4 runs: 189–227 words, 16–18 citations
- [x] Full suite passes → 340/340

**Out of scope:** re-running the graded evaluation (me, 2026-10-05); an in-app
notice when citations are bunched at the end (only if the wording does not help).
**Depends on:** T-072 (so a test that makes the model write HTML is already harmless).
**Notes:** the citation criterion added 2026-10-05 at my choice, after their test
showed one answer with every citation in its last sentence; the measurement showed it
happened as often before the day's changes as after.

---

### T-072 — Render the model's answer as text; only the app's own chips are HTML

**Status:** done
**Size:** S  ·  **Branch:** `t/T-072-escape-answer`  ·  **Phase:** 3

**Goal:** nothing the model writes can become live HTML in the browser.

**Why:** found 2026-10-05: `app.py` renders `render_citation_chips()`' output with
`unsafe_allow_html=True`, and the answer text is passed through unescaped.

**Acceptance criteria**
- [x] The answer is HTML-escaped before chips are inserted; tests with
  `<img src=x onerror=…>`, `<script>`, `<a href="javascript:…">` and markdown
  `[x](javascript:…)` show them rendered as text → `AnswerRenderingSafetyTests`, 6 tests,
  written first and failing (8 failures) before the change
- [x] A chip's `href` is only built from an `https://` URL on huggingface.co, arxiv.org or
  youtube.com; anything else gets no chip; tests → including `http://huggingface.co` and
  `huggingface.co.evil.example`
- [x] Citations, quote links and ordinary markdown (bold, lists) still render; checked in
  a real browser with one injected answer and one real answer → injected `<img onerror>`,
  `javascript:` link and `[site](https://evil.example)` shown as text, page title unchanged,
  0 links besides the chip; the backtick case gives 2 live chips; the app on this branch
  answered "What has happened in AI the last 4 days in regards to image generation?" with
  5 chips in a numbered list, no chip HTML as text
- [x] Full suite passes → 332/332

**Out of scope:** the prompt (T-073).
**Depends on:** —
**Notes:** **Plan changed while in progress (2026-10-05),** with my approval: I
then saw chips shown as raw HTML; the cause was the model's backticks (KB-034).
Escaping the text alone would not fix that, so the answer is now rendered by the app with
markdown-it-py (HTML, links, images and autolinks off), chips go only into text tokens,
and the result is one HTML block on one line. markdown-it-py 4.2.0 was already pinned in
`requirements.txt` (a dependency of rich, via Streamlit); using it directly was approved by
I (CLAUDE.md: ask before adding a dependency).

---

### T-071 — The app listens only on this machine

**Status:** done
**Size:** S  ·  **Branch:** `t/T-071-localhost-only`  ·  **Phase:** 3

**Goal:** no other machine can reach Since while it runs.

**Why:** found 2026-10-05: `.streamlit/config.toml` has no `server.address`, so Streamlit
listens on every interface, and this machine has a public IP. Anyone could reach the app,
including the Sources page that starts fetches and writes files.

**Acceptance criteria**
- [x] `server.address = "127.0.0.1"` in `.streamlit/config.toml`, with the reason; XSRF
  protection not disabled
- [x] Started with `Since.bat`: `netstat` shows the port bound to `127.0.0.1` only, and the
  browser opens and answers a question → done with `streamlit run app.py`, the command
  `Since.bat` runs, reading the same config: `127.0.0.1:8501 LISTENING` only; Streamlit
  prints one URL, `http://127.0.0.1:8501`; `http://<LAN IPv4>:8501` refused; in a real
  browser "Has Anthropic been mentioned in the last week?" answered with 7 citation chips.
- [x] Before the change, the same `netstat` check is recorded → `0.0.0.0:8501` and
  `[::]:8501 LISTENING`; Streamlit printed a Network URL (<LAN IPv4>) and an External
  URL (<public IPv4>, the router's public IPv4, not on this machine). The machine has
  global IPv6 addresses, which `[::]` covered. What stopped outside
  connections was the firewall alone
- [x] README says the app is reachable only from the machine it runs on

**Out of scope:** Ollama (already `127.0.0.1`, checked 2026-10-05).
**Depends on:** —

---

### T-070 — Presentation day: demo questions in the running app, then defense-prep

**Status:** todo
**Size:** S  ·  **Branch:** — (docs-only)  ·  **Phase:** 3

**Goal:** the demo shown live has been rehearsed in the real app on the day's data, and
I have practised against hard questions.

**Why:** the two checks moved out of T-048 when it became the Slidev deck (2026-10-05).
A pipeline run is not the app (process lesson, 2026-10-02 handoff).

**Acceptance criteria**
- [ ] On the presentation day or the day before, after the app's own update, each demo
  question in the deck's speaker notes is asked in the browser; answer, citations and
  time are recorded in the ticket. Any question whose answer no longer matches its slide
  is replaced, and the slide updated
- [ ] `defense-prep` is run against the finished deck, and the questions it raises that
  the deck's "likely questions" note lacks are added to it

**Out of scope:** changing the app.
**Depends on:** T-048.
**Notes:** the ticket's date is set by my presentation date, not yet known.

---

### T-069 — Re-run the date-aware vs plain evaluation against the frozen dataset

**Status:** done
**Size:** M  ·  **Branch:** `t/T-069-frozen-eval`  ·  **Phase:** 3

**Goal:** the report's evaluation numbers describe the app as it is after T-061–T-068,
measured on the same frozen dataset the answer key was written for.

**Why:** T-061 (date line), T-066 (date phrases, weekdays), T-067 (candidate pool) and
T-068 (source words) all change what arm A retrieves or what the model is told. The live
store now runs to 2026-10-05 and holds 5 papers on or before 2026-09-16 that the frozen
set does not (1189 vs 1184), so the answer key does not apply to it.

**Acceptance criteria**
- [x] The frozen archive is unpacked to `data/eval_frozen/raw/` and matches
  `docs/eval-dataset-manifest.txt` exactly (1279 files) before anything runs → checked by
  the script before building, and again afterwards: "matches the frozen manifest exactly"
- [x] A separate store is built from it in `data/eval_frozen/chroma_store/`; the live
  `data/raw/` and `data/chroma_store/` are not touched → live: 1795 files and 2985 chunks
  before and after
- [x] Arm A mirrors the app (date range, ranking, source filter, the range passed to the
  answer); both arms are told the anchor (2026-09-17) as today → `generate_answer()` gains
  `today`; the report's anchor is 2026-09-17; the source filter fired in 4 of 15 arm-A
  runs (questions 7, 8, 11, 12)
- [x] The 15 questions × 2 arms run, output in `docs/eval-results/`, with the same layout
  and grading boxes as T-032's → `2026-10-05-1443-t069-frozen-date-aware-vs-plain.md`; 30
  runs, 0 retries, 0 cut off
- [x] I grade it — the agent does not grade (T-032's rule) → graded 2026-10-05:
  **A better 7, B better 1, equivalent 5, both wrong 2** (T-032's last run: 8/0/5/2)

**Out of scope:** changing the questions or the answer key; grading.
**Depends on:** T-067, T-068.
**Notes:** I approved the re-run (2026-10-05). My notes on the grading:
- B's single win (F06) came from A ranking "Benchmark Radar" and a news video's "Real
  Suite" above SWE-Bench Pro Verified, which the answer key calls the wrong ranking — not
  a date-filter failure.
- F14 failed the same way for the sixth time across three runs: both arms cited only
  YouTube, no HF paper, even at 200 candidates instead of 60. That rules out pool size and
  confirms the semantic gap; recorded in `docs/PLAN.md`'s risk register.
- The grading file first had F06 as "both wrong" and F15 as "equivalent"; my
  list (B better, A better) is the correct one, and the file was set to match it.

---

### T-068 — A question that names papers or videos searches only that source

**Status:** done
**Size:** S  ·  **Branch:** `t/T-068-source-words`  ·  **Phase:** 3

**Goal:** "papers", "research", "videos", "YouTube" and their Swedish forms narrow the
search to that source, and the answer's caption says so.

**Why:** the 2026-10-05 probe run: "What were the most important papers yesterday?"
retrieved no papers even from 400 candidates; news videos won on the text.

**Acceptance criteria**
- [x] `vg09.source_filter.detect_source()`: paper words → "hf", video words → "youtube",
  both or neither → None; "video" as a topic ("video generation", "text-to-video",
  "video model") is not a source word → 4 tests, including eval questions 3, 7 and 12
- [x] `retrieve()`/`query_candidates()` take `source`, combined with the date filter in
  one `where` → 2 tests
- [x] The caption under the answer adds "Papers only (the question mentions papers)" or
  "Videos only (…)" → test
- [x] Real runs: "most important papers this week" → 33 papers, 0 videos; "the three
  latest videos" → 35 video excerpts, 0 papers
- [x] Full suite passes → 325/325

**Out of scope:** guaranteeing a mix when no source is named; the eval re-run (T-069).
**Depends on:** T-067.
**Notes:** Affects eval questions 7, 8, 11 (→ papers; their expected answers are papers
only) and 12 (→ videos; expected answer is a video). "Har Palantir nämnts i någon
video?" now searches only videos, but still misses the 2026-09-16 "Palunteer" caption —
a misspelling the embedding doesn't match; found here, not caused here. "research" means
papers: the app's own example "What's new in AI agent research this week?" now searches
papers only.

---

### T-067 — Fetch enough candidates that the per-document limit can't empty the answer

**Status:** done
**Size:** S  ·  **Branch:** `t/T-067-candidate-pool`  ·  **Phase:** 3

**Goal:** a generic question fills the excerpt budget and can reach papers, instead of
stopping at a few news videos.

**Why:** the 2026-10-05 probe run: "What's new this week?" packed 12 excerpts from 6
videos, 38% of the budget, and no papers. Its 60-candidate pool, sized before T-027's
two-per-document limit existed, was taken entirely by those 6 videos; the week's first
paper chunk ranked 71st of the 248 in the window.

**Acceptance criteria**
- [x] `CANDIDATE_POOL_SIZE` 60 → 200, with the measurement in its comment → unit test
  that the pool asked for reaches past rank 71
- [x] Over the 18 probe questions (search only, no answers): every question fills
  96–99% of the budget; "What's new this week?" 38% → 97% with 18 papers; the Swedish
  agents question 49% → 98%; 11 of 18 packed sets change, the 7 already full do not
- [x] Retrieval time measured: median 1.06 s → 1.27 s
- [x] Full suite passes → 318/318

**Out of scope:** guaranteeing a mix of papers and videos (T-068 handles a question that
names one); re-running the Phase 3 evaluation (T-069).
**Depends on:** T-027.
**Notes:** I approved this and T-068/T-069 together (2026-10-05).

---

### T-066 — Understand everyday date phrases, and tell the model the weekday

**Status:** done
**Size:** S  ·  **Branch:** `t/T-066-date-phrases`  ·  **Phase:** 3

**Goal:** "yesterday", "on Friday", "since Monday", "since September", "in August" and
"between September 20 and 25" filter to the dates they mean, and the model knows which
weekday each date is.

**Why:** the 2026-10-05 probe run (18 questions): five of those phrases were ignored, so
the whole store was searched, and "between September 20 and September 25" became
September 20 alone. The model called Sunday 2026-10-04 a Tuesday and a Friday.

**Acceptance criteria**
- [x] English and Swedish: two-date ranges (between/from/–, "mellan den 20 och den 25
  september"), "yesterday"/"igår", weekdays ("on Friday", "last Friday", "i fredags"),
  "since" + yesterday/weekday/date/month, "in"/"during"/"i" + month, "this month" →
  10 new tests; questions naming no range still give None (12-question sweep)
- [x] The date line says "Today is Monday, 2026-10-05" and names the range's weekdays,
  from a fixed English list (not the system locale) → 2 tests; real cost re-measured at
  66 tokens with the longest weekday names, inside T-061's 70 reserved
- [x] The probe's failed questions resolve correctly against the real store → "between
  September 20 and 25": 2026-09-20..25, sources cited from all six days (was one day);
  "on Friday": 2026-10-02; "since Friday": 2026-10-02..05; "since September":
  2026-09-01..10-05; "yesterday": Sunday 2026-10-04, correctly answered as having no
  papers
- [x] Full suite passes → 317/317

**Out of scope:** years ("everything from 2025"); "next week" (nothing is in the future);
calendar-aligned weeks (the rolling 7-day window stays, T-043).
**Depends on:** T-061.
**Notes:** "since Monday" asked on a Monday means today only — the literal reading.
"What was new on Friday?" retrieved the right 32 sources, but the answer cited none of
them — an answer-quality finding, not a date one.

---

### T-065 — The quote check must not flag a quoted title

**Status:** done
**Size:** S  ·  **Branch:** `t/T-065-quoted-titles`  ·  **Phase:** 3

**Goal:** a correctly quoted paper or video title no longer produces T-064's warning.

**Why:** found in the 18-question probe run (2026-10-05): three answers quoted a title
("Does Learning Protein Folding Generalize to Broader Reasoning?", "Circuit Hypernetworks
for Quantum-Augmented Diffusion Language Models", "the end of the app era") and were
flagged, because the check searched the abstract or transcript but not the title.

**Acceptance criteria**
- [x] A source's title is part of the text a quote is checked against → unit test
- [x] The three quotes from the probe run are accepted against the real store → all three
  `True`
- [x] Full suite passes → 306/306

**Out of scope:** the other probe findings, raised with me.
**Depends on:** T-064.
**Notes:** —

---

### T-064 — Warn when a quote is not in the source it is credited to

**Status:** done
**Size:** S  ·  **Branch:** `t/T-064-check-quotes`  ·  **Phase:** 3

**Goal:** an answer that credits a quote to a source that doesn't contain it says so
under the answer, instead of presenting the claim as sourced.

**Why:** found in T-063's browser run (2026-10-05): the model said video `lnB4Zckx_34`
had "the identical statement" ("I've been working in Claude Code and Codex for months…"),
and that video never mentions Claude Code. A safeguard is needed.

**Acceptance criteria**
- [x] Each quote of 4+ words is credited to a source number: a citation bracket right
  after it, else the last source named before it in the same sentence, else the first
  named after it in that sentence → 7 tests in `CreditedSourcesTests`, including the
  real false answer
- [x] A quote is checked against the credited source's whole document (the full
  transcript or abstract on disk), not just the excerpt, case and punctuation ignored →
  tests. **Changed during the work:** an exact match flagged 4 of 12 real quotes whose
  source was right (the model quotes loosely: "a personal agent" for "the personal
  agent"). The check is now the share of the quote's three-word sequences found in the
  source, accepted at 0.6 — measured: right source 0.67–0.86, the real false claim
  0.00, best unrelated video 0.46
- [x] Every quote not found is listed under the answer with its source number, in a
  warning that says to check it, and names the source that does contain it when one of
  the answer's sources does → the real false answer rendered with `st.warning` in a
  browser: "(credited to source 23; it is in source 25)". In the app itself, three live
  answers showed no warning; the model could not be made to misattribute on demand, so
  the app's own three-line wiring was not seen firing
- [x] The real false answer from T-063's run produces the warning for source 23 and not
  for source 25 → against the real store: `[(quote, [23], 25)]`
- [x] Full suite passes → 305/305

**Out of scope:** checking paraphrased claims; changing the prompt to make the model
quote more carefully; removing the false sentence from the answer.
**Depends on:** T-063.
**Notes:** Measured on real answers (2026-10-05), with the tolerant check: one "Quote what
they said" answer about Meta's Muse credited 4 of 5 quotes to the wrong video — each
quote was word for word (score 1.0) from another retrieved video. In the same run of 5
questions, the other 4 answers credited 7 quotes and none was flagged.

---

### T-063 — A quoted video sentence links to the second it is spoken

**Status:** done
**Size:** S  ·  **Branch:** `t/T-063-quote-timestamps`  ·  **Phase:** 3

**Goal:** when an answer quotes a video word for word, its number opens the video where
the quote is spoken, not at the start of the excerpt around it.

**Why:** found by me (2026-10-05): "Has Claude Code been mentioned in the last
week?" quoted a sentence spoken at 9:50 behind a link to 9:32, the excerpt's start. An
excerpt is about 1.5 minutes (median gap between excerpts 84 s, 90th percentile 94 s).

**Acceptance criteria**
- [x] Quoted passages of 4+ words are found in the answer (straight or curly quotes, an
  ellipsis splitting a passage) and located in the video's own transcript lines; the
  link starts 2 seconds before that line (my choice) → 12 tests in
  `tests/test_quote_links.py`, real segments from the reported video
- [x] A quote not in the cited excerpt is looked up in the whole video, because the model
  can put a verbatim quote under the wrong excerpt number of the same video (found in
  the browser: 9:50 words cited as the 14:56 excerpt) → unit test
- [x] A quote not found in that video, or a paraphrase, leaves the excerpt's start, and the
  tooltip says "(excerpt from 9:32, about 1.5 minutes long)"; a located quote says
  "(the quote, at 9:48)" → 2 tests in `RenderCitationChipsTests`
- [x] The reported case resolves to the right moment → against the real store, my
  answer text gives 590.44 s (9:50) and a link to `&t=588`; in the browser the
  same question gave chip 25 → `&t=594` (quote spoken at 9:56, checked in the transcript)
- [x] Full suite passes → 288/288

**Out of scope:** shorter excerpts (would need a re-index and a new evaluation); linking a
paraphrase to a precise moment; checking that a quote attributed to a source is really in
it (see Notes).
**Depends on:** T-062.
**Notes:** The browser run also showed the model claiming "the identical statement" in a
second video (`lnB4Zckx_34`) that never mentions Claude Code. The link fell back
correctly, but the answer's claim was false — a separate problem, raised with me.

---

### T-062 — A citation number opens its paper or video directly

**Status:** done
**Size:** S  ·  **Branch:** `t/T-062-chip-links`  ·  **Phase:** 3

**Goal:** one click on a number in the answer opens the cited paper or video, and hovering
over it says what it is.

**Why:** my request (2026-10-05): a number that only scrolls to the source list
needs a second click to reach the source.

**Acceptance criteria**
- [x] A chip links to the cited excerpt's own URL (for a video, the `&t=` moment of that
  excerpt) and opens in a new tab → 2 tests; 275/275 pass
- [x] A chip carries "Paper: <title>" or "Video: <title>" as its tooltip and accessible
  name, with the title HTML-escaped → unit test with a title containing `"` and `<`
- [x] The source list below the answer is unchanged → `app.py`'s cards untouched; heading
  and cards present in the browser
- [x] In the browser: hovering a chip shows the title, clicking it opens the source in a
  new tab, and the app's own tab stays on the answer → `target`, `rel`, `title` and
  `aria-label` survive Streamlit's rendering (read from the live DOM); clicking chip 1
  opened huggingface.co/papers/2610.02826 in a second tab while the app's tab stayed;
  video chips 9 and 11 for one video carried `&t=0` and `&t=1297`. The native tooltip
  itself was not seen (it does not appear in automated screenshots)

**Out of scope:** changing the source cards; styling the tooltip beyond the browser's own.
**Depends on:** —
**Notes:** the source list stays as it is (2026-10-05).

---

### T-061 — Tell the model today's date and the time range already applied

**Status:** done
**Size:** S  ·  **Branch:** `t/T-061-date-in-prompt`  ·  **Phase:** 3

**Goal:** a question about "today" or "this week" is answered from the sources retrieval
selected, instead of the model rejecting them as being from the future.

**Why:** found by me (2026-10-05). "What has happened with AI today?" retrieved 34
excerpts, all dated 2026-10-05, and the model answered that they were "a future date",
reasoning that today "would be a date in 2023 or 2024". The prompt never states the
date, so the model falls back on its training-era sense of it.

**Acceptance criteria**
- [x] The user message states today's date, and when a date range was applied, that the
  sources were selected for that range and must not be discarded for their date → 3
  tests in `BuildUserMessageTests`
- [x] The extra line's real token cost is measured and taken off `CHUNK_BUDGET_TOKENS`;
  `docs/DESIGN.md`'s budget arithmetic matches → 63 tokens measured (prompt_eval_count
  191 → 254), 70 reserved, budget 11787 → 11717, max top-k still 24
- [x] Re-asking "What has happebned with Ai today?" against the real store gives an answer
  that summarises the 2026-10-05 sources with citations → before: "a future date", no
  citations; after, two runs: 10 and 4 citations, both summarising that day's papers,
  prompt_eval_count 11612/16000. Run through the pipeline, not yet in the browser
- [x] Full test suite passes → 273/273

**Out of scope:** changing how date ranges are resolved (D-012); the eval set re-run.
**Depends on:** —
**Notes:** KB-005 (num_ctx), D-012 (relative windows anchor to the latest feed date).

---

### T-060 — Start the app with a double-click

**Status:** done
**Size:** S  ·  **Branch:** `t/T-060-launcher`  ·  **Phase:** 3

**Goal:** the app is opened by double-clicking a file or a desktop shortcut, not by typing
a command in a terminal.

**Why:** my request (2026-10-05). An update on opening (T-059) only helps if
opening is easy; a terminal command is not something to hand a customer.

**Acceptance criteria**
- [x] `Since.bat` in the repository root starts the app from the project's `.venv`
  whatever the current directory is, and the browser opens on the app → started with
  `Start-Process` from `%TEMP%` (what a double-click does), `/_stcore/health` answered
  `ok`. I confirmed the browser opened (2026-10-05): two tabs, one per test start.
  A literal double-click in Explorer was not done by the agent
- [x] If `.venv` is missing, the window says so in one sentence and points at the README,
  instead of closing → checked with a copy of the file in an empty folder (rather than
  renaming the real venv): the sentence, then "Press any key", exit code 1
- [x] README's "Start the app" section leads with the double-click and says how to put a
  shortcut on the desktop
- [x] A desktop shortcut opens the app → created; started through it, `/_stcore/health` answered `ok`

**Out of scope:** an installer; an icon file; detecting an already-running app.
**Depends on:** —
**Notes:** D-018. `.streamlit/config.toml` gains `server.showEmailPrompt = false`:
Streamlit's first-run email prompt would otherwise wait forever in a window nobody types in.

---

### T-059 — Update by itself when the app opens, with a setting to turn it off

**Status:** done
**Size:** M  ·  **Branch:** `t/T-059-update-on-open`  ·  **Phase:** 3

**Goal:** opening the app is enough to get current data; nobody has to remember Update now.

**Why:** my decision (2026-10-05, D-018): data fell behind twice without the user
noticing, and GOAL promises "always caught up when you ask".

**Acceptance criteria**
- [x] A pure function decides whether to start, and refuses when: the setting is off; no
  sources have been saved (first start); a job is running; a job finished today. It
  starts when the last job was interrupted or finished on an earlier day → 9 tests in
  `StartOnOpenTests`, 270/270 pass
- [x] `update_on_open` round-trips through `data/sources.json`; a file without it loads as
  on → 2 tests; the author's real pre-T-059 file loaded as on in the browser
- [x] The Sources page has a toggle "Update when the app opens", saved on change → in the
  browser: off wrote `"update_on_open": false`, on wrote `true`
- [x] The header says "Updating…" with the current step while a job runs, and the counts
  change after it finishes, without a page reload and without wiping an answer on screen
  → in the browser: a tab opened before the update showed "Updating… YouTube: checking
  @NateBJones" without a reload; a question asked during the update was answered (18.6s)
  and stayed on screen after the update finished and "Updating…" cleared. The update
  found nothing new, so a change in the counts was not seen
- [x] When the last update ended with errors, the header says so in plain words, and an
  Ollama connection failure reads "Ollama isn't running" → 4 tests in `UpdateNoteTests`;
  not seen in a browser (Ollama was not stopped)
- [x] Opening the app in a fresh browser session with no update today starts one; opening
  a second tab does not start another → in the browser: with today's finish in the status
  file, opening started nothing; with the finish set to yesterday, a new tab started job
  pid 13696 at 13:20:20, and a further tab left the same pid and start time; with the
  setting off, a new tab started nothing. The status file was restored after each test

**Out of scope:** scheduled updates with the app closed (parked, D-018); a per-source
update schedule.
**Depends on:** T-055, T-056.
**Notes:** D-018.

---

### T-058 — At most five YouTube channels, with the reason shown on the page

**Status:** done
**Size:** S  ·  **Branch:** — (committed on `main`)  ·  **Phase:** 3

**Goal:** the Sources page says how many channels are sensible and stops at that number.

**Why:** my request (2026-10-02). Every channel adds minutes to every update:
videos are fetched 3–8 seconds apart on purpose, and a blocked one is transcribed locally.

**Acceptance criteria**
- [x] `vg09.sources.MAX_CHANNELS = 5`; `add_channel()` refuses a sixth with a message;
  removing one makes room again; a longer hand-edited file still loads → 2 new tests,
  253/253 pass
- [x] The page states the limit and the reason, and locks the field and the Add button
  when the list is full → checked in a browser: with a fifth (test) channel added, the
  field was disabled and read "The list is full at 5. Remove one to add another."; after
  removing it the field was enabled again and my four channels were unchanged
- [x] The page's own duplicate check is gone; it calls `add_channel()`, so the rules live
  in one place

**Out of scope:** a limit on Hugging Face; measuring the real time per channel.
**Depends on:** T-053, T-056.
**Notes:** Five is my number, not a measured threshold.

---

### T-057 — Sources: README, presentation and a fresh-clone run through the page

**Status:** done — with the limits stated in Notes
**Size:** S  ·  **Branch:** — (committed on `main`)  ·  **Phase:** 3

**Goal:** a new user can follow the README from clone to first answer using the Sources
page, with no terminal ingest commands.

**Why:** the README describes hardcoded channels and three terminal commands (D-017).

**Acceptance criteria**
- [x] README describes the Sources page ("Start the app", "Choosing sources and fetching
  them"); the terminal commands remain as the alternative, with a warning not to rebuild
  the store while the app is answering (KB-026); two new limitations listed
- [x] `docs/presentation.md` mentions the Sources page and its checklist uses it
- [x] A clone with no `data/` is taken through Sources in a real browser → a fresh
  `git clone` at `8914a2a`, 2026-10-02: the app opened on Sources at `/` with 0 papers,
  0 videos, the suggestion banner and the four default channels as "Not fetched yet";
  three were removed and both history settings set to 1 week (saved correctly to the
  clone's own `data/sources.json`); Update now finished in 121s with 233 papers, 2
  videos (both via Whisper), 279 chunks; "What is new in the last week?" answered in 15s
  in the same app, citing both videos

**Out of scope:** new features.
**Depends on:** T-056.
**Notes:** The first attempt at this run found a real defect: the job hung in Whisper
because the CUDA libraries were looked up in `<repo>/.venv` (KB-028). Fixed, then the run
above. **Limits of what was run:** one week of history and one channel, not the default
eight weeks and four channels; the clone used the main project's Python environment, so
README's `pip install -r requirements.txt` step was not repeated (it was in T-034).

---

### T-056 — Sources page in the app: list, add, remove, update, first run, stale marker

**Status:** review — six criteria checked in a real browser; the stale-data marker is
unit-tested only
**Size:** M  ·  **Branch:** — (committed on `main`)  ·  **Phase:** 3

**Goal:** everything D-017 describes is usable from the app.

**Why:** D-017; `docs/DESIGN.md` § Sources page.

**Acceptance criteria**
- [x] The app has two pages, the question page and Sources, and the question page
  behaves as before → Streamlit navigation, `vg09/sources_page.py`. Enter submitted a
  question on the new structure; one click on Ask was not re-tried after the restructure
- [x] Sources shows Hugging Face (on/off, weeks) and each channel with its real document
  count and latest feed date → `docs/screenshots/t056-sources-page.png`. Changing the
  toggle or the week counts was not exercised in the browser
- [x] Adding a channel checks the address against YouTube first → a made-up address gave
  "Couldn't find a YouTube channel…" and saved nothing; `@3blue1brown` was saved and
  shown as "Not fetched yet — searchable after the next update"
- [x] Removing a channel asks for confirmation, then its documents are gone → done twice
  for real on the test channel: gone from the list, the store (63 → 62 videos) and
  `data/raw/`; my four channels untouched (13/12/25/12)
- [x] "Update now" shows the time warning, starts the job, shows live progress, and
  cannot be started twice → real run from the page: progress per channel, button disabled
  throughout, page refreshed itself at the end, 251s in all for one new 3blue1brown
  video (Whisper). Asking a question during the fetch stages was **not** tried
  successfully; during the store-writing stage it is refused with a message by design
- [x] With no data and no `data/sources.json`, the app opens on Sources with the default
  channels pre-selected → seen in T-057's fresh-clone run
- [ ] The header marks data more than two days old — `staleness_note()` is unit-tested;
  not seen in a browser because the data is current

**Out of scope:** automated UI tests (the project has none); scheduled ingest.
**Depends on:** T-053, T-054, T-055.
**Notes:** UI text in English (D-016). Three real defects were found by running it and
fixed: (1) a question asked while the job wrote the store, and every question after the
job finished, failed with Chroma's "Error finding id" — the app's cached client no longer
matched the files. Fixed by `store.reset_client()` when a job has finished
(`ingest_job.refresh_store_if_updated()`), by refusing questions during the writing
stage (`is_writing_store()`), and by the job writing only new chunks (4s instead of
45s). After the fix a question in the same app process cited the newly added channel's
video. (2) The page told an existing user their channels were "suggestions"; now only on
a first start. (3) `/ask` gave "Page not found" — the default page lives at `/`.
**Open, seen once, not explained:** the first question asked about a minute after an
update that had used Whisper waited 120s and ended with "Ollama isn't responding"; the
same question a minute later answered in 7s. `bge-m3` was found unloaded afterwards.

---

### T-055 — Ingest as a background job with a status file

**Status:** done
**Size:** M  ·  **Branch:** — (committed on `main`)  ·  **Phase:** 3

**Goal:** one function starts the whole ingest (fetch, then rebuild the store) as a
separate process, and another reports how far it has come.

**Why:** D-017: the app must be able to start ingest and stay usable while it runs.

**Acceptance criteria**
- [x] `vg09/ingest_job.py`: `start()` launches the job as a separate process and returns
  at once; `status()` reads `data/ingest_status.json`
- [x] The job honours `data/sources.json` → unit-tested for all three cases; the
  new-channel backfill also ran for real (`@3blue1brown`, added in the app, got the
  four-week window and one video while the other four only caught up)
- [x] A second `start()` while one runs is refused (seen for real); a status whose
  heartbeat is old is reported as interrupted (seen for real, after the crash below).
  Liveness is the heartbeat only, not the process id
- [x] A failure in one stage is recorded and the store is still rebuilt → unit-tested;
  not seen for real
- [x] Unit tests (20) with everything external mocked; real runs: the first **died**,
  the second and third completed from the app in 182s and 251s with no errors

**Out of scope:** the page itself (T-056); cancelling a running job.
**Depends on:** T-053, T-054.
**Notes:** Two things only the real runs showed. (1) The first run died 980 passages into
the store rebuild with `PermissionError`: Windows won't replace the status file while a
reader has it open, and the app reads it every two seconds. Writes and reads now retry
for up to two seconds. (2) Checking four channels with nothing new took 316s, because
YouTube was asked for the details of 50 videos per channel. `_list_channel()` now asks
only about videos not on disk and stops at the first one older than the window: 12s.

---

### T-054 — Record each video's channel, so a channel can be counted and removed

**Status:** done
**Size:** M  ·  **Branch:** — (committed on `main`)  ·  **Phase:** 3

**Goal:** the store knows which channel every video came from.

**Why:** D-017: per-channel counts on the page, and removing a channel has to remove
its documents. Today neither `Document` nor chunk metadata records the channel.

**Acceptance criteria**
- [x] `Document.channel` (optional) is set for every newly fetched video and carried
  into chunk metadata; papers have none. Old raw files without the key still load
- [x] A one-time migration assigns a channel to every existing video by listing each
  configured channel, and reports any video it could not assign →
  `scripts/t054_assign_channels.py`, real run 2026-10-02: 62 assigned (NateBJones 25,
  theAIsearch 13, mreflow 12, ColeMedin 12), 0 unassigned
- [x] `vg09.store` can report documents and latest feed date per channel, and delete a
  channel's chunks; raw files for a removed channel are deleted too →
  `channel_stats()`, `remove_channel_data()`. **The removal was only run against mocks
  and a temporary directory, never against the real store** — it deletes my data
- [x] After the migration and a store rebuild on the real data, every YouTube chunk has
  a channel, and the per-channel counts sum to the total number of videos → 1243 YouTube
  chunks, 0 without a channel; 25+13+12+12 = 62 = `corpus_stats()`'s video count
- [x] Unit tests cover the metadata, the per-channel stats and the removal → 226/226

**Out of scope:** the page (T-056).
**Depends on:** T-053.
**Notes:** **A stored-format change** (`Document`, chunk metadata) — additive, same
shape as D-007. I approved it 2026-10-02, with the condition that their current
four channels and all current data stay as they are unless they choose to change them.
A pending video retried later gets no channel (its marker doesn't record one) and would
show up under no channel in `channel_stats()`; there are none today.

---

### T-053 — Sources configuration file, read by ingest instead of the hardcoded list

**Status:** done
**Size:** S  ·  **Branch:** — (committed on `main`)  ·  **Phase:** 3

**Goal:** which channels are fetched is decided by `data/sources.json`, not by code.

**Why:** D-017. First slice: no UI yet, no stored-format change, terminal flow unchanged.

**Acceptance criteria**
- [x] `vg09/sources.py` loads and saves `data/sources.json`; with no file it returns the
  four defaults from `vg09/channels.py` and says the configuration is not saved yet
- [x] A channel can be added from `@handle`, a bare handle, or a `youtube.com/@handle`
  address with or without `/videos`; anything else is rejected with a message; adding an
  existing channel and removing an unknown one are rejected
- [x] `vg09.youtube_backfill.run()` fetches the configured channels; `catch_up_hf()`
  does nothing when Hugging Face is switched off
- [x] Unit tests cover the above with the file path patched to a temporary directory;
  the existing suite still passes → `tests/test_sources.py` (9 tests) plus one in
  `tests/test_catchup.py`; 219/219 pass. No real ingest was run with a saved file yet

**Out of scope:** checking that a channel exists on YouTube (T-056); the page.
**Depends on:** —
**Notes:** —

---

### T-052 — Specify the Sources page and slice it into tickets

**Status:** done
**Size:** S  ·  **Branch:** — (docs-only)  ·  **Phase:** 3

**Goal:** the Sources page exists as a written design, a decision
and checkable tickets before any of it is built.

**Why:** explicit instruction (2026-10-02), after I saw that a cloned repo
carries their own four channels in code.

**Acceptance criteria**
- [x] `docs/DESIGN.md` § Sources page; D-017; tickets T-053–T-057 with dependencies

**Out of scope:** building any of it.
**Depends on:** —
**Notes:** Beyond `docs/GOAL.md`'s Definition of done; the presentation (T-048) is
still outstanding.

---

### T-051 — One action submits a question: Enter or one click on Ask

**Status:** done
**Size:** S  ·  **Branch:** — (committed on `main`)  ·  **Phase:** 3

**Goal:** typing a question and pressing Enter, or typing it and clicking Ask once,
each runs the question.

**Why:** reported by me from using the app (2026-10-02): they had to press Enter
and then click Ask. The field and the button were a bare `st.text_input` plus
`st.button`; the typed text is only committed on Enter or blur, and the rerun that
commit triggers swallowed the click.

**Acceptance criteria**
- [x] The field and the button are one `st.form` (`border=False`, so the layout is
  unchanged) with `st.form_submit_button`
- [x] Checked in a real browser with real key presses and clicks, on the caught-up data:
  typing then one click on Ask answers (no Enter); typing then Enter answers (no click);
  an example button fills the field and one click on Ask answers
- [x] `docs/screenshots/t042-ui-{light,dark}-theme.png` retaken, now showing the
  caught-up corpus (1609 papers, 62 videos, through 2026-10-02)

**Out of scope:** an automated UI test (this project has none).

**Depends on:** T-042.
**Notes:** 209/209 unit tests pass; none of them exercise `app.py`.

---

### T-050 — Ask button contrast: darken the accent so white text reaches WCAG AA

**Status:** done
**Size:** S  ·  **Branch:** — (committed on `main`)  ·  **Phase:** 3

**Goal:** every piece of text set on the accent colour meets WCAG AA (4.5:1).

**Why:** T-045 left this open: the Ask button's white label on `#C17F1A` was 3.32:1.
Both fixes were compared side by side
(`docs/screenshots/t050-ask-button-options.png`); the darker accent was chosen over dark
button text.

**Acceptance criteria**
- [x] The accent is the lightest shade of the same hue on which white reaches 4.5:1 →
  `#A26B16`, 4.52:1 (`scripts/t050_button_contrast_options.py` computes it)
- [x] It is changed everywhere the accent lives: `vg09.ui_helpers.ACCENT_COLOR`, both
  themes in `.streamlit/config.toml`, the three uses in `docs/assets/since-mark.svg`
- [x] Citation chips, which had dark text on the accent (3.86:1 on the new shade), now
  have white text (4.52:1)
- [x] A test computes the contrast from the constant and fails below 4.5 →
  `test_white_text_on_the_accent_reaches_wcag_aa`; 209/209 pass
- [x] Checked in a running browser, both themes: button and chip computed as
  `rgb(162, 107, 22)` with `rgb(255, 255, 255)` text
- [x] `docs/screenshots/t042-ui-{light,dark}-theme.png` retaken, same question and
  1252×1222 viewport as before

**Out of scope:** any other change to T-045's identity.

**Depends on:** T-045.
**Notes:** 4.52:1 passes with little margin; a lighter accent would fail the test.

---

### T-049 — Retrieval takes over a minute per question: find the cause and fix it

**Status:** done
**Size:** S  ·  **Branch:** — (committed on `main`)  ·  **Phase:** 3

**Goal:** a question's retrieval step takes seconds, not a minute, so the app is usable
live.

**Why:** KB-023 recorded 40–100s retrieval and left the cause open. Measured again
2026-10-02: 61s retrieval against 11s generation for one question. Unusable in a live
demonstration.

**Acceptance criteria**
- [x] Each retrieval step is timed separately with Ollama's loaded models recorded after
  each → `scripts/t049_time_retrieval_steps.py`: every request cost about 2s whatever it
  did, both models stayed loaded throughout
- [x] The cause is confirmed by changing one thing and re-measuring → same script with
  `http://127.0.0.1:11434`: `retrieve()` 68.56s → 1.36s, identical result (29 chunks,
  11444 tokens)
- [x] `vg09.store`, `vg09.retrieval` and `vg09.answer` address Ollama as `127.0.0.1`, and
  a test fails if any of them goes back → `OllamaAddressTests`; 208/208 pass
- [x] Re-measured after the change with no override → `retrieve()` 1.17s
- [x] KB-023 marked superseded, KB-024 written
- [x] Seen in the running Streamlit UI, not only through the pipeline functions → real
  browser run 2026-10-02: 17.2s from click to answer for F05 and 13.3s for a second
  question, of which the UI's own "Time" tile (generation) was 7.4s and 9.3s

**Out of scope:** the old feasibility scripts under `scripts/`, which keep `localhost`
as records of past runs; reducing the number of requests retrieval makes.

**Depends on:** —
**Notes:** Timings recorded before this ticket include the overhead (KB-024 lists which).

---

### T-048 — Presentation as a Slidev deck in Since's own design

**Status:** in-progress
**Size:** M  ·  **Branch:** `t/T-048-slidev-deck`  ·  **Phase:** 3

**Goal:** I can present Since from a slide deck that looks like the app, with
speaker notes, a timeline as its carrying visual, and the central claim as a chart —
`docs/GOAL.md` Definition of done item 5.

**Why:** the only Definition of done item not met. The deliverable is a live demo and
presentation, not a written report (2026-10-02). Slidev chosen as the tool, with
honesty about failures and Since's own look (2026-10-05, D-019).

**Acceptance criteria**
- [ ] `presentation/` holds a Slidev deck (`slides.md`, `package.json` with exact
  versions, lockfile); `npm install` then `npm run build` succeed from a clean folder,
  and `npm run dev` shows it in a browser
- [ ] The deck uses Since's identity, not Slidev's default: accent `#A26B16`, Instrument
  Sans, `docs/assets/since-mark.svg`, and a light theme → checked by screenshots of every
  slide, reviewed by me
- [ ] A timeline ("what has happened since…") is the visual thread: on the cover and
  reused to frame the demo, the date-aware claim and the close
- [ ] The date-aware vs plain result is a chart of the three graded runs
  (2026-09-20, 2026-09-22, 2026-10-05: A better 7/8/7, B better 1/0/1), not a table
- [ ] Structure follows my choice: problem → the app (real screenshots of Since
  taken from the running app) → the AI chain → what we measured → "AI gets it wrong: what
  we saw" (KB-029, KB-030, KB-031, F14) → lessons → questions. Every slide has speaker
  notes in Swedish with timing; every number cites its source file in the notes
- [ ] The two unverified-number habits of the earlier deck are not repeated: no number

**Out of scope:** asking the demo questions in the app on the day and `defense-prep`
(T-070); a demo video; changing the app.
**Depends on:** T-032, T-033, T-069 (the graded results it reports).
**Notes:** **Rewritten 2026-10-05** at my request. It was "Draft the live
demonstration and presentation", status `review`, with `docs/presentation.md` as a
run-of-show (three criteria met: Swedish draft with timed sections, numbers traceable,
demo questions verified by `scripts/t048_verify_demo_questions.py` on 2026-10-02). The
two unmet criteria (I editing the draft; asking the questions in the running UI)
moved: the first is replaced by me reviewing the deck, the second went to T-070.
`docs/presentation.md` stays as the source of the content until the deck replaces it.

---

### T-047 — README: the "Since" name and logo, and correct its stale UI facts

**Status:** done
**Size:** XS  ·  **Branch:** `t/T-047-readme-since`  ·  **Phase:** 3

**Goal:** the README presents the app as "Since", with its logo, and no longer
describes a UI that no longer exists.

**Why:** (2026-09-24) after T-044–T-046 merged, the README needed the new name and
the logo. Reading it showed three statements that
became false during this session, all in the section about using the UI. Leaving
known-false instructions in a file being edited for the UI's identity would be worse
than fixing them, so they're included here and named:
- "press 'Fråga' (Ask)": the button is "Ask" (T-042, D-016)
- "The interface labels are in Swedish": English since D-016
- "the model-size comparison is still pending": T-033 is done and graded

**Acceptance criteria**
- [x] Title is "Since" with `docs/assets/since-mark.svg` beside it
- [x] The repository name "research-feed-assistant" stays where it's a real identifier
  (the clone URL, the `cd` path), and the README says the app is called Since
  inside that repo. Same boundary T-045 drew: display name only.
- [x] The three stale statements above are corrected; nothing else in the README changes

**Out of scope:** renaming the GitHub repository, `CLAUDE.md`'s project heading, or
the `vg09` package.

 — Logo mark: timeline-with-marker SVG in the header and as the favicon

**Status:** done
**Size:** S  ·  **Branch:** `t/T-046-logo-mark`  ·  **Phase:** 3

**Goal:** "Since" has a mark, not just a wordmark. It's a timeline: a faded line for
what's already been seen, a solid line for what's new, and a dot at the "since" point.
It's shown left of the wordmark in the header and used as the browser-tab favicon.

**Why:** my explicit instruction (2026-09-24), with the SVG supplied verbatim.

**Acceptance criteria**
- [x] `docs/assets/since-mark.svg` is exactly the supplied SVG, with `CURRENT_ACCENT`
  replaced by the accent in use (`#C17F1A`, `vg09.ui_helpers.ACCENT_COLOR`)
- [x] Rendered in the header left of the "Since" wordmark, vertically centred, about
  26px tall
- [x] Wordmark tightened: letter-spacing -0.3px. Weight **not** raised, see Notes.
- [x] The same SVG file is the browser-tab favicon
- [x] Checked live in both themes, with a close-up header screenshot
- [x] `.venv/Scripts/python.exe -m unittest discover -s tests` passes

**Depends on:** T-045 (the header, wordmark and accent this builds on). Branched from
`t/T-045-visual-identity`, which isn't merged yet.

**Evidence (2026-09-24)**
- Tests: `Ran 207 tests ... OK` (2 new: the SVG has the accent three times and no
  `CURRENT_ACCENT` left; the header `<img>` is an SVG data URI with `alt=""`).
- Live, fresh `streamlit run app.py`: the mark's bounding box is 26×26px, and its
  vertical centre is 109.0px against the wordmark's 108.99px. The wordmark's computed
  style is `font-weight: 700`, `letter-spacing: -0.3px`, Instrument Sans. The favicon
  `<link>` is an SVG data URI that decodes byte-identical to the header mark (both come
  from `docs/assets/since-mark.svg` via `vg09.ui_helpers.LOGO_MARK_PATH`: Streamlit's
  `page_icon` turns a local `.svg` path into a data URI).
- Both themes switched from the main menu (backgrounds `rgb(255, 255, 255)` and
  `rgb(14, 17, 23)`). Close-ups are in `.playwright-mcp/` (gitignored, not committed):
  `t046-header-{light,dark}.png` at 1×, `t046-brand-{light,dark}-3x.png` zoomed.

**Notes**
- **Weight:** the wordmark was already 700, the heaviest weight Instrument Sans ships.
  Google Fonts returns HTTP 400 for `wght@800`. A heavier setting would give a
  browser-synthesised faux bold, which smears the letterforms, so the tighter
  tracking alone does the "logo, not heading" work. If more weight is wanted, the
  real options are a larger size or a different face for the wordmark only. That's
  my call.
- **Mark geometry, as supplied:** the dot (r 4.5 at x 9) covers x 4.5–13.5, so the
  faded "already seen" line (x 2–22) only shows as a stub left of the dot, about 3px
  at 26px tall, and at 35% opacity it's faint on white. Rendered exactly as
  specified, not adjusted.
- The header `<img>` has `alt=""`: the adjacent "Since" wordmark already names it,
  so the SVG's own `aria-label` would otherwise be read twice.

**Lockup follow-up (my review, 2026-09-24).** All values below were measured from
rendered pixels (element screenshots at 1× and at CSS zoom 4×), not taken from the CSS:
- **Gap:** before, the visible space from the line's end to the S was 9.5px (CSS gap
  0.45rem, plus the SVG's right padding and the S's side bearing). CSS gap is now
  5.5px, which measures **8.0px** of visible space at 4×.
- **Size:** the brief asked for the mark to be "roughly the height of the S" and also
  said it looked "slightly oversized". Measured, the dot is 9px and the S is 15px, so
  matching the S would have made the dot bigger. Asked, with zoomed comparisons of
  both readings. My decision: **keep the current 26px size.**
- **Vertical centre:** the geometric centres already matched (0.0px at 4×). At 1× the
  dot rendered 1px below the S's centre (13.0 vs 12.0) because of pixel snapping.
  Fixed with `line-height: 26px` on the wordmark (both boxes start on the same whole
  pixel) plus `top: -0.5px` on the mark. Now **0.0px** at 1×. At 4×, standing in for
  high-DPI screens, the dot is 0.5px high, the compromise between the two. A full
  -1px nudge measured 0.5px *high* at 1×, so it wasn't used. The half-pixel offset
  doesn't blur the dot: its edge profile is the same, just mirrored.
- Close-ups in `.playwright-mcp/` (gitignored): `t046-header-{light,dark}.png` (1×),
  `t046-brand-{light,dark}-4x.png` (zoomed). Tests: `Ran 207 tests ... OK`.
- Full-page screenshots retaken on request, showing the logo lockup:
  `docs/screenshots/t042-ui-{light,dark}-theme.png`. Same question, same 1252×1222
  viewport, theme switched in place. Pipeline: Sep 4-17 · 60 · 20 · 20 · 8.8s,
  context 7434/16000 (46%); 11 citation chips, 5 source cards.

### T-045 — Visual identity: rename to "Since", a real typeface, one accent colour

**Status:** done
**Size:** M  ·  **Branch:** `t/T-045-visual-identity`  ·  **Phase:** 3

**Goal:** the chat UI has a real, deliberate visual identity instead of reading as
stock Streamlit (default font, default red button, a big centered title) - a real
name ("Since"), a distinct typeface, one consistent accent colour, and a compact
header, flat throughout, working in both themes.

**Why:** my explicit instruction (2026-09-24).

**Numbering mix-up, recorded so the history reads correctly:** the
visual-identity work was first called "T-044", but T-044 had already been used
earlier the same session for the pipeline-strip follow-ups ("Date range" tile,
smaller metrics, retaken screenshots). Since ticket IDs are never reused, the
visual-identity work became T-045. A merge of
`t/T-044-ui-polish` was expected to contain the visual identity. It didn't, and the
T-044 screenshots still showed the old name, font and red button. The mismatch came
out before anything was merged. My decision (2026-09-24): numbers stay as they are.
**T-044 = pipeline-strip tweaks, T-045 = visual identity**, no renumbering.

**Acceptance criteria**
- [x] The app is renamed "Since" - display strings only (`app.py`'s `page_title` and
  header), matching T-035's own precedent: the `vg09` package/import path and
  `vg09.store.COLLECTION_NAME` stay explicitly out of scope, untouched
- [x] Header redesigned: "Since" small and left-aligned, with the real corpus counts
  and freshness on the *same line* to its right - no big centered `st.title()`, no
  subtitle line
- [x] Question field placeholder reads "What's happened since…"
- [x] Typeface: a distinct Google Fonts sans (Instrument Sans - see Notes for why over
  Inter) replaces the Streamlit default, applied throughout - scoped to avoid breaking
  Streamlit's own icon-font glyphs (the reasoning expander's arrow, etc.), which use
  their own higher-specificity font rule
- [x] One accent colour, chosen and justified, replaces Streamlit's default red -
  applied via `.streamlit/config.toml`'s `primaryColor` (Streamlit's own supported
  theming mechanism, not CSS overrides fighting its internals) so the Ask button and
  the context-budget bar pick it up natively in both themes. By decision (this
  reverses T-042's own per-source-type chip coloring): citation chips also switch to this one accent,
  dropping the blue/terracotta paper-vs-video distinction chips used to carry - source
  type stays visible via the (unchanged) PAPER/VIDEO badge on each source card
- [x] Pipeline metrics stay smaller than the answer text - already shipped in T-044,
  confirmed still true after this ticket's header/font/colour changes, not re-done
- [x] Flat throughout (no gradients, no box-shadow, no emoji), both Streamlit themes
  confirmed working - real screenshots, not assumed
- [x] `.venv/Scripts/python.exe -m unittest discover -s tests` passes
- [x] Both T-042/T-044 screenshots retaken for real showing the new identity (name,
  header, typeface, accent), light and dark theme, committed over the existing files

**Evidence (2026-09-24)**
- Tests: `Ran 203 tests ... OK` (202 before this ticket's last fix, plus
  `test_citation_chip_text_overrides_streamlit_link_color`).
- Live run: fresh `streamlit run app.py` against the real store and Ollama
  (`qwen3:30b-a3b`), question "Has Anthropic been mentioned in the last two weeks?".
  Pipeline strip: Date range Sep 4-17, Candidates 60, After dedup 20, Packed 20,
  Time 11.4s, Context budget 7434 / 16000 tokens (46%). Answer had 8 citation chips
  and 6 source cards.
- Computed styles checked in the browser (not assumed from the CSS):
  `.app-name` font-family `"Instrument Sans", ...`. `document.fonts` shows Instrument
  Sans and Material Symbols Rounded both loaded. Chip background `rgb(193, 127, 26)`
  (= `#C17F1A`), chip text `rgb(26, 26, 26)`, no underline. Page background
  `rgb(255, 255, 255)` in light and `rgb(14, 17, 23)` in dark, both switched from the
  main menu's System/Light/Dark control.
- Screenshots: `docs/screenshots/t042-ui-light-theme.png`,
  `docs/screenshots/t042-ui-dark-theme.png` (same answer, theme switched in place).
  Retaken after the follow-up fixes below, from a later run of the same question:
  Time 13.8s, 5 chips, 4 source cards, other pipeline numbers unchanged.

**Follow-up fixes (my review of the screenshots, 2026-09-24)**
- Source-card title links used Streamlit's default blue, which clashed with the
  accent. They now use the body text colour with a 2px amber underline. Amber text
  was not used because it's 3.32:1 on white, too low for text. Scoped via a new
  `st.container(key="source_cards")`. Computed styles: link `rgb(49, 51, 63)` in
  light and `rgb(250, 250, 250)` in dark (equal to body text in both), underline
  `rgb(193, 127, 26)`.
- Source-type badges: the VIDEO badge was red/terracotta, which reads as an error.
  All types are now one neutral grey, `#6b6b6b` (white label 5.33:1), and the label
  text carries the type. Computed: `rgb(107, 107, 107)` in both themes.
- Empty question field confirmed on a fresh page load: `value` is empty,
  `:placeholder-shown` is true, and the placeholder reads "What's happened since…".
- Tests: `Ran 205 tests ... OK` (2 new: badges are one grey, links use the accent
  underline).

**Bugs found during live verification, all fixed in this ticket**
1. `st.markdown(CUSTOM_CSS, unsafe_allow_html=True)` with a `<link>` tag ahead of the
   `<style>` block rendered the raw CSS as visible page text. Fixed: `st.html()`.
2. `st.html()` strips `<link>` tags, so the font never loaded. Fixed: `@import` as the
   first rule inside `<style>`.
3. `html, body, .stApp` alone lost the cascade to Streamlit's own
   `[data-testid="stMarkdownContainer"]` font rule (equal specificity, also
   `!important`). Fixed: selector broadened to `[data-testid], [data-testid] *`.
4. That broadened selector overrode the Material icon font, so the reasoning
   expander's arrow rendered as the literal text "keyboard_arrow_right". Fixed: a
   later, more specific `[data-testid="stIconMaterial"]` rule restoring
   `Material Symbols Rounded`.
5. A top-level `[theme]` section in `.streamlit/config.toml` removed the viewer's
   System/Light/Dark toggle entirely and ignored the OS dark-mode preference. Fixed:
   `[theme.light]` and `[theme.dark]` sections, each setting only `primaryColor`.
6. Citation chips rendered their numbers as blue underlined link text on the amber
   (Streamlit's markdown link rule beat `.citation-chip`; the same bug was already
   visible on T-042/T-044's terracotta chips). Fixed: selector scoped under
   `stMarkdownContainer` with `!important` on color and text-decoration. Chip text is
   dark (`#1a1a1a`, 5.24:1 on the accent) rather than white (3.32:1, below WCAG AA
   for small text).

**Open, not fixed here:** the Ask button keeps Streamlit's own white label on the
accent: 3.32:1, below the 4.5:1 AA threshold for normal-size text. Fixing it means
either overriding Streamlit's primary-button styles (including its darker hover and
active states, which dark text would not suit) or choosing a different accent. That's
a design call for me, not an implementation detail.

**Also observed, outside this ticket's scope:** in one of the three live runs of
the same question, the model answered only "Yes [18]". It was a real, correctly
cited, but near-useless one-line answer. The other two runs gave full multi-source
answers. That's answer-generation variance, not UI, and it's worth a ticket if it
recurs.

**Out of scope:** `vg09`/`COLLECTION_NAME` (explicitly named out of scope in the
instruction); renaming `README.md`/`CLAUDE.md`'s own project identity
("research-feed-assistant") - the instruction says "rename the UI", not the project;
self-hosting the Google Font instead of loading it from Google's CDN (see Notes).

**Depends on:** T-035 (the out-of-scope precedent this follows), T-042 (chips, badges,
pipeline strip - what this restyles), T-044 (metric sizing, already done).
**Notes:** **Typeface choice:** Instrument Sans over Inter - Inter is excellent but has
become the default choice for enough modern products that it risks reading as generic
again, the exact complaint this ticket exists to fix; Instrument Sans is comparably
clean and legible at small UI sizes (this app has a lot of small numeric labels -
dates, counts, citation numbers) while reading as a more deliberate choice.

**Accent choice:** `#C17F1A`, a warm amber. It's clearly different from Streamlit's
stock red, and it avoids indigo/violet, the other common "not the default" pick,
which is used widely enough to read as generic too. It holds up against both
backgrounds: 3.32:1 against light's white and 5.69:1 against dark's `#0e1117`. Both
clear the 3:1 WCAG minimum for non-text UI elements (the button fill, progress bar
and chip backgrounds). One hex value lives in two places, `.streamlit/config.toml`
(`primaryColor`) and `vg09.ui_helpers.ACCENT_COLOR`. A test fails if they diverge.

**Local-first note, flagged not silently absorbed:** loading a font from Google's CDN
is this chat UI's first real runtime dependency on an external network call outside
ingest - a genuine, if minor, exception to `docs/GOAL.md`'s "local-first" framing,
worth naming even though Google Fonts was the chosen source. The font stack
falls back to system sans-serif fonts if the CDN is unreachable (standard CSS
fallback), so the UI still renders and functions correctly offline - nothing actually
breaks, only the specific typeface choice is affected.

---

### T-044 — Pipeline strip follow-ups: "Date range" shows the resolved window, metrics sized below the answer

**Status:** done
**Size:** S  ·  **Branch:** `t/T-044-ui-polish`  ·  **Phase:** 3

**Goal:** T-042's pipeline strip tells me the actual resolved date window at a
glance instead of a coarse category label, and its five metric tiles read as
supporting detail, not as the visually dominant thing on the page.

**Why:** my explicit instruction (2026-09-24), found while reviewing T-042's real
screenshots for a report: (1) the "Mode" tile said "Filtered"/"None"/etc. - true, but
less useful than just showing the real window ("Sep 11-17"); (2) `st.metric`'s default
hero-number styling makes five pipeline numbers visually outrank the answer paragraph
they're describing, backwards for what matters most on the page. Also: T-042's two
committed screenshots were taken before T-043 landed, so they show T-042's own real,
live-found bug (an English question resolving to no date filter) - stale evidence for
a report about the current, fixed UI.

**Acceptance criteria**
- [x] The pipeline strip's first tile is labeled "Date range" (not "Mode") and shows
  the real resolved window compactly (e.g. "Sep 11-17"), or "None" when no window was
  resolved → `vg09.ui_helpers.format_date_range_short()` (new, 6 tests: same-month,
  single-day, month-boundary, year-boundary, `None`, and a portability test confirming
  no POSIX-only `strftime` flags are used - this project runs on Windows). Reflects the
  actual `date_range` passed to `retrieve()` (post manual-override), not the merely-
  interpreted one. Confirmed live: a real question resolving "the last two weeks"
  showed **"Sep 4-17"**, matching the caption below it exactly
  ("2026-09-04 – 2026-09-17")
- [x] The pipeline strip's five metric values render visually smaller than the answer
  text below them → `st.container(key="pipeline_strip")` + CSS scoped to
  `.st-key-pipeline_strip [data-testid="stMetricValue"/"stMetricLabel"]` (0.95rem
  values, 0.7rem labels - below Streamlit's ~1rem body text default). Confirmed live in
  both themes: the five tiles (Date range/Candidates/After dedup/Packed/Time) read as
  supporting detail under the answer paragraph, not competing with it - the status
  bar's Papers/Videos/Chunks tiles untouched, confirmed still full-sized in the same
  screenshots
- [x] Both T-042 screenshots retaken for real on current `main`, with a real question
  that actually resolves a date window ("Has Anthropic been mentioned in the last two
  weeks?" - now resolves via T-043, where the original screenshots predate it and show
  `Mode: None`) - light and dark theme, committed over the existing files
  (`docs/screenshots/t042-ui-light-theme.png`/`t042-ui-dark-theme.png`). Real numbers
  in the new screenshots: Date range Sep 4-17, Candidates 60, After dedup 20, Packed
  20, Time 13.4s, context budget 7434/16000 (46%), 6 real citation chips linking to 6
  real source cards
- [x] `.venv/Scripts/python.exe -m unittest discover -s tests` passes → **194/194**
  (2 net new: 4 `ShortModeLabelTests` removed, 6 `FormatDateRangeShortTests` added)

**Out of scope:** any other T-042 design decision (chip/badge colors, card layout,
example questions).

**Depends on:** T-042 (the pipeline strip this refines), T-043 (needed for a screenshot
that actually shows a resolved English date window).
**Notes:** `short_mode_label()` removed outright rather than deprecated - it had
exactly one caller (`app.py`'s pipeline strip, now `format_date_range_short()`) and its
own 5 tests, both gone in this same ticket; nothing else in the repo referenced it.

---

### T-043 — English relative-time date extraction, matching the Swedish parser's real rules

**Status:** done
**Size:** M  ·  **Branch:** `t/T-043-english-date-parsing`  ·  **Phase:** 3

**Goal:** `vg09.date_range`'s relative-time extraction (date-range filtering and
recency-ranking detection) works the same in English as it already does in Swedish -
the project's core "what's new"/"has Q progressed" feature no longer silently turns
itself off for a question that isn't written in Swedish.

**Why:** my explicit instruction (2026-09-24), upgraded from a risk-register entry
to a real bug: D-016 (2026-09-23) switched the UI to English by default, and T-042's
own live verification found the real, direct consequence - an English question about
"the last two weeks" resolved to no date filter at all. The core feature was off for
every question not written in Swedish - not acceptable to leave as a deferred
risk-register row once actually seen happening.

**Acceptance criteria**
- [x] `vg09.date_range.extract_date_range()`/`detect_recency_ranking()` handle English
  relative-time phrases alongside the existing Swedish ones, unchanged: "the last/past
  N weeks/days/months", "this week"/"last week"/"the last month" (no number, same
  rolling-window convention as Swedish, not calendar-aligned), "today", real month-name
  absolute dates in both English word orders ("September 16th" and "the 16th of
  September"), and "the latest"/"most recent" for ranking mode - English uses its own
  separate words for the window-vs-ranking distinction rather than a 1:1 translation of
  Swedish's overloaded "senaste"
- [x] Same rules as the Swedish side: "month" means a real calendar month
  (`_subtract_months()`), not a fixed 30 days; a bare plural with no number ("recent
  weeks") stays unresolvable (`None`), never guessed at
- [x] Tested against real English translations of all 15 of `docs/eval-questions.md`'s
  real questions, written by hand once, not machine-translated at run time →
  `scripts/t043_test_english_date_extraction.py`, same methodology as T-021's own
  script (right/wrong/unparseable_ok/unparseable_wrong)
- [x] The original Swedish results are confirmed unchanged - re-run for real, not
  assumed → `scripts/t021_test_date_extraction_against_eval_questions.py` re-run
  unchanged, same 8/0/7/0 result as T-021's original
- [x] Unit tests mirror the existing Swedish test classes one-for-one (`tests/
  test_date_range.py`) - 25 new tests, including both English absolute-date word
  orders and "today" (not exercised by any of the 15 real questions)
- [x] `.venv/Scripts/python.exe -m unittest discover -s tests` passes

**Real results (both, as instructed):**
- **Swedish (re-run, unchanged):** right=8, wrong=0, unparseable_ok=7,
  unparseable_wrong=0 - identical to T-021's original.
- **English (new, real translations):** right=8, wrong=0, unparseable_ok=7,
  unparseable_wrong=0 - **identical tally, question for question**, to the Swedish run.
  Full per-question breakdown, both languages:
  `docs/eval-results/2026-09-24-t043-english-date-extraction.md`.
- Ranking detection (`detect_recency_ranking()`, not covered by the window-extraction
  scripts above) checked separately for the three real ranking questions (F01/F03/F06):
  `True` in both languages; the window questions and the ambiguous bare plural (F09)
  correctly `False` in both.

**Out of scope:** any other language; a general natural-language date parser (this
stays a small, fixed, closed vocabulary matching T-014's real 15 questions plus their
real English translations, same philosophy T-021 established); changing the Swedish
patterns themselves (confirmed byte-for-byte behaviorally unchanged, not just "probably
fine").

**Depends on:** T-021 (the Swedish parser and its real verification methodology, both
reused directly), T-042/D-016 (found this and made it a real bug, not a risk).
**Notes:** `docs/DESIGN.md`'s "Date range: the UI ↔ retrieval contract" section and
`docs/PLAN.md`'s risk register both updated - the risk-register row T-042 wrote for
this exact gap is now marked resolved, not left as a stale "not fixed" note.

---

### T-042 — Redesign the Streamlit UI: status bar, live pipeline strip, citation chips, source cards

**Status:** done
**Size:** L (four largely-independent UI sections plus a language switch, but layout/
presentation only — no retrieval, answer or citation logic changes; see Notes for why
kept as one ticket)  ·  **Branch:** `t/T-042-ui-redesign`  ·  **Phase:** 3

**Goal:** the chat UI shows me what the pipeline actually did — real corpus size
and freshness, the retrieval pipeline filling in stage by stage as it runs, inline
citations that link to real source cards below — instead of a bare answer and a bullet
list, using only data the pipeline already produces.

**Why:** my explicit instruction (2026-09-23). Layout and presentation only, by
explicit scope: `vg09.date_range`, `vg09.retrieval`, `vg09.answer`, `vg09.citations`'
actual behavior is unchanged - this ticket surfaces more of what they already compute,
it does not change what they compute.

**Acceptance criteria**
- [x] **Status bar:** real corpus counts (papers, videos, chunks) and freshness ("caught
  up through `<latest feed_date>`"), read from the real store/watermarks, never
  hardcoded → new `vg09.store.corpus_stats()`, tested (`CorpusStatsTests`). Plus 3
  example-question buttons, one per `docs/GOAL.md` question type, each filling the
  question field on click (`st.button(on_click=...)` + `st.session_state`, confirmed
  live - clicking "Did X come up" correctly filled the real question text). **Real run:
  Papers 1184, Videos 41, Chunks 1971, Caught up through 2026-09-17** - the real
  production store, not fixtures
- [x] **Pipeline strip:** filled in progressively while a query runs, via `st.empty()`
  placeholders updated per stage - not one spinner. Shows mode, candidates, after dedup,
  packed, response time, context-budget bar. Confirmed progressive *live*, not just by
  reading the code: a mid-flight snapshot during a real run showed `Mode: None` already
  resolved while Candidates/After dedup/Packed/Time still read "…", proving the page
  updates stage by stage as real data becomes available, not all at once. Real runs:
  `Candidates 60 → After dedup 49 → Packed 32 → Time 13.9s`, `Context budget: 11484 /
  16000 tokens (72%)` → new `vg09.retrieval.RetrievalResult.candidates_after_dedup`
  (additive field, tested against real dedup scenarios in `test_retrieval.py`)
- [x] **Citation chips:** inline `[N]` markers become clickable, source-type-colored
  chips linking to the matching source card - confirmed live: a real answer's `[1]`,
  `[11]`, `[28]` rendered as blue chips linking to `#cite-1`/`#cite-2`/`#cite-3`, and two
  numbers citing the same document (`[14]`/`[15]` → the same video) both linked to the
  same card. Built from `render_citation_chips()` (`vg09.ui_helpers`, 7 tests) - reuses
  `build_citations()`'s own unlinked/descriptive classification rather than re-deciding
  it, only extracts which numbers to link
- [x] **Source cards** replace the bullet list: source-type badge, title, feed date,
  arXiv date, timestamped video links, `text_source` badge, retrieval rank - confirmed
  live with real cards (`PAPER` badge + `arXiv 2026-09-08` + `retrieval rank #32`;
  `VIDEO` badge + `whisper`/`captions` badge + real timestamped `&t=` link). Needed one
  additive field T-042 added to `vg09.citations.Citation` (`text_source: str | None`) -
  `is_fallback` alone collapses captions/whisper/title_description into two states, the
  card needs the real three-tier distinction; `is_fallback`'s own meaning and every
  existing caller is unchanged
- [x] Kept unchanged: the retry notice, the incomplete-answer warning, the collapsed
  reasoning expander, the manual date-range override, and the empty state → same
  conditions, same triggers, text translated (D-016) but logic untouched
- [x] Design constraints followed: flat (no gradients, no box-shadow), legible in both
  light and dark Streamlit theme, no emoji → confirmed live in both themes (Streamlit's
  own theme toggle, real screenshots each). Chips/badges use fixed, deliberately
  theme-independent swatch colors (not CSS-variable-derived) so they read the same
  regardless of active theme - simpler and more robust than computing theme-adaptive
  colors, verified legible in both real screenshots
- [x] UI-facing text is English throughout (D-016) → every existing Swedish string in
  `app.py`/`vg09.ui_helpers.describe_retrieval_mode()` translated, not just new text
- [x] New pure logic has unit tests, mocked at the same boundaries this project's
  existing tests already use - no live network/GPU calls added → 21 new tests across
  `test_store.py`/`test_retrieval.py`/`test_ui_helpers.py`
- [x] `.venv/Scripts/python.exe -m unittest discover -s tests` passes → **168/168**
  (21 new)
- [x] A real, live verification: the app launched for real, real questions asked through
  the real browser UI (Playwright) against the real production store/Ollama,
  screenshotted in both light and dark theme - not assumed from reading the code. **Two
  real, live-only-discoverable bugs found and fixed in the same session, before
  committing:** (1) `st.metric`'s value truncates with an ellipsis in a narrow column -
  "Unfiltered" rendered as "Unfilt…" and the freshness date as "2026-09-…" - fixed by
  shortening the mode labels to ≤8 characters (tested,
  `test_every_label_is_short_enough_not_to_truncate...`) and moving the freshness value
  out of a 4th equal-width metric column into a plain caption with room to render in
  full. (2) A running Streamlit dev server does not reliably pick up edits to imported
  local modules (only `app.py`'s own top-level changes) - the fix above was invisible
  until the server process was stopped and restarted fresh; confirmed by seeing the OLD
  "Unfiltered" text still render after the file was already saved, then the NEW "None"
  after a clean restart - not a code bug, but a real verification-process gotcha worth
  knowing for next time

**Out of scope:** any change to what a question resolves to, what gets retrieved, how an
answer is generated, or how a citation is resolved — `vg09.date_range`, `vg09.retrieval`'s
actual candidate/dedup/pack behavior, `vg09.answer`, `vg09.citations`'s classification
rules are all unchanged. Conversation history, accounts, multi-user (`docs/GOAL.md`'s
own non-goals, untouched by a layout ticket). Renaming `vg09.ui_helpers.
describe_retrieval_mode()`'s Swedish output is in scope (it's UI-facing text), but its
logic (which mode fired, and why) is not.

**Depends on:** T-025 (the UI this redesigns), T-024 (citations), T-027 (dedup, the count
this surfaces).
**Notes:** Kept as one ticket despite four largely-independent sections because they
share one real constraint worth checking together, not four separate times: every new
number displayed must come from data the pipeline already produces, verified against a
real run, not estimated or recomputed for display purposes. The language-switch
acceptance criterion was added mid-ticket: switch from Swedish to English for consistency with
D-013 (answers are always English) and this being public OSS, recorded as **D-016**.

**Real, unplanned finding surfaced by this ticket's own live verification, not fixed
here (out of scope - `vg09.date_range` logic untouched):** `vg09.date_range`'s
relative-time extraction only matches Swedish phrases. One of T-042's own new English
example questions ("Has Anthropic been mentioned in the last two weeks?") demonstrated
this directly - it resolved to `Mode: None` (unfiltered), not a date-filtered window.
Not new behavior, but newly visible now that the UI's own example questions are English
(D-016) rather than Swedish. Added to `docs/PLAN.md`'s risk register rather than fixed
silently or hidden by picking different example wording.

---

### T-041 — Grill-me follow-ups: stale DESIGN.md numbers, comma-list descriptive citations, missing probe truncation check

**Status:** done
**Size:** S  ·  **Branch:** `t/T-041-grill-me-findings`  ·  **Phase:** 3

**Goal:** three real gaps a Phase 3 `/grill-me` review found (2026-09-23) are closed:
`docs/DESIGN.md` no longer contradicts the real, currently-shipped budget constants; a
descriptive "all N sources" claim written as a comma-separated enumeration is caught the
same way a numeric range already is; and the one real Ollama call site in the repo that
skips `CLAUDE.md`'s `prompt_eval_count`-vs-`num_ctx` check gets it, like every other one.

**Why:** found by `/grill-me` across the whole of Phase 3 (T-031-T-040), triaged by me
2026-09-23, not hypothetical:
1. `docs/DESIGN.md`'s "What happens if retrieved chunks don't fit" section states the
   top-k ceiling as `27` and cites `vg09.retrieval.CHUNK_BUDGET_TOKENS` by name as
   `13245`, unqualified - both are T-038's numbers, superseded by T-039's `24`/`11787`
   and correctly marked superseded everywhere else in the same file, but missed here.
2. D-015's range fix (T-040) only checks a comma-separated *piece's own span* against
   `RANGE_DESCRIPTIVE_THRESHOLD` - a bare number always has span 1, so a model writing
   `[1,2,3,...,31]` instead of `[1-31]` produces 31 real citations, unprotected, even
   though it's the identical "describing the whole source list" failure mode T-040
   exists to catch.
3. `scripts/t039_reasoning_length_probe.py` makes a real `/api/chat` call with an
   explicit `num_ctx` but never checks the real `prompt_eval_count` against it - the one
   real Ollama call site in the repo that doesn't, per `CLAUDE.md`'s hard rule, which
   names no scripts exception.

**Acceptance criteria**
- [x] `docs/DESIGN.md`'s "What happens if retrieved chunks don't fit" section states
  `24` (not `27`) and `11787` (not `13245`) for `vg09.retrieval.CHUNK_BUDGET_TOKENS`,
  matching the same superseded-number marking already used everywhere else in the file
  → both numbers corrected in place, `11787` annotated `(T-039)` matching the file's
  own convention
- [x] `vg09.citations.build_citations()` treats "more than the threshold's worth of bare
  numbers named in one bracket" as descriptive too, not just "one range piece whose own
  span exceeds the threshold" - `[1,2,3,4,5,6]` (6 bare numbers, no dash) is classified
  the same way `[1-6]` already is → the per-piece `any(... > threshold ...)` check
  replaced with `sum(... for start, end in bounds) > threshold`; constant renamed
  `RANGE_DESCRIPTIVE_THRESHOLD` → `DESCRIPTIVE_BRACKET_THRESHOLD` (no longer
  range-specific). `docs/DECISIONS.md` D-015 updated with a **Follow-up (T-041)**
  paragraph describing the corrected counting rule - the threshold value (5) and its
  original reasoning are unchanged, only the earlier, incomplete implementation
- [x] A unit test covers the real shape this ticket names (31 comma-separated bare
  numbers, `[1,2,...,31]`) classifying as descriptive, matching the existing `[1-31]`
  test built from the same real F12-A answer →
  `RangeCitationTests::test_same_claim_spelled_out_as_31_comma_separated_bare_numbers_
  is_also_descriptive`; full `test_citations.py` suite (30 tests) still passes
  unchanged - the sum-based rule is a strict superset of the old per-piece check, so no
  existing test needed touching
- [x] `scripts/t039_reasoning_length_probe.py`'s real streamed call checks the real
  `prompt_eval_count` against `NUM_CTX` and prints the same truncation-risk/close-to-
  `num_ctx` warning every other real Ollama call site in the repo already does → added
  right after the streamed response's final chunk (`done`), same wording/thresholds as
  `vg09.answer._chat_once()`/`vg09.retrieval.count_qwen_tokens()`
- [x] `.venv/Scripts/python.exe -m unittest discover -s tests` passes with the new test
  included → **145/145 pass** (1 new)

**Out of scope:** the `app.py` retry/incomplete UI branches still unverified in a live
browser - I am verifying that myself; T-033 (separate, already-written
ticket, picked up next).

**Depends on:** T-040 (D-015, the threshold this refines), T-039 (the `DESIGN.md`
numbers being corrected, the probe script gaining the check).
**Notes:** Found by `/grill-me` across Phase 3 (T-031-T-040), 2026-09-23 - see that
review's own report (this session) for full context on all findings, including the two
not picked up here (UI verification, deferred to me; T-033, already its own
ticket). No live-browser UI work included here.

---

### T-040 — Resolve range-shaped bracket references (`[1-20]`, `[21-22]`) in citations; don't explode a near-total-source range into one citation per source

**Status:** done
**Size:** M  ·  **Branch:** `t/T-040-range-citations`  ·  **Phase:** 3

**Goal:** a real answer that cites a numeric range (`[1-20]`, `[21-22]`) resolves those
numbers the same way a comma-separated bracket already does, instead of silently falling
into `unlinked_references` and dropping a real cited source — without treating a range that
merely enumerates most or all of the offered sources as if it were evidence for a specific
claim.

**Why:** found for real while grading T-032's output (2026-09-22), not hypothetical. F10-A's
real answer wrote `[1-20]` and `[21-22]` — `vg09.citations.build_citations()`'s comma-split
(`match.group(1).split(",")`) sees `"1-20"` as a single non-digit token, so the whole bracket
is reported unlinked; the YouTube video cited only via `[21-22]` never appears in the
citation list at all, only in the "Hänvisningar ... som inte kunde kopplas" note. T-028 fixed
exactly this failure mode for commas ("a multi-number bracket doesn't even reach
`unlinked_references`, it's dropped from consideration entirely") but never covered ranges.
Separately, F12-A wrote `[1-31]` to support "Palantir is not mentioned" — the same
descriptive-enumeration shape T-024's own ticket already flagged as a known limitation on
real F12 output ("I've reviewed all 38 sources [1] to [38]" — a range describing all sources,
not evidence for a claim, "worth watching in Phase 3 if false-positive citations turn out to
be common on negative answers specifically"). That predicted risk is now real: naively
resolving every number in a near-total-source range would turn one descriptive sentence into
up to 31 false citations — worse than today's unlinked-and-flagged behavior, not better.

**Acceptance criteria**
- [x] `build_citations()` recognizes a bare numeric range inside a bracket (`"1-20"`,
  `"21-22"`, mixed with commas, e.g. `"1, 2-3"`) and, when the range is short enough (see
  below), resolves each number in it against `source_map` exactly as the existing
  comma-separated case does — each resolved number becomes a citation (deduped by
  `doc_id`), each unresolved number is reported individually in `unlinked_references`,
  matching T-028's existing per-number behavior → `vg09.citations.part_bounds()`
  (renamed from `expand_part()`, see this ticket's own follow-up below: it now returns
  bounds, never a materialized list, so the size check runs before any range is built)
- [x] A real range well under the threshold (F10-A's real `[21-22]`, 2 numbers) resolves
  normally into individual citations — unit test built from the real F10-A bracket text
  → `RangeCitationTests::test_real_shape_short_range_resolves_like_a_comma_list`
- [x] A long range (the real F10-A shape `[1-20]`, and the real F12-A shape `[1-31]`) does
  **not** resolve into one citation per number, and is **not** added to
  `unlinked_references` either — it's collected into a new
  `CitationResult.descriptive_ranges`, per **D-015** (my decision, 2026-09-22): a range
  of at most `RANGE_DESCRIPTIVE_THRESHOLD = 5` numbers is a real citation, more is
  descriptive → `RangeCitationTests::test_real_shape_range_covering_the_days_papers_is_
  descriptive`, `test_real_shape_reviewed_all_sources_range_is_descriptive_not_31_citations`,
  plus a boundary test (5 resolves, 6 is descriptive)
- [x] An out-of-range number inside an otherwise-valid short range is unlinked
  individually, not dropped and not failing the whole range (mirrors T-028's existing
  out-of-range-within-comma-list behavior) →
  `test_out_of_range_number_within_a_short_range_is_unlinked_individually`
- [x] Existing non-numeric-range brackets (T-024's original `[Title, YYYY-MM-DD]` case) and
  existing comma-separated brackets (T-028) are unaffected — full existing
  `tests/test_citations.py` suite passes unchanged, plus the new range tests →
  `test_existing_behavior_unaffected_comma_list_and_non_numeric_bracket`, plus a reversed-
  range test (`[5-1]`) confirming a malformed range still falls back to unlinked, not a
  crash
- [x] `.venv/Scripts/python.exe -m unittest discover -s tests` passes with the new tests
  included → **131/131 pass** (11 new, one added by the follow-up fix below)

**Follow-up fix (same ticket), pre-merge `deep-review` finding (2026-09-22):** the
original `expand_part()` called `list(range(start, end + 1))` for every range piece
*before* the descriptive-size check ran, so a single pathological or hallucinated
bracket in real model output (e.g. `[1-500000000]`) would materialize a huge list -
verified at ~7.4s and large transient memory for that exact bracket - before being
discarded as descriptive, on a code path that runs on every real rendered answer over
untrusted model text. Fixed: renamed to `part_bounds()`, now returns the inclusive
`(start, end)` bounds only - `end - start + 1` is checked against
`RANGE_DESCRIPTIVE_THRESHOLD` before any `range()`/`list()` call happens at all; numbers
are only actually built once every piece in the bracket is confirmed at or under the
threshold (at most 5 per piece). New test asserts both the classification and a <0.5s
wall-clock bound for the same `[1-500000000]` bracket that previously took ~7.4s.
131/131 tests pass.

**Out of scope:** retroactively fixing `docs/eval-results/2026-09-22-0027-t032-date-aware-
vs-plain.md` (already committed, ungraded-in-this-sense output stays as it was actually
produced); any other bracket shape the model might still invent beyond numeric
ranges/comma-lists (D-015's own residual-limitation note in `docs/DESIGN.md`); the
retrieval/packing pipeline upstream of citation resolution.

**Depends on:** T-024 (citation resolution), T-028 (the comma-list precedent this extends).
**Notes:** the threshold/policy question this ticket originally left open was decided by me
on 2026-09-22 and recorded as **D-015**: ranges of at most 5 numbers link as normal
citations, longer ranges are descriptive — not expanded, not shown as unlinked, logged
separately. `CitationResult.descriptive_ranges` is rendered in both evaluation scripts
(`scripts/t031_evaluation_harness.py`, `scripts/t032_date_aware_vs_plain_comparison.py`,
"_Beskrivande intervall..._") and, beyond what D-015's instruction named, also in the
production chat UI (`app.py`, same caption pattern as `unlinked_references`) — added there
too so a descriptive range doesn't silently vanish from the one screen an actual user sees,
consistent with T-024/T-025's own "never silently dropped" principle; flagged here in case
that was over-reach beyond what was asked. Found while grading
`docs/eval-results/2026-09-22-0027-t032-date-aware-vs-plain.md` (F10 Bedömning note: "A
skrev intervall [1-20] och [21-22] som inte kopplades, så videon saknas i källistan."; F12
Bedömning note: "A använde intervallet [1-31], samma citeringsbugg som F10."). Not re-run
against the real T-032 comparison file — the committed grading stays exactly as I
graded it; this fix only changes future runs.

---

### T-039 — Raise `NUM_PREDICT` to 4000 and retry once on `done_reason == "length"`

**Status:** done — the one unverified criterion (the retry notice in a running UI) was
checked 2026-10-02: the real `app.py` was run in a browser with `NUM_PREDICT` lowered to
500 in that process only, and both the retry notice and the incomplete-answer warning
appeared (`docs/screenshots/t039-retry-notice-live.png`)
**Size:** M  ·  **Branch:** `t/T-039-raise-num-predict-and-retry-on-truncation`  ·  **Phase:** 3

**Goal:** A question whose reasoning happens to run long no longer comes back with an empty
answer: the reservation covers the reasoning tail actually measured, and the rare answer
that is still cut off gets one automatic second attempt before the user ever sees it.

**Why:** T-032's real run hit `done_reason=="length"` on 4 of 30 calls (F06-A, F07-A, F11-B,
F14-A), each with an empty answer, despite T-028's raise to 2542 and T-038's packing fix.
A read-only probe (32 real runs, high cap, streamed so reasoning and answer tokens are
counted separately) found the cause: sampling variance in reasoning length, on top of a
T-028 cap that was sized from only 3 samples of one question (worst 1842). Real reasoning
ranged 1054-2864 tokens; totals reached 3118; 5/32 runs exceeded 2542. I approved
the fix (2026-09-22): raise the cap, and retry once on `length`.

**Acceptance criteria**
- [x] `vg09.answer.NUM_PREDICT == 4000` and `vg09.retrieval.CHUNK_BUDGET_TOKENS == 11787`
  (`16000-173-40-4000`); a unit test asserts `CHUNK_BUDGET_TOKENS + 173 + 40 + NUM_PREDICT
  == NUM_CTX`, so the two constants can't drift apart again → `ReservationArithmeticTests`
- [x] `generate_answer()` calls Ollama at most twice: a `stop` answer makes exactly one call
  and `retries == 0`; a `length` first answer triggers exactly one more call; if that one
  is `stop` the result is that answer with `retries == 1, incomplete == False`; if it is
  also `length` the result is the second response with `retries == 1, incomplete == True`.
  Each call independently keeps CLAUDE.md's `num_ctx` / `prompt_eval_count` checks. Unit
  tests cover all three paths (mocked, no live Ollama) → `RetryOnLengthTests`; 120/120
  pass. **Verified live (2026-09-22, pre-merge check):** `scripts/t039_verify_retry_live_
  probe.py` monkeypatches `vg09.answer.NUM_PREDICT` down to 500 in-process only
  (`vg09/answer.py` on disk untouched, restored to 4000 before the script exits) and runs
  3 real questions (F01/F06/F11) through the real `generate_answer()` against the real
  store/Ollama. All 3 real runs: first attempt `done_reason=="length"`, a real second
  Ollama call was made, `retries==1`, and - since the retry was *also* cut off at the low
  cap - `incomplete==True` with the retry's own (empty, cap fully consumed by reasoning)
  answer returned, not silently presented as complete. All four checks (a-d) passed on
  all 3 real questions - the retry path the mocks already covered now also fires and
  behaves correctly for real, closing this gap
- [x] The chat UI shows a notice when `retries > 0` (in addition to, not instead of, the
  existing "ofullständigt" warning when the retry was also cut off) → `st.info` in
  `app.py`. **Unverified: not run in a live Streamlit session (only `py_compile`d), and
  there is no automated UI test in this project**
- [x] T-031's and T-032's scripts print the retry count per call and T-032's output file
  header states totals (calls, retries made, calls still `length` after retry); no other
  part of the file format changes → per-arm `**omförsök:** N` field added to the existing
  header line, plus one totals line in the file header
- [x] `docs/DESIGN.md` § Reasoning + answer reservation records the 32-sample measurement
  (highest total 3118) and why T-028's 3 samples were not enough; budget math, max top-k
  (`11787 // 488 = 24`) and the `done_reason` section are updated to match. New KB entry
  and decision record the finding and the retry policy → KB-019, D-014
- [x] Real check, same anchor for both budgets: for all 15 real questions the first 5
  packed chunks under 11787 equal the first 5 deduped candidates (T-028's check, redone
  with T-038's real formatted-source measurement), plus how many chunks each budget packs
  → top-5 identical for 15/15; 9 questions lose 3-5 chunks (35 total), 6 unchanged; the
  smaller packed set is always a prefix of the larger
  (`docs/eval-results/2026-09-22-t039-chunk-budget-impact.txt`)
- [x] `docs/eval-results/2026-09-20-2136-t032-date-aware-vs-plain.md` is byte-identical to
  before this ticket (`git diff` empty); T-032's 15×2 is re-run into a new file of the same
  format; the number of `length` results and of retries made are reported. Full unit suite
  passes. **Needs real Ollama + the production store; these two are the only criteria not
  checkable in a plain dev environment.** → `docs/eval-results/2026-09-22-0027-t032-
  date-aware-vs-plain.md`: **30/30 `stop`, 0 `length`, 0 retries made.** Max
  `prompt_eval_count` 11662 (73%), max elapsed 23.2s. Ungraded, committed as such (as T-032
  did); grading is my step

**Out of scope:** more than one retry; changing the reasoning itself (shorter reasoning,
`think` budget); making the cap adaptive per question type; grading the new run (my own
step, as in T-032); T-033.

**Depends on:** T-028 (the number being replaced), T-038 (packing measurement), T-032 (the
run being repeated).
**Notes:** Probe: 4 truncated arms × 5 samples + 4 non-truncated controls × 3 samples.
Reasoning tokens per sample — F06-A 1795-2685, F07-A 1773-2864, F11-B 1632-2177, F14-A
1054-1640, controls 1076-1841. Truncation is not explained by prompt size or chunk count
(F14-A/F11-B have the largest prompts and the lowest reasoning); open-ended
synthesis questions reason longer than yes/no ones. Raw samples committed under
`docs/eval-results/`. Budget cost of the raise: 1458 tokens fewer for retrieved chunks.

---

### T-038 — Fix the packing-budget undercount T-031 found: measure the real formatted source string, not bare chunk text

**Status:** done
**Size:** M  ·  **Branch:** `t/T-038-fix-packing-budget-undercount`  ·  **Phase:** 3

**Goal:** `pack_to_budget()` measures the *real* token cost of what actually gets sent to
the model for each chunk — including the `"[N] Title (url, feed date)\n"` wrapper
`vg09.answer._format_source()` adds — so the packed prompt can never silently exceed the
budget the way it did for T-031's real F07 run.

**Why:** T-031's real run found `pack_to_budget()` measures only `count_qwen_tokens(c.text)`
— the chunk's bare document text — while `vg09.answer._format_source()` wraps every packed
chunk in real title/url/feed-date text before it's actually sent to the model, uncounted.
For F07 (44 packed chunks), real `prompt_eval_count` was 15349 — 1891 tokens over the
~13458 the budget math assumes — which ate directly into the 2542-token reasoning+answer
reservation and left F07's real answer completely empty (`done_reason=="length"`). This is
a structural gap present since T-008/T-022's original design, not unique to F07 — five
other questions in the same run logged a real "close to num_ctx" warning (95-97%),
consistent with the same undercount. Must land before **T-032** (date-aware vs plain
retrieval comparison), which would otherwise compare two arms against a broken shared
budget and produce untrustworthy results either way.

**Acceptance criteria**
- [x] The exact formatting logic that turns a packed chunk into its real prompt text
  (`"[N] Title (url, feed date)\n{text}"`) lives in one place, reused by both the real
  token-counting during packing and the real prompt construction at generation time — not
  two copies that can drift apart → `vg09.answer._format_source()` moved to
  `vg09.retrieval.format_source()` (public); `vg09.answer.build_user_message()` imports and
  reuses it
- [x] `pack_to_budget()` measures `count_qwen_tokens()` against that real formatted string
  for each candidate, not `c.text` alone → `PACKING_PLACEHOLDER_SOURCE_NUMBER = 99`
  (2-digit, matching the real range seen in production — up to 45 packed chunks — so the
  placeholder's own token cost is a close, very slightly conservative stand-in for whatever
  the real final number turns out to be)
- [x] `docs/DESIGN.md`'s § Context budget is corrected → stated plainly:
  `CHUNK_BUDGET_TOKENS`'s top-level arithmetic (`16000-173-40-2542=13245`) did **not** need
  to change — the reservation formula was always correct, only the per-chunk measurement
  was wrong. What needed re-deriving: the "max top-k" ceiling, corrected from
  `13245 // 400 = 33` to **`13245 // 488 = 27`**, where 488 is a real measured worst-case
  chunk (`scripts/t038_measure_wrapper_overhead.py` against the production store: 405 bare
  tokens + 83 real wrapper tokens, the longest real title in the store)
- [x] A new KB entry records the finding → **KB-018**: the packing budget has under-counted
  the real prompt sent to the model since T-008 (real overhead measured at 41-83
  tokens/chunk), and F07 (T-031) was the first real question to actually tip over it
- [x] Existing unit tests updated (`make_candidate()`/`make_doc_candidate()` fixtures and
  inline integration-test metadata gained real `title`/`url`/`feed_date`) and a new test
  (`test_measures_the_real_formatted_source_not_bare_text`) directly asserts
  `pack_to_budget()` measures the formatted string, not bare `c.text` — plus a direct
  `FormatSourceTests` class for the moved function. 113/113 tests pass
- [x] Real re-verification: all 15 real questions re-run through T-031's harness after the
  fix (`docs/eval-results/2026-09-20-2043-t031-harness.md`) → **15/15 `done_reason==
  "stop"`, zero empty answers, zero `length` truncations.** Max real `prompt_eval_count`:
  13005 (F03, **81%** of 16000) — comfortably under the 90% (14400) threshold. Full
  per-question numbers in Notes
- [x] The real 300-second `ReadTimeout` checked against real elapsed call times from the
  re-verification run → real elapsed `generate_answer()` times ranged **7.7s-18.4s** across
  all 15 questions, ~16x margin under 300s even at the slowest. **Recommendation: leave it
  at 300s** — the one real `ReadTimeout` seen (T-031's first attempt, F03) does not look
  like an undersized timeout given this run's real numbers; far more consistent with a
  transient hiccup (GPU/network) than genuine near-300s generation time. Not changed

**Out of scope:** re-deriving `NUM_PREDICT`/the reasoning+answer reservation itself (T-028's
own settled measurement, unaffected by this bug); the two comparison tickets (T-032/T-033)
— they resume now that this has landed.

**Depends on:** T-022 (owns `pack_to_budget()`), T-023 (owns `_format_source()`), T-031
(found this for real).
**Notes:** Real per-question `prompt_eval_count` / elapsed time from the post-fix
re-verification run, `today=2026-09-17` (D-012):

| Fråga | prompt_eval_count | % of num_ctx | elapsed | done_reason |
|---|---|---|---|---|
| F01 | 12826 | 80% | 16.4s | stop |
| F02 | 12870 | 80% | 13.5s | stop |
| F03 | 13005 | 81% | 17.4s | stop |
| F04 | 7936 | 50% | 10.6s | stop |
| F05 | 9634 | 60% | 10.4s | stop |
| F06 | 12701 | 79% | 15.5s | stop |
| F07 | 12748 | 80% | 18.4s | stop |
| F08 | 12794 | 80% | 8.4s | stop |
| F09 | 12824 | 80% | 7.7s | stop |
| F10 | 7455 | 47% | 9.8s | stop |
| F11 | 11216 | 70% | 15.6s | stop |
| F12 | 12860 | 80% | 12.0s | stop |
| F13 | 9699 | 61% | 11.2s | stop |
| F14 | 12906 | 81% | 13.6s | stop |
| F15 | 7782 | 49% | 10.1s | stop |

F07 specifically (the question that came back completely empty before this fix): real
answer is now a full, well-formed 3-paragraph response citing 5 real sources, chunks
packed dropped from 44 (buggy, over-budget) to 37 (correct, within the real 13245 budget).

---

### T-037 — Open Phase 3: PLAN updates and the Phase 3 ticket set

**Status:** done
**Size:** S  ·  **Branch:** — (docs-only, see note)

**Goal:** Phase 3 is formally open and its work exists as checkable tickets instead of only
`docs/PLAN.md`'s umbrella checkboxes — same pattern T-016/T-026 established for opening
Phase 1 and Phase 2.

**Why:** `docs/PLAN.md`'s own rule: "when a phase starts, turn its checkboxes into tickets
in `docs/TICKETS.md` using the `ticket-write` skill." My explicit go-ahead to start
Phase 3, with the exact scope for this round named: an evaluation harness plus its two
named comparisons, README/LICENSE/fresh-clone, the project rename, and the two deferred
risk-register test-coverage items — explicitly **not** including Phase 3's third checklist
item (report/presentation), and explicitly **no execution** of any ticket this round.

**Acceptance criteria**
- [x] `docs/PLAN.md`'s "Current phase" is set to Phase 3
- [x] `docs/PLAN.md`'s Phase 3 checklist references the tickets that now back each item,
  and explicitly notes the one checklist item (report/presentation) with no ticket yet
- [x] Tickets T-031 through T-036 written, each with observable acceptance criteria and
  correct `Depends on` chains
- [x] Two out-of-scope items surfaced while writing the tickets, not silently folded in:
  T-035 (rename) explicitly excludes the `vg09` package/import path and the Chroma
  `COLLECTION_NAME` stored-data identifier, flagging both as separate decisions per
  `CLAUDE.md`'s stop-and-ask rule for stored data formats and blast-radius-large changes
- [x] None of T-031–T-036 executed — this ticket covers only the planning artifacts

**Out of scope:** doing any of T-031 through T-036's actual work; writing a ticket for
Phase 3's report/presentation checklist item (not part of this round's instruction).

**Depends on:** T-029, T-030 (Phase 2's own close-out, completed the same session).
**Notes:** Docs-only, same shape as T-016/T-026. The risk-register rows for `store.py`/
`youtube_backfill.py` (Phase 1's `grill-me` findings) are updated to point at T-036 instead
of the old "Deferred to Phase 3, T-020's triage" placeholder text.

---

### T-036 — Test coverage for the two deferred risk-register items: `store.py` and `youtube_backfill.py`

**Status:** done
**Size:** M  ·  **Branch:** `t/T-036-store-and-backfill-tests`  ·  **Phase:** 3

**Goal:** the two test-coverage gaps Phase 1's `grill-me` review found and deferred to
Phase 3 (`docs/PLAN.md`'s risk register) are closed: `vg09/store.py`'s compliance with
`CLAUDE.md`'s hard rules, and `vg09/youtube_backfill.py`'s orchestration logic, are both
under real test for the first time.

**Why:** both were flagged by name in the risk register with "Deferred to Phase 3" as the
plan, not "won't fix" — `store.py` implements two of `CLAUDE.md`'s three hard rules
(explicit `bge-m3`, explicit `num_ctx`) with nothing to catch a future refactor that
silently drops either; `youtube_backfill.py` is "the riskiest orchestration code in the
ingest pipeline, verified only by real production runs" (T-019's own self-flagged note).
Phase 3 is the last chance to close this before the project is published.

**Acceptance criteria**
- [x] A test asserts `vg09.store.embed_batch()`'s real request body always includes
  `model="bge-m3"` and an explicit `num_ctx` — mocked at the `requests.post` boundary,
  matching this project's existing test pattern → `EmbedBatchTests`
  (`tests/test_store.py`); also covers the return value passing embeddings through
  unmodified, and (beyond this criterion's literal ask, matching T-029's already-
  established pattern for the project's other two Ollama call sites) that a non-2xx
  response raises via `raise_for_status()` before `.json()` is ever read
- [x] A mocked test covers `youtube_backfill.py`'s resumability: a video already present in
  `data/raw/` (via `document.exists()`) is skipped, not re-fetched, on a second run →
  `ResumabilityTests` (`tests/test_youtube_backfill.py`), including a two-run test
  (fetched on run 1, confirmed skipped — `normalize` not called — on run 2)
- [x] A mocked test covers its pacing: the pause-between-videos call happens between
  consecutive video attempts, asserted against a mocked sleep/pause function — no real
  wall-clock wait in the automated suite → `PacingTests`; asserts the actual interleaved
  call order (`process:vidA, pause, process:vidB, pause`), that the duration is drawn from
  the module's own `random.uniform(*SHORT_PAUSE_SECONDS)` call (not a guessed literal),
  and that an already-done video costs no pause at all (never reaches `_process_video()`)
- [x] A mocked test covers watermark-write-on-completion: the watermark is written only
  after the full backfill window completes successfully, and stays unwritten if the run is
  interrupted partway → `WatermarkWriteTests`; also covers the real distinction this
  module's own code draws between a handled per-channel listing failure (watermark still
  advances - a real, caught case) and an uncaught exception from `normalize()` genuinely
  interrupting the run (watermark stays unwritten)
- [x] `.venv/Scripts/python.exe -m unittest discover -s tests` passes with the new tests
  included, no live network or GPU calls added to the automated suite → **144/144 pass**
  (13 new: 4 in `EmbedBatchTests`, 9 in `test_youtube_backfill.py`)

**No real defect found** — both modules already behaved exactly as their own code comments
and this ticket's risk-register origin described; every new test passed against the
existing, unmodified implementation. Neither `vg09/store.py` nor `vg09/youtube_backfill.py`
was changed.

**Out of scope:** fixing any real defect these tests might surface — if one turns up, it
gets its own ticket, not a silent fix bundled into this one (unless genuinely trivial and
directly caused by writing the test itself, noted if so). **N/A — none found.**

**Depends on:** —
**Notes:** Both risk-register rows cite the Phase 1 `grill-me` review (2026-09-19) as their
origin; both rows in `docs/PLAN.md`'s risk register marked resolved by this ticket
(2026-09-22), original wording kept struck through rather than deleted.

---

### T-035 — Rename the project from "VG-09" to "research-feed-assistant" (user-facing naming only)

**Status:** done
**Size:** S  ·  **Branch:** `t/T-035-project-rename`  ·  **Phase:** 3

**Goal:** the project's real, current name — "research-feed-assistant" — replaces the
placeholder codename "VG-09" everywhere a human reading the published repo would see it,
without touching anything that would require a data migration or a mechanical rewrite of
every import in the codebase.

**Why:** (2026-09-20) "VG-09" is still the name in `CLAUDE.md`
and elsewhere, but the project is about to be published as OSS under its real name.

**Acceptance criteria**
- [x] Every occurrence of "VG-09" in `CLAUDE.md` (the "What this is" section, examples,
  branch/PR naming illustrations, etc.) is replaced with "research-feed-assistant" or the
  appropriate grammatical form → only one real occurrence existed: the title line
  (`# CLAUDE.md — VG-09`); the "What this is"/stack sections never named the project by
  this codename in the first place
- [x] `app.py`'s UI-facing strings (`st.set_page_config(page_title=...)`,
  `st.title(...)`) say "research-feed-assistant", not "VG-09" → both updated
- [x] A repo-wide search for "VG-09" is run (`grep -rn "VG-09"`, excluding `.venv`/
  `__pycache__`) and every *currently-live, forward-looking* occurrence is updated;
  historical records are deliberately left unchanged — full accounting:
  - **Changed:** `CLAUDE.md:1` (title), `app.py:23-24` (page title/heading)
  - **Left alone, real external path (matches this ticket's own out-of-scope list):**
    `docs/eval-questions.md:26` and `docs/sessions/2026-09-19-...md:20`, both referencing
    the real frozen-archive directory `C:\AIProjects\VG-09-frozen\`; `scripts/
    t020_freeze_dataset.py`'s `ARCHIVE_DIR` (already named out of scope below)
  - **Left alone, historical/planning text describing the rename itself, not live
    branding:** `docs/PLAN.md:129`, and every "VG-09" inside `docs/TICKETS.md` (this
    ticket's own body text, T-025's completed acceptance-criterion quoting a past
    placeholder string, T-013's note referencing the same frozen-archive path) —
    rewriting these would misrepresent what was actually true when they were written
- [x] Existing tests pass unchanged — a pure display-string rename shouldn't touch any
  test assertion that isn't itself asserting the old name → 131/131 pass, unchanged

**Out of scope, flagged explicitly rather than silently decided:**
- The Python package itself, `vg09/` (all 41 files that `import vg09`/`from vg09...`) —
  renaming the actual package/import path is a mechanical but blast-radius-large change
  touching every module in the codebase, not a "few files" S-sized rename. A real decision
  for me: is `vg09` (the import path) worth renaming too, given nobody outside this
  repo depends on it yet, or does it stay as an internal implementation detail separate
  from the project's public-facing name?
- `vg09.store.COLLECTION_NAME = "vg09_chunks"` — this is a **stored data identifier** in
  the real, existing production Chroma store (`data/chroma_store/`, gitignored). Renaming
  it without a migration step would orphan the existing local collection (a fresh
  `get_or_create_collection()` call under a new name starts empty) — a real, if
  self-inflicted, data-loss risk for whoever already has a populated local store. Per
  `CLAUDE.md`'s stop-and-ask rule for stored data formats, this needs an explicit decision
  (rename + migration script, or leave it), not a silent rewrite bundled into a "S-sized"
  cosmetic rename
- `scripts/t020_freeze_dataset.py`'s `ARCHIVE_DIR = Path(r"C:\AIProjects\VG-09-frozen")` —
  this is a reference to a real external directory that exists on disk under that literal
  name (the T-020 frozen-dataset archive). Changing the string without also renaming the
  real directory would break the script; left alone here as out of scope, not silently
  "fixed" into a path that doesn't exist

**Depends on:** —
**Notes:** Scoped deliberately narrow (display strings and current-facing docs only) after
finding, while writing this ticket, that a full rename touches a real stored-data
identifier and 41 importing files — exactly the kind of thing `CLAUDE.md` says to flag and
stop on rather than fold into a routine rename. Executed 2026-09-22, ahead of T-034 (which
depends on it) per my explicit instruction. `vg09` (the import path) and
`COLLECTION_NAME`/`t020_freeze_dataset.py`'s `ARCHIVE_DIR` remain exactly as flagged above
— still open, unresolved decisions, not silently revisited here.

---

### T-034 — README, Apache-2 LICENSE, and a real fresh-clone test

**Status:** done
**Size:** M  ·  **Branch:** `t/T-035-project-rename` (T-034 built on T-035's branch since it
depends on the rename landing first — see T-035's own Notes)  ·  **Phase:** 3

**Goal:** anyone can clone the public repo, follow only the README, and reach a first real
answer from the chat UI — proven by actually doing it, not assumed because the code exists.

**Why:** `docs/GOAL.md`'s Definition of done requires "a public GitHub repo with Apache-2
`LICENSE` and a README covering install, ingest and asking," and `docs/PLAN.md`'s Phase 3
exit criteria requires "a fresh-clone test following the README only." Neither exists yet.

**Acceptance criteria**
- [x] `README.md` covers: what the project does (one paragraph, from `docs/GOAL.md`),
  prerequisites (Ollama, the specific models pulled, Python version), install steps, how to
  run ingest (backfill + catch-up), how to run the chat UI (`streamlit run app.py`), and
  where the evaluation results live → written for someone who finds the repo on GitHub with
  no prior context, per my explicit instruction; also covers GPU/VRAM (RTX 4090 tested),
  the Swedish-UI/English-answer nuance (D-013), and known limitations (below)
- [x] `LICENSE` at the repo root is the real, unmodified Apache-2.0 license text → fetched
  from `https://www.apache.org/licenses/LICENSE-2.0.txt`, byte-identical (11358 bytes),
  including the Appendix's bracketed placeholder boilerplate, unmodified
- [x] A real fresh clone (a separate directory, not the existing working copy) is tested
  end to end: clone → follow only what the README says, nothing outside it → reach a first
  real answer in the chat UI. Run for real, not assumed → **done in full, for real, real
  numbers below**
- [x] Any step the fresh-clone test finds missing, wrong, or assumed is fixed in the README
  itself before this ticket closes → **nothing needed fixing** — every documented command
  ran exactly as written, no undocumented step, no silent workaround
- [x] `docs/GOAL.md`'s Definition of done README/LICENSE criterion can be pointed to
  directly as met → it is, by this ticket

**Real fresh-clone run (2026-09-22), against `t/T-035-project-rename`'s tip
(includes T-035's rename), in an isolated scratch directory — never the real working
copy or its `data/`:**
1. `git clone --branch t/T-035-project-rename <repo> <scratch>/fresh-clone-test`
2. `python -m venv .venv` → Python 3.12.10, matching the README's stated requirement
3. `pip install -r requirements.txt` → clean install, no errors, no version conflicts
4. `python scripts/t015_hf_backfill.py` → real HF Daily Papers API, **1208 papers, 56
   days fetched, 0 skipped** (correct for a first run), new watermark `2026-09-20`
5. `python scripts/t017_youtube_backfill.py` → real yt-dlp/YouTube/local Whisper, all 4
   channels reached, **37 attempts: 5 real captions, 30 Whisper fallback (captions
   blocked, D-009), 2 title+description fallback, 6 already-done**, watermark
   `2026-09-22` — the real caption-block-then-Whisper-then-fallback chain this project
   has documented since D-009/D-010 exercised itself for real, unprompted, exactly as
   designed
6. `python scripts/t012_build_store.py` → real `bge-m3` embedding calls,
   **1251 documents, 2039 chunks, `collection.count()==2039`**, 253.4s
7. `streamlit run app.py` → real browser (Playwright), page title renders
   "research-feed-assistant" (confirming T-035's rename end to end, not just in source)
8. Asked the real question "Vad har hänt med AI-agenter den senaste veckan?" → **a real,
   complete English answer** (D-013 - Swedish question, English answer, confirmed) citing
   6 real sources (4 HF papers with feed date + arXiv date, 2 YouTube videos with
   timestamped links), no empty/incomplete/error state. Screenshot evidence kept outside
   the repo (scratchpad, not committed - it's a one-off manual verification artifact, not
   project data)

Confirms `docs/GOAL.md`'s success criterion ("A fresh clone reaches a first answer by
following the README only") and Definition of done #1 for real, not by inspection.

**Out of scope:** CI/CD (no pipeline decided yet, per `CLAUDE.md`'s "still undecided"
stack notes); packaging/publishing to PyPI or similar; the evaluation results themselves
(T-031/T-032/T-033) — the README references where they'll live, doesn't require them
finished first.

**Depends on:** T-035 (so the README is written under the project's real name from the
start, not written against "VG-09" and then edited).
**Notes:** `docs/GOAL.md`'s known limitations list was adapted, not copied verbatim, for
one item: D-005 already ties `bge-m3`'s multilingual embedding to GOAL's own Swedish-
retrieval caveat ("relevant to docs/GOAL.md's known limitation that Swedish questions may
retrieve worse than English ones") — the README states the limitation accurately given
that decision (multilingual embedding, verified for real, T-006) rather than repeating
GOAL.md's pre-D-005 phrasing unchanged. `docs/GOAL.md` itself was not edited - flagging
this discrepancy for whoever next revisits that doc, per `CLAUDE.md`'s rule to flag rather
than silently adapt when reality has moved past a reference document.

---

### T-033 — Comparison 2: `qwen3:30b-a3b` vs `qwen3:8b` on the same 15 real questions

**Status:** done — real run complete, graded by me 2026-09-23: A better 4, B
better 0, equivalent 9, both wrong 2 (`docs/eval-results/2026-09-23-1516-t033-model-
size-comparison.md`)
**Size:** M  ·  **Branch:** `t/T-033-model-size-comparison`  ·  **Phase:** 3

**Goal:** the same 15 real questions, same retrieved context, run through both models in
D-005's VRAM-differentiated pair — so I can judge for themselves whether the
larger-VRAM model earns its cost over the smaller one.

**Why:** `docs/PLAN.md`'s Phase 3 exit criteria names this comparison explicitly
("large vs small model"); D-005 is the decision that chose this specific pair
(VRAM-differentiated, not "small vs large" model size) and named this as the eventual test.

**Acceptance criteria**
- [x] `vg09.answer.generate_answer()` accepts an explicit model name as a parameter rather
  than always using the hardcoded `CHAT_MODEL` constant — a minimal, backward-compatible
  signature change (default value stays `qwen3:30b-a3b`, so `app.py` and every existing
  test/caller is unaffected) → `generate_answer(question, chunks, model=CHAT_MODEL)`,
  threaded through `_chat_once()`; all 24 pre-existing `test_answer.py` tests pass
  unchanged (none pass `model=`), plus 2 new (`test_model_defaults_to_the_chat_model_
  constant`, `test_explicit_model_overrides_the_default`)
- [x] Reuses T-031's harness and output format: each of the 15 questions is run through
  **both** models with the **same retrieved chunks held identical** between the two runs,
  so only the model varies, not the retrieved context → `scripts/t033_model_size_
  comparison.py`; retrieval runs exactly once per question, both `generate_answer()` calls
  share the same `retrieval.chunks` object. Confirmed for real, not just by code
  inspection: every one of the 15 real questions shows the identical `prompt_eval_count`
  for Modell A and Modell B (e.g. F01: 11389 both)
- [x] Output shows both models' answers and citations per question, clearly labeled by
  model name, in the same human-gradable format T-031 established → "Modell A"/"Modell B"
  sections per question, facit shown once beneath both, same `☐ A bättre ☐ B bättre
  ☐ Likvärdiga ☐ Båda fel` line T-032 uses
- [x] Both models are called with the same explicit `num_ctx=16000` and the same
  `prompt_eval_count`-vs-`num_ctx` truncation-risk check (`CLAUDE.md`'s hard rule) — `qwen3:
  8b` doesn't get a silently different/default context window just because it's the
  smaller model → same `_chat_once()` for both, `num_ctx` never varies by `model`; asserted
  directly in `test_explicit_model_overrides_the_default`
- [x] Real run against the production store/Ollama completes all 15 questions × 2 models
  with no unhandled exception; if switching between the two loaded models mid-run costs
  real reload time (KB-003's original finding about this model pair), that cost is measured
  and reported, not assumed away → **30/30 real calls completed, `stop`, 0 retries.**
  Every question alternates model, so every call is a real switch - real elapsed times
  (reload-inclusive) reported per model: `qwen3:30b-a3b` min 8.2s/max 18.5s/avg 12.4s;
  `qwen3:8b` min 9.5s/max 33.0s/avg 16.8s. The smaller-VRAM model was slower on average,
  not faster - consistent with D-005's own point that `qwen3:30b-a3b` is MoE (~3B active
  params/token) while `qwen3:8b` is dense (all 8B active every token), so "smaller VRAM"
  does not mean "less compute per token." **Real, unplanned bug found and fixed same
  session:** the script's console `print()` of the reload-time summary crashed
  (`UnicodeEncodeError`) on a `→` character the Windows console's cp1252 encoding can't
  represent - happened *after* the real output file was already written (confirmed intact,
  all 15 questions, correct real data), so no data was lost; fixed by using `->` instead

**Out of scope:** the retrieval-mode comparison (T-032, already done); changing which model
production (`app.py`) actually uses — it stays on `qwen3:30b-a3b`, D-005's chosen default.

**Depends on:** T-031 (the harness), D-005 (the model pair).
**Notes:** Output:
`docs/eval-results/2026-09-23-1516-t033-model-size-comparison.md`, real run, committed,
then graded by me 2026-09-23 (A better 4, B better 0, equivalent 9, both wrong 2).
Notable from the grading itself: `qwen3:8b` was equivalent in 9/15 but slower on average
(16.8s vs 12.4s) despite fewer active parameters (dense vs `qwen3:30b-a3b`'s MoE, D-005);
where it lost (F03/F04/F06) the pattern repeats - it enumerates everything topically
similar rather than ranking or narrowing to what the question asked; F13 saw it drift
into Chinese mid-answer despite D-013's explicit English-answer instruction; F12 and F14
were missed by both models, matching both arms of T-032 - a retrieval gap, not a
model-size effect.

---

### T-032 — Comparison 1: date-aware retrieval vs plain similarity search on the same 15 real questions

**Status:** done
**Size:** M  ·  **Branch:** `t/T-032-date-aware-vs-plain-comparison`  ·  **Phase:** 3

**Goal:** for each of the 15 real questions, both the real date-aware retrieval result and
a plain (unfiltered, similarity-only) retrieval result are produced side by side — the
comparison the whole project's central claim (`docs/GOAL.md`) rests on.

**Why:** `docs/GOAL.md`'s core claim is that date-aware retrieval answers these three
question types better than plain similarity search; `docs/PLAN.md`'s Phase 3 exit criteria
names this comparison explicitly. Nothing in the codebase has run this comparison for real
yet — T-021/T-022/T-027's own real testing exercised date-aware retrieval alone, never
compared side by side against the plain-search alternative on the same questions.

**Acceptance criteria**
- [x] Reuses T-031's harness: each question is run twice — once with the real resolved
  `date_range`/`ranking` (date-aware, exactly as `app.py` behaves), once with
  `date_range=None` and `ranking=False` forced (plain similarity search only) →
  `scripts/t032_date_aware_vs_plain_comparison.py`, imports `load_questions_with_facit()`/
  `describe_mode()` directly from `scripts/t031_evaluation_harness.py` so the two harnesses
  can't drift on what "the 15 real questions" means
- [x] Output shows both arms' answers and citations per question, clearly labeled, so a
  human can compare without cross-referencing two separate files → "Läge A"/"Läge B"
  sections per question, facit shown once beneath both, real run:
  `docs/eval-results/2026-09-20-2136-t032-date-aware-vs-plain.md`
- [x] For the questions where date-awareness plausibly matters most, both arms' retrieved
  sources' real feed dates are visible in the output, not just the final answer prose →
  every citation line leads with its real feed date in bold
- [x] Real run against the production store/Ollama completes all 15 questions × 2 arms
  with no unhandled exception → 30/30 real calls completed. **Real finding, not a new
  bug:** 4/30 hit `done_reason=="length"` (F06-A, F07-A, F11-B, F14-A) despite T-038's
  packing-budget fix — same `prompt_eval_count` as T-031's clean re-verification run for
  the identical arm/question in at least one case (F06-A, F07-A: byte-for-byte same
  packed context both times), so this is sampling variance in how much the model reasons
  before answering, exactly the residual risk T-028 already documented (reasoning ranged
  61.5-92.1% of the cap across identical real re-runs) — not a packing regression. Each
  instance is visibly marked "⚠ OFULLSTÄNDIGT" in the output for manual grading
- [x] `docs/PLAN.md`'s Phase 3 "results table committed" exit criterion — the real,
  ungraded output is committed (moved from the gitignored `data/eval_results/` to tracked
  `docs/eval-results/`, per my explicit instruction) so it's part of the repo and the
  report. **Grading itself (the `☐ A bättre ☐ B bättre ☐ Likvärdiga ☐ Båda fel` lines) is
  still my own manual step, not done as part of this** — committed-but-ungraded,
  not committed-because-graded

**Out of scope:** the model-size comparison (T-033); any change to `vg09.retrieval` itself
— the plain-search arm is an existing call shape, not new code.

**Depends on:** T-031 (the harness), T-038 (the packing-budget fix — this comparison would
have been untrustworthy without it, per T-038's own Why section).
**Notes:** Marked `done` for the harness/real-run work itself; the "results table
committed" criterion is explicitly left unchecked above since grading is my own
step, still pending as of this ticket closing.

---

### T-031 — Evaluation harness: run the 15 real questions, D-012's anchor explicit, human-gradable output

**Status:** done
**Size:** M  ·  **Branch:** `t/T-031-evaluation-harness`  ·  **Phase:** 3

**Goal:** a script that runs all 15 of T-014's real questions through the real pipeline and
produces each answer plus its resolved citations in a format a human can read straight
through — no automated pass/fail verdict, no model-based grading. This is the shared
foundation T-032 and T-033's comparisons both build on.

**Why:** `docs/PLAN.md`'s Phase 3 exit criteria requires an evaluation script; my explicit
instruction that grading is manual, against `docs/eval-questions.md`'s facit, never
delegated to a model. D-012 requires the anchor be set explicitly wherever T-014's
questions are re-run against the pipeline — this is exactly such a re-run.

**Acceptance criteria**
- [x] Questions are loaded live from `docs/eval-questions.md` (not retyped), matching
  T-021's established pattern (`re.finditer(r"^Fr[aå]ga (\d+): (.+)$", ...)`) →
  `scripts/t031_evaluation_harness.py::load_questions_with_facit()`, also parses each
  question's full facit block (everything under its own `### Fråga NN` heading) live from
  the same file, per my explicit format instruction (see Notes)
- [x] `today` is set explicitly via `vg09.store.latest_feed_date()` (D-012) once, at the
  top of the run — not hardcoded to a specific date, not re-derived per question → real
  run anchored at **2026-09-17**
- [x] For each question: `vg09.date_range.resolve_date_range()`/`detect_recency_ranking()`
  resolve the real date range/ranking mode, `vg09.retrieval.retrieve()` returns the real
  packed chunks, `vg09.answer.generate_answer()` produces the real answer, and
  `vg09.citations.build_citations()` resolves its real citations — the exact same call
  sequence `app.py` uses, against the real store/Ollama, not a synthetic fixture → done,
  identical call sequence
- [x] Output is one human-readable file (Markdown) with one section per question, showing:
  the question's F-number and text, the resolved date range/ranking mode, the full answer
  text, and its resolved citations (title, feed date, url) — laid out so it can be read
  straight through against `docs/eval-questions.md`'s facit without cross-referencing code
  → extended per my explicit instruction mid-ticket: each section also reproduces the
  facit's own "Bedömningskriterier"/"Förväntade källor" text verbatim immediately below the
  real answer, plus a `☐ Godkänt ☐ Fel` line, so grading needs zero cross-referencing
- [x] A real run against the production store/Ollama produces output for all 15 questions
  with no unhandled exception → **15/15**, written to
  `data/eval_results/2026-09-20-2004-t031-harness.md` (gitignored, `data/`) — first attempt
  hit a real `ReadTimeout` on F03's `/api/chat` call after 300s (transient — a clean retry
  completed all 15 with no error)

**Real, significant finding from this run, not fixed here (out of scope for the harness
ticket itself):** **F07's real answer came back completely empty**, `done_reason=="length"`
— worse than T-028's original truncation (which at least produced partial text). Root
cause investigated, not just observed: `vg09.retrieval.pack_to_budget()` measures each
candidate's token cost via `count_qwen_tokens(c.text)` — the chunk's *bare* text only.
`vg09.answer._format_source()` then wraps every packed chunk in `"[N] {title} ({url}, feed
date {date})\n{text}"` before it's actually sent to the model — real title/url/date text
that was never counted during packing. For F07 (44 packed chunks), real
`prompt_eval_count` was **15349** — 1891 tokens over the ~13458 the budget math
(`173+40+13245`) assumes as an upper bound, roughly 43 tokens/chunk of uncounted citation-
wrapper overhead. That 1891-token overrun ate directly into the 2542-token
reasoning+answer reservation (16000-15349=651 tokens of real headroom left, not 2542),
leaving nothing for the answer once reasoning alone consumed what was left. This is a
**structural undercount in the packing budget, present since T-008/T-022's original
design** — not unique to F07, just usually not severe enough to visibly fail. Five
other questions in this same run (F01, F03, F06, F07, F08) logged a real `close to
num_ctx` warning (95-97% of 16000) via the existing hard-rule check, consistent with this
same undercount. **Not fixed as part of T-031** — flagged for me to decide how to
address (e.g. `count_qwen_tokens()` measuring the formatted source string instead of bare
`c.text`, which would require re-deriving `CHUNK_BUDGET_TOKENS` again, T-008/T-028-style).
**Fixed in T-038**, same session — see that ticket's own entry (KB-018) for the real root
cause and the re-verification evidence.

**Out of scope:** grading/scoring logic — I do this manually, by reading the
output against the facit; the two comparison arms (T-032/T-033) — this ticket is the
shared harness they both extend; committing any one specific run's output as "the" result
— that's each comparison ticket's own concern once I have reviewed it; fixing the
packing-budget undercount finding above.

**Depends on:** T-014 (the real questions), T-021/T-022/T-023/T-024 (the pipeline this
calls), D-012 (the anchor), T-029 (the error handling this harness will exercise for real).
**Notes:** The output format was extended beyond this ticket's original acceptance
criteria (facit block reproduced verbatim per question, plus a grading checkbox line) by
my explicit instruction given right before execution — the criteria above already
reflect the extended, actually-built format, not the original narrower one, per this
project's rule that an in-progress ticket's drift gets a Notes line rather than silent
acceptance-criteria rewriting.

---

### T-030 — Answers are always in English, regardless of the question's language

**Status:** done
**Size:** S  ·  **Branch:** `t/T-030-english-answers`  ·  **Phase:** 2

**Goal:** the model always answers in English, whatever language the question was asked
in - a deliberate, explicit language policy recorded as a decision and enforced in the
system prompt, not left to whatever the model happens to do by default.

**Why:** my explicit instruction, 2026-09-20. The project ships as OSS (Apache-2,
`docs/GOAL.md`) and is meant to be usable internationally; its sources (HF Daily Papers
abstracts, YouTube transcripts) are English. Questions must keep working in any language -
`bge-m3`'s multilingual embedding already handles that (T-006, D-005) and this ticket
doesn't touch it - only the answer's output language is being pinned down.

**Acceptance criteria**
- [x] A new decision (`D-013`) is recorded in `docs/DECISIONS.md`: answers are always
  English; questions may be asked in any language → D-013, with the rejected alternative
  (mirror the question's language) and cost spelled out
- [x] `vg09.answer.SYSTEM_PROMPT` states the English-answer rule explicitly → new line,
  "Always answer in English, even if the question is asked in a different language."
- [x] The new system prompt's real qwen3 token count is re-measured (same method as
  T-008/T-024 - `POST /api/generate`, `num_predict:1`, real `prompt_eval_count`), and
  `docs/DESIGN.md`'s § Context budget and `vg09.retrieval.CHUNK_BUDGET_TOKENS` are updated
  to match if the count changed → real measurement: **173 qwen3 tokens** (was 157).
  `CHUNK_BUDGET_TOKENS` 13261 → 13245; max top-k unchanged at 33 (same 400-token band);
  `docs/DESIGN.md`'s Context budget section and `vg09/retrieval.py`'s comments updated
- [x] A unit test asserts the English-answer instruction is present in `SYSTEM_PROMPT`, so
  a future prompt rewrite can't silently drop it →
  `tests/test_answer.py::SystemPromptTests::test_english_answer_instruction_is_present`,
  111/111 tests pass
- [x] A real end-to-end call (not just the static prompt text) confirms a Swedish question
  produces an English answer, against the real store/Ollama →
  `scripts/t030_verify_english_answer.py`, real run against the production store/Ollama:
  two real Swedish questions ("Vad har hänt med AI-agenter den senaste veckan?", "Har
  Palantir nämnts i någon video?") both produced fluent English answers, citing real
  sources by number as usual - questions still work in Swedish (T-006/D-005's multilingual
  embedding, untouched), only the answer's language changed

**Out of scope:** changing how questions are parsed/embedded (already language-agnostic,
T-006/D-005); translating citation titles or source excerpts (they stay as the source
wrote them).

**Depends on:** T-023 (owns `SYSTEM_PROMPT`), T-006/D-005 (`bge-m3`'s multilingual
embedding, unaffected by this ticket).
**Notes:** D-013 flags one residual, unresolved-here consequence: `docs/eval-questions.md`'s
facit is written and graded in Swedish - a strict Phase 3 re-grading against this decision
would need to expect an English answer even though the facit's own descriptive text stays
Swedish. Not rewritten as part of this ticket; left for whoever next re-runs that eval set.

---

### T-029 — Fix the four grill-me findings from the Phase 2 review

**Status:** done
**Size:** M (four independent fixes from one review pass, bundled as one ticket per
my explicit instruction - see Notes)  ·  **Branch:** `t/T-029-phase-2-grill-me-fixes`  ·
**Phase:** 2

**Goal:** the four real defects the Phase 2 `grill-me` review found (2026-09-20) are fixed:
D-011's written text matches what production and every real evaluation re-run actually do;
a real Ollama failure surfaces as a clear message instead of a raw traceback; `app.py` uses
T-021's own override contract instead of a hand-rolled copy of it; and real titles can't
break a rendered citation link.

**Why:** `grill-me`'s own findings, triaged by me 2026-09-20. (1) is a real
reality-contradicts-documentation case per `CLAUDE.md`'s own rule - D-011 as written
prescribes an eval anchor (2026-09-16) that every real re-run of T-014's questions
(T-027, T-028) has actually contradicted, and would - if ever followed literally - exclude
`YTG0rdHPTDE` again, the exact case D-011 exists to stop excluding. (2) is a real gap in
the single most user-facing code path (`vg09/store.py::embed_batch()` already does this
correctly; the two other real Ollama call sites don't). (3)/(4) are real, if smaller,
inconsistencies the same review found by reading the shipped code, not hypothesized.

**Acceptance criteria**
- [x] D-011 (`docs/DECISIONS.md`) is rewritten so the anchor is the same in both
  production and evaluation - `vg09.store.latest_feed_date()` (the dataset's real latest
  `feed_date`, 2026-09-17 for the current frozen set) - not two different rules for two
  callers → D-011's `Status` changed to `superseded by D-012`, its original text kept intact
  (nothing deleted); new **D-012** written with the unified rule. D-012 also records an
  honest residual gap found while writing it, not smoothed over: a single anchor can't
  reproduce every individually-written per-question facit window exactly (HF-only window
  questions are one calendar day off from the anchor text, harmless in practice for this
  frozen dataset since HF has no real content on the extra day - see D-012's Cost section)
- [x] `docs/eval-questions.md`'s anchor references are updated to say
  2026-09-17/`latest_feed_date()`/D-012, not 2026-09-16/D-011 - the facit's own written
  windows/content (F01-F15's expected sources, dates, answers) untouched, confirmed by
  `git diff docs/eval-questions.md` touching only the "Time-window conventions" callout box,
  no line under "## Questions"
- [x] `vg09/answer.py::generate_answer()` and `vg09/retrieval.py::count_qwen_tokens()` call
  `resp.raise_for_status()` before reading the response body, matching
  `vg09/store.py::embed_batch()`'s existing pattern → **correction to this ticket's own
  Why section, found while implementing:** `count_qwen_tokens()` already had
  `raise_for_status()` (T-022 shipped it correctly the first time) - the grill-me finding
  that named both functions was wrong about this one; only `generate_answer()` was actually
  missing it. Fixed there; `count_qwen_tokens()`'s call renamed for consistency only, no
  behavior change. Both now have a dedicated unit test for a mocked non-2xx response
  confirming the exception raises before `.json()`/any field is read
  (`test_answer.py::test_non_2xx_response_raises_before_reading_the_body`,
  `test_retrieval.py::CountQwenTokensTests::test_non_2xx_response_raises_before_reading_the_body`) -
  110/110 tests pass
- [x] That exception is caught once, at the UI boundary (`app.py`), and shown as a clear
  Swedish message - "Ollama svarar inte – är den igång och är modellen nedladdad?" - instead
  of an unhandled traceback reaching the Streamlit page → `app.py`'s retrieval/answer/
  citation block wrapped in `try/except requests.exceptions.RequestException` (the common
  base class covering both a non-2xx `raise_for_status()` and Ollama simply not running -
  `ConnectionError` - with one handler)
- [x] `app.py` calls `resolve_date_range(question, today, manual_override=manual_range)`
  directly for the range actually used, instead of computing `interpreted_range` and then
  separately picking between it and `manual_range` by hand - the override precedence lives
  in exactly one place (`vg09.date_range`), not two → done; `interpreted_range` is now only
  computed (with `manual_override=None`) for `describe_retrieval_mode()`'s own display
  purposes, never used to derive the actual `date_range`
- [x] Titles interpolated into `app.py`'s citation markdown links are escaped so a real
  title containing `]`, `)`, or other markdown-significant characters can't break the
  rendered link - tested against at least one real title pulled from `data/raw/` containing
  such a character → `vg09.ui_helpers.escape_markdown_link_text()`; tested against the real
  title "He Built The Ultimate Spy Tool (Free and Open-Source)"
  (`data/raw/youtube/2026-09-16/S2VJU5DQqlU.json`, embedded as a literal since `data/raw/`
  is gitignored, per D-004 - test file says so). That real title's parens turned out not to
  be the dangerous character under CommonMark (parens inside `[text]` don't need escaping;
  only `]`/`[`/backslash do) - the real title confirms escaping doesn't mangle ordinary
  punctuation, and a synthetic `[SOTA]`-shaped title covers the actually-dangerous case

**Out of scope:** `latest_feed_date()` running a full collection scan up to twice per UI
interaction (grill-me's fifth finding) - noted as a `docs/PLAN.md` risk-register row only,
not fixed here, per my explicit instruction. Any other Ollama/network call site not
named above. Rewriting `docs/eval-questions.md`'s facit content itself.

**Depends on:** T-027, T-028 (produced the anchor drift this corrects), D-011 (the decision
being amended).
**Notes:** Bundled as one ticket per my explicit instruction, even though the four
fixes are independent of each other and could ship as separate commits/PRs - all four come
from the same single `grill-me` review pass and none has enough surface area alone to
justify its own ticket. `docs/PLAN.md`'s risk register gets a new row for the deferred
fifth finding as part of this ticket's own doc updates, even though it isn't an acceptance
criterion above.

---

### T-012 — Chunk, embed and store documents with feed date metadata (idempotent)

**Status:** done
**Size:** M  ·  **Branch:** `t/T-012-chunk-embed-store`

**Goal:** normalized documents from `data/raw/` (T-009's collectors, populated by T-015's HF
backfill now and T-017's YouTube backfill once it unblocks) are chunked, embedded with
`bge-m3`, and stored in ChromaDB with feed date as filterable metadata and arXiv
`publishedAt` alongside for citations — and re-running ingest never creates duplicates.
Works against HF-only data now; picks up YouTube documents automatically once T-017 adds
them to `data/raw/`, no code change needed.

**Why:** `docs/PLAN.md` Phase 1's second checklist item. D-004 (ChromaDB), D-005 (`bge-m3`)
and D-002 (feed date semantics) need to land in real storage code, with chunk size and top-k
chosen against T-008's measured budget rather than guessed.

**Acceptance criteria**
- [x] Chunking/embedding reads normalized documents from `data/raw/` rather than calling the
  HF/YouTube collectors directly → `vg09/store.py`'s `load_documents()`, skips
  `*.pending.json` and `_done.json` by filename
- [x] Chunk size is chosen using T-008's documented context budget, with the reasoning cited
  → HF: one chunk/paper (max 363 < 400-token cap); YouTube: character-budget windows
  calibrated to a real qwen3-tokenizer measurement (`scripts/t012_caption_token_calibration.py`)
  targeting 350/400 tokens
- [x] Each chunk is embedded via an explicit `bge-m3` call → `vg09/store.py::embed_batch()`,
  `num_ctx=8192` explicit, batched real calls, never Chroma's default embedder (verified by
  self-review catching and fixing a `query_texts=` slip in a smoke-test script before it
  reached the real store)
- [x] Each chunk is stored with `feed_date` as filterable metadata → `feed_date_ordinal`
  (`date.toordinal()`, int, per KB-004) alongside the human-readable string
- [x] Running ingest twice over the same `data/raw/` contents produces the same
  document/chunk count both times → real run: 1184/1184/1184 (docs/chunks/collection.count())
  both times, `collection.upsert()` with deterministic ids
- [x] A query filtered to a feed-date range returns only chunks inside that range, in the
  real schema → `scripts/t012_verify_date_filter.py` against the real 1184-chunk production
  store: `[2026-09-01, 2026-09-14]` → 306 chunks, all confirmed in range, strict subset of
  unfiltered

**Additional requirements from this ticket's instructions, also done:**
- [x] HF: one chunk per paper (`vg09/chunking.py::chunk_hf_document`)
- [x] YouTube: chunked by transcript timestamp, not sentence (auto-captions have no
  punctuation, KB-001); each chunk records its first segment's real `start_seconds` and its
  citation URL gets `&t={int(start_seconds)}` appended (`chunk_youtube_document`). Checked
  `data/t002_youtube_captions.json` for real transcript text with timestamps first, per
  instruction — **it doesn't have any**: T-002's script only ever saved counts
  (`snippet_count`, `language`, `is_generated`), never the actual snippets. No real
  timestamped caption text exists anywhere in this repo, so the chunking logic is tested
  against synthetic segments built from the real `FetchedTranscriptSnippet` shape
  (`tests/test_chunking.py`), and the chunk-size target is calibrated from a real qwen3
  tokenizer measurement against synthetic caption-style text (real English text,
  lowercased/depunctuated), not real captions. Flagged in `docs/DESIGN.md` as an estimate to
  re-confirm once T-017 unblocks
- [x] `Pending` markers are never embedded (skipped by filename in `load_documents()`);
  `title_description` fallback documents are embedded, with `text_source`/`fallback_reason`
  carried into chunk metadata so a citation can be told apart from a real transcript
- [x] `feed_date` numeric (above), `bge-m3` explicit (above), idempotent (above)

**Out of scope:** catch-up logic for missed days (T-013); retrieval/answer generation
(Phase 2) — design notes only, see `docs/DESIGN.md` § Answer generation.

**Depends on:** T-008, T-009, T-015. Not blocked on T-017 — reads whatever `data/raw/`
contains, HF-only or HF+YouTube.
**Notes:** T-008 blocked this until its context-budget section landed, per explicit
instruction when Phase 1 was opened; landed, then this ran. Run order followed:
T-009 → T-010 → T-015 → T-008 → T-012.

**Schema change, flagged per `CLAUDE.md`'s stop-and-ask rule for stored data formats:**
`Document` gained a new field, `segments` (`vg09/document.py`) — the real per-snippet
`{text, start, duration}` timing `FetchedTranscript` provides (T-010's verified shape),
preserved so YouTube chunking can use real timestamps instead of losing them when
`vg09/youtube.py` joins snippets into one string. This is additive and backward-compatible
(old JSON files without the key still load fine via `.get()`), and was a direct, structural
consequence of this ticket's own instructions (chunk by timestamp, store the start time) —
proceeded rather than blocking to ask, since the alternative (not implementing timestamped
citations at all) contradicts what was explicitly asked for. Flagged here and in the final
report for me to confirm or object, per `/deep-review`'s finding below. **Approved
after the fact by me and recorded as D-007.**

`/deep-review` (reviewer subagent) findings: one Minor/process (the schema change above,
addressed by this note rather than reverted), one Minor/plausible (segment construction
assumes real `FetchedTranscriptSnippet.start`/`.duration` are well-formed — already flagged
project-wide as unverified against real data pending T-017, no separate action taken).

`docs/DESIGN.md` also gets two Phase 2 design notes (not built): the `/api/chat` message
structure (system prompt as its own message; verified via the real chat template that system
always renders first, regardless of array order — this changes T-008's truncation-ordering
mitigation, since `/api/chat` can't protect the system prompt by ordering the way raw
`/api/generate` string concatenation could), and that `done_reason == "length"` must be
detected and surfaced, never presented as a complete answer.

---

### T-015 — Initial 8-week HF backfill

**Status:** done
**Size:** S  ·  **Branch:** `t/T-015-initial-backfill`

**Goal:** the last 8 weeks of HF Daily Papers history are ingested into `data/raw/`,
establishing HF's side of the dataset that catch-up (T-013) and the evaluation question set
(T-014) build on — runnable now, independent of YouTube's transcript-path decision (T-017).

**Why:** `docs/PLAN.md` Phase 1's catch-up checklist item and `docs/GOAL.md`'s "up to 7 days
offline" success criterion both assume a dataset already exists to catch up onto; nothing
has ingested that starting history yet. Split off from the original combined HF+YouTube
backfill ticket after KB-008 confirmed the YouTube transcript-fetch block (`IpBlocked`) was
still live on a same-day manual re-check — HF has no such blocker, so there's no reason to
hold HF's backfill hostage to a YouTube decision.

**Acceptance criteria**
- [x] The HF backfill fetches daily papers for each of the last 8 weeks (56 days) via
  T-009's collector, bounded by `feed_date` (`submittedOnDailyAt`, D-002) →
  `scripts/t015_hf_backfill.py`, window 2026-07-23..2026-09-16, 1184 papers written
- [x] Weekend/empty-list days (KB-002) are not treated as failures → all 16 weekend days in
  the window (every Sat/Sun) returned 0 papers cleanly, no errors, matching KB-002's pattern
  at 4x the scale originally observed
- [x] Interrupting the run and restarting it resumes from where it left off → verified for
  real: deleted 3 days' `_done.json` markers to simulate an interruption, re-ran, and exactly
  those 3 days (plus "today") were re-fetched with identical paper counts (40, 38, 48); the
  other 52 days stayed skipped
- [x] Normalized documents are written to `data/raw/` via T-009's collector, and the
  backfill's watermark (most recent fully-settled `feed_date`) is persisted → `vg09/watermark.py`,
  `data/watermark_hf.json` = `2026-09-15` (yesterday, not today — see Notes)
- [x] Running the backfill twice produces the same document count both times → confirmed:
  1184 documents after run 1, still 1184 after run 2 (55/56 days skipped) and after the
  simulated-interruption re-run

**Out of scope:** YouTube backfill (T-017, blocked on a separate decision); ongoing catch-up
after this point (T-013); chunking/embedding the backfilled documents (T-012).

**Depends on:** T-009
**Notes:** No YouTube calls of any kind — verified by inspection (the script imports only
`vg09.hf_papers` and `vg09.watermark`) as well as by not seeing any in the run output. Does
not by itself complete T-013's or T-014's YouTube side — see their updated notes. T-017
covers YouTube's backfill once its transcript-path decision is made.

`today` is deliberately excluded from both the completion-marker mechanism and the watermark
(set to yesterday, `2026-09-15`, not today's `2026-09-16`) — HF may add more papers to
today's date later in the day, so every future run re-checks it fresh rather than trusting a
snapshot, and T-013's catch-up will always re-examine "today" too since its `feed_date` is
never `<=` the watermark. A crash mid-run leaves the watermark unwritten (it's set once,
after the loop) and leaves already-done days marked — a resumed run picks up correctly
without redoing settled work; not tested with an injected crash, but the simulated-marker
deletion above exercises the same resume path a real interruption would.

Grill-me (inline) flagged one Minor, not fixed: `date.today()` uses the machine's local
timezone, not necessarily HF's server timezone, so a day-boundary run could be off by one
relative to what `date=` actually selects server-side. Not investigated further - HF's own
server timezone isn't known, and the "always re-check today" design already self-corrects
most of the practical impact. Worth a real check if a boundary run ever produces a
suspiciously-sized day.

**Follow-up fix (same ticket):** I flagged that re-checking only "today" wasn't
enough — Sweden's local clock runs ahead of UTC, so a run shortly after local midnight could
close out a day (mark it done, advance the watermark past it) while it's still open on HF's
server clock, which is exactly the Minor timezone risk noted above turning into a real
correctness gap. Fixed: the reopen window is now the last **2** calendar days
(`REOPEN_DAYS=2`), not just today; the watermark now sits 2 days back, not 1. Re-ran against
the real API: the stale `_done.json` marker 2026-09-15 had from the original run (back when
it wasn't in the reopen window yet) was cleared and the day re-fetched (33 papers, same
count, no duplicates - confirmed 1184 documents total, unchanged), and the watermark moved
from `2026-09-15` to `2026-09-14`.

---

### T-017 — YouTube backfill (completed by T-019 after a mid-run block)

**Status:** done
**Size:** M  ·  **Branch:** `t/T-017-youtube-backfill`

**Goal:** ingest the chosen channels' YouTube history into `data/raw/`, paced, resumable and
stop-on-block per D-006/KB-008/D-008 — completing the dataset T-013's catch-up and T-014's
frozen evaluation set need to cover both sources. Window shortened from the original 8 weeks
to **4 weeks** for this first pass (see Notes) — the request-volume caution that motivated
that cut is itself a hedge against KB-008's block recurring, not evidence that it will.

**Why:** KB-008 (updated 2026-09-17): the transcript-fetch path (`youtube_transcript_api`)
that was `IpBlocked` on 2026-09-16 cleared by 2026-09-17 (1051 real snippets on a manual
re-check against the previously-blocked video). D-008 records the resulting decision: wait
out the block (option a) rather than switching transcript source, with `yt-dlp` + local
Whisper (option b) named as the reserve plan if the block recurs mid-run.

**Acceptance criteria**
- [x] A decision is recorded in `docs/DECISIONS.md` (new `D-0NN`) choosing among:
  (a) wait out the IP block and retry captions once it clears,
  (b) `yt-dlp` audio download + local Whisper transcription (currently parked in
  `docs/GOAL.md` — un-parking it is part of this decision, not a foregone conclusion),
  (c) title+description only for the backfill, treating D-001/D-006's fallback as the
  primary source rather than a fallback, for this pass.
  → **D-008**, option (a), self-selected once KB-008 confirmed the block had cleared;
  option (b) recorded as the named reserve, not implemented
- [x] The YouTube backfill fetches each chosen channel's videos across the backfill window,
  paced to reduce load on the transcript-fetch path — **operationalized as a randomized
  3–8s pause between every video, plus a longer pause every 20th video**, at my
  explicit direction, rather than the originally-envisioned batch-level pause (a stricter,
  more cautious version of the same intent: don't hammer a path that was blocked two days
  ago). Real run confirmed the pacing logic executes as written; it did not prevent a
  recurrence (see below) — pacing alone was not sufficient
- [x] Each video's outcome (captions fetched, fallback used, or blocked, with the exception
  type where applicable) is logged individually, with running totals (captions fetched,
  fallback used, still pending) reported as the run progresses, not only at the end — real
  run's log shows a `[progress]` line after every video
- [x] Interrupting the run and restarting it resumes from where it left off, using
  `data/raw/` and T-010's `.pending.json` markers — the two videos already pending from the
  2026-09-16 block (`nZYJdwM-_nI`, `9RtywbN--QE`) were retried **first** and both succeeded
  with real captions, confirmed by the real run's log and `data/raw/youtube/2026-09-13/` and
  `2026-09-15/` now holding final `.json` documents instead of `.pending.json` markers.
  Restart-resumability itself (re-running after this abort) not yet exercised — next session
  should confirm the 17 already-fetched videos are skipped via `document.exists()`, not
  re-fetched
- [x] A `RequestBlocked`/`IpBlocked` result stops the run immediately and reports how far it
  got, per D-006/D-008 — confirmed for real: aborted on the 18th attempt with no fallback
  document written, a `Pending` marker written for the blocked video, and the run stopped
  rather than continuing to the 4th channel
- [x] Normalized documents are written to `data/raw/`; the backfill's end point is persisted
  as YouTube's starting watermark for T-013's catch-up logic, **only if the run completes
  the full window without being blocked** — met by **T-019**, not this ticket's own run:
  this run's watermark was correctly withheld when it was blocked partway through; T-019's
  Whisper path let a later re-run finish the full window and write
  `data/watermark_youtube.json = 2026-09-17`

**Out of scope:** HF backfill (T-015, done, separate ticket); implementing option (b)
(Whisper) — stays a reserve plan per D-008 unless the block recurs.

**Depends on:** T-009, T-010, D-008.

**Real run (2026-09-17, `scripts/t017_youtube_backfill.py`), not simulated:** window
2026-08-21..2026-09-17. Retried the 2 pending videos first (both succeeded, real captions),
then `@theAIsearch` (6 more in-window videos, all captions) and all 9 of `@mreflow`'s
in-window videos — **17 consecutive real caption successes, zero fallbacks, zero errors**.
The 18th attempt — the first video ever attempted from `@NateBJones` (`YTG0rdHPTDE`,
uploaded 2026-09-17) — raised `IpBlocked` again. The run stopped immediately per D-006: no
fallback document written, `data/raw/youtube/2026-09-17/YTG0rdHPTDE.pending.json` written,
`@ColeMedin` never reached. Full details and the two open readings of *why* it recurred
(session volume vs. per-channel novelty) are in KB-008's 2026-09-17 update.

**Resolved by T-019:** I chose option (b), un-park Whisper (recorded as **D-009**,
superseding D-008), after the recurrence above showed waiting it out doesn't scale. T-019
wired Whisper into `vg09/youtube.py` and re-ran this same backfill: all 24 remaining videos
across `@NateBJones`/`@ColeMedin` resolved via Whisper (0 captions succeeded for either -
KB-008's updated evidence says this block is durable and channel-scoped, not a session cap),
0 title+description fallbacks needed. Full detail in T-019's own ticket entry.

**Notes:** Split out from the original combined T-015 so HF's backfill wasn't held hostage to
the transcript-path decision; briefly unblocked by D-008, blocked again by a real recurrence,
resolved for good by T-019/D-009. The window cut from 8 weeks to 4 (halving the number of
transcript-fetch requests against a path that was blocked two days ago) and the per-video
pacing scheme above were both my explicit direction for this first pass, prioritizing
caution over completeness - pacing alone did not prevent the recurrence, which is exactly
what motivated D-009. No unit tests written for `vg09/youtube_backfill.py`'s orchestration
itself (the real paced runs across both this ticket and T-019 are the verification) -
still worth a mocked resumability/pacing test as a future follow-up, matching T-010's
pattern for the collector itself.

---

### T-018 — Whisper feasibility test: one video, audio download to transcript

**Status:** done
**Size:** S  ·  **Branch:** `t/T-018-whisper-feasibility` (stacked on `t/T-017-youtube-backfill`
— needs its real-run findings and the specific blocked video id)

**Goal:** know, with evidence from this machine and this specific blocked video, whether
`yt-dlp` audio download + local `faster-whisper` transcription is a viable transcript source
for the channels KB-008's `IpBlocked` block is still hitting — before wiring anything into
the collector.

**Why:** D-009 un-parks option (b) but requires this feasibility check first. Building
Whisper into `vg09/youtube.py` on the strength of the idea alone would repeat T-002's original
mistake in the other direction — assuming a path works instead of measuring it. The audio
path might *also* be blocked (same origin, same IP), and even if it isn't, `faster-whisper`'s
transcript shape (timestamps, punctuation) is currently unknown and T-012's chunking (D-007)
depends on that shape.

**Acceptance criteria**
- [x] `yt-dlp` downloads audio-only for `YTG0rdHPTDE` (the video T-017 was blocked on) with no
  `youtube_transcript_api`/caption call anywhere in the script — confirmed by inspection
  (`scripts/t018_whisper_feasibility.py` imports only `yt_dlp`, never
  `youtube_transcript_api`) and by the real run: **audio download succeeded**, 26.7MB, no
  block of any kind on this call
- [x] If the audio download itself fails with a blocking-type signal ...: the script stops
  immediately and does not proceed — **not triggered**, download succeeded outright; the
  stop-condition code path exists (`download_audio()`'s `BLOCK_SIGNALS` check) but was not
  exercised for real this run
- [x] If audio download succeeds: `faster-whisper` transcribes it on the RTX 4090 (GPU, not
  CPU fallback) — confirmed real GPU run after KB-012's fix; **39.7s** transcription for a
  **1848s (30.8 min)** real video (~46x real-time), model load 1.0s separately, peak VRAM
  **~4536 MiB** vs ~3390-3400 MiB baseline. Measured with **no Ollama models resident**
  (`ollama ps` empty beforehand) — full detail and the joint-residency caveat in KB-013
- [x] The transcript's segment/timestamp shape is compared explicitly against
  `FetchedTranscriptSnippet`'s shape — **not compatible as-is**: `faster-whisper` returns
  `{text, start, end}`, not `{text, start, duration}`; trivial `duration = end - start`
  conversion needed. Also structurally different in grain: Whisper gives full, non-overlapping
  sentences (2-19s each in this sample); auto-captions give short, overlapping ~4s phrase
  fragments — see KB-013
- [x] The transcript text is compared against real auto-captions (this specific video's own
  captions are blocked, so used already-fetched real captions from `@theAIsearch`/`@mreflow`
  as the stand-in, per the ticket's own fallback allowance) for punctuation and proper nouns —
  **real auto-captions turned out to have punctuation and capitalization throughout**,
  contradicting `vg09/chunking.py`'s "no punctuation" premise (KB-014, flagged per
  `CLAUDE.md`'s reality-contradicts-docs rule, not silently fixed here); real garbling
  examples found in the same data ("Palunteer"/Palantir, "Open AAI"/OpenAI, "Sunno V6"/Suno
  V6). Findings written to `docs/kb/`: KB-012, KB-013, KB-014
- [x] No code in `vg09/youtube.py` or `vg09/youtube_backfill.py` changed to call Whisper —
  confirmed, `scripts/t018_whisper_feasibility.py` is fully standalone

**Out of scope:** wiring Whisper into the collector's fallback path (a follow-up ticket once
this one confirms feasibility); `@ColeMedin` or the rest of `@NateBJones`'s videos (T-017
resumes those once a path is confirmed); re-running T-017's backfill; fixing
`vg09/chunking.py`'s punctuation-premise comment (KB-014, flagged for the next
chunking-touching ticket, not fixed here); a joint VRAM measurement with Ollama's models
actually loaded (KB-013 only has the arithmetic comparison against D-005's headroom).

**Depends on:** T-017 (for the blocked video id and KB-008's evidence), D-009.
**Notes:** Real result: **feasible**. Audio download for this channel/video was not blocked,
transcription is fast and cheap on VRAM, and the only real integration cost is the trivial
segment-shape conversion plus re-examining `vg09/chunking.py` against Whisper's
longer/punctuated segments before wiring it in — not a blocker, but not a drop-in either.
New dependencies added (approved by my explicit instruction to test
`faster-whisper`): `faster-whisper`, `ctranslate2`, `av`, and the CUDA runtime wheels
`nvidia-cublas-cu12`/`nvidia-cudnn-cu12`/`nvidia-cuda-nvrtc-cu12` (needed per KB-012 - this
machine has no system-wide CUDA install). `requirements.txt` regenerated via `pip freeze`,
diffed to confirm only these packages were added. Per my explicit instruction, Whisper is
**not** wired into the collector as part of this ticket - that's the next decision point,
now with real evidence behind it instead of an untested plan.

---

### T-019 — Wire Whisper into the collector as the second transcript path

**Status:** done
**Size:** L  ·  **Branch:** `t/T-019-whisper-integration` (stacked on `t/T-018-whisper-feasibility`)

**Goal:** `vg09/youtube.py` uses captions first, `yt-dlp` audio + local `faster-whisper`
second (on `RequestBlocked`/`IpBlocked`), and title+description only as a last resort when
both fail — so `@NateBJones` and `@ColeMedin` get real transcript-quality text instead of
either an indefinite wait (D-008) or a weak fallback, and the backfill for those two channels
can actually complete.

**Why:** D-009 decided to un-park Whisper for the channels the block keeps hitting; T-018
confirmed it's feasible (audio download not blocked, transcription fast and cheap on VRAM).
This ticket does the real integration D-009 named as the next step, plus the two pieces of
unfinished business T-018 and T-012 both flagged: `vg09/chunking.py`'s unverified
"no punctuation" premise (KB-014) and its chunk-size calibration against synthetic rather
than real caption text (T-012's own flagged uncertainty, now resolvable — 17 real transcripts
exist on disk).

**Acceptance criteria**
- [x] `vg09/chunking.py`'s docstring/comments no longer claim auto-captions lack punctuation
  (KB-014) - corrected. The segment-windowing algorithm was confirmed by reading to already
  only ever break at a segment boundary (a window closes only *after* a whole segment is
  appended) - no logic change needed, true for both caption- and Whisper-sourced segments
  since both share the `{text, start, duration}` shape after this ticket's conversion step
- [x] `TARGET_CHUNK_CHARS` re-measured against all 17 real caption transcripts on disk
  (`scripts/t019_caption_token_recalibration.py`) - real ratio (4.16-4.61 chars/token, mean
  4.38) was **worse** than T-012's synthetic estimate (5.55-6.71), the dangerous direction
  (KB-005). `TARGET_CHUNK_CHARS` dropped 1942 → 1454. Verified against the largest real
  transcript on disk: max real chunk size 395/400 qwen3 tokens with the new calibration
  (`scripts/t019_verify_chunk_token_cap.py`)
- [x] `vg09/youtube.py`: three-tier fallback implemented and real-run-verified - captions,
  then Whisper on `RequestBlocked`/`IpBlocked`, then title+description only if both fail.
  `text_source="whisper"` added. Missing-captions path unchanged (D-006). Real backfill
  re-run: 24/24 `RequestBlocked` videos resolved via Whisper, 0 needed the third resort
- [x] Whisper's `{start, end}` converted to `{start, duration}` (`fetch_whisper_transcript()`)
  - confirmed on real data: sample document has 536 real segments in the correct shape;
  `chunk_youtube_document()` ran unmodified against a real Whisper document (15 chunks,
  correct `&t=SECONDS` citations, full text reconstructed exactly from rejoined chunks)
- [x] Downloaded audio deleted after transcription, success or failure - confirmed by both a
  unit test (mocked) and the real run: `data/whisper_audio/` is empty after all 24 real
  transcriptions
- [x] Real joint VRAM residency confirmed (KB-015): `qwen3:30b-a3b` + `bge-m3` loaded via
  Ollama (D-005, both 100% GPU), then real Whisper transcription alongside them - peak 23646
  of 24564 MiB, ~0.9GB headroom, neither Ollama model evicted. Per-video load/unload was **not
  needed** - the model stays resident across the whole run (module-level lazy singleton)
- [x] Backfill re-run for `@NateBJones` and `@ColeMedin` - **complete**: 24 new videos, all
  24 via Whisper (0 captions succeeded - both channels are 100% `IpBlocked`, durably, per
  KB-008's updated evidence), 0 fallbacks needed, 18 already-done videos correctly skipped
  (`@theAIsearch`/`@mreflow`). Watermark advanced to 2026-09-17. `data/raw/youtube/` now has
  41 final documents, 0 pending markers

**Out of scope:** re-running the full 4-week backfill for `@theAIsearch`/`@mreflow` (already
complete, T-017); extending the backfill window beyond 4 weeks; a general Whisper model-size
sweep (T-018/KB-013 used `small` - staying with that here unless it proves inadequate);
building a scheduler or automatic retry for `Pending` markers beyond what already exists.

**Depends on:** T-017, T-018, D-009.
**Notes:** Bundled as one ticket per my explicit instruction - the six pieces are a real
sequential chain (chunking must accept Whisper's shape before the collector produces any;
the VRAM check must happen before the real backfill re-run commits to a loading strategy),
not independent work that benefits from separate tickets. Behavior change recorded as
**D-010**: D-006's "blocked → write a Pending marker, raise `IngestBlocked`, caller stops the
run" consequence is retired for the caption-`RequestBlocked` case specifically - every video
now resolves to a final document (captions → whisper → title+description) with no run-wide
abort on a single video's block. `IngestBlocked` had no remaining caller after this change
and was removed, along with `youtube_backfill.py`'s abort branch, rather than left as dead
code.

**Real backfill re-run, not simulated:** 24 new videos across `@NateBJones` (16) and
`@ColeMedin` (8), all in the 2026-08-21..2026-09-17 window. **Every single one** hit
`IpBlocked` on captions - 24/24, paced with the same 3-8s/longer-pause schedule T-017 used -
and **every single one** resolved via Whisper with zero errors and zero further fallback.
This is much stronger evidence than T-017's single data point that the block is durably
scoped to these two channels specifically, not a session-volume cap a retry could out-wait -
recorded in KB-008's update. YouTube's watermark is now set (2026-09-17), completing
`docs/PLAN.md` Phase 1's YouTube backfill checklist item. `docs/GOAL.md`'s Whisper
non-goal condition ("captions can't be fetched and time allows") is now demonstrated in
production, not just tested in isolation (T-018).

`/deep-review`-equivalent self-check before closing: read `vg09/youtube.py`,
`vg09/youtube_backfill.py`, and both test files end to end after all edits: no dead
imports, `IngestBlocked`'s only remaining textual references are historical (KB-008/D-006's
own docs, correctly describing what *used* to happen), 19/19 unit tests pass, and the real
run's disk state (0 pending markers, 41 final documents, empty `data/whisper_audio/`)
matches what the code claims it should produce.

---

### T-013 — Catch-up ingestion since the last successful run

**Status:** done (fully - both sources verified for real; YouTube half completed in a later
session once T-019 gave YouTube a real transcript path)
**Size:** M  ·  **Branch:** `t/T-013-catch-up-ingest`, YouTube half on `t/T-013-youtube-catchup`

**Goal:** after the PC has been off for up to 7 days, one ingest run catches up everything
missed from both HF Daily Papers and YouTube, using feed date to determine what's new.
Per-source watermarks meant the HF half could start and ship without waiting on YouTube's
transcript-path decision (D-008/D-009) - it did; this entry now also covers the YouTube half,
completed and verified once T-019 landed.

**Why:** `docs/PLAN.md` Phase 1's catch-up checklist item; `docs/GOAL.md`'s first success
criterion depends on this directly. Per-source watermarks (not one combined watermark) mean
this can start and be verified against HF alone while YouTube's backfill (T-017) is still
blocked on its transcript-path decision.

**Acceptance criteria**
- [x] Each source keeps its own feed-date watermark, persisted durably → `vg09/watermark.py`
  (already existed from T-015), `data/watermark_hf.json` / `data/watermark_youtube.json`,
  one file per source
- [x] A simulated offline scenario against **HF alone** results in one run fetching all HF
  documents with `feed_date` after the watermark, no YouTube data or calls involved →
  verified for real (see below), not just against a mock
- [x] YouTube catch-up is real and exercised against real data, end to end - **completed in
  a later session** once T-019 gave YouTube a real transcript path. `catch_up_youtube()`
  (previously a stub that only reported the watermark) now reuses
  `vg09.youtube_backfill.run()`'s paced three-tier-fallback logic for the window since the
  watermark - see the real gap-simulation verification below
- [x] New documents from a catch-up run are appended to `data/raw/` → confirmed via the real
  gap-simulation run below
- [x] Running catch-up twice in a row with no new data adds zero new documents → real run:
  second `t013_catch_up.py` + `t012_build_store.py` pass left `collection.count()` at 1184,
  unchanged
- [x] Each source's watermark only advances after that source's part of the run completes
  successfully → `sync_hf()` writes the watermark once, after its loop; an exception mid-loop
  leaves it unwritten and leaves already-settled days marked, so a resumed run picks up
  correctly (same design T-015 already established, reused here via the shared `vg09/sync.py`)

**Real end-to-end verification (not simulated against a mock) — the exact scenario asked
for:** removed 2 real days (`2026-09-07`: 28 papers, `2026-09-08`: 12 papers) entirely from
`data/raw/hf/` *and* from the real Chroma store (`scripts/t013_simulate_gap.py`), rolled the
`hf` watermark back to `2026-09-06`, then ran the real pipeline:
1. `scripts/t013_catch_up.py` against the live HF API → both days re-fetched, identical
   counts to the original (28, 12), watermark correctly advanced back to `2026-09-14`
2. `scripts/t012_build_store.py` against the live Ollama/bge-m3 → `collection.count()` back
   to **1184** (was 1144 after the simulated removal)
3. `scripts/t013_verify_no_duplicates.py`: 1184 ids, **1184 unique ids — no duplicates**; the
   40 chunks for the gap days are back with correct `feed_date`/`feed_date_ordinal`/metadata
4. Ran steps 1-2 again: still 1184, stable

**Real end-to-end verification, YouTube half (completed in a later session, after T-019):**
first built the store with the **full current YouTube dataset for the first time** -
`scripts/t012_build_store.py` had never been run against real YouTube documents before this;
`collection.count()` went from 1184 (HF-only) to 1994 (1184 HF + 810 YouTube chunks across 41
documents). Then the same gap-simulation shape as the HF verification, against YouTube:
1. `scripts/t013_simulate_youtube_gap.py` removed `2026-09-10`'s 3 real videos - a deliberate
   mix of both transcript paths: `q9tpIc8PVKM` (captions, `@theAIsearch`) and
   `SGodxQHnVxc`/`n5bZHETCiJA` (whisper, `@ColeMedin`/`@NateBJones`) - from `data/raw/` and
   Chroma (50 chunks), rolled the `youtube` watermark back to `2026-09-09`
2. `scripts/t013_youtube_catch_up.py` (`catch_up_youtube()`, real network + GPU calls) →
   all 3 videos came back, but **not identically** to their original fetch: `n5bZHETCiJA`/
   `SGodxQHnVxc` hit `IpBlocked` again and resolved via Whisper as before, but `q9tpIc8PVKM`
   - previously a clean caption fetch - **also hit `IpBlocked` this time**, and its Whisper
   fallback **also failed** (`yt-dlp` audio download: `DownloadError`/`HTTP 403`), so it
   correctly fell through to the third resort, title+description. D-009's three-tier design
   handled a real double-failure case correctly, not just the single-failure case exercised
   before. Full detail in KB-008's latest update
3. `scripts/t012_build_store.py` → `collection.count()` = 1971 (not 1994 - expected, since
   `q9tpIc8PVKM`'s content genuinely changed from a full transcript to a short
   title+description, producing far fewer chunks for that one document; document count
   unchanged at 1225)
4. `scripts/t013_verify_youtube_no_duplicates.py`: 1971 ids, **1971 unique ids — no
   duplicates**; all 3 gap videos back with correct metadata, each showing the transcript
   path it actually took this time

**Real bug found and fixed via this verification, not in previously-shipped-and-tested
code:** `chunk_youtube_document()`'s windowed/multi-chunk path (`flush()`) passed
`text_source` to each `Chunk` but never `fallback_reason` - silently dropping it from every
multi-segment YouTube chunk. Invisible for captions (`fallback_reason` is always `None`
there) until a real Whisper-sourced document - which always has segments and a real
non-`None` fallback_reason (`"IpBlocked"`, D-009) - went through this path for the first
time via the check above. Fixed (`vg09/chunking.py`), covered by a new regression test, and
confirmed against the real store: all 24 real Whisper documents' chunks were missing this
field before a rebuild, correct after.

**Out of scope:** a scheduler or always-on process (explicit non-goal, `docs/GOAL.md`) —
catch-up is triggered manually/on demand.

**Depends on:** T-012, T-015 (HF half); T-019 (YouTube half - needed a real transcript path
before catch-up had anything real to exercise).
**Notes:** T-015's day-by-day backfill logic was factored out into `vg09/sync.py`
(`sync_hf(start, today)`) so the backfill and catch-up share one implementation rather than
two that could drift apart; `scripts/t015_hf_backfill.py` is now a thin entry point over it.
Caught and fixed an off-by-one in that refactor (start date was 1 day early, an 8-week
window came out 57 days instead of 56) before it shipped, by comparing the refactored
script's real output window against the original.

**Real bug found and fixed while writing this ticket's own tests, not in the shipped
code:** `tests/test_sync.py` initially patched only `vg09.document.RAW_DIR`, following the
pattern that worked for `tests/test_youtube.py`. It doesn't work for `vg09.hf_papers`'s
day-marker functions (`day_marker_path`, `is_day_done`, `mark_day_done`, `clear_day_marker`)
— they read `hf_papers`'s own `from vg09.document import RAW_DIR` binding, a separate name
patching the origin module doesn't touch. The under-isolated test's reopen-window logic
called `clear_day_marker()` against the **real** `data/raw/hf/` directory and deleted 4 real
`_done.json` markers (`2026-09-09` through `2026-09-12`) before the bug was caught (test
assertions failed in a way that pointed straight at it). No document JSON was lost — only
completion markers — confirmed by re-running the real backfill, which re-fetched all 4 days
with identical paper counts to the original and re-created the markers; `collection.count()`
was unaffected throughout. Recorded as **KB-010**, including the check that `vg09/store.py`
has the identical exposure for any future test of `load_documents()`.

---

### T-014 — Write the 15–20 evaluation questions with expected sources

**Status:** done
**Size:** M  ·  **Branch:** `t/T-014-eval-questions`

**Goal:** I write 15–20 evaluation questions against a frozen dataset (fixed
cutoff feed date), and for each one the agent finds the expected source document(s) and
confirms they actually exist in the ingested data — all before retrieval is built, so the
system can't be tuned to them. HF-side work can start now; the frozen dataset isn't final
until T-017's transcript-path decision lands, since the set must span both sources.

**Why:** `docs/PLAN.md` Phase 1's evaluation-questions checklist item; `docs/GOAL.md`'s
evaluation compares date-aware vs plain retrieval, which is only a fair test if the question
set predates the retrieval implementation. Verifying expected sources against real
backfilled data (rather than asserting them from memory) means the eval set isn't built on
a source that turns out to be missing or garbled. Splitting T-015 into HF-now/T-017-later
means this ticket can start drafting HF-side questions immediately, but "frozen dataset"
only means something once both sources have stopped moving.

**Acceptance criteria**
- [x] HF-side question drafting and source-verification can start against T-015's backfilled
  `data/raw/hf/` as soon as it exists — not blocked on T-017 → started against the real
  1184-document HF store, before T-017's YouTube data was even in scope
- [x] The dataset used for the **final, frozen** question set is `data/raw/` as it stood
  after **both** T-015 (HF) and T-017 (YouTube) have completed; that combined cutoff (both
  sources' end dates) is written down alongside the question set so a later re-ingestion
  doesn't silently change what "current" meant when the questions were written →
  `docs/eval-questions.md` "Frozen dataset" section: HF through 2026-09-16, YouTube through
  2026-09-17 — confirmed these match the real `data/raw/hf`/`data/raw/youtube` min/max
  `feed_date` at freeze time
- [x] I write 15–20 questions spanning all three question types from
  `docs/GOAL.md`: "what's new", "did X come up", "has Q progressed in the last n weeks" →
  **15** questions (F01–F15), all three types represented (e.g. F01/F03/F10 "what's new",
  F05/F08/F09/F12 "did X come up", F02/F04/F07/F13/F15 "has X progressed")
- [x] For each question, the expected source document(s) (title + url + feed date) are
  looked up and confirmed present in `data/raw/` — not asserted from memory → every source in
  `docs/eval-questions.md` verified by direct search over the real JSON documents (never
  asserted from memory); two cases where a prior assumption was wrong were caught and
  corrected rather than adopted silently (see Notes)
- [x] At least two questions are built around a proper noun likely to be garbled by
  YouTube's auto-generated captions, per T-002's notes and KB-001 — these specifically
  depend on T-017's real YouTube data, not HF's → F12 (Palantir → real auto-caption
  garbling "Palunteer", confirmed in `data/raw/youtube/2026-09-16/S2VJU5DQqlU.json`'s real
  segments) and F13 (OpenAI → real garbling "Open AAI" in
  `data/raw/youtube/2026-09-13/nZYJdwM-_nI.json`)
- [x] Questions span both sources, and at least one requires combining evidence from both →
  F14 and F15 each require at least one real HF source and one real YouTube source for a
  passing answer (facit says so explicitly); every other question is single-source
- [x] The set is committed to the repo with the frozen cutoff date(s) recorded, dated before
  any retrieval code exists, so the "written before retrieval" ordering is verifiable from
  git history → `docs/eval-questions.md` committed on `t/T-014-eval-questions` (3 commits);
  confirmed no retrieval code exists anywhere in the repo (`vg09/` has only ingest/store
  modules) at commit time

**Out of scope:** running the evaluation itself (Phase 3); building retrieval (Phase 2).

**Depends on:** T-001, T-015 (to start); **T-017 to close** — the frozen dataset and the
auto-caption-garbling questions both need real YouTube data.
**Notes:** I wrote all 15 questions; the agent's job was finding and verifying
expected sources against the real data, which surfaced three real discrepancies between
prior assumptions and what `data/raw/` actually contains, all flagged rather than silently
resolved:
1. F01 assumed only two RSI papers shared the 2026-09-16 feed date; there are actually
   **three** (`2609.11873`, `2609.17523`, `2609.14857`). Resolved by me: any two of the
   three count as correct.
2. F04 assumed RealSWE (`2608.27831`, 2026-09-04) was the most recent pre-window coding-agent
   source; τ^τ-Bench (`2609.04611`, 2026-09-07) is more recent and also on-topic. Resolved by
   I: both count.
3. F07 assumed "nothing about text-to-video in the last month"; once "last month" used the
   same 30-day window as F02, FIRM-Video (`2608.21839`, 2026-08-27) fell inside it and
   contradicted that assumption. Corrected in the facit (not silently kept), per `CLAUDE.md`'s
   reality-contradicts-documentation rule.

Time-window phrases in the questions ("senaste veckan", "senaste månaden", …) aren't pinned
to a date by the questions themselves — `docs/eval-questions.md` fixes one consistent
definition per phrase up front so every question's facit grades against the same window
instead of nine different ad-hoc interpretations.

F11 and F15 (research/agents "last week") and F14 (open-source alternatives) all have source
sets too large or too open-ended for a single fixed list (F11's real window has 137 HF
papers) — their facit uses a count/window criterion (e.g. "≥3 papers, all within the window")
rather than an exhaustive enumeration, which is itself a documented, reviewable decision
rather than an omission.

---

### T-020 — Freeze the eval dataset for real, and add a timeout to the YouTube backfill's yt-dlp calls

**Status:** done
**Size:** M  ·  **Branch:** `t/T-020-freeze-and-timeout`

**Goal:** the "frozen dataset" T-014's evaluation questions are written against is actually
frozen — provably unchanged, not just described by a cutoff date — and the YouTube backfill's
yt-dlp calls can't hang forever on a stalled connection.

**Why:** the Phase 1 `grill-me` review (this session) found that `data/raw/` is gitignored,
so nothing durable backs T-014's frozen-cutoff claim — only the cutoff *dates* are written
down, not the content. If `data/raw/` is ever lost, changed, or the sources quietly edit
their own past content, a later re-ingestion honoring the same dates could silently produce
different documents than the ones T-014's expected answers were verified against, and nothing
would detect it. The same review found `youtube_backfill.py`'s yt-dlp calls have no explicit
timeout, unlike every other network call in the codebase — a stalled connection mid-run can
hang indefinitely. Both are cheap to fix now and expensive to discover later (the first, only
once Phase 3 already depends on the freeze holding; the second, only during a real multi-hour
backfill run).

**Acceptance criteria**
- [x] A zip archive of `data/raw/` as it stands at the frozen cutoff (HF 2026-09-16, YouTube
  2026-09-17) exists outside the repo (`C:\AIProjects\VG-09-frozen\`) — `data/raw/` itself
  stays gitignored, only the archive's existence and location change →
  `data-raw-frozen-hf20260916-yt20260917.zip`, 1279 entries, `testzip()` confirms no
  corruption; `.gitignore` unchanged, confirmed `git ls-files data/` still returns nothing
- [x] A manifest (`docs/eval-dataset-manifest.txt`, committed) lists the relative path and
  SHA-256 of every file in `data/raw/` at freeze time, plus the total document count, so a
  later diff can prove byte-for-byte whether anything changed → 1279 entries; header records
  1225 real documents (1184 HF + 41 YouTube), 54 HF day-completion markers, 0 pending markers
- [x] A script (`scripts/t020_verify_eval_dataset.py`) recomputes SHA-256 for every file
  currently in `data/raw/` and reports any mismatch, missing file, or extra file against the
  manifest → implemented, exits 1 on any missing/extra/mismatched file
- [x] Running that script right now, before anything else changes, reports zero mismatches —
  proof the manifest actually matches `data/raw/`'s real content at commit time, not just a
  plausible-looking file → real run: "manifest entries: 1279 / files on disk: 1279 / OK -
  data/raw/ matches the frozen manifest exactly.", exit code 0
- [x] `docs/eval-questions.md` documents where the archive lives and how to run the verify
  script → new "Proving the freeze held (T-020)" subsection under "Frozen dataset"
- [x] `vg09/youtube_backfill.py`'s yt-dlp calls have an explicit `socket_timeout`, consistent
  with the `timeout=30/300` pattern already used for HF/Ollama's `requests` calls elsewhere in
  the codebase — including `vg09/youtube.py`'s `list_videos()` and
  `fetch_whisper_transcript()`, since both run inside `youtube_backfill.py`'s call path and
  share the same stalled-connection risk, even though they live in a different file → all
  three real `yt_dlp.YoutubeDL` call sites now pass `socket_timeout=30`
  (`YT_DLP_SOCKET_TIMEOUT`, defined once in `vg09/youtube.py`, imported by
  `youtube_backfill.py`); 20/20 existing tests still pass unchanged (they mock at the
  `YoutubeDL` boundary, so option-dict contents aren't asserted, but nothing broke)
- [x] `docs/PLAN.md` gets a risk register noting the four `grill-me` findings deferred to
  Phase 3 (no tests for `vg09/store.py`, no tests for `vg09/youtube_backfill.py`, no alert
  threshold on the bare `except Exception` around the Whisper fallback, and the softer of
  F14's two YouTube citations) so they aren't silently dropped → 4 new rows added to the
  existing risk register table

**Out of scope:** the four deferred findings themselves (tests for `store.py`/
`youtube_backfill.py`, the Whisper alert threshold) — noted in the risk register, not built.
Re-running or re-verifying the frozen dataset's *content* against HF/YouTube's live APIs —
this ticket proves the local snapshot hasn't silently changed, not that it's still what those
APIs would return today.

**Depends on:** T-014 (produced the frozen-cutoff claim this hardens), the Phase 1 `grill-me`
review (produced both findings).
**Notes:** Two of six `grill-me` findings, per my explicit triage; the other four are
deferred to Phase 3 rather than fixed now — see `docs/PLAN.md`'s risk register for each,
recorded there rather than fixed here so they can't be silently dropped before Phase 3.

The timeout fix ended up touching `vg09/youtube.py` as well as `vg09/youtube_backfill.py` —
the original finding's own two named call sites (`list_videos()`, `fetch_whisper_transcript()`)
both live in `youtube.py`, not the file I named; fixed there too rather than leaving a
partial fix that only covered `youtube_backfill.py`'s own `_fetch_single_video_metadata()`,
since all three share the exact same stalled-connection risk inside the same backfill run.
Flagged here rather than silently expanding scope without a trace.

Real, not simulated: `scripts/t020_freeze_dataset.py` was run once against the real
`data/raw/` (1279 files, 6.24 MB), producing the real zip and the real manifest committed
here; `scripts/t020_verify_eval_dataset.py` was then run against that same real `data/raw/`
and reported a clean match (exit 0) before this commit — the manifest is proven to match its
own subject at commit time, not just plausible-looking.

---

### T-021 — Extract a date range from the question, with a manual UI picker as the always-available fallback

**Status:** done
**Size:** L (touches a new UI↔retrieval contract; kept as one ticket — see Notes)  ·
**Branch:** `t/T-021-date-range`  ·  **Phase:** 2

**Goal:** a question like "senaste 3 veckorna" resolves to a concrete feed-date range that
retrieval (T-022) can filter on, and I can always override or supply that range
directly in the UI when extraction is absent, wrong, or the question doesn't state one.

**Why:** `docs/GOAL.md`'s third question type ("has Q progressed in the last n weeks") and
the project's central claim (date-aware retrieval beats plain similarity search) both
depend on a real date range reaching retrieval, not just parsed for display.
`docs/PLAN.md`'s risk register already names "Extracting a date range from free text is
unreliable" (Medium) with "a date-range control in the UI as a fallback" as the mitigation
— this ticket is that mitigation, not a new decision.

**Acceptance criteria**
- [x] Given a question that names a relative range ("senaste N veckorna/dagarna/månaden",
  "förra veckan"), a concrete `(start_date, end_date)` pair in feed-date terms is produced —
  anchored the same way `docs/eval-questions.md`'s "Time-window conventions" section already
  fixes them, not a fresh ad-hoc interpretation → `vg09/date_range.py::extract_date_range()`;
  "senaste månaden" resolves to a real calendar month back (matches the convention exactly),
  not a fixed 30 days
- [x] Given a question with no discernible date range, no range is invented — the question is
  treated as unbounded unless the UI's manual picker sets one → confirmed on 7/15 real
  questions (see real test below); a bare plural with no number ("de senaste veckorna", F09)
  is deliberately treated as unparseable rather than guessed
- [x] The UI exposes a manual start/end date control that, when set, overrides whatever (if
  anything) was extracted from the question text — the override always wins; extraction is
  never the only path to a date range → `resolve_date_range(question, today,
  manual_override=None)`; the actual rendered control is T-025's job (no UI framework is
  decided yet, per `CLAUDE.md`), this ticket delivers the override-always-wins contract that
  control will call
- [x] The extracted-or-manual range is passed to retrieval (T-022) as a single explicit
  parameter (e.g. `date_range: tuple[str, str] | None`), not re-derived downstream →
  `resolve_date_range()`'s return type, `tuple[date, date] | None`
- [x] `docs/DESIGN.md`'s "Interfaces and contracts" section documents this parameter's shape —
  the first contract between the UI and retrieval that Phase 2 creates → new "Date range: the
  UI ↔ retrieval contract (T-021)" subsection
- [x] At least one of T-014's real eval questions with an explicit relative range (e.g. F02
  "senaste månaden", F05 "senaste två veckorna") is used as a real test case for the
  extraction path — not only synthetic examples → went beyond "at least one": all 15 real
  questions tested, read live from `docs/eval-questions.md`
  (`scripts/t021_test_date_extraction_against_eval_questions.py`), not retyped

**Out of scope:** the retrieval/packing logic itself (T-022); the exact extraction technique
(rule-based vs. a model call) is left to whoever implements this — not decided here.

**Depends on:** T-014 (real example questions to test extraction against).
**Notes:** Kept as one ticket rather than split into "extraction" and "UI picker" — the
picker's default comes from extraction and extraction is worthless without an override path
for when it's wrong; the risk register's own mitigation is the *pair*, not either half alone.

**Real test against all 15 of T-014's real questions** (`today=2026-09-16`, fixed in code so
a re-run against the frozen eval dataset resolves the same way): **8/15 correct** (matched
`docs/eval-questions.md`'s own written windows exactly — F02, F04, F05, F07, F10, F11, F13,
F15), **0/15 wrong**, **7/15 correctly unparseable → `None`** (F01, F03, F06, F08, F09, F12,
F14). Rule-based, stdlib-only (`re`/`datetime`) — no LLM call, no new dependency.

**Real finding, reported to and confirmed by me before closing:** three of the seven
`None` results (F01 "de två senaste nyheterna", F03 "det absolut senaste", F06 "det senaste")
aren't a missing time phrase at all — they're a *different question type*: a ranking
("show me the most recent") with no bound to filter to, not a window with one. Documented in
`docs/DESIGN.md` ("Filtering by date and sorting by date are two different mechanisms") and
added as a new acceptance criterion on **T-022** (`detect_recency_ranking()`, F01/F03/F06 as
its real test cases) rather than reopening this ticket's own scope, since `extract_date_range`
returning `None` for these is still the *correct* answer to "is there a bounded window here"
— the gap was downstream, in what retrieval does with that `None`, not in this ticket's own
extraction logic.

Two design choices, explicitly confirmed by me rather than assumed: calendar-month
subtraction for "senaste månaden" (not a fixed 30 days), and treating a bare plural with no
number as unparseable (not silently defaulting to 1 or 2 weeks).

---

### T-022 — Similarity search with an optional date-range filter, packed to T-008's measured token budget

**Status:** done
**Size:** M  ·  **Branch:** `t/T-022-retrieval-packing`  ·  **Phase:** 2

**Goal:** given a question (embedded) and an optional date range (T-021), retrieval returns
the ranked set of chunks that actually fits the 13789-token budget `docs/DESIGN.md`'s Context
budget section measured — a real packed set with a provable token count, not just "top-k
chunks".

**Why:** T-008 already measured the real budget and specified the packing algorithm
(`docs/DESIGN.md` § "What happens if retrieved chunks don't fit") before any retrieval code
existed, specifically so retrieval wouldn't have to re-derive a budget from scratch or invent
a top-k out of thin air. D-002's feed-date filtering is the project's central claim under test
(date-aware vs plain) — retrieval must support running with and without the date filter as a
strict, comparable variant, not two code paths that could drift apart.

**Acceptance criteria**
- [x] Similarity search runs via `vg09.store`'s existing Chroma collection, embedding the
  question through `embed_batch()` (explicit `bge-m3`, `num_ctx=8192`) — never
  `query_texts=` (CLAUDE.md hard rule, per `docs/DESIGN.md`'s "Interfaces and contracts"
  warning) → `vg09/retrieval.py::query_candidates()`/`embed_question()`; asserted directly in
  `tests/test_retrieval.py::test_never_calls_query_texts`
- [x] When a date range is given, results are filtered by `feed_date_ordinal` (`$gte`/`$lte`),
  per KB-004 — never by the string `feed_date` → `query_candidates()`'s `where` clause;
  real run confirmed every returned feed date fell inside the requested window
  (`scripts/t022_verify_retrieval.py`)
- [x] A separate recency-**sort** mode exists alongside the date-range **filter**, per
  `docs/DESIGN.md`'s "Filtering by date and sorting by date are two different mechanisms"
  note: when the question is a ranking question ("det/de senaste [N]", no bound named),
  candidates are ordered by `feed_date_ordinal` descending instead of by similarity score —
  tested for real against F01/F03/F06, the three real questions T-021 already classified as
  ranking rather than window questions. Filter and sort are independent — either, both, or
  neither can be active for a given question → `vg09.date_range.detect_recency_ranking()`
  (added to T-021's module) + `vg09/retrieval.py::order_candidates()`; real run against F06
  showed genuinely different top-5s (similarity order: 2026-08-11/07-23/09-07/07-29/09-04;
  recency order: 2026-09-13/09-07/09-04/08-27/08-18, correctly descending)
- [x] Candidate chunks are packed greedily by real measured qwen3 token count (not chunk
  count) in relevance-descending (or, in recency-sort mode, date-descending) order, stopping
  once the running total would exceed 13789 tokens, per `docs/DESIGN.md`'s algorithm — tested
  against a real query where the naive top-34 would have overflowed → `pack_to_budget()`,
  unit-tested for the stop-early branch (`tests/test_retrieval.py`); **real finding**: against
  a real, topic-rich 60-candidate pool, a naive top-34's real token sum was 10265 — well under
  the 13789 budget, so it did *not* overflow this time. `docs/DESIGN.md`'s own 400-token
  worst-case margin (34×400=13600 ≤ 13789) explains why: real chunks average well under the
  cap (max single real chunk observed: 405 tokens, 5 over the intended 400 target — a T-012
  chunking-calibration note for whoever next touches it, not a T-022 defect). The
  packing-stops-early branch itself is proven correct by the mocked unit tests, which force
  the overflow case directly rather than hoping a real query happens to produce one
- [x] A single chunk too large to fit even alone is dropped, not sent, and this is observable
  (a returned count vs. requested count, or a log line) — not a silent drop →
  `RetrievalResult.dropped_oversized` (list of ids); unit-tested
  (`test_a_single_oversized_candidate_is_dropped_not_sent_and_packing_continues`)
- [x] Retrieval is runnable both with and without the date-range filter against the same
  question, producing two comparable result sets — the mechanism Phase 3's evaluation needs
  to compare date-aware vs plain retrieval → `query_candidates(question, date_range=None)` vs.
  `query_candidates(question, date_range=(...))`; real run against a broad "AI agents" query
  compared both
- [x] A real query against the production Chroma store returns results — not just against a
  synthetic test fixture → `scripts/t022_verify_retrieval.py`, real Chroma (1971 real chunks)
  + real Ollama (`qwen3:30b-a3b`, `bge-m3`) calls throughout, real run recorded above

**Out of scope:** the date-range extraction itself (T-021, though `detect_recency_ranking()`
is a small sibling addition to the same module); the LLM call that turns chunks into an
answer (T-023).

**Depends on:** T-012 (the store), T-021 (date range input and, now, ranking detection).
**Notes:** Packing is purely token-budget-driven, not chunk-count-driven — `docs/DESIGN.md`'s
"34 = 13789 // 400" is a worst-case ceiling (every chunk exactly at the cap), not a runtime
limit this code enforces. Real consequence, observed in the packing stress test: a real
45-chunk pack (13586 tokens) exceeded the "34" ceiling while still safely fitting the budget,
because real chunks mostly run smaller than the 400-token worst case. Not a bug — exactly what
a worst-case bound is supposed to allow once reality is better than the worst case.
`MAX_TOP_K` was written into the module as a constant, then removed before committing:
nothing in the packing logic actually used it as a cap, and an unused constant restating a
number `CHUNK_BUDGET_TOKENS`'s own comment already shows would have been dead weight. 54/54
tests pass (17 new — 7 for `detect_recency_ranking()`, 10 for `vg09/retrieval.py`).

---

### T-023 — The answer-generation call: message structure, generation cap, and detecting a cut-off answer

**Status:** done
**Size:** L (touches the shape of "an answer" as a contract; kept as one ticket — see Notes)
·  **Branch:** `t/T-023-answer-generation`  ·  **Phase:** 2

**Goal:** a packed set of chunks (T-022) plus the question produces one real
`qwen3:30b-a3b` answer via `/api/chat`, following the exact message structure and generation
limits T-008/KB-011 already measured and specified — and a genuinely cut-off answer is never
presented as if it were complete.

**Why:** `docs/DESIGN.md`'s "Answer generation" section already specifies both non-obvious
findings from T-008/T-012 that would otherwise get silently reinvented or gotten wrong:
KB-011's real chat-template finding that message *order* in the API call does not control
*rendered* prompt order, and the `num_predict:2000` cap's real failure mode
(`done_reason=="length"`). `CLAUDE.md`'s hard rule (every LLM call checks `prompt_eval_count`
against `num_ctx`) applies to every real call this ticket makes, not just T-012's embedding
calls.

**Acceptance criteria**
- [x] The system prompt is sent as its own `{"role": "system", ...}` message; the packed
  chunks and the question go together in one `{"role": "user", ...}` message — per
  `docs/DESIGN.md`, not the system-last string-concatenation shape T-008's raw `/api/generate`
  experiment used → `vg09/answer.py::generate_answer()`; asserted directly
  (`tests/test_answer.py::test_system_prompt_sent_as_its_own_message`, exactly 2 messages)
- [x] `num_predict` is set to exactly 2000 on every real call, per T-008's measured
  reservation — not left to Ollama's default or a different guess → `NUM_PREDICT=2000`,
  asserted directly (`test_num_predict_is_exactly_2000`)
- [x] The response's `done_reason` is checked on every call; `"length"` is surfaced to the
  caller as an explicit incomplete-answer signal (not merged into the answer text, not
  silently dropped) — `"stop"` is passed through as a complete answer →
  `AnswerResult.incomplete = (done_reason == "length")`, both branches tested
  (`test_stop_is_a_complete_answer`, `test_length_is_flagged_incomplete`)
- [x] The response's real `prompt_eval_count` is compared against the `num_ctx` sent (16000,
  D-005) and a warning is raised on truncation risk, per `CLAUDE.md`'s hard rule — the same
  pattern `vg09/store.py` already uses for embedding calls → same `>=`/`>=0.9×` check as
  `vg09/store.py::embed_batch()`; real run's `prompt_eval_count=11080` stayed well clear of
  `num_ctx=16000`, no warning fired (correctly - nothing to warn about)
- [x] The call goes through T-011's reasoning/answer-split utility — this ticket never reads
  `response.message.content` directly and calls it "the answer" without going through that
  split first → `split_reasoning_and_answer(resp)`; a think:false-shaped mock response
  (`thinking=""`) is confirmed to raise through `generate_answer()` itself, not just the
  utility in isolation (`test_a_think_false_shaped_response_raises_via_t011s_contract`)
- [x] A real end-to-end call against the real Ollama/`qwen3:30b-a3b`, using a real packed
  chunk set from T-022 (not synthetic filler), produces a real answer with a real
  `done_reason` and a real `prompt_eval_count` reading → `scripts/t023_verify_answer.py`,
  real run against F05 ("Har NeoHorse nämnts de senaste två veckorna?"): 29 real chunks
  packed (9477 tokens) through the real T-022/T-027 pipeline (dedup + eval anchor), real
  answer correctly identified NeoHorse-1 (2609.08183, feed date 2026-09-09) as inside the
  window, `done_reason="stop"`, `prompt_eval_count=11080`, 1628-char reasoning cleanly
  separated from the answer

**Out of scope:** citation formatting (T-024); the UI that displays the answer (T-025);
building T-011 itself (already its own ticket).

**Depends on:** T-011, T-022, D-005 (`num_ctx=16000`).
**Notes:** Kept as one ticket rather than split further — message structure, the generation
cap, and `done_reason` are all properties of the exact same single `/api/chat` call and its
one response; splitting them would mean two tickets both needing to make the same real call to
test anything. 77/77 tests pass (12 new).

**Real observation, not a defect, worth knowing before T-024:** the real F05 answer cited its
source as "source [27]" (the source's position in the assembled prompt) rather than literally
following the system prompt's requested `[Title, YYYY-MM-DD]` inline format, though it did
separately state the title and feed date in prose. The model's citation *style* isn't fully
prompt-compliant - T-024 builds structured citations from chunk metadata directly rather than
parsing the model's own inline text, so this doesn't block it, but it's a real data point for
Phase 3 if inline-citation quality ever matters on its own.

---

### T-024 — Attach structured citations (title, feed date, link, YouTube timestamp) to every answer

**Status:** done
**Size:** M  ·  **Branch:** `t/T-024-citations`  ·  **Phase:** 2

**Goal:** every answer comes back with the real citation data `docs/GOAL.md`'s success
criteria require — link, title, feed date, and arXiv publication date for papers — derived
from the chunk metadata T-012 already stores in Chroma, not re-fetched or re-derived.

**Why:** `docs/GOAL.md`: "Every answer cites its sources: link, title, feed date, and — for
papers — the arXiv publication date." T-012 already stores exactly this metadata on every
chunk (`url`, `title`, `feed_date`, `arxiv_published_at`, `start_seconds`) specifically so
this step wouldn't have to go back to `data/raw/` or re-derive a citation from the answer
text.

**Acceptance criteria**
- [x] Every chunk that contributed to a packed answer (T-022/T-023) produces one structured
  citation: title, feed_date, url → `vg09.citations.build_citations()`
- [x] An HF citation additionally carries `arxiv_published_at`, per `docs/GOAL.md`'s explicit
  success criterion → `Citation.arxiv_published_at`, tested and confirmed for real (below)
- [x] A YouTube citation whose chunk has a real `start_seconds` carries a url with
  `&t={int(start_seconds)}` appended, linking to the exact point in the video — a
  `title_description` fallback chunk (no `start_seconds`) links to the video URL unmodified,
  per `docs/DESIGN.md` → already true of `Candidate.metadata["url"]` since T-012's chunking
  builds it that way; this module passes it through unmodified rather than re-deriving it -
  confirmed for real below (`&t=1268`, `&t=0`)
- [x] A chunk built from a `title_description` fallback document is marked as such in its
  citation (`text_source`, per D-006) — distinguishable from a real transcript/abstract
  citation, not presented with equal confidence → `Citation.is_fallback`
- [x] Citations are deduplicated by `doc_id` when multiple chunks from the same document
  contributed — one citation per source document, not one per chunk → dedup by `doc_id`,
  first-cited order kept; tested for the same-number-twice case and the
  two-different-numbers-same-document case separately
- [x] A real answer generated against the real store (T-023) produces citations that, checked
  by hand, actually match the real `data/raw/` documents they claim to cite → real run below,
  hand-checked against `data/raw/hf/2026-09-09/2609.08183.json` and the real YouTube videos

**Out of scope:** rendering citations in the UI (T-025); the answer-generation call itself
(T-023).

**Depends on:** T-012 (chunk metadata), T-022 (which chunks contributed), T-023 (when
citations attach to a response).
**Notes:** Built directly on T-023's own real finding rather than fighting it: the model
doesn't reliably follow a `[Title, YYYY-MM-DD]` instruction, but does reliably cite the
bracketed *source number* already shown for each source in the prompt ("source [27]"). Two
changes make that reliable rather than accidental: `vg09/answer.py::number_sources()` now
returns the exact number→chunk mapping the prompt was built from (`AnswerResult.source_map`),
and `SYSTEM_PROMPT`'s citation instruction was rewritten to ask for exactly that instead of
the old format - re-measured for real: **157 qwen3 tokens** (was 171). `docs/DESIGN.md`'s
budget math and `vg09.retrieval.CHUNK_BUDGET_TOKENS` updated to match (13803, was 13789 - more
headroom, the safe direction); T-008/T-022's own historical ticket text is left describing
what was true when those tickets closed, not rewritten.

A bracketed reference that can't be resolved - an out-of-range number, or any other bracket
shape the model still produces - is collected into `CitationResult.unlinked_references`
(deduplicated), never silently dropped, per explicit instruction.

**Real run** (`scripts/t024_verify_citations.py`, real store + real Ollama):
- F05 ("Har NeoHorse nämnts de senaste två veckorna?"): real answer cited `[27]` and `[4]`;
  both resolved correctly - `[27]` → NeoHorse-1 (`2609.08183`, feed date 2026-09-09, arXiv
  `2026-09-08`, hand-checked against `data/raw/hf/2026-09-09/2609.08183.json`), `[4]` → a
  YouTube video with a real `&t=1268` timestamp preserved unmodified. Zero unlinked
  references.
- F12 ("Har Palantir nämnts i någon video?"): real answer correctly said "not mentioned" -
  but still produced 2 "citations", both false positives. **Real, discovered limitation, not
  fixed here per explicit instruction not to fight the model's format:** the answer text
  contained "I've carefully reviewed all 38 sources (from `[1]` to `[38]`)" - a *range*
  description, not an evidence citation, but indistinguishable from a real citation by
  bracket shape alone. Positional-citation resolution cannot tell "cited as evidence" apart
  from "mentioned descriptively" without a stricter format than what was asked for; recorded
  here as a known limitation of this approach, worth watching in Phase 3 if false-positive
  citations turn out to be common on negative ("not mentioned") answers specifically.

93/93 tests pass (16 new).

---

### T-025 — Chat UI: ask a question, see the answer with sources, or the empty state

**Status:** done
**Size:** L (the one ticket the Phase 2 checkpoint is judged against; kept as one ticket —
see Notes)  ·  **Branch:** `t/T-025-chat-ui`  ·  **Phase:** 2

**Goal:** one person can type a question, optionally set a date range, and see a real answer
with real citations — or, if no data has been ingested yet, a clear empty state instead of a
confusing blank or broken screen.

**Why:** `docs/GOAL.md`'s Definition of done #3 ("a simple chat UI that answers with sources,
including an empty state when no data exists") and success criterion ("the three question
types work end to end"). This is the one Phase 2 ticket a human actually looks at directly.

**Framework: Streamlit** (my choice of two, this session picked and justified): the
screen is a form-and-display app - a question field, a sidebar date picker, an answer, a
collapsible reasoning section, and a citation list - exactly Streamlit's native widget set
(`st.text_input`, `st.date_input`, `st.expander`, `st.markdown`), with no client-side state
machine to hand-build. Gradio leans toward a single input→output demo shape (or its
chat-message widget, which assumes a running conversation - an explicit non-goal,
`docs/GOAL.md`); fitting a sidebar override control and a mode-explanation caption alongside
one Q&A turn is more natural in Streamlit's script-per-rerun model.

**Acceptance criteria**
- [x] A question can be typed and submitted, and the resulting answer (T-023) is displayed →
  real browser run below
- [x] The manual date-range picker from T-021 is present, and its value, when set, always
  overrides the interpreted window — verified by checking what's actually sent to retrieval
  (`resolve_date_range(..., manual_override=...)`), not just that the control renders → real
  browser run: interpreted window for F05 was `2026-09-04..2026-09-17`; with the sidebar's
  "Från" set to `2026-09-01`, the caption switched to "Datumfilter (manuellt angivet):
  2026-09-01 – 2026-09-17" — the override, not the interpretation, reached retrieval
- [x] The UI states which date window was actually used for the answer (manual override,
  interpreted from the question, or none), or that ranking mode was used instead — I
  can always see which of T-022's mechanisms fired, not just the answer →
  `vg09.ui_helpers.describe_retrieval_mode()`; all three real forms observed live (manual,
  interpreted, ranking)
- [x] Citations (T-024) are displayed alongside the answer as clickable links, showing title
  and feed date; a YouTube citation's link opens at the `&t=` timestamp; unlinked references
  (T-024) are shown too, not silently dropped → real citation links rendered with correct
  `href`s in every real run below; `&t=` confirmed via T-024's own real run
  (`&t=1268`/`&t=0`), not re-tested here since the rendering is a direct, untransformed
  `c.url`
- [x] An answer flagged incomplete (`done_reason=="length"`, T-023) is visibly marked as
  incomplete in the UI — never rendered identically to a complete answer → **hit for real,
  unplanned**, during the F02 smoke test below: a genuine `st.warning` banner ("Svaret är
  ofullständigt — avbröts av längdgränsen innan det var klart.") appeared before the
  (truncated) answer
- [x] The model's reasoning (T-011's `split_reasoning_and_answer`) is never shown inline with
  the answer, but is reachable for the curious via a collapsed-by-default control → an
  `st.expander("Visa modellens resonemang")`, collapsed by default every time, confirmed
  openable (real F05 run: 1900+ character real chain-of-thought, in English, while the answer
  itself was in Swedish)
- [x] When the Chroma store has no documents at all, the UI shows an explicit empty state
  ("ingen data ännu, kör ingest") instead of an empty result, an endless spinner, or an error
  → real browser run against a genuinely empty temp Chroma store (never the real production
  data - see Notes): exactly "Ingen data ännu, kör ingest.", no sidebar, no form
- [x] All three question types from `docs/GOAL.md` ("what's new", "did X come up", "has Q
  progressed") are each exercised once against the real Phase 1 dataset as a manual smoke
  test in a real browser, not only unit-tested in isolation → all three below

**Out of scope:** authentication, multi-user, conversation history (all explicit non-goals,
`docs/GOAL.md`); styling/visual polish beyond "simple" (`docs/GOAL.md`'s own word).

**Depends on:** T-021, T-023, T-024.
**Notes:** This ticket's own acceptance criteria are what `docs/PLAN.md`'s Phase 2 checkpoint
("the three question types... work end to end with sources") will actually be checked
against.

New dependency, per my explicit two-way choice: `streamlit==1.64.0` (+ its own
dependencies - `pandas`, `altair`, `pyarrow`, etc., all pulled in transitively, not chosen
individually). `pip check` reports no conflicts; `websockets` was downgraded 17.1→16.1.1 by
Streamlit's own pin, harmless (nothing else in this project pins it).

**Real browser smoke test** (`streamlit run app.py`, Playwright, real store + real Ollama —
not simulated), all three question types:
- **"did X come up"** (F05, "Har NeoHorse nämnts de senaste två veckorna?"): interpreted
  window `2026-09-04..2026-09-17`; correct answer citing NeoHorse-1
  (`https://huggingface.co/papers/2609.08183`, 2026-09-09, arXiv 2026-09-08); complete
  (`done_reason="stop"`). Re-run with a manual override (`2026-09-01..2026-09-17`) confirmed
  the override reaching retrieval, per above.
- **"what's new"/ranking** (F06, "Vad är det senaste inom benchmarking av coding agents?"):
  mode caption correctly read "Läge: sortering efter senaste (rankning, inget datumfilter)";
  real answer correctly named SWE-Bench Pro Verified with a properly rendered Markdown list;
  complete.
- **"has Q progressed"** (F02, "Vad har hänt med GUI agents den senaste månaden?"):
  interpreted window `2026-08-17..2026-09-17`; **real `done_reason="length"`** - the
  incomplete-answer banner fired for real, unplanned, on a genuinely large candidate pool
  (broad topic, month-wide window). The answer itself was correctly cited
  (LLaDA-UI, `2609.13287`) despite being cut off mid-list - confirms the incomplete flag and
  a genuinely truncated real answer aren't mutually exclusive somehow rendering wrong.

**Empty-state check, without touching real production data:** a throwaway, session-only
script (not committed) monkeypatched `vg09.store.STORE_PATH` to a fresh, empty temp
directory *before* importing anything else, then ran only the empty-state branch in a real
Streamlit session on a separate port. Confirmed the exact expected text and that nothing
else in the app renders when the store is empty - the real 1971-chunk production store was
never at risk.

---

### T-026 — Open Phase 2: PLAN updates and the Phase 2 ticket set

**Status:** done
**Size:** S  ·  **Branch:** — (docs-only, see note)

**Goal:** Phase 2 is formally open and its work exists as checkable tickets instead of only
`docs/PLAN.md`'s umbrella checkboxes, so work can start from a backlog rather than from a
chat instruction — same pattern T-016 established for opening Phase 1.

**Why:** `docs/PLAN.md`'s own rule: "when a phase starts, turn its checkboxes into tickets in
`docs/TICKETS.md` using the `ticket-write` skill." My explicit go-ahead to start Phase 2,
with five already-settled design points named to be carried into the tickets rather than
re-decided: date range extraction + a manual UI picker as fallback (risk register); T-008's
context budget (greedy packing by measured token count, `num_predict:2000`); the system
message / user message split (KB-011); detecting and surfacing `done_reason=="length"`; and
citations (title, feed date, link, YouTube `&t=`).

**Acceptance criteria**
- [x] `docs/PLAN.md`'s "Current phase" is set to Phase 2
- [x] `docs/PLAN.md`'s Phase 2 checklist references the tickets that now back each item
- [x] Tickets T-021 through T-025 written for Phase 2's checklist items, each with observable
  acceptance criteria and correct `Depends on` chains, plus T-011 (already existed, moved
  here from Phase 1) confirmed still in scope
- [x] Every already-settled point named in my go-ahead is a concrete acceptance
  criterion in one of T-021/T-022/T-023/T-024, not left as background context that could get
  silently reinterpreted later: date range + UI picker fallback → T-021; greedy token-budget
  packing → T-022; `num_predict:2000` and system/user message split → T-023; `done_reason`
  detection → T-023; citations → T-024
- [x] None of T-011/T-021–T-025 executed — this ticket covers only the planning artifacts

**Out of scope:** doing any of T-011/T-021 through T-025's actual work.

**Depends on:** T-014 (real eval questions T-021 tests against), T-020 (this session's prior
work).
**Notes:** Docs-only, same shape as T-016. `docs/DESIGN.md`'s "Answer generation" section and
`docs/PLAN.md`'s risk register already carried the design decisions this ticket set draws
from — nothing here is a new decision, only turning existing ones into checkable work.

---

### T-027 — Deduplicate retrieval candidates per document; anchor relative windows to the whole dataset, not one source

**Status:** done
**Size:** M  ·  **Branch:** `t/T-027-dedup-and-window-anchor`  ·  **Phase:** 2

**Goal:** two real, measured retrieval defects fixed, both found by re-running T-014's 15
real questions through T-022's retrieval and comparing the top 5 against the facit's expected
sources: (1) a document with many chunks (a long YouTube transcript) can crowd every other
document out of the top of the ranking purely by chunk volume; (2) a relative window
("senaste veckan") anchors to one source's cutoff, silently excluding genuinely newer content
from a faster-moving source.

**Why:** Real measurement this session found both, concretely. (1) F02/F14/F15's real top-5
results were dominated by 2-4 duplicate chunks from a single video each, while the correctly
on-topic expected documents ranked respectably (7th-36th of 60 real candidates) but never
appeared in the top 5 shown to a human or passed on to answer generation. (2) F15's single
most relevant real candidate by similarity (`YTG0rdHPTDE`, rank 6 of 1971) was excluded from
its filtered candidate pool entirely, because the window (2026-09-10..2026-09-16) was anchored
to HF's cutoff (2026-09-16) while that video's real `feed_date` is 2026-09-17 - one day past
HF's cutoff, but not past YouTube's own. Sources ingest at their own pace (T-013's per-source
watermarks already model this); anchoring a shared window to the slowest source is wrong in
general, not just for this one eval question.

**Acceptance criteria**
- [x] `vg09/retrieval.py` deduplicates candidates by `doc_id` after ordering (similarity or
  recency) and before packing - at most 2 chunks survive per document, the highest-ranked
  (earliest in the given order) kept, in both filter and ranking mode → `dedup_by_doc()`,
  `MAX_CHUNKS_PER_DOC=2`; doesn't inspect `ranking` at all, just operates on whatever order
  it's given, so it's identical code for both modes by construction
- [x] The dedup step is real, not just a display-time trick: `pack_to_budget()` never sees
  more than 2 chunks from the same document, so answer generation (T-023) can't be handed 4-5
  chunks from one video while a more relevant document is dropped entirely → wired into
  `retrieve()`: `query_candidates → order_candidates → dedup_by_doc → pack_to_budget`
- [x] A function exists that returns the latest `feed_date` actually present across the whole
  ingested dataset (both sources combined) - not a per-source watermark (deliberately a few
  days conservative, T-015's `REOPEN_DAYS`) and not any single source's cutoff →
  `vg09.store.latest_feed_date()`, a full metadata scan for the max `feed_date_ordinal`; real
  result against the production store: **2026-09-17** (confirmed against
  `data/watermark_youtube.json`'s own `2026-09-17`, and one day past
  `data/watermark_hf.json`'s conservative `2026-09-14`, which is itself two days behind HF's
  real latest content of 2026-09-16 - exactly the gap this ticket's Why section predicted)
- [x] That function, not a hardcoded or single-source date, is what test/measurement code
  passes as `today` when resolving a relative window - real re-run against the frozen dataset
  now anchors at 2026-09-17 (YouTube's real latest content), not 2026-09-16 (HF's cutoff) →
  confirmed in the real re-run below
- [x] The design decision (anchor to the whole dataset's real latest content, not a
  per-source watermark or a single source's cutoff) is recorded in `docs/DECISIONS.md` → D-011
- [x] Re-running T-014's 15 real questions through the fixed pipeline is reported: the new
  headline hit count, and confirmation `YTG0rdHPTDE` is no longer excluded from F15 → **11/14**
  (up from 9/14 strict, or 10/14 with F04 counted correct-by-design, before this ticket).
  F15 flipped MISS → HIT: `YTG0rdHPTDE` now ranks 2nd in its own filtered pool (was excluded
  entirely before). F10's top 5 went from 1 distinct document (the same video 5 times) to 4
  distinct documents. Full per-question breakdown in this ticket's Notes
- [x] Existing `tests/test_retrieval.py` still passes; new tests cover the dedup cap directly
  (not just observed indirectly via a real query) → 62/62 tests pass (8 new: 5 for
  `dedup_by_doc()` directly, 1 updated + 1 new full-pipeline integration test, 2 for
  `vg09.store.latest_feed_date()` in a new `tests/test_store.py`)

**Out of scope:** fixing the real semantic/register gap found in the same investigation
(dense HF abstracts ranking far from broad conversational questions, regardless of language) -
that is a measurement result for Phase 3's evaluation, not a bug; recorded in
`docs/PLAN.md`'s risk register as a known limitation instead. Reconciling `docs/eval-
questions.md`'s already-written facit window dates (F02/F04/F05/F07/F11/F13/F15's windows
were computed against the 2026-09-16 anchor) with the new 2026-09-17 anchor - flagged for me
to decide, not silently rewritten, since that document is T-014's closed, reviewed
output.

**Depends on:** T-022 (the retrieval module this fixes), T-013 (per-source watermarks, the
rejected alternative anchor).
**Notes:** Real re-run against T-014's 15 real questions, both fixes applied together
(`today=2026-09-17`, dedup capped at 2/doc): **11/14** correct (F09 excluded - correct
answer is "no source"; F04 counted correct-by-design per explicit instruction - its real
expected sources predate any "last week"-style window, so finding nothing in-window is the
right outcome, not a miss). Two real, honest results, not both wins:

- **F15 fully fixed** by the window-anchor change: `YTG0rdHPTDE` (rank 6 of 1971 by pure
  similarity) was excluded outright before this ticket (window ended 2026-09-16, video's
  `feed_date` is 2026-09-17); now included and ranks 2nd in its own filtered, deduped pool.
- **F02 still misses**, for a *third*, different reason than F14/F15's semantic gap or the
  crowding this ticket fixes for F10/F15: checked directly (not inferred) - after dedup, the
  5 expected GUI-agent papers rank 7th/11th/18th/19th of 38 deduped candidates, an
  *improvement* over before (were 7th/12th/23rd/24th of 60 undeduped), but still outside the
  top 5, because **five separate YouTube videos** (`1qGH6NwTj3o`, `qYe1GsMRElw`,
  `6XgSpFdD3EU`, `JwTCjarfJYw`, `YTG0rdHPTDE`) each independently rank well for this broad
  query and each get to keep 2 chunks under the cap - capping at 2 reduces crowding from one
  dominant document, but doesn't fix crowding from *several* moderately-relevant ones at
  once. **Left as-is, by my explicit decision, not tuned further:** narrowing the cap or
  the pool's top-k specifically to make F02 pass would be tuning the retrieval against one
  eval question's known answer - exactly what T-014's frozen-before-retrieval-exists
  ordering was designed to prevent. The context budget (13789 tokens, `docs/DESIGN.md`) has
  room for well more than 5 chunks - top-5 is only what this measurement *displays*, not a
  hard ceiling retrieval enforces - so whether 5 vs. more chunks reaching the real model
  actually helps is a real question for Phase 3's evaluation against real generated answers,
  not something to decide by eye against one question's top-5 printout now.
- **F06 unchanged (MISS)** - not a crowding problem: its ranking-sort mode reorders whatever
  the initial 60-candidate similarity pool already contains by date, and the expected source
  (SWE-Bench Pro Verified) was never in that pool to begin with (a pool-composition gap
  dedup can't touch).

---

### T-028 — Reasoning can eat the whole generation cap; citations with more than one number in a bracket aren't resolved

**Status:** done
**Size:** M  ·  **Branch:** `t/T-028-truncation-and-multi-citations` (citations fix,
merged), `t/T-028-raise-num-predict` (this branch)  ·  **Phase:** 2

**Goal:** three real findings from my own manual use of the chat UI (T-025),
against the real question "Vad har hänt med AI-agenter senaste veckan?": (1) measure why a
real answer got cut off (`done_reason=="length"`) rather than guess, and propose - not
build - a fix; (2) `vg09.citations.build_citations()` doesn't resolve a bracket with more
than one number ("[17, 18]"); (3) as a direct consequence of (2), a real answer that cited
three sources in one such bracket only produced one citation.

**Why:** real defects I found in already-shipped Phase 2 code (T-023/T-024), not
hypothetical. (2)/(3) are silent data loss exactly of the kind `CLAUDE.md` and T-024's own
design (`unlinked_references`, never silently dropped) were meant to prevent - a multi-number
bracket doesn't even reach `unlinked_references`, it's dropped from consideration entirely
per number after the first.

**Acceptance criteria**
- [x] The real question is re-run against the real store/Ollama at least twice (sampling is
  stochastic, T-008's own established practice), measuring the real qwen3 token count of the
  reasoning and of the answer separately, and reporting both against the 2000-token
  `NUM_PREDICT` cap - reported in this ticket's Notes, not silently assumed
- [x] Two candidate fixes are written up with their real tradeoff (a higher `NUM_PREDICT`
  against `docs/DESIGN.md`'s chunk budget, vs. a system-prompt instruction asking for shorter
  reasoning) - **neither is implemented**; I pick → **I picked option 1** (raise
  `NUM_PREDICT`). Implemented: `1842` (worst observed reasoning) `+ 400` (room for a full
  answer) `+ 300` (margin - half the observed 612-token spread) `= 2542`, derived from the
  measurement per explicit instruction, not a round number.
  `vg09.retrieval.CHUNK_BUDGET_TOKENS` recomputed to `13261` (was 13803); `docs/DESIGN.md`
  updated throughout (system prompt/reasoning/chunk-budget/top-k sections). Re-verified: the
  exact same real question, re-run 3 more times with the new cap, `done_reason=="stop"` all
  three times (1903/1800/1608 real total reasoning+answer tokens - comfortably under 2542
  where the old 2000 cap had already failed once in 3 tries)
- [x] Confirm the smaller resulting chunk budget (13261, down from 13803) doesn't cost real
  recall - re-run all 15 of T-014's real questions' full pipeline under both the old and new
  budget and compare packed chunk counts, and re-confirm the top-5-vs-facit headline (11/14,
  T-027) using the **same anchor T-027 used** (`today=2026-09-17`, not D-011's later
  eval-pinned `2026-09-16`) → `scripts/t028_verify_chunk_budget_impact.py`, real run against
  the real store/Ollama. Packed chunk count dropped by 1-2 chunks on 5/15 questions (F01
  47→45, F03 45→43, F06 44→42, F07 46→44, F08 46→45 - all broad/unfiltered or ranking
  questions with large candidate pools); the other 10 (all date-filtered, smaller pools) were
  unaffected. **Top-5 - what's actually shown/prioritized - was unchanged by the budget cut
  on all 15 of 15 questions**, confirmed directly (not assumed) by comparing each question's
  top-5 packed-chunk ids against the new budget's packed list. T-027's own two named
  checkpoints reproduced exactly at the same anchor: F15's `YTG0rdHPTDE` still in top-5 (HIT,
  as T-027 found), F06's `2609.08149` still absent from top-5 (MISS, as T-027 found). The
  11/14 headline holds - the budget cut costs no measured recall
- [x] `vg09.citations.build_citations()` resolves every number in a bracket containing more
  than one, comma-separated (`"[17, 18]"`, `"[17,18]"`, `"[17, 18, 19]"`) - each number
  resolved independently against `source_map`, exactly as if it were its own single-number
  bracket
- [x] A bracket where some numbers resolve and others don't (out of range) reports only the
  failing numbers as unlinked (e.g. `"[99]"`), not the whole original bracket text - the
  numbers that did resolve still become real citations
- [x] A non-numeric bracket that happens to contain a comma (the original `[Title,
  YYYY-MM-DD]` shape, if the model ever still produces it) is still reported as one whole
  unlinked reference, unchanged from T-024's existing behavior - the comma-splitting logic
  only applies once every comma-separated piece is confirmed to be a bare number
- [x] Deduplication by `doc_id` (T-024) still applies across numbers within the same bracket,
  not just across separate brackets
- [x] A unit test covers the exact real shape found - a bracket citing three sources, one
  citation missing before the fix - and confirms the fix produces three, not one

**Out of scope:** raising `NUM_PREDICT` or rewriting the system prompt (finding 1) - proposed
only, pending my choice; any other citation format the model might invent beyond
comma-separated numbers in one bracket.

**Depends on:** T-023 (generation cap), T-024 (citation resolution).
**Notes:** Real measurement, three runs against the real store/Ollama, same question
("Vad har hänt med AI-agenter senaste veckan?", live anchor `today=2026-09-17`, 20 chunks
packed, 6082 chunk tokens, `prompt_eval_count=7192` all three runs - only the generated
reasoning/answer varied):

| Run | `done_reason` | reasoning tokens | reasoning % of 2000 cap | answer tokens |
|---|---|---|---|---|
| 1 | `stop` | 1230 | 61.5% | 272 |
| 2 | `length` | **1842** | **92.1%** | 176 (visibly cut off mid-word) |
| 3 | `stop` | 1349 | 67.5% | 322 |

Reasoning alone ranged 61.5-92.1% of the entire 2000-token cap across three real runs on the
*same* question and the *same* retrieved context - only sampling varied. Run 2 reproduces my
real finding directly: reasoning left only 158 tokens of headroom before the answer
even started, and the answer was cut off mid-word. This is a real, repeatable risk, not a one-off

**Candidate fixes, neither built:**
1. **Raise `NUM_PREDICT`.** Costs directly against `docs/DESIGN.md`'s chunk budget
   (currently 13803 = 16000-157-40-2000) - e.g. raising to 3000 (≈1000 tokens of headroom
   over run 2's real 2018-token total) would drop the chunk budget to 12803, a ~7% cut. Given
   T-027's real finding that packed chunk counts (20-45 observed) sit well under the
   worst-case 34-chunk ceiling anyway, this is likely affordable, but not measured here.
2. **Ask for shorter reasoning in the system prompt.** Preserves the full chunk budget, but
   asking a model to constrain its own chain-of-thought is a materially less reliable lever
   than instructing final-answer content (reasoning is a separate generation channel the
   model doesn't visibly self-moderate the same way, per every real reasoning trace seen this
   session running to 1000-1900+ characters regardless of question breadth).

Neither was picked or measured further - that's explicitly my decision, not this
ticket's.

**Follow-up (same session): I picked option 1.** `NUM_PREDICT` raised to 2542
(derivation above, checked into `vg09/answer.py`). Re-verification, real, not simulated:

- **Truncation fixed:** the exact same question, 3 more real runs, `done_reason=="stop"`
  every time (reasoning+answer totals: 1903, 1800, 1608 - all comfortably under 2542, where
  the old 2000 cap had failed once in 3 tries). One of these runs also produced a real
  multi-number citation (`"[7, 11]"`), confirmed to resolve correctly (both numbers pointed
  to the same real document, correctly deduplicated to one citation) - a live confirmation of
  this same ticket's citation fix, not constructed.
- **Chunk-budget sufficiency check: finished in a later session.** First attempt used the
  wrong anchor (`today=2026-09-16`, D-011's later eval-pinned value) and produced a
  misleading 10/14 headline - **not a real regression**, just comparing against the wrong
  baseline (T-027's original 11/14 was measured at `today=2026-09-17`). Caught before
  trusting it. The corrected re-run, `scripts/t028_verify_chunk_budget_impact.py`
  (`today=2026-09-17` throughout, matching T-027's own anchor), found: packed chunk count
  dropped by 1-2 on 5/15 questions (all broad/unfiltered or ranking questions with large
  candidate pools - F01, F03, F06, F07, F08), unaffected on the other 10 (date-filtered,
  smaller pools); **top-5 was unchanged on all 15 of 15 questions**, confirmed directly; and
  T-027's own two named checkpoints (F15 HIT, F06 MISS) reproduced exactly. The 11/14
  headline holds - see this ticket's acceptance criteria above for the full result.

---

### T-011 — Separate Qwen3's reasoning from its answer before display

**Status:** done
**Size:** S  ·  **Branch:** `t/T-011-reasoning-answer-split`  ·  **Phase:** 2

**Goal:** any code that calls a Qwen3 chat model and shows or stores its output keeps the
reasoning (chain-of-thought) and the final answer as two distinct values, never one merged
string.

**Why:** KB-007/D-005 found `think:false` does not suppress reasoning — it merges it into
the response/content field instead of separating it into `thinking`. A clean answer-only
string requires `think:true`, reading `thinking` and the answer as separate fields (D-005's
"Cost" section). Nothing that displays or stores a Qwen3 response should accidentally show
raw chain-of-thought as if it were the answer.

**Acceptance criteria**
- [x] A shared utility takes a raw Ollama chat/generate response called with `think:true`
  and returns `(reasoning, answer)` as two separate strings → `vg09.llm.
  split_reasoning_and_answer()`; verified against a real live `/api/chat` call
  (`qwen3:30b-a3b`, `think=True`) — real response keys `['role', 'content', 'thinking']`,
  split into a 1080-char reasoning string and a clean one-sentence answer
- [x] A unit test covers the response shape KB-007 confirmed (reasoning in `thinking`, not
  merged into content, when `think:true` is used) → `tests/test_llm.py::
  test_think_true_shape_splits_cleanly`
- [x] A unit test covers the failure mode KB-007 found: the utility either detects a merged
  `think:false` response, or the code path is guarded to never call with `think:false` →
  both: `split_reasoning_and_answer()` raises on an empty `thinking` field (KB-007's real,
  observed `think:false` signature), tested directly
  (`test_think_false_shape_is_detected_and_raises`, plus a defensive
  `test_missing_thinking_key_entirely_is_also_detected`); *and* T-023's answer-generation
  call always passes `think=True` explicitly, never `False`
- [x] Phase 2's answer-generation code goes through this utility rather than reading the raw
  response field directly → satisfied by T-023 (implemented immediately after this ticket in
  the same session) — `vg09/answer.py` never reads `response["message"]["content"]` directly
- [x] `docs/DESIGN.md`'s "Interfaces and contracts" section documents this as a project-wide
  contract → new "Reasoning/answer split is a project-wide contract" subsection

**Out of scope:** anything else in the answer-generation pipeline (retrieval, prompt
assembly, citations) — this is only the reasoning/answer split.

**Depends on:** T-006, T-007
**Notes:** Moved from Phase 1 to Phase 2 — no Phase 1 code calls an LLM, so there was no
real caller to build this utility against yet. Phase 2's answer generation is its first
caller; see `docs/PLAN.md`'s Phase 2 checklist.

---

## Done

### T-001 — Commit GOAL/PLAN and point CLAUDE.md at them

**Status:** done
**Size:** S  ·  **Branch:** — (see note)

**Goal:** the repo's docs describe a real project instead of an empty placeholder, and that
state is committed so it survives.

**Why:** `docs/GOAL.md` and `docs/PLAN.md` were filled in but uncommitted, and
`CLAUDE.md`'s "What this is" section still said the repo was undefined. Every later ticket
depends on this being true and in git.

**Acceptance criteria**
- [x] `CLAUDE.md`'s "What this is" section is rewritten to give the one-sentence summary
  from `docs/GOAL.md` and points to `docs/GOAL.md` (goal) and `docs/PLAN.md` (phases)
  instead of saying the repo is empty/undefined
- [x] `CLAUDE.md` no longer contains the placeholder line "VG-09 is an empty repository —
  no code, README or stated goal exists yet"
- [x] `git log` shows one commit, message `T-001: ...`, containing `CLAUDE.md`,
  `docs/GOAL.md`, `docs/PLAN.md`, and `docs/TICKETS.md` (with this ticket set) — commit
  `56a9f09`
- [x] `git status` is clean after the commit
- [x] The commit message carries a `T-001` prefix so the pre-commit hook accepted it

**Out of scope:** `docs/DESIGN.md`, the "Stack" and "Hard rules" sections of `CLAUDE.md` —
those stay placeholders until Phase 0 produces real architecture decisions.

**Depends on:** —
**Notes:** Committed directly to `master` as the repo's root commit rather than on
`t/T-001-bootstrap-docs` — there was no prior commit to branch from, so the branch
convention starts properly with T-002. The root commit also swept in the rest of the
harness scaffolding (`.claude/`, `docs/DESIGN.md`, `docs/DECISIONS.md`, `docs/HANDOFF.md`,
`docs/kb/INDEX.md`, `docs/sessions/README.md`, `docs/skill-template.md`), all of it
untracked placeholder content with nothing to review — not scope creep, just what "first
commit of a new repo" means.

---

### T-002 — YouTube captions feasibility test

**Status:** done
**Size:** M  ·  **Branch:** `t/T-002-youtube-captions`

**Goal:** know, with evidence from this machine, whether captions can be fetched for the
chosen YouTube channels — the input the transcript-source decision rests on.

**Why:** `docs/PLAN.md` Phase 0 exit criteria requires the transcript source decided
(captions vs. title+description) before Phase 1 ingest is built; `docs/GOAL.md` non-goals
gate Whisper on this test failing.

**Acceptance criteria**
- [x] A script fetches captions for the latest videos of 3–5 chosen channels (at least 3
  videos attempted per channel) → `scripts/t002_youtube_captions.py`, run against all 4
  channels, 5 videos each (20 total)
- [x] For each attempt, success/failure and error type (no captions, blocked, other) is
  recorded → per-video result in `data/t002_youtube_captions.json` (gitignored, local only)
- [x] Success rate and error types are written to `docs/kb/` via `kb-entry` →
  [KB-001](kb/KB-001-youtube-caption-availability.md)
- [x] The title + description fallback is confirmed available for at least one video that
  has no captions → **accepted as not fully met, deferred rather than blocking.** 20/20
  videos had captions, so there was no real failure to exercise the fallback against in this
  throwaway script; only that `yt-dlp` returns non-empty `title`/`description` for every
  video was confirmed (KB-001). I accepted D-001 on the strength of the 100%-success
  result. **Deferred to Phase 1:** the fallback path must be verified with a unit test that
  simulates a failed caption fetch inside the real ingest/collector code, not re-tested here.
  That requirement belongs on the Phase 1 collector ticket when it's written.
- [x] `docs/DECISIONS.md` gets a new `D-0NN` entry recording the transcript-source choice,
  with the evidence cited → D-001

**Out of scope:** the real ingest pipeline, chunking, storage — this only establishes
whether the source works.

**Depends on:** T-001
**Notes:** Added `yt-dlp` and `youtube-transcript-api` (see `requirements.txt`) — approved
by me up front. KB-001 additionally records that all 20 captions were
auto-generated (not manual), which risks misspelled proper nouns (model/company/people
names) — the Phase 1 evaluation question set must include at least a couple of questions
built around a proper noun likely to be garbled by auto-captions, to actually measure this
rather than assume it's fine.

---

### T-003 — HF Daily Papers API feasibility test

**Status:** done
**Size:** S  ·  **Branch:** `t/T-003-hf-daily-papers`

**Goal:** know that the HF Daily Papers API gives the fields the project needs, for both
recent and past dates.

**Why:** `docs/PLAN.md` Phase 0 requires confirming which fields exist and that past dates
work, before Phase 1 builds a collector on top of the API.

**Acceptance criteria**
- [x] A script calls `/api/daily_papers?date=` for each of the last 14 days →
  `scripts/t003_hf_daily_papers.py`, 2026-09-02 through 2026-09-15, all HTTP 200
- [x] For each response, presence of title, abstract, publication date and arXiv id is
  confirmed (or the missing ones are named) → all present, but not where assumed: abstract
  is `summary` not `abstract`, arXiv id is `paper.id` not top-level — see
  [KB-002](kb/KB-002-hf-daily-papers-shape.md)
- [x] At least one date more than 10 days in the past returns data, confirming historical
  dates work → 2026-09-02/03/04 all returned entries
- [x] One raw JSON response is saved into the repo → trimmed to 3 entries at
  `docs/kb/samples/daily_papers_2026-09-15_sample.json` (the full day is ~250KB of mostly
  author/avatar metadata, not worth committing in full)
- [x] Findings written to `docs/kb/` via `kb-entry` → KB-002

**Out of scope:** normalizing the response into the Phase 1 document shape — this only
confirms the raw API's behaviour.

**Depends on:** T-001
**Notes:** No new dependency needed — `requests` was already a transitive dependency from
T-002. The 4 weekend dates in the 14-day window returned an empty list (HF Daily Papers
doesn't publish on Sat/Sun) — that's expected, not a bug. The `publishedAt` vs
`paper.submittedOnDailyAt` divergence this ticket surfaced was resolved by me as
**D-002**: "publication date" throughout the project means feed date
(`submittedOnDailyAt` for papers, YouTube upload date for videos); arXiv `publishedAt` is
stored as extra metadata and shown in citations only. `docs/GOAL.md` and `docs/PLAN.md`
Phase 1 updated to match.

---

### T-004 — Local model test on the RTX 4090 (Ollama)

**Status:** done
**Size:** S  ·  **Branch:** `t/T-004-local-model`

**Goal:** know that one large (~30B class, quantized) and one small (~8B) model both run on
this PC via Ollama and can answer a question from pasted context, with speed and VRAM
recorded.

**Why:** `docs/PLAN.md` Phase 0 requires the model pair chosen and recorded before later
phases build retrieval and evaluation around them.

**Acceptance criteria**
- [x] One ~30B-class quantized model and one ~8B model are pulled and run via Ollama on the
  RTX 4090 → `llama3.1:8b` and `qwen2.5:32b`, Ollama 0.34.0
- [x] Each model is given the same test question with pasted context and produces an
  answer → `scripts/t004_local_model.py`, both answered correctly
- [x] Response time and peak VRAM usage are recorded for each model → cold and warm timings
  recorded; VRAM readings come with an honest methodology caveat (see KB-003 — `nvidia-smi`
  measures total GPU memory, not per-process)
- [x] Findings are written to `docs/kb/` via `kb-entry` →
  [KB-003](kb/KB-003-ollama-vram-and-timing.md)
- [x] `docs/DECISIONS.md` gets a new `D-0NN` entry recording the chosen model pair, with the
  evidence cited → D-003

**Out of scope:** the retrieval/answer-generation pipeline (Phase 2) — this only confirms
the models run and answer from pasted context.

**Depends on:** T-001
**Notes:** Ollama was already installed on this machine (0.34.0); confirmed via
`nvidia-smi` that this session is running on the real RTX 4090 from `docs/PLAN.md`'s
hardware section, not a generic sandbox — so the GPU-dependent result is real, not
simulated. Two findings worth carrying into Phase 2 planning (both in KB-003): a cold-start
run made the large model look faster than the small one (it was disk-load overhead, not
inference — always compare warm timings), and `qwen2.5:32b` doesn't fit entirely in 24GB
VRAM at its default context (20% spills to CPU), and the two models evict each other rather
than co-residing.

---

### T-005 — Vector store date-range filtering test

**Status:** done
**Size:** M  ·  **Branch:** `t/T-005-vector-store-date-filter`

**Goal:** know that a candidate vector store can filter by feed-date metadata
combined with similarity search, before committing to it for Phase 1.

**Why:** `docs/GOAL.md`'s claim under test is that date-aware retrieval beats plain
similarity search; that only works if the store can filter by date range at all.
`docs/PLAN.md` Phase 0 requires this confirmed before committing to a store.

**Acceptance criteria**
- [x] A small test collection of documents with varying feed dates (as metadata, per D-002)
  is inserted into a candidate vector store → 8 docs in ChromaDB, `feed_date` spanning
  2026-06-01 to 2026-09-14
- [x] A query demonstrates similarity search restricted to a date range, returning only
  documents inside that range → all 4 filtered results confirmed inside
  [2026-09-01, 2026-09-14]
- [x] A second query without the date filter is run against the same data to confirm the
  filtered and unfiltered results differ as expected → confirmed, filtered set is a strict
  subset dropping the June/August documents
- [x] Findings are written to `docs/kb/` via `kb-entry` →
  [KB-004](kb/KB-004-chromadb-date-filtering.md)
- [x] `docs/DECISIONS.md` gets a new `D-0NN` entry recording the chosen vector store, with
  the evidence cited → D-004

**Out of scope:** the production schema for Phase 1 storage — this is a throwaway test
collection.

**Depends on:** T-001
**Notes:** Candidate (ChromaDB) chosen with me before installing, per `CLAUDE.md`
"In-loop" — asked, got ChromaDB over LanceDB/sqlite-vec, then installed. KB-004 flags a
real cost worth remembering: Chroma's default embedding model isn't bundled, it's an
~80MB silent download on first use to a user-level cache outside the project — needs a
README mention for the "fresh clone reaches a first answer" success criterion.

---

### T-006 — Needle test and same-family model pair + embedding model re-selection

**Status:** done
**Size:** M  ·  **Branch:** `t/T-006-model-pair-revision`

**Goal:** know Ollama's real context-window behavior (num_ctx, silent truncation), and
replace T-004's model pair with a same-family chat pair plus a deliberately chosen
embedding model, all verified to share the RTX 4090's 24GB VRAM without evicting each
other.

**Why:** T-004 paired `llama3.1:8b` with `qwen2.5:32b` — different families, which
confounds size with family in the planned large-vs-small evaluation (`docs/GOAL.md`).
KB-003 also showed `qwen2.5:32b` spills 20% onto CPU at its default context. KB-004 flagged
that ChromaDB's default embedding model was accepted silently, not chosen — and it shares
the same GPU as the chat models, so it has to be verified alongside them, not assumed to
just fit. Bundled as one ticket rather than several because the needle test's num_ctx
finding is a direct input to the chat-pair check (16k context), and the embedding model's
VRAM footprint is a direct input to whether the chat pair actually leaves room for it — not
independent concerns.

**Acceptance criteria**
- [x] A needle-in-haystack test (~12k tokens of filler with one unique fact planted at the
  very start, then a question requiring that fact back) is run against at least one
  currently-pulled model. `docs/kb/` gets a `kb-entry` documenting what `num_ctx` Ollama
  actually used for that request, how `num_ctx` is set, and whether content beyond
  `num_ctx` is silently truncated or surfaced as an error/warning → `llama3.1:8b`,
  [KB-005](kb/KB-005-ollama-num-ctx-silent-truncation.md): default is 32768, undersized
  `num_ctx` silently drops the front of the prompt, no error
- [x] ChromaDB's default embedding model is checked for its real max sequence length and
  whether text beyond that length is silently truncated → 256 tokens,
  [KB-006](kb/KB-006-chroma-default-embedder-256-token-limit.md): silently truncated,
  confirmed via source reading and two empirical tests (identical embeddings for a
  differing tail; `collection.add()` accepts an overlong doc with no error)
- [x] Before downloading anything: candidate same-family chat pairs AND a candidate
  multilingual embedding model presented to me for approval → asked via
  `AskUserQuestion`; I chose `qwen3:30b-a3b` + `qwen3:8b` over Gemma3 27b+4b, with
  `bge-m3` as the only real multilingual embedding candidate found in Ollama's library
- [x] Once approved: chat pair pulled, large model at explicit `num_ctx=16000` shows 100%
  GPU via `ollama ps`, confirmed by `nvidia-smi`; embedding model pulled and tested with a
  Swedish question against English text → all confirmed,
  [KB-007](kb/KB-007-qwen3-bge-m3-stack.md): correct top match, cosine 0.6810 vs next-best
  0.3821
- [x] With the large chat model and the embedding model **both** loaded, `ollama ps`
  confirms both resident simultaneously without evicting each other, real VRAM headroom
  recorded → both 100% GPU, `nvidia-smi` 22100-22118 MiB / 24564 MiB, ~2.4GB headroom,
  stable before and after a real generation call
- [x] If no same-family chat pair meets the GPU bar, the fallback is tried → **not
  needed**, `qwen3` cleared the bar on the first attempt; per my explicit
  condition, this would have required stopping to report before falling back, not an
  automatic switch
- [x] `docs/DECISIONS.md` gets a new decision recording the full stack, `D-003` marked
  superseded → **D-005** (as anticipated — D-004 was ChromaDB from T-005), `D-003` marked
  `Superseded by D-005`

**Out of scope:** re-running the actual large-vs-small evaluation (Phase 2) — this only
re-establishes the stack and its context-window/VRAM behaviour.

**Depends on:** T-004, T-005
**Notes:** I added three conditions when approving the chat pair: (1) stop and report
rather than auto-falling-back if the VRAM bar wasn't met with the embedding model also
loaded — not triggered, bar was met; (2) test `think:false` and note the timing
difference — done, KB-007 also found `think:false` doesn't suppress reasoning, it just
merges it into `response`; (3) frame D-005 by VRAM footprint (~6GB vs ~20GB), not
large/small, since `qwen3:30b-a3b` (MoE) has fewer active parameters per token than the
dense `qwen3:8b` — done. `docs/PLAN.md`'s "Local model" Phase 0 checkbox re-ticked now that
this is done.

---

### T-007 — Verify KB-007's think claim, write CLAUDE.md hard rules, grill-me Phase 0

**Status:** done
**Size:** M  ·  **Branch:** `t/T-007-phase0-checkpoint`

**Goal:** close the Phase 0 checkpoint's three loose ends — confirm KB-007's `think:false`
finding wasn't an artifact of the wrong endpoint, turn Phase 0's findings into enforceable
project rules, and get an adversarial pass on Phase 0 as a whole before Phase 1 starts.

**Why:** KB-007's `think:false` test used `/api/generate`; Ollama's `think` parameter may
behave differently on `/api/chat`, so the finding needs re-checking via the correct
endpoint before it's trusted. `CLAUDE.md`'s "Hard rules" and "Stack" sections are still
placeholders even though Phase 0 now has concrete findings (KB-005, KB-006) and decisions
(D-001–D-005) to derive them from. `docs/PLAN.md` requires a `grill-me` pass at every
checkpoint before declaring a phase complete, and that hasn't been run on Phase 0 as a
whole yet — only on individual tickets as they closed.

**Acceptance criteria**
- [x] The exact JSON request body sent in KB-007's `think:false` test is quoted → confirmed
  `think` was already top-level, not nested under `options`:
  `{"model": "qwen3:30b-a3b", "prompt": "...", "stream": false, "think": false, "options": {"num_ctx": 16000}}`
- [x] The same comparison re-run against `/api/chat` → `scripts/t007_verify_think_chat.py`,
  identical shape of result: `think:false` leaves `thinking` empty but the reasoning
  narrative appears inside `message.content` anyway
- [x] Finding recorded → KB-007 held up on the second endpoint too (not superseded);
  updated in place with the `/api/chat` confirmation, since the claim itself wasn't wrong,
  just under-evidenced on one endpoint. Separately, while checking this, found and
  **corrected** a real error in KB-007's own "Confidence and limits": it speculated VRAM
  headroom might shrink under a longer conversation because "the KV cache grows with
  actual usage" — verified directly that this is false (`nvidia-smi`: 21410 MiB at a
  trivial prompt vs 21431 MiB at an 8002-token prompt, same `num_ctx=16000` — no meaningful
  growth). Ollama pre-allocates the KV cache for the full `num_ctx` at load
- [x] `CLAUDE.md`'s "Hard rules" filled in with the three rules (num_ctx always explicit,
  every call compares `prompt_eval_count` to `num_ctx`, embeddings always `bge-m3` never
  Chroma's default)
- [x] `CLAUDE.md`'s "Stack" section updated with D-001, D-002, D-004, D-005
- [x] `grill-me` (design-decision mode) run on Phase 0 as a whole. Findings:
  - **Serious, fixed:** KB-007's VRAM-growth speculation was wrong — corrected above with
    real evidence, not just reworded
  - **Serious, deferred (not silently dropped):** the real risk hiding behind the VRAM
    question is token budget, not VRAM — nobody has estimated whether a real RAG prompt
    (system + retrieved chunks + history + question) stays under `num_ctx=16000`, and
    KB-005 already proved silent front-truncation is real. Added to `docs/PLAN.md`'s risk
    register with a concrete mitigation (estimate token counts before finalizing Phase 1
    chunk size / retrieval top-k)
  - **Minor, reported not fixed:** D-002's "feed date" label covers two structurally
    different real-world events (HF's curatorial feed-inclusion date vs. YouTube's actual
    upload date) — not wrong, but worth remembering when designing citations, so the label
    doesn't imply more uniformity than the underlying sources actually have

**Out of scope:** any Phase 1 work.

**Depends on:** T-002, T-003, T-004, T-005, T-006
**Notes:** Bundled three different kinds of work into one ticket per my explicit
instruction. The most valuable output wasn't the planned verification (KB-007's claim held
up) — it was the review process surfacing and fixing a real error in KB-007's own
speculative caveat, and identifying a Serious token-budget risk for Phase 1 that nothing
upstream had flagged. Phase 0 is now genuinely complete; Phase 1 has not been started.

---

### T-009 — HF + YouTube collectors → normalized document shape

**Status:** done
**Size:** M  ·  **Branch:** `t/T-009-collectors`

**Goal:** the HF Daily Papers and YouTube collectors both produce documents in one shared
shape (source, url, title, feed date, text — plus arXiv `publishedAt` as extra metadata for
papers), so downstream chunking and storage never need to know which source a document came
from.

**Why:** `docs/PLAN.md` Phase 1's first checklist item. D-001 (transcript source) and D-002
(feed date semantics) are decided but not yet real code.

**Acceptance criteria**
- [x] A shared document type (source, url, title, feed_date, text, optional
  arxiv_published_at) is defined in code → `vg09/document.py`'s `Document` dataclass
- [x] The HF collector produces documents in this shape, using `paper.submittedOnDailyAt` as
  `feed_date` (D-002) and `paper.summary` as `text` (KB-002's field-name correction, not
  `abstract`) → `vg09/hf_papers.py`, confirmed against a live 2026-09-16 response (20 papers,
  sample `2609.06986` written with every field populated)
- [x] The YouTube collector produces documents in this shape, using the video's upload date
  as `feed_date`, captions as `text` when available, falling back to title+description per
  D-001 → `vg09/youtube.py`; the fallback path is the one actually exercised this run (see
  Notes)
- [x] Running each collector against real data produces at least one document with every
  required field populated — no field silently empty when the source data has it →
  `scripts/t009_run_collectors.py`, both collectors, zero missing fields
- [x] Every normalized document a collector produces is written to `data/raw/` → confirmed:
  `data/raw/hf/2026-09-16/2609.06986.json`,
  `data/raw/youtube/2026-09-15/9RtywbN--QE.json`, etc.

**Out of scope:** chunking, embedding, storage (T-012); the fallback unit test (T-010);
catch-up logic (T-013).

**Depends on:** T-001, T-002, T-003
**Notes:** `data/raw/` is the durable normalized-document store — T-012 reads from it rather
than calling collectors directly, and T-013's catch-up runs append to it. T-015's backfill
uses this same collector code, so its output lands here too.

Real finding, not a simulated one: the first run against YouTube crashed with `IpBlocked` —
the same machine that got 20/20 caption successes in T-002 (2026-09-15) was fully blocked
one day later, on 2 requests. The original code only caught 3 of `CouldNotRetrieveTranscript`'s
many subclasses (`TranscriptsDisabled`, `NoTranscriptFound`, `VideoUnavailable`), so it
crashed instead of falling back — fixed to catch the shared parent class, matching D-001's
actual intent ("captions unavailable", not an enumerated list of reasons). Re-run then
triggered the D-001 fallback for real on both videos, producing valid documents. Recorded as
KB-008, which also sharpens T-015's stop-on-block criterion — this is a real risk, not a
hypothetical one. Grill-me pass (inline) found one Serious issue (the fallback discarded
*why* captions failed, which T-015 will need) — fixed by logging the exception type at the
point of fallback rather than swallowing it. The caption-success code path itself
(`FetchedTranscript`'s iteration — verified against the installed library's source, not
guessed) was not empirically exercised this session, since every attempt hit the IP block;
only the fallback path got real execution.

---

### T-010 — Fallback unit test: distinguish missing captions from being blocked

**Status:** done
**Size:** M  ·  **Branch:** `t/T-010-caption-fallback-test`

**Goal:** the YouTube collector treats a per-video "captions missing" failure and an
IP-level "blocked" failure (KB-008) as two different outcomes — missing falls back to
title+description as a final document; blocked writes nothing final, marks the video
pending, and aborts the run — each covered by a mocked unit test, with no live network call.

**Why:** T-002's acceptance criteria accepted the fallback as unverified; T-009 then hit a
real `IpBlocked` failure (KB-008) and, because the code didn't distinguish it from an
ordinary missing-captions case, nearly wrote it as a normal fallback document — which would
have silently produced a full backfill of weak documents in T-015 with no signal that
captions had stopped working. The two failure modes need different handling, not the same
fallback.

**Acceptance criteria**
- [x] The YouTube collector distinguishes two cases: captions missing
  (`TranscriptsDisabled`, `NoTranscriptFound`, and similar non-`RequestBlocked` failures)
  falls back to title+description and writes a final document; blocked (`RequestBlocked`,
  `IpBlocked`) writes no final document, writes a pending marker for the video instead, and
  aborts the run rather than continuing to the next video → `vg09/youtube.py`'s `normalize()`
  catches `RequestBlocked` before the broader `CouldNotRetrieveTranscript`
- [x] `Document` gains `text_source` (`"captions"` | `"title_description"`) and
  `fallback_reason` (the exception class name, or `None` when `text_source` is `"captions"`)
  → `vg09/document.py`
- [x] A unit test forces a missing-captions exception and asserts a final document is
  written with `text_source="title_description"` and the right `fallback_reason` →
  `tests/test_youtube.py::test_missing_captions_falls_back_to_title_description`
- [x] A unit test forces a `RequestBlocked`/`IpBlocked` exception and asserts: no final
  document is written, a pending marker is written for that video, and the collector raises
  rather than silently continuing →
  `test_blocked_writes_no_final_document_marks_pending_and_raises`
- [x] A unit test forces the caption-success path with a mocked `FetchedTranscript` (built
  from the library's real dataclasses) and asserts `text_source="captions"`,
  `fallback_reason=None`, and the joined transcript text →
  `test_captions_available_uses_the_real_transcript_shape`
- [x] All tests run with no live YouTube call (mocked `YouTubeTranscriptApi` and, for the
  `collect_channel` test, mocked `list_videos`) → `.venv/Scripts/python.exe -m unittest
  discover -s tests -v`, 4 tests, all pass, 0.010s
- [x] The two YouTube documents T-009 wrote during the actual `IpBlocked` run
  are converted to pending markers (`*.pending.json`, `reason="IpBlocked"`) via a local
  script against the already-fetched data — no re-fetch, no YouTube call
- [x] D-001 is updated via a new decision entry recording the missing-vs-blocked
  distinction, superseding D-001 → **D-006**, `D-001` marked `Superseded by D-006`

**Out of scope:** re-testing caption availability against real channels (done, KB-001);
Whisper (parked, `docs/GOAL.md`); actually retrying pending videos later (T-015's job).

**Depends on:** T-009
**Notes:** No live YouTube calls (transcript or yt-dlp) made for this ticket, per explicit
instruction — every test is mocked, and the `data/raw/` cleanup was a local file operation
on already-fetched data. Framework: stdlib `unittest`/`unittest.mock`, not `pytest` — no
test framework had been chosen for the project yet, and adding one is a dependency decision
that wasn't asked for here; `dev-environment` skill updated with the real test command.

Grill-me (inline) found one additional Serious issue beyond the three requested tests: a
video blocked in one run and successfully fetched in a later run would leave a stale
`*.pending.json` marker alongside the new final document, since nothing cleared it — a
future retry consumer (T-015) would keep re-treating a resolved video as pending. Fixed with
`vg09.document.clear_pending()`, called from `collect_channel` after every successful final
write, and covered by a fourth test
(`CollectChannelTests::test_a_later_success_clears_an_earlier_pending_marker`).

---

### T-008 — Context budget for the RAG prompt in docs/DESIGN.md

**Status:** done
**Size:** S  ·  **Branch:** `t/T-008-context-budget`

**Goal:** know, in measured tokens, how much of `num_ctx=16000` remains for retrieved
chunks once the system prompt, the question, and a reasoning+answer reservation are
accounted for — so chunk size and top-k get chosen against a real number, not a guess.

**Why:** `docs/PLAN.md`'s risk register (added at T-007's `grill-me`, Phase 0 checkpoint)
flags that nobody has estimated whether a real RAG prompt (system + retrieved chunks +
question) stays under `num_ctx=16000` — and KB-005 already proved an undersized `num_ctx`
silently drops the **front** of the prompt with no error. D-005's "Cost" section adds that
`qwen3:30b-a3b`'s reasoning mode consumes real tokens of its own that must be budgeted for,
not assumed away.

**Acceptance criteria**
- [x] `docs/DESIGN.md` gets a new "Context budget" section giving explicit token counts for:
  system prompt, a representative question, and a reasoning+answer reservation → § Context
  budget (RAG prompt, `num_ctx=16000`): system prompt 171 tokens, question 40 tokens
  reserved, reasoning+answer 2000 tokens reserved
- [x] The reasoning+answer reservation is based on a measured sample (`prompt_eval_count`
  and `eval_count` from a real `qwen3:30b-a3b` call with `think:true`, per D-005/KB-007),
  not an estimate → 3 real questions run twice each (6 samples) against real HF abstracts as
  context, `eval_count` ranged 515-1150, `num_predict:2000` set as the actual generation
  ceiling
- [x] The remaining budget for retrieved chunks is expressed both as a token count and as a
  resulting max top-k at an assumed chunk size → 13789 tokens remaining; 400-qwen3-token
  chunk cap (measured against all 20 real abstracts, max observed 363); max top-k = 34
- [x] The section states what happens if the budget is exceeded (cites KB-005) and how
  retrieved chunks should be ordered in the prompt so the least recoverable content isn't
  first to be dropped → § "What happens if retrieved chunks don't fit": greedy-pack by real
  measured token count, chunks-least-relevant-first/system+question-last ordering, drop a
  single oversized chunk rather than send an overflowing prompt, real per-call
  `prompt_eval_count` vs `num_ctx` check as backstop
- [x] `docs/PLAN.md`'s risk register row on this topic is updated to point at this section
  as the resolving evidence → updated, likelihood downgraded Medium → Low with the residual
  YouTube-transcript caveat named explicitly

**Out of scope:** implementing chunking/retrieval code (T-012); the real evaluation
(Phase 3).

**Depends on:** T-006, T-007
**Notes:** Two tokenizers measured, not assumed equal, per explicit instruction: qwen3's
(via `/api/generate`, `num_predict:1`, reading `prompt_eval_count`) for the real `num_ctx`
budget, and bge-m3's (via `/api/embed`) for the embedding-time chunk-size ceiling — bge-m3
tokenizes the same real text to ~15-20% more tokens than qwen3 at median/max, confirming
they aren't interchangeable. All measurements against real HF Daily Papers abstracts already
in `data/raw/` (T-009's verification run) — no synthetic filler, no YouTube calls (none were
needed for this ticket). Caveat carried into the risk register: the 400-token chunk cap is
sized from HF abstracts only; no real YouTube transcript text exists yet (KB-008 — captions
still blocked as of T-010) to confirm chunking holds once T-015 backfills real transcripts.

Grill-me (inline) on the measurement script itself found two real violations of `CLAUDE.md`'s
own hard rules before this was reported done: the `/api/embed` call never set `num_ctx`
explicitly, and nothing compared `prompt_eval_count` against `num_ctx` to warn on
truncation risk. Both fixed (`EMBED_NUM_CTX=8192` set explicitly, a
`_warn_if_truncation_risk()` check added to every counting/generation call) and the full
measurement re-run to confirm the numbers held (they did, unchanged for tokenizer counts;
`eval_count` varied run-to-run as expected from stochastic sampling — reported as a range
from two runs, not a single sample). Also recorded **KB-009**: Ollama's `num_predict:0` does
not mean "generate nothing" (produced 485 tokens on a 9-word prompt) — `num_predict:1` is
the correct minimal-cost call for a tokenizer-only measurement.

---

### T-016 — Open Phase 1: PLAN/GOAL updates and the Phase 1 ticket set

**Status:** done
**Size:** S  ·  **Branch:** — (docs-only, see note)

**Goal:** Phase 1 is formally open and its work exists as checkable tickets instead of only
as `docs/PLAN.md`'s umbrella checkboxes, so work can start from a backlog rather than from a
chat instruction.

**Why:** `docs/PLAN.md` requires turning a phase's checkboxes into tickets via `ticket-write`
when the phase starts; T-007's handoff named this as the next session's first action.
`docs/GOAL.md` also needed conversation history recorded as an explicit non-goal/parked item
before Phase 1 scope could be considered settled, since it bears on the context-budget work
in T-008.

**Acceptance criteria**
- [x] `docs/PLAN.md`'s "Current phase" is set to Phase 1
- [x] `docs/GOAL.md` gets conversation history added under Non-goals and Parked
- [x] Tickets T-008 through T-015 written for Phase 1's checklist items, each with
  observable acceptance criteria and correct `Depends on` chains
- [x] T-011 (separate Qwen3's reasoning from its answer) written, then on my review moved
  to Phase 2 — no Phase 1 code calls an LLM, so Phase 1 had no real caller for it;
  `docs/PLAN.md`'s Phase 2 checklist updated to reference it
- [x] T-015 (initial 8-week backfill) added ahead of T-013 on my review, since catch-up
  needs a real starting watermark rather than an assumed one; T-013 and T-014 updated to
  depend on it
- [x] T-014 rewritten on my review to reflect I writing the questions and the
  agent verifying expected sources against the frozen backfilled dataset, rather than the
  agent drafting the questions
- [x] `data/raw/` established as the durable normalized-document contract on my review:
  T-009 and T-015 write there, T-012 reads from there (never re-fetching from YouTube to
  rebuild the database), T-013 appends there, and T-014's frozen dataset is defined as
  `data/raw/` as it stood at T-015's backfill end date
- [x] Run order recorded on my review — T-009 → T-010, T-015 (backfill, own terminal)
  with T-008 in parallel → T-012 → T-013 → T-014 — in both `docs/PLAN.md`'s Phase 1 section
  and T-012's notes
- [x] None of T-008–T-015 executed — this ticket covers only the planning artifacts

**Out of scope:** doing any of T-008 through T-015's actual work.

**Depends on:** T-007
**Notes:** Three-pass ticket-writing: the first pass (T-008–T-014) was revised after my
review into a second set (T-008–T-015, plus T-011 moved to Phase 2), then a third pass added
the `data/raw/` storage contract and run order — all before any of T-008–T-015 was committed
or started, per explicit instruction to hold all commits until review.
