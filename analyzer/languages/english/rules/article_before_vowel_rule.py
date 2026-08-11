from __future__ import annotations

import re
from typing import List

from analyzer.base_rule import BaseRule
from analyzer.models import DetectedError


class ArticleBeforeVowelRule(BaseRule):
    """
    [HEURISTIC] Flags the indefinite article 'a' appearing directly before a
    vowel-starting word (should be 'an').

    Words that begin with a vowel letter but a consonant sound (e.g. 'uniform',
    'university') are whitelisted to avoid false positives.
    """

    name = "ArticleBeforeVowel"

    # Matches 'a' followed by a vowel-starting word; captures the following word
    # so we can check it against the consonant-sound whitelist.
    _PATTERN = re.compile(r'\ba\s+([aeiou]\w*)', re.IGNORECASE)

    # Words that start with a vowel letter but are pronounced with a consonant
    # sound — 'a uniform' and 'a university' are correct, not errors.
    _CONSONANT_SOUND = frozenset({
        "uniform", "uniforms", "uniformly",
        "university", "universities",
        "unique", "uniquely", "uniqueness",
        "union", "unions",
        "unit", "units",
        "united",
        "universe", "universal", "universally",
        "user", "users",
        "use", "used", "using", "useful", "useless", "usually", "usual",
        "utility", "utilities",
        "unanimous", "unanimously",
        "unicorn", "unicorns",
        "upon",
        "european", "europeans",
        "one", "once",
        "eulogy", "eulogies",
        "euphemism", "euphemisms",
    })

    def check(self, sentence: str, tokens: List[str]) -> List[DetectedError]:
        errors: List[DetectedError] = []
        for match in self._PATTERN.finditer(sentence):
            following_word = match.group(1).lower()
            if following_word in self._CONSONANT_SOUND:
                continue
            errors.append(DetectedError(
                sentence=sentence,
                error_type="ArticleBeforeVowel",
                message=(
                    f"[HEURISTIC] 'a {following_word}' — use 'an' before a vowel sound."
                ),
            ))
        return errors
