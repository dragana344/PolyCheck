from __future__ import annotations

import re
from typing import List, Tuple

from analyzer.base_rule import BaseRule
from analyzer.models import DetectedError


class CommonConfusionRule(BaseRule):
    """
    [HEURISTIC] Flags a hardcoded set of commonly confused word sequences.
    Each entry is a (pattern, wrong_form, suggestion) tuple.
    """

    name = "CommonConfusion"

    _CONFUSIONS: List[Tuple[re.Pattern, str, str]] = [
        (re.compile(r'\bshould\s+of\b', re.IGNORECASE), "should of", "should have"),
        (re.compile(r'\bwould\s+of\b', re.IGNORECASE), "would of", "would have"),
        (re.compile(r'\bcould\s+of\b', re.IGNORECASE), "could of", "could have"),
        (re.compile(r'\bmust\s+of\b', re.IGNORECASE), "must of", "must have"),
        (re.compile(r'\byour\s+welcome\b', re.IGNORECASE), "your welcome", "you're welcome"),
        (re.compile(r'\btheir\s+(is|are|was|were)\b', re.IGNORECASE), "their is/are/was/were", "there"),
    ]

    def check(self, sentence: str, tokens: List[str]) -> List[DetectedError]:
        errors: List[DetectedError] = []
        for pattern, wrong, suggestion in self._CONFUSIONS:
            if pattern.search(sentence):
                errors.append(DetectedError(
                    sentence=sentence,
                    error_type="CommonConfusion",
                    message=(
                        f"[HEURISTIC] '{wrong}' is commonly confused — "
                        f"did you mean '{suggestion}'?"
                    ),
                ))
        return errors
