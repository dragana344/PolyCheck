"""
English Levenshtein-based spell hint rule.

IMPORTANT — HONESTY ABOUT WHAT THIS RULE IS:
This is a HEURISTIC approximation, NOT a real spell checker.  It flags tokens
that are exactly 1 edit away from a common English word.  It cannot tell
the difference between a genuine typo ("teh") and an intentional rare word
("zed", "lye", "ode").  False-positive rate grows with shorter words.

Use it as a rough hint layer, not as authoritative grammar feedback.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from analyzer.base_rule import BaseRule
from analyzer.models import DetectedError
from analyzer.utils import levenshtein

_WORDLIST_PATH = Path(__file__).parent / "wordlist.json"


class LevenshteinSpellRule(BaseRule):
    """
    [HEURISTIC] Flag tokens that are 1 Levenshtein edit away from a known
    common English word.  Only considers tokens of 3+ characters to avoid
    noise from short function words.
    """

    name = "LevenshteinSpellCheck"

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
            # Skip tokens that appear capitalised in the raw sentence —
            # they are likely proper nouns, not misspellings.
            if token[0].upper() + token[1:] in sentence:
                continue

            # Pass 1: distance-1 (high confidence).
            suggestion = None
            for ref in self._wordlist:
                if levenshtein(token, ref) == 1:
                    suggestion = ref
                    break

            # Pass 2: distance-2 fallback for longer tokens only.
            # Short words have too many distance-2 neighbours so we restrict
            # this to tokens of 6+ characters to keep false positives low.
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
                        f"[HEURISTIC] '{token}' may be misspelled — "
                        f"did you mean '{suggestion}'?"
                    ),
                ))
        return errors
