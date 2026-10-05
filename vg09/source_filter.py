"""T-068: a question that names one kind of source searches only that source.

The 2026-10-05 probe run: "What were the most important papers yesterday?" retrieved no
papers at all, even from 400 candidates - the word "papers" was matched as text, and
news videos that talk about new things won. Same rule-based, closed-vocabulary approach
as `vg09.date_range`, English and Swedish.

"video" on its own is not a source word: "video generation" and "text-to-video" are
research topics (eval questions 3 and 7, both answered by papers). Only the plural
"videos", or "a/the/latest video" not followed by a topic word, mean YouTube.
"""

from __future__ import annotations

import re

_PAPER_WORDS = (
    r"papers?|research|arxiv|abstracts?|publications?"
    r"|forskning(?:en)?|artikel(?:n)?|artiklar(?:na)?"
)
_VIDEO_TOPIC_WORDS = (
    r"generation|genereation|generator|generators|model|models|diffusion|editing"
    r"|understanding|synthesis|tokenizer|reasoning|benchmark"
)
_VIDEO_WORDS = (
    r"youtube|youtubers?|channels?|videos"
    r"|(?:a|the|this|that|any|which|latest|recent|last|newest"
    r"|någon|nagon|en|den|denna|vilken|varje|senaste)\s+video(?!\s+(?:" + _VIDEO_TOPIC_WORDS + r")\b)"
    r"|videor(?:na)?|videon|videoklipp(?:en)?|klipp(?:et|en)?|kanal(?:en|er|erna)?"
)


def detect_source(question: str) -> str | None:
    """"hf" when the question names papers, "youtube" when it names videos, None when
    it names both or neither - None searches everything, as before."""
    q = question.lower()
    papers = re.search(r"\b(?:" + _PAPER_WORDS + r")\b", q) is not None
    videos = re.search(r"\b(?:" + _VIDEO_WORDS + r")\b", q) is not None
    if papers == videos:
        return None
    return "hf" if papers else "youtube"
