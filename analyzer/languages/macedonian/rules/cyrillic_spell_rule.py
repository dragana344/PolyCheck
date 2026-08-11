"""
Macedonian Levenshtein-based spell hint rule (Cyrillic).

IMPORTANT — HONESTY ABOUT WHAT THIS RULE IS:
This is a HEURISTIC approximation.  Levenshtein distance 1 on Cyrillic tokens
catches simple single-character typos (missed letter, swapped letter,
wrong key on Cyrillic keyboard layout).  It cannot handle:
  - Morphological inflections (Macedonian lacks case declension but has
    definite articles as suffixes, plural forms, verb conjugations).
  - Dialectal spelling variation.
  - Proper nouns that happen to be 1 edit away from a common word.

Label every produced error as [HEURISTIC].
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from analyzer.base_rule import BaseRule
from analyzer.models import DetectedError
from analyzer.utils import levenshtein

_WORDLIST_PATH = Path(__file__).parent / "common_words.json"


class CyrillicSpellRule(BaseRule):
    """
    [HEURISTIC] Flag Cyrillic tokens that are 1 Levenshtein edit away from
    a known common Macedonian word.  Only tokens of 3+ characters are checked.
    """

    name = "CyrillicLevenshteinSpellCheck"

    # Macedonian definite article suffixes (postposed).
    # If stripping one of these gives a stem that is in the wordlist,
    # the token is a valid definite form — not a misspelling.
    _DEFINITE_SUFFIXES = ('от', 'та', 'то', 'те', 'ов', 'ва', 'во', 'ве')

    def __init__(self) -> None:
        with open(_WORDLIST_PATH, encoding="utf-8") as fh:
            self._wordlist: List[str] = json.load(fh)
        self._wordlist_set: frozenset = frozenset(self._wordlist)

    def _is_definite_form(self, token: str) -> bool:
        """Return True if token is a known word with a definite article suffix."""
        for suffix in self._DEFINITE_SUFFIXES:
            if token.endswith(suffix) and len(token) > len(suffix) + 1:
                stem = token[: -len(suffix)]
                if stem in self._wordlist_set:
                    return True
        return False

    def check(self, sentence: str, tokens: List[str]) -> List[DetectedError]:
        errors: List[DetectedError] = []
        for token in tokens:
            if len(token) < 3:
                continue
            if token in self._wordlist_set:
                continue
            # Skip tokens that appear capitalised in the raw sentence —
            # they are likely proper nouns, not misspellings.
            if token[0].upper() + token[1:] in sentence:
                continue
            # Skip valid definite forms (продавницата, книгата, денот…).
            if self._is_definite_form(token):
                continue

            # Pass 1: distance-1 (high confidence).
            suggestion = None
            for ref in self._wordlist:  # list preserves priority order
                if levenshtein(token, ref) == 1:
                    suggestion = ref
                    break

            # Pass 2: distance-2 fallback for longer tokens only.
            if suggestion is None and len(token) >= 7:
                for ref in self._wordlist:
                    if levenshtein(token, ref) == 2:
                        suggestion = ref
                        break

            if suggestion is not None:
                errors.append(DetectedError(
                    sentence=sentence,
                    error_type="PossibleSpelling",
                    message=(
                        f"[HEURISTIC] '{token}' може да е погрешно напишан — "
                        f"дали мислевте '{suggestion}'?"
                    ),
                ))
        return errors
