"""
Enhanced spell checking rule using pyspellchecker.

Differences from LevenshteinSpellRule:
  - Uses word frequency to pick the most likely correction (not just distance 1).
  - Catches typos that are 2 edits away, not just 1.
  - No wordlist.json needed — the library ships its own dictionary.
  - Far fewer false positives on real but uncommon words.

Not enabled by default. To use it, install the dependency and swap it in
for LevenshteinSpellRule in EnglishChecker._build_rules().

Requires: pip install pyspellchecker
"""

from __future__ import annotations

from typing import List

from spellchecker import SpellChecker

from analyzer.base_rule import BaseRule
from analyzer.models import DetectedError

_spell = SpellChecker()


class EnhancedSpellRule(BaseRule):
    """
    [HEURISTIC] Flags tokens that are likely misspelled using pyspellchecker.
    Picks the most frequency-weighted correction candidate rather than the
    first word within edit distance 1.  Tokens under 4 characters are skipped
    to reduce noise from abbreviations and short function words.
    """

    name = "EnhancedSpellCheck"

    def check(self, sentence: str, tokens: List[str]) -> List[DetectedError]:
        candidates = [t for t in tokens if len(t) >= 4]
        misspelled = _spell.unknown(candidates)
        errors: List[DetectedError] = []
        for word in misspelled:
            correction = _spell.correction(word)
            if correction and correction != word:
                errors.append(DetectedError(
                    sentence=sentence,
                    error_type="PossibleSpelling",
                    message=(
                        f"[HEURISTIC] '{word}' may be misspelled — "
                        f"did you mean '{correction}'?"
                    ),
                ))
        return errors
