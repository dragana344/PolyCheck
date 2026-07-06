from __future__ import annotations

import re
from typing import List

from analyzer.base_rule import BaseRule
from analyzer.models import DetectedError


class ConsecutivePunctuationRule(BaseRule):
    """
    [HEURISTIC] Flags two or more consecutive punctuation characters.
    A valid ellipsis (...) is explicitly excluded.
    """

    name = "ConsecutivePunctuation"

    _PATTERN = re.compile(r'[!?.,;:]{2,}')

    def check(self, sentence: str, tokens: List[str]) -> List[DetectedError]:
        errors: List[DetectedError] = []
        for match in self._PATTERN.finditer(sentence):
            if match.group() == '...':
                continue
            errors.append(DetectedError(
                sentence=sentence,
                error_type="ConsecutivePunctuation",
                message=(
                    f"[HEURISTIC] Consecutive punctuation '{match.group()}' detected."
                ),
            ))
        return errors
