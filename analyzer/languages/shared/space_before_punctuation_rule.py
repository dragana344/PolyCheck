"""
Shared rule: space immediately before punctuation marks.

Applies to any language that uses Western-style punctuation placement
(comma, period, exclamation mark, question mark, semicolon, colon).
Languages that put spaces before certain marks (e.g. French guillemets)
would need to override this or use a language-specific variant.
"""

from __future__ import annotations

import re
from typing import List

from analyzer.base_rule import BaseRule
from analyzer.models import DetectedError


class SpaceBeforePunctuationRule(BaseRule):
    """
    [HEURISTIC] Flags one or more spaces immediately preceding a
    punctuation character (, . ! ? ; :).

    Each occurrence in the sentence is reported separately so that a
    sentence with multiple spacing errors is fully described.
    """

    name = "SpaceBeforePunctuation"

    # One or more spaces followed by a punctuation character.
    _PATTERN = re.compile(r" +([,\.!?;:])")

    def check(self, sentence: str, tokens: List[str]) -> List[DetectedError]:
        errors: List[DetectedError] = []
        for match in self._PATTERN.finditer(sentence):
            punct = match.group(1)
            errors.append(DetectedError(
                sentence=sentence,
                error_type="SpaceBeforePunctuation",
                message=f"[HEURISTIC] Space before '{punct}' at position {match.start()}.",
            ))
        return errors
