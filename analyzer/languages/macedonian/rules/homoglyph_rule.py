from __future__ import annotations

from typing import List

from analyzer.base_rule import BaseRule
from analyzer.models import DetectedError

# Latin characters that are visually identical (or nearly so) to Cyrillic
# equivalents: a→а, e→е, o→о, c→с, p→р, x→х, A→А, B→В, C→С, E→Е,
# K→К, M→М, O→О, P→Р, T→Т, X→Х
_HOMOGLYPHS = frozenset('aeopcxABCEKMOPTX')


class HomoglyphRule(BaseRule):
    """
    [HEURISTIC] Detects Latin characters that are visually indistinguishable
    from Cyrillic characters in sentences that contain Cyrillic text.  These
    are invisible errors — the word looks correct on screen but contains the
    wrong Unicode codepoint (e.g. Latin 'a' instead of Cyrillic 'а').
    Only fires when at least one Cyrillic character is also present.
    """

    name = "HomoglyphDetection"

    def check(self, sentence: str, tokens: List[str]) -> List[DetectedError]:
        cyrillic_present = any('Ѐ' <= ch <= 'ӿ' for ch in sentence)
        if not cyrillic_present:
            return []

        found = sorted(set(ch for ch in sentence if ch in _HOMOGLYPHS))
        if not found:
            return []

        return [DetectedError(
            sentence=sentence,
            error_type="Homoglyph",
            message=(
                f"[HEURISTIC] Латински знаци {found} кои визуелно изгледаат "
                f"идентично со кирилски се пронајдени во кирилски текст — "
                f"можна ненамерна замена на знаци."
            ),
        )]
