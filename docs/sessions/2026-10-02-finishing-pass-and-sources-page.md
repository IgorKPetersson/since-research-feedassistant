# Session tree · 2026-10-02 · Finishing pass, fresh data, and the Sources page

**Tickets:** T-047, T-048, T-049, T-050, T-051, T-052–T-058 · **Handoff:** docs/HANDOFF.md
§ 2026-10-02 (evening)
**Read this if you want to know:** why retrieval took a minute and what fixed it, why the
accent colour changed, how the Sources page and the background ingest job came about, or
which defects only a real run exposed.

## 1. "Are we done?"  [T-047]
   - 1.1 Status check from HANDOFF, PLAN, TICKETS and git
     · outcome: T-047's branch unmerged, T-039 in `review`, button contrast open, report
       and presentation outstanding
   - 1.2 Merged T-047 to `main` and pushed, as the one mandatory item
   - 1.3 Items 1–4 had been called done while faults were still open
     · outcome: the claim had been made from documents and tests, not from running the
       app. Ran a real question; found data 15 days old and retrieval at 61s. **Process
       lesson:** "done" was reported for things not run that day, and real gaps were
       called small

## 2. Presentation draft  [T-048]
   - 2.1 The deliverable is a live demonstration, not a written report; no draft existed
   - 2.2 `docs/presentation.md` written, numbers traced to repo files
   - 2.3 Demo questions re-chosen after the catch-up moved the date windows (§ 6)
     · outcome: `scripts/t048_verify_demo_questions.py`; draft not yet reviewed

## 3. Retrieval took a minute  [T-049]
   - 3.1 Timed each step with the loaded models recorded: every request cost about 2s
   - 3.2 Changed only the address: `retrieve()` 68.6s → 1.4s, identical result
     · outcome: KB-024 supersedes KB-023. Every wall-clock time recorded before today
       includes the overhead

## 4. Accent colour and contrast  [T-050]
   - 4.1 Two options drawn side by side for me; they chose the darker accent
   - 4.2 Follow-on: citation chips had dark text, which fails on the darker accent
     · outcome: chips now white; a test computes the contrast from the constant

## 5. Enter then Ask  [T-051]
   - 5.1 Found by using the app
     · outcome: field and button made one form. No unit test could have caught it

## 6. Data was 15 days old  [no ticket — an ingest run]
   - 6.1 The app only fetched when told to, not daily
     · outcome: catch-up run (425 papers, 21 videos, 4 via Whisper), store rebuilt

## 7. Sources page: specification  [T-052]
   - 7.1 A clone carries no data but does carry the four hardcoded channels
   - 7.2 Proposal sketched, agreed, written as `docs/DESIGN.md` § Sources page and D-017
   - 7.3 Rejected: a committed config file; topic filtering at ingest; a thread in the app

## 8. Sources: configuration and channel field  [T-053, T-054]
   - 8.1 `vg09/sources.py`; defaults when no file exists, so the terminal flow is unchanged
   - 8.2 Stored-format change (`channel`) approved before building
     · outcome: the four existing channels and their data stay as they are
   - 8.3 Migration assigned all 62 existing videos, 0 unassigned

## 9. Sources: background job  [T-055]
   - 9.1 Separate process with a heartbeat; liveness by heartbeat, not process id
   - 9.2 First real run died on `PermissionError` replacing the status file under a reader
     · outcome: retry on both write and read; KB-025
   - 9.3 A no-op update took 316s, asking YouTube about 50 videos per channel
     · outcome: ask only about videos not on disk, stop at the first too-old one: 12s

## 10. Sources: the page  [T-056, T-058]
   - 10.1 Page built; add, remove and update all exercised in a browser on a test channel
   - 10.2 Questions failed during and after a job with Chroma's "Error finding id"
     · outcome: cached client reset when a job finishes; questions refused during the
       writing stage; job writes only new chunks (45s → 4s); KB-026
   - 10.3 Dead end avoided: building the new store in a second directory and swapping.
     · outcome: not built — renaming a directory the app holds open fails on Windows, and
       the reset plus a short refusal was enough
   - 10.4 First question after a Whisper update hung 120s on Ollama, once
     · outcome: unresolved, KB-027 (provisional)
   - 10.5 Channel limit of five
   - 10.6 Not yet seen in a browser: the first-start flow, the stale-data marker

## 11. README and presentation for Sources  [T-057]
   - 11.1 README rewritten around the Sources page; terminal commands kept as the alternative
   - 11.2 Fresh-clone run through the page: outcome recorded in T-057
