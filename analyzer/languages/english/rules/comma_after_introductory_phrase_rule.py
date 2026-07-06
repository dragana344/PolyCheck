from __future__ import annotations

import re
from typing import List

from analyzer.base_rule import BaseRule
from analyzer.models import DetectedError

_INTRODUCTORY = (
    'However', 'Therefore', 'Furthermore', 'Moreover', 'Nevertheless',
    'Consequently', 'Additionally', 'Finally', 'Meanwhile', 'Otherwise',
    'Instead', 'Indeed', 'Thus', 'Hence', 'Nonetheless', 'Subsequently',
    'First', 'Second', 'Third', 'Lastly',
)


class CommaAfterIntroductoryPhraseRule(BaseRule):
    """
    [HEURISTIC] Flags sentences that start with a common introductory word
    not followed by a comma (e.g. 'However the dog' should be
    'However, the dog').
    """

    name = "MissingIntroductoryComma"

    _PATTERN = re.compile(
        r'^(' + '|'.join(_INTRODUCTORY) + r')\s+[A-Za-z]',
        re.IGNORECASE,
    )

    def check(self, sentence: str, tokens: List[str]) -> List[DetectedError]:
        match = self._PATTERN.match(sentence)
        if match:
            word = match.group(1)
            return [DetectedError(
                sentence=sentence,
                error_type="MissingIntroductoryComma",
                message=(
                    f"[HEURISTIC] '{word}' at the start of a sentence should "
                    f"be followed by a comma."
                ),
            )]
        return []
