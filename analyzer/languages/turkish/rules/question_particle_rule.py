from __future__ import annotations

import re
from typing import List

from analyzer.base_rule import BaseRule
from analyzer.models import DetectedError

# Matches a word where the Turkish question particle (mi/mı/mu/mü) appears to
# be incorrectly joined to the preceding word, with an optional personal ending.
#
# Group 1 — stem (the word before the particle)
# Group 2 — question particle (mi/mı/mu/mü)
# Group 3 — optional personal ending (sun, sın, …)
_PATTERN = re.compile(
    r"\b(\w+)(mi|mı|mu|mü)"
    r"(sunuz|sınız|siniz|sünüz|sun|sın|sin|sün)?\b",
    re.IGNORECASE | re.UNICODE,
)

# Turkish words that legitimately end in mi/mı/mu/mü and should never be
# flagged.  Only words whose stem is ≥ 5 characters need to be listed here
# because shorter stems are already filtered by the length check below.
_WHITELIST = {
    "islami",   # Islamic (stem "isla" = 4 chars, would otherwise be caught)
}


class QuestionParticleRule(BaseRule):
    """
    [HEURISTIC] Flags cases where the Turkish question particle mi/mı/mu/mü
    appears to be written without a space before it (e.g. 'geldinmi' should
    be 'geldin mi').

    False-positive reduction strategy
    ----------------------------------
    Turkish has many words that incidentally end in mi/mı/mu/mü (e.g. 'cami',
    'resmi', 'azami').  Two filters together keep false positives low:

    1. Stem length ≥ 5 characters.
       Words like 'cami' (stem 'ca' = 2), 'resmi' (stem 'res' = 3), and
       'azami' (stem 'aza' = 3) all have stems shorter than 5, so they are
       skipped automatically without needing to be whitelisted.

    2. Whitelist of known legitimate words whose stem happens to be ≥ 5 chars
       (currently only 'islami' with stem 'isla' = 4 chars falls into this
       gap and is explicitly whitelisted).
    """

    name = "QuestionParticle"

    def check(self, sentence: str, tokens: List[str]) -> List[DetectedError]:
        errors: List[DetectedError] = []

        for match in _PATTERN.finditer(sentence):
            full_word = match.group(0)
            stem = match.group(1)
            particle = match.group(2)

            # Filter 1: stem too short to be a real word + question particle.
            if len(stem) < 5:
                continue

            # Filter 2: known legitimate words.
            if full_word.lower() in _WHITELIST:
                continue

            errors.append(DetectedError(
                sentence=sentence,
                error_type=self.name,
                message=(
                    f"[HEURISTIC] '{full_word}' — question particle "
                    f"'{particle}' should be written as a separate word "
                    f"(e.g. '{stem} {full_word[len(stem):]}')."
                ),
            ))

        return errors