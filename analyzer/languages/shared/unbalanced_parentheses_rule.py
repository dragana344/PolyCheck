from __future__ import annotations

from typing import List

from analyzer.base_rule import BaseRule
from analyzer.models import DetectedError


class UnbalancedParenthesesRule(BaseRule):
    """
    [HEURISTIC] Flags a sentence where the count of opening parentheses does
    not match the count of closing parentheses.
    """

    name = "UnbalancedParentheses"

    def check(self, sentence: str, tokens: List[str]) -> List[DetectedError]:
        if sentence.count('(') != sentence.count(')'):
            return [DetectedError(
                sentence=sentence,
                error_type="UnbalancedParentheses",
                message="[HEURISTIC] Mismatched parentheses — opening and closing counts differ.",
            )]
        return []
