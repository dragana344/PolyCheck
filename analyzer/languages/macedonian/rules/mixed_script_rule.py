"""
Mixed-script detection rule for Macedonian text.

IMPORTANT — HONESTY ABOUT WHAT THIS RULE IS:
This is a HEURISTIC signal detector, not a grammar rule.  It flags Latin
character sequences inside text that is expected to be written in Macedonian
Cyrillic.  Common causes of false positives:
  - Intentional foreign words, brand names, or abbreviations in Latin script.
  - Code snippets embedded in prose.
  - Personal names transliterated from a Latin-script language.

The rule is useful for catching accidental keyboard-layout switches (a
frequent real-world error on Macedonian computers where Cyrillic and Latin
layouts share the same keyboard).
"""

from __future__ import annotations

import re
from typing import List

from analyzer.base_rule import BaseRule
from analyzer.models import DetectedError


class MixedScriptRule(BaseRule):
    """
    [HEURISTIC] Flag sequences of 2+ consecutive Latin characters that appear
    inside what is otherwise expected to be Macedonian (Cyrillic) text.
    Single Latin characters (e.g. "e" used as a letter in informal writing)
    are ignored to reduce noise.
    """

    name = "MixedScriptDetection"

    # Two or more consecutive ASCII letters — short enough to be a
    # keyboard-slip but long enough to skip stray single characters.
    _LATIN_RE = re.compile(r"[A-Za-z]{2,}")

    def check(self, sentence: str, tokens: List[str]) -> List[DetectedError]:
        errors: List[DetectedError] = []
        for match in self._LATIN_RE.finditer(sentence):
            errors.append(DetectedError(
                sentence=sentence,
                error_type="MixedScript",
                message=(
                    f"[HEURISTIC] Латинска секвенца '{match.group()}' "
                    f"пронајдена во очекуван македонски (кирилски) текст. "
                    f"Можна грешка во распоред на тастатура или намерна "
                    f"употреба на странски збор."
                ),
            ))
        return errors
