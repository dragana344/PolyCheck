from __future__ import annotations

import re
from typing import List

from analyzer.base_rule import BaseRule
from analyzer.models import DetectedError


class ArticleBeforeVowelRule(BaseRule):
    """
    [HEURISTIC] Flags the indefinite article 'a' appearing directly before a
    vowel-starting word (should be 'an').  Note: words with a vowel letter but
    a consonant sound (e.g. 'unique', 'uniform') will be false positives.
    """

    name = "ArticleBeforeVowel"

    _PATTERN = re.compile(r'\ba\s+[aeiouAEIOU]', re.IGNORECASE)

    def check(self, sentence: str, tokens: List[str]) -> List[DetectedError]:
        errors: List[DetectedError] = []
        for match in self._PATTERN.finditer(sentence):
            errors.append(DetectedError(
                sentence=sentence,
                error_type="ArticleBeforeVowel",
                message=(
                    f"[HEURISTIC] '{match.group().strip()}' — use 'an' before a vowel sound."
                ),
            ))
        return errors
