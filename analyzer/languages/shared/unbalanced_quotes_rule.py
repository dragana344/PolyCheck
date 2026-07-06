from __future__ import annotations

from typing import List

from analyzer.base_rule import BaseRule
from analyzer.models import DetectedError


class UnbalancedQuotesRule(BaseRule):
    """
    [HEURISTIC] Flags a sentence that contains an odd number of double-quote
    characters, which typically indicates an unclosed or unopened quotation.
    Only double quotes are checked; single quotes are skipped because they
    overlap with apostrophes and produce too many false positives.
    """

    name = "UnbalancedQuotes"

    def check(self, sentence: str, tokens: List[str]) -> List[DetectedError]:
        if sentence.count('"') % 2 != 0:
            return [DetectedError(
                sentence=sentence,
                error_type="UnbalancedQuotes",
                message="[HEURISTIC] Odd number of double-quote characters — possible unclosed quotation.",
            )]
        return []
