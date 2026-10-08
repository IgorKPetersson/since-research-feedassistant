# KB-014 — real fetched auto-generated captions DO have punctuation and capitalization, contradicting an unverified assumption in `vg09/chunking.py`

**Area:** YouTube ingest — captions
**Status:** verified (5 real documents, 2 channels; supersedes an unverified assumption, not
a prior KB entry - see Consequences)
**Date:** 2026-09-17  ·  **From:** T-018 (found while comparing captions against Whisper's
output, not the ticket's primary question)

## Claim
Real `youtube_transcript_api` auto-generated caption text, as actually fetched and stored by
this project (T-017's real backfill run), consistently includes sentence punctuation
(periods, question marks) and correct capitalization. This directly contradicts
`vg09/chunking.py`'s docstring claim that "auto-generated captions have no punctuation,
so sentence splitting would be unreliable" - a claim attributed there to KB-001, which does
**not** actually say this (KB-001 only discusses proper-noun misspelling risk, never
punctuation). The "no punctuation" premise was never verified against real caption text at
the time T-012 was built (KB-008: captions were `IpBlocked` throughout T-012's session) - it
was a plausible-sounding assumption about auto-captions in general that real data now
contradicts for this project's actual channels.

## Evidence
Checked 5 real documents across 2 channels, all `text_source="captions"`, fetched by
T-017's 2026-09-17 run:

- `S2VJU5DQqlU` (mreflow): `"What if anybody could have the power of Palunteer on their home
  computer? That's exactly what my friend Belaval Sadu created with his God's Eye View
  project..."`
- `nZYJdwM-_nI` (theAIsearch): `"AI never sleeps and this week has been absolutely insane.
  Deepseek releases their latest model and it's an absolute beast..."`
- `9RtywbN--QE` (theAIsearch): `"This is currently the best open- source music generator you
  can use. You can run this with 4 GB of VRAM or less..."`
- `q9tpIc8PVKM` (theAIsearch): `"This is currently the best image model in the world. OpenAI
  just released GPT Image 2.5..."`

All four show periods, question marks and capitalized sentence starts throughout, not just
at isolated spots. Same real data also shows the proper-noun-garbling risk KB-001 *did*
predict, now with concrete examples: **"Palunteer"** for what is almost certainly
**"Palantir"**, **"Open AAI"** for **"OpenAI"**, **"Sunno V6"** for **"Suno V6"**, and an
odd mid-word break, **"open- source"**.

## Consequences
Flagged per the project's rule that reality contradicting reference documentation gets fixed
and flagged, not silently adapted around: `vg09/chunking.py`'s design rationale for
timestamp-based (not sentence-based) YouTube chunking rests partly on a premise that turns
out to be false for this project's real data. This does **not** mean the timestamp-based
chunking approach was wrong - chunking by real per-snippet timestamp is still needed for
accurate `&t=SECONDS` citations regardless of punctuation, and auto-caption snippets still
overlap and fragment mid-sentence (KB-013) in a way that would complicate sentence-based
splitting even with punctuation present. But the *stated reason* in the code comment is
inaccurate and should be corrected the next time `vg09/chunking.py` is touched, and the
proper-noun garbling examples above are ready-made material for T-014's evaluation
questions (which already require at least one question built around a garbled proper noun,
per KB-001/T-002's notes) - no need to wait for a garbled example to turn up later, three
real ones already exist.

Not fixed as part of this ticket - T-018 is a Whisper feasibility test, not a chunking
change; this is reported for me and the next chunking-touching ticket to act on.

## Confidence and limits
5 documents, 2 of the project's 4 channels (`@theAIsearch`, `@mreflow`); `@NateBJones` and
`@ColeMedin` not checked (no real captions fetched from them yet - `@NateBJones` is where
KB-008's block recurred). Not confirmed whether punctuation presence is universal across all
auto-generated YouTube captions or specific to these channels/videos/upload dates - YouTube's
auto-caption punctuation model may have changed over time or vary by video. Worth
re-checking once `@NateBJones`/`@ColeMedin` captions are eventually fetched (whenever their
IP block situation resolves).
