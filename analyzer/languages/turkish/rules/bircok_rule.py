from __future__ import annotations

import re
from typing import List

from analyzer.base_rule import BaseRule
from analyzer.models import DetectedError

# 'bir çok' must be joined ('birçok').  The \b after 'çok' keeps derived
# words like 'bir çokluk' from matching.
_SEPARATE_PATTERN = re.compile(r"\bbir çok\b", re.IGNORECASE)

# 'birşey' must be separated ('bir şey').  Suffixed forms (birşeyi,
# birşeyden…) are included — no legitimate word starts with 'birşey'.
_JOINED_PATTERN = re.compile(r"\bbirşey\w*", re.IGNORECASE)


class BircokRule(BaseRule):
    """
    [HEURISTIC] Flags two mirror-image spelling errors around 'bir':
      - 'bir çok' written separately (should be 'birçok')
      - 'birşey' written joined (should be 'bir şey'), including
        suffixed forms such as 'birşeyi' and 'birşeyden'.
    """

    name = "Bircok"

    def check(self, sentence: str, tokens: List[str]) -> List[DetectedError]:
        errors: List[DetectedError] = []

        for match in _SEPARATE_PATTERN.finditer(sentence):
            errors.append(DetectedError(
                sentence=sentence,
                error_type=self.name,
                message=(
                    f"[HEURISTIC] '{match.group()}' should be written "
                    f"as one word: 'birçok'."
                ),
            ))

        for match in _JOINED_PATTERN.finditer(sentence):
            word = match.group()
            suffix = word[len("birşey"):]
            errors.append(DetectedError(
                sentence=sentence,
                error_type=self.name,
                message=(
                    f"[HEURISTIC] '{word}' should be written as two words: "
                    f"'bir şey{suffix.lower()}'."
                ),
            ))

        return errors
