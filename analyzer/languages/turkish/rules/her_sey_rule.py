from __future__ import annotations

import re
from typing import List

from analyzer.base_rule import BaseRule
from analyzer.models import DetectedError

# Matches 'herşey' plus any attached suffixes (herşeyi, herşeyden, herşeye…).
# The joined spelling is always incorrect per TDK, so matching the suffixed
# forms as well costs nothing in false positives: no legitimate Turkish word
# starts with 'herşey'.
_PATTERN = re.compile(r"\bherşey\w*", re.IGNORECASE)


class HerSeyRule(BaseRule):
    """
    [HEURISTIC] Flags the incorrect joined spelling of the Turkish phrase
    'her şey' (e.g. 'Herşey yolunda' should be 'Her şey yolunda'),
    including suffixed forms such as 'herşeyi' and 'herşeyden'.
    """

    name = "HerSey"

    def check(self, sentence: str, tokens: List[str]) -> List[DetectedError]:
        errors: List[DetectedError] = []

        for match in _PATTERN.finditer(sentence):
            word = match.group()
            suffix = word[len("herşey"):]
            errors.append(DetectedError(
                sentence=sentence,
                error_type=self.name,
                message=(
                    f"[HEURISTIC] '{word}' should be written as "
                    f"'her şey{suffix.lower()}'."
                ),
            ))

        return errors
