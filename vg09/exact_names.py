"""T-095: names in a question that should be looked up as written, not only by meaning.

Semantic search finds a paper about "NeoHorse" because the abstract is about it, but it
can't say that "AutoDev" appears nowhere: absence from the top results is not absence
from the sources. So names are also matched as text, case-insensitively, inside the same
date and source filter (Chroma's `where_document` `$regex`). That gives two things:

- candidates that contain the name go to the front of retrieval, when the name is
  distinctive (found in at most `DISTINCTIVE_MAX_DOCS` documents in the searched scope);
- a count of documents containing each name, which the app reports as fact, so "not
  found" means "no source in this scope contains the text", not a guess.

What counts as a name: text in quotes, a word with a capital letter after its first
character (NeoHorse, OpenAI), a word in capitals of three or more letters (LEGO, GUI), a
word mixing letters and digits (GPT-6, Qwen3), and a capitalised word that doesn't start
the sentence (Palantir). No vocabulary of known names is used.
"""

from __future__ import annotations

import re

DISTINCTIVE_MAX_DOCS = 25
_QUOTED = re.compile(r"[\"“”'‘’]([^\"“”'‘’]{2,40})[\"“”'‘’]")
_WORD = re.compile(r"[A-Za-zÅÄÖåäö0-9][A-Za-zÅÄÖåäö0-9.+-]*[A-Za-zÅÄÖåäö0-9+]|[A-Za-z]")


def exact_names(question: str) -> list[str]:
    """Names in `question`, in order, without duplicates (case-insensitive)."""
    found: list[str] = [m.group(1).strip() for m in _QUOTED.finditer(question)]
    unquoted = _QUOTED.sub(" ", question)
    sentence_start = True
    for m in _WORD.finditer(unquoted):
        word = m.group(0)
        before = unquoted[:m.start()].rstrip()
        sentence_start = not before or before[-1] in ".!?:"
        if _is_name(word, sentence_start):
            found.append(word)
    seen, names = set(), []
    for name in found:
        if name.lower() not in seen:
            seen.add(name.lower())
            names.append(name)
    return names


def _is_name(word: str, sentence_start: bool) -> bool:
    """Each hyphen-separated part is judged on its own, so a compound such as
    "AI-verktyg" is not a name while "LEGO-RL" and "GPT-6" are."""
    if len(word) < 3 or not any(c.isalpha() for c in word):
        return False
    parts = [p for p in word.split("-") if p]
    for part in parts:
        letters = [c for c in part if c.isalpha()]
        if any(c.isupper() for c in part[1:]) and any(c.islower() for c in part):
            return True  # NeoHorse, OpenAI, AutoDev
        if len(letters) >= 3 and all(c.isupper() for c in letters):
            return True  # LEGO, GUI
        if letters and any(c.isdigit() for c in part):
            return True  # Qwen3
    if len(parts) == 2 and parts[1].isdigit() and parts[0][:1].isupper():
        return True  # GPT-6
    # Palantir: a capitalised word in the middle of a sentence, not part of a compound.
    return len(parts) == 1 and word[0].isupper() and word[1:].islower() and not sentence_start


def name_regex(name: str) -> str:
    """The case-insensitive whole-word pattern for Chroma's `$regex`."""
    return r"(?i)(?:^|\W)" + re.escape(name) + r"(?:\W|$)"
