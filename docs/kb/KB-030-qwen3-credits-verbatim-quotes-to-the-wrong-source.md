# KB-030 — The model quotes word for word but credits the quote to the wrong source

**Area:** Local model behaviour — citation accuracy
**Status:** verified
**Date:** 2026-10-05  ·  **From:** T-063, T-064 / session 2026-10-05 § 5.1

## Claim
`qwen3:30b-a3b` copies quotes accurately from the retrieved excerpts but often attaches
them to the wrong citation number, either another video in the same answer or another
excerpt of the same video. It also quotes loosely ("a personal agent" for "the personal
agent"), so an exact-match check rejects correct quotes.

## Evidence
- T-063's browser run: the answer said video `lnB4Zckx_34` contained "the identical
  statement" ("I've been working in Claude Code and Codex for months…"). That video never
  mentions Claude Code; the quote is in another source of the same answer.
- T-064 measurement over 5 real questions: one "Quote what they said" answer about Meta's
  Muse credited 4 of 5 quotes to the wrong video, each one word for word (score 1.0) from
  another retrieved video. The other 4 answers credited 7 quotes, none wrong.
- Exact matching flagged 4 of 12 correctly credited quotes. The share of three-word
  sequences found in the source separates them: right source 0.67–0.86, the false claim
  0.00, best unrelated video 0.46. The threshold is 0.6.
- T-063 also saw a correct quote placed under the wrong excerpt number of the right video.

## Consequences
- Quote → source checks must search the whole document, not the cited excerpt (T-063's
  timestamp lookup and T-064's warning both do).
- The warning names the source that does contain the quote, when one of the answer's
  sources does.
- The model is also never told a video's channel, so it guessed "Matt Wolfe, Future Tools"
  as a speaker in the 18-question probe. Not fixed.

## Confidence and limits
About 20 real quotes across 6 answers on one day; the misattribution could not be produced
on demand afterwards. Paraphrased claims are not checked at all. The 0.6 threshold comes
from these few measurements.
