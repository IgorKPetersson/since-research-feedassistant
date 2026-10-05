# KB-034 — A backtick pair in the model's answer turns the app's citation chips into visible HTML text

**Area:** UI (Streamlit / markdown rendering) — chips inside the model's markdown
**Status:** verified
**Date:** 2026-10-05  ·  **From:** T-072

## Claim
Until T-072, `app.py` inserted the citation chips (`<a class="citation-chip" …>`) into the
model's markdown and let Streamlit's markdown parse the whole thing. Under CommonMark, a
code span opened by a backtick takes everything up to the next backtick as literal text,
including raw HTML. When the model wrote a backtick before some citations and another
after them, those chips were shown as `<a class="citation-chip" href=…>` text in green
code style, while chips outside the pair stayed links.

## Evidence
- My report, 2026-10-05: chips 29–31 of one answer shown as HTML, 25 and 32–34 as
  links, although 25 and 30 pointed to the same video with the same title.
- Not reproduced by 10 real answers or 8 constructed list layouts without backticks.
- Reproduced exactly with one backtick before chip 29 and one after chip 31: in
  markdown-it-py (2 live chips, 2 shown as text) and in Streamlit 1.64 in a real browser
  (screenshot in the session, same green code text as I saw).
- Rare because the model seldom writes backticks around citations; the defect existed
  since T-042 put chips into the markdown.

## Consequences
`render_citation_chips()` now renders the answer itself with markdown-it-py (HTML, links,
images and autolinks off) and puts chips only into text tokens, never code; the result is
one HTML block on one line, so Streamlit's markdown does not re-interpret it. The same
change escapes any HTML the model writes (D-020).

## Confidence and limits
Mechanism verified in both parsers; my exact raw answer was not captured, so it
is the only explanation found that fits every detail, not a replay of that answer.
