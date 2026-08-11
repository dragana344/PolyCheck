from __future__ import annotations

import re
from typing import List

from analyzer.base_rule import BaseRule
from analyzer.models import DetectedError

# Adversative conjunctions that require a comma before them when joining clauses.
# 'туку' is excluded at sentence-start because it can mean "just/only" there.
_CONJUNCTIONS = ('но', 'ама', 'туку')

# Matches a conjunction preceded by a non-comma character (space + word boundary).
# Negative lookbehind ensures there is no comma immediately before the space.
_PATTERN = re.compile(
    r'(?<![,])\s+\b(' + '|'.join(_CONJUNCTIONS) + r')\b',
    re.IGNORECASE,
)

# Matches the same conjunction at the very start of the sentence — skip those
# because 'Но/Ама/Туку' can legitimately open a sentence without a preceding comma.
_SENTENCE_START = re.compile(
    r'^(' + '|'.join(_CONJUNCTIONS) + r')\b',
    re.IGNORECASE,
)


class CommaBeforeConjunctionRule(BaseRule):
    """
    [HEURISTIC] Flags the adversative conjunctions 'но', 'ама', 'туку' when
    they join two clauses without a preceding comma.

    Example:
        Wrong:   Таа сака да оди но нема пари.
        Correct: Таа сака да оди, но нема пари.

    Limitations:
      - Cannot distinguish clause-joining use from other uses without a parser.
      - 'туку' at the start of a sentence is skipped (often means "just/only").
    """

    name = "MissingCommaBeforeConjunction"

    def check(self, sentence: str, tokens: List[str]) -> List[DetectedError]:
        if _SENTENCE_START.match(sentence.strip()):
            return []

        errors: List[DetectedError] = []
        for match in _PATTERN.finditer(sentence):
            word = match.group(1)
            errors.append(DetectedError(
                sentence=sentence,
                error_type="MissingCommaBeforeConjunction",
                message=(
                    f"[HEURISTIC] Пред '{word}' треба да стои запирка "
                    f"кога поврзува две реченични целини."
                ),
            ))
        return errors
