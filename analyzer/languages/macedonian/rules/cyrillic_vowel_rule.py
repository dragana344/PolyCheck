from __future__ import annotations

import re
from typing import List

from analyzer.base_rule import BaseRule
from analyzer.models import DetectedError


class CyrillicVowelRule(BaseRule):
    """
    [HEURISTIC] Flags Cyrillic tokens of 3+ characters that contain no
    Macedonian vowel (а, е, и, о, у).  A real Macedonian word almost always
    contains at least one vowel; a vowel-free token is almost certainly a typo
    or garbled input.

    Exception: Macedonian has a small set of valid words where 'р' acts as a
    syllabic consonant (e.g. мрк, крв, крст). These are excluded from flagging.
    """

    name = "CyrillicNoVowel"

    _TOKEN_RE = re.compile(r'[Ѐ-ӿ]{3,}')
    _VOWELS = frozenset('аеиоуАЕИОУ')

    # Valid Macedonian words that contain no standard vowel because 'р' or 'ч'
    # acts as a syllabic consonant.
    _VALID_VOWELLESS = frozenset({
        'прв', 'прст', 'крв', 'врв', 'грб', 'грч', 'смрт', 'црв', 'црн', 'црп',
        'срп', 'трг', 'трн', 'брз', 'брк', 'врз', 'грд', 'грст', 'крст', 'стрв',
        'врт', 'цврст', 'мрк',
    })

    def check(self, sentence: str, tokens: List[str]) -> List[DetectedError]:
        errors: List[DetectedError] = []
        for match in self._TOKEN_RE.finditer(sentence):
            word = match.group()
            if word.lower() in self._VALID_VOWELLESS:
                continue
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
