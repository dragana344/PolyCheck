"""
Shared rule: sentence should begin with an uppercase letter.

Python's str.isupper() and str.islower() are Unicode-aware, so this rule
works for both Latin (A–Z) and Cyrillic (А–Я and Macedonian extensions)
scripts without any language-specific subclassing.

The rule skips non-alphabetic leading characters (digits, quotation marks,
etc.) and checks only the first alphabetic character of the sentence.
"""

from __future__ import annotations

from typing import List

from analyzer.base_rule import BaseRule
from analyzer.models import DetectedError


class SentenceCapitalizationRule(BaseRule):
    """
    [HEURISTIC] Flags sentences whose first alphabetic character is
    lowercase.

    Limitations:
      - Titles, headings, and list items often start with lowercase by
        convention and will be incorrectly flagged.
      - Sentences that begin with a digit are skipped entirely, since the
        first letter after a number is not expected to be capitalised.
    """

    name = "SentenceCapitalization"

    def check(self, sentence: str, tokens: List[str]) -> List[DetectedError]:
        if len(tokens) < 3:
            return []
        stripped = sentence.strip()
        if stripped and stripped[0].isdigit():
            return []
        for ch in stripped:
            if ch.isalpha():
                if ch.islower():
                    return [DetectedError(
                        sentence=sentence,
                        error_type="Capitalization",
                        message=f"[HEURISTIC] Sentence starts with lowercase '{ch}'.",
                    )]
                break
        return []
