from __future__ import annotations

import re
from typing import List

from analyzer.base_rule import BaseRule
from analyzer.models import DetectedError


class CyrillicVowelRule(BaseRule):
    """
    [HEURISTIC] Flags Cyrillic tokens of 2+ characters that contain no
    Macedonian vowel (а, е, и, о, у).  A real Macedonian word always contains
    at least one vowel; a vowel-free token is almost certainly a typo or
    garbled input.
    """

    name = "CyrillicNoVowel"

    _TOKEN_RE = re.compile(r'[Ѐ-ӿ]{2,}')
    _VOWELS = frozenset('аеиоуАЕИОУ')

    def check(self, sentence: str, tokens: List[str]) -> List[DetectedError]:
        errors: List[DetectedError] = []
        for match in self._TOKEN_RE.finditer(sentence):
            word = match.group()
            if not any(ch in self._VOWELS for ch in word):
                errors.append(DetectedError(
                    sentence=sentence,
                    error_type="CyrillicNoVowel",
                    message=(
                        f"[HEURISTIC] Кирилскиот збор '{word}' не содржи "
                        f"самогласка — можна печатна грешка."
                    ),
                ))
        return errors
