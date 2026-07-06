from __future__ import annotations

import re
from typing import List

from analyzer.base_rule import BaseRule
from analyzer.models import DetectedError

# Digits immediately followed by lowercase Turkish letters (2024te, 10da).
# Deliberately case-sensitive: real Turkish suffixes are lowercase, while
# uppercase trailing letters are tech/unit notation (5G, 4K, 25MB) that must
# not be flagged.
_PATTERN = re.compile(r"\b(\d+)([a-zçğıöşü]+)\b")

# Lowercase measurement/tech units that legitimately follow a number without
# an apostrophe (5kg, 10cm, 3x).  Turkish case suffixes never collide with
# these strings.
_UNITS = {
    "kg", "g", "gr", "mg", "t",
    "km", "m", "cm", "mm",
    "l", "lt", "ml", "cc",
    "gb", "mb", "kb", "tb",
    "tl", "kr",
    "w", "kw", "v", "mah",
    "hz", "khz", "mhz", "ghz",
    "px", "dk", "sn", "ms",
    "x",
}


class NumberSuffixRule(BaseRule):
    """
    [HEURISTIC] Flags numbers followed by a Turkish suffix without an
    apostrophe (e.g. '2024te' should be '2024'te', '10da' should be '10'da').

    Limitations:
      - Only detects numbers immediately followed by lowercase letters.
      - Does not verify whether the suffix itself is grammatically correct.
      - Unit abbreviations written in lowercase (5kg, 10cm) are skipped via
        a whitelist; unusual units not on the list may still be flagged.
    """

    name = "NumberSuffix"

    def check(self, sentence: str, tokens: List[str]) -> List[DetectedError]:
        errors: List[DetectedError] = []

        for match in _PATTERN.finditer(sentence):
            number, letters = match.group(1), match.group(2)

            if letters in _UNITS:
                continue

            errors.append(DetectedError(
                sentence=sentence,
                error_type=self.name,
                message=(
                    f"[HEURISTIC] '{match.group()}' may require an "
                    f"apostrophe before the suffix "
                    f"(e.g. '{number}'{letters}')."
                ),
            ))

        return errors
