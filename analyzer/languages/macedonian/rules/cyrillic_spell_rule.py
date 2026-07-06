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

    def __init__(self) -> None:
        with open(_WORDLIST_PATH, encoding="utf-8") as fh:
            self._wordlist: List[str] = json.load(fh)

    def check(self, sentence: str, tokens: List[str]) -> List[DetectedError]:
        errors: List[DetectedError] = []
        for token in tokens:
            if len(token) < 3:
                continue
            if token in self._wordlist:
                continue
            for ref in self._wordlist:
                if levenshtein(token, ref) == 1:
                    errors.append(DetectedError(
                        sentence=sentence,
                        error_type="PossibleSpelling",
                        message=(
                            f"[HEURISTIC] '{token}' е на растојание 1 "
                            f"(Levenshtein) од честиот збор '{ref}'"
                        ),
                    ))
                    break
        return errors
