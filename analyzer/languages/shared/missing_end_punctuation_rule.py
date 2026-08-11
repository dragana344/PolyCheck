"""
Shared rule: sentence does not end with a recognised terminal punctuation mark.

Applicable to any language that uses . ! ? as sentence-enders.
Very short fragments (< 4 characters) are skipped because they are likely
not full sentences (labels, headers, list items).
"""

from __future__ import annotations

import re
from typing import List

from analyzer.base_rule import BaseRule
from analyzer.models import DetectedError


class MissingEndPunctuationRule(BaseRule):
    """
    [HEURISTIC] Flags sentences that do not end with . ! ? or … (U+2026).

    Closing quotation marks and brackets after the terminal mark are
    allowed (e.g. 'He said "hello."' is fine).

    Limitations:
      - Cannot distinguish genuine sentences from titles or list items.
      - Sentences split mid-paragraph may appear to lack end punctuation.
    """

    name = "MissingEndPunctuation"

    # Terminal punctuation optionally followed by closing quotes/brackets.
    _END_OK = re.compile(
        r'[.!?\u2026]'          # terminal mark
        r'["\'\u2018\u2019\u201c\u201d\u00bb\]\)]*'  # optional closers
        r'\s*$'
    )

    _MIN_LENGTH = 4  # skip fragments shorter than this

    def check(self, sentence: str, tokens: List[str]) -> List[DetectedError]:
        s = sentence.strip()
        if len(s) < self._MIN_LENGTH:
            return []
        # Skip short fragments — headings and list items rarely end with
        # terminal punctuation and should not be flagged.
        if len(tokens) < 3:
            return []
        if not self._END_OK.search(s):
            return [DetectedError(
                sentence=sentence,
                error_type="MissingEndPunctuation",
                message="[HEURISTIC] Sentence does not end with terminal punctuation (. ! ?).",
            )]
        return []
