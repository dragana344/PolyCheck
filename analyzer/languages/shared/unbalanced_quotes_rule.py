from __future__ import annotations

from typing import List

from analyzer.base_rule import BaseRule
from analyzer.models import DetectedError

# Macedonian/European curly quote characters.
_CURLY_OPEN  = '„'  # „  LOW-9 DOUBLE QUOTATION MARK  (opens in MK)
_CURLY_CLOSE = '“'  # "  LEFT DOUBLE QUOTATION MARK   (closes in MK)


class UnbalancedQuotesRule(BaseRule):
    """
    [HEURISTIC] Flags sentences with unbalanced quotation marks.

    Two styles are checked independently:
      - ASCII double quotes (") -- odd count means unbalanced.
      - Macedonian/European curly quotes (U+201E / U+201C) -- opening
        and closing counts must match.

    Single quotes are skipped because they overlap with apostrophes and
    produce too many false positives.
    """

    name = "UnbalancedQuotes"

    def check(self, sentence: str, tokens: List[str]) -> List[DetectedError]:
        errors: List[DetectedError] = []

        if sentence.count('"') % 2 != 0:
            errors.append(DetectedError(
                sentence=sentence,
                error_type="UnbalancedQuotes",
                message="[HEURISTIC] Odd number of double-quote characters -- possible unclosed quotation.",
            ))

        if sentence.count(_CURLY_OPEN) != sentence.count(_CURLY_CLOSE):
            errors.append(DetectedError(
                sentence=sentence,
                error_type="UnbalancedQuotes",
                message="[HEURISTIC] Mismatched curly quotes -- opening and closing counts differ.",
            ))

        return errors
