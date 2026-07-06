r"""
Shared rule: consecutive identical words (case-insensitive).

Uses a regex on the raw sentence rather than the pre-tokenized token list
so that short words (e.g. 'to to', 'на на') which some tokenizers discard
are still detected.

Python's re module with re.UNICODE makes \w match all Unicode word characters,
including Cyrillic, so this rule works correctly for both Latin and Cyrillic
scripts without any subclassing.
"""

from __future__ import annotations

import re
from typing import List

from analyzer.base_rule import BaseRule
from analyzer.models import DetectedError


class RepeatedWordRule(BaseRule):
    """
    [HEURISTIC] Flags any word that appears twice in a row (separated only
    by horizontal whitespace).  Matching is case-insensitive so 'The the'
    and 'Таа таа' are both caught.

    One error is emitted per repeated pair, even if the same word repeats
    more than twice.
    """

    name = "RepeatedWord"

    # \b(\w+)\b – capture one word; [ \t]+ – one or more spaces/tabs;
    # \b\1\b    – the same word again (IGNORECASE makes \1 case-insensitive).
    _PATTERN = re.compile(r"\b(\w+)\b[ \t]+\b\1\b", re.IGNORECASE | re.UNICODE)

    def check(self, sentence: str, tokens: List[str]) -> List[DetectedError]:
        errors: List[DetectedError] = []
        for match in self._PATTERN.finditer(sentence):
            word = match.group(1)
            errors.append(DetectedError(
                sentence=sentence,
                error_type="RepeatedWord",
                message=f"[HEURISTIC] Word '{word}' appears twice consecutively.",
            ))
        return errors
