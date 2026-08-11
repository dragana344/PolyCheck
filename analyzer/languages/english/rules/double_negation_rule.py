from __future__ import annotations

import re
from typing import List

from analyzer.base_rule import BaseRule
from analyzer.models import DetectedError


class DoubleNegationRule(BaseRule):
    """
    [HEURISTIC] Flags sentences that contain a negative auxiliary verb or
    'never' alongside a second negative word (no/nobody/nothing/nowhere/
    neither).  This catches the classic double-negative pattern
    ('I don't have no money') without requiring a full parse tree.
    """

    name = "DoubleNegation"

    _NEG_AUX = re.compile(
        r"\b(don't|doesn't|can't|won't|isn't|aren't|wasn't|weren't|"
        r"haven't|hasn't|hadn't|wouldn't|couldn't|shouldn't|never|not)\b",
        re.IGNORECASE,
    )
    _NEG_WORD = re.compile(
        r'\b(no|nobody|nothing|nowhere|neither)\b',
        re.IGNORECASE,
    )

    def check(self, sentence: str, tokens: List[str]) -> List[DetectedError]:
        if self._NEG_AUX.search(sentence) and self._NEG_WORD.search(sentence):
            return [DetectedError(
                sentence=sentence,
                error_type="DoubleNegation",
                message="[HEURISTIC] Possible double negation detected.",
            )]
        return []
