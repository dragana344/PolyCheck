from __future__ import annotations

import re
from typing import List

from analyzer.base_rule import BaseRule
from analyzer.models import DetectedError


class ApostropheRule(BaseRule):
    """
    [HEURISTIC] Flags common English contractions written without an apostrophe
    (e.g. 'dont' instead of 'don't').  The check is case-insensitive and
    uses whole-word matching to avoid false positives inside longer words.
    """

    name = "MissingApostrophe"

    _PATTERN = re.compile(
        r'\b(dont|doesnt|cant|wont|isnt|arent|wasnt|werent|havent|hasnt|'
        r'hadnt|wouldnt|couldnt|shouldnt|mustnt|theyre|youre|hes|shes|'
        r'weve|theyve|ive|youve)\b',
        re.IGNORECASE,
    )

    def check(self, sentence: str, tokens: List[str]) -> List[DetectedError]:
        errors: List[DetectedError] = []
        for match in self._PATTERN.finditer(sentence):
            errors.append(DetectedError(
                sentence=sentence,
                error_type="MissingApostrophe",
                message=(
                    f"[HEURISTIC] '{match.group()}' looks like a contraction "
                    f"missing an apostrophe."
                ),
            ))
        return errors
