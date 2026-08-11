"""
Shared rule: double (or multiple) consecutive spaces.

Applies to any language because whitespace normalisation is script-agnostic.
"""

from __future__ import annotations

import re
from typing import List

from analyzer.base_rule import BaseRule
from analyzer.models import DetectedError


class DoubleSpaceRule(BaseRule):
    """
    [HEURISTIC] Flags two or more consecutive space characters within a
    sentence.  A single match per sentence is reported to avoid flooding
    the output when an entire paragraph was copy-pasted with bad spacing.
    """

    name = "DoubleSpace"

    _PATTERN = re.compile(r" {2,}")

    def check(self, sentence: str, tokens: List[str]) -> List[DetectedError]:
        errors = []
        for match in self._PATTERN.finditer(sentence):
            errors.append(DetectedError(
                sentence=sentence,
                error_type="DoubleSpace",
                message=(
                    f"[HEURISTIC] {len(match.group())} consecutive spaces detected "
                    f"at position {match.start()}."
                ),
            ))
        return errors
