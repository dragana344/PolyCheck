"""
Turkish Levenshtein-based spell hint rule.

IMPORTANT -- HONESTY ABOUT WHAT THIS RULE IS:
This is a HEURISTIC approximation. Turkish is agglutinative: a single stem
can produce hundreds of valid word forms via suffixes. The wordlist contains
common base forms and the most frequent inflected forms, but cannot cover
every valid Turkish word. False positives will occur for valid but uncommon
inflected forms not in the wordlist.

Levenshtein distance-1 catches simple single-character typos. Distance-2
fallback is applied only to tokens of 7+ characters to limit false positives.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from analyzer.base_rule import BaseRule
from analyzer.models import DetectedError
from analyzer.utils import levenshtein

_WORDLIST_PATH = Path(__file__).parent / "wordlist.json"


class TurkishSpellRule(BaseRule):
    """
    [HEURISTIC] Flag Turkish tokens that are 1 Levenshtein edit away from a
    known common Turkish word. Only tokens of 3+ characters are checked.

    Turkish is agglutinative so a stem can appear with many suffixes. The most
    common personal/possessive suffixes are stripped before lookup so that valid
    inflected forms like 'gidiyorum' or 'arkadaşım' are not falsely flagged.
    """

    name = "TurkishLevenshteinSpellCheck"

    # Personal verb endings (present continuous) and possessive noun endings.
    # Ordered longest-first so the first matching strip is the most specific.
    # Suffixes tried in order — the loop stops at the first stem found in
    # the wordlist, so person-only endings come before the combined forms
    # (e.g. try stripping just 'um' first so 'gidiyorum' → 'gidiyor' hits
    # the wordlist before the longer 'iyorum' strip gives the bare stem 'gid').
    _SUFFIXES = (
        # Personal endings (strip to reach the tense-marked stem)
        "sunuz","siniz","sünüz","sınız",
        "sun","sin","sün","sın",
        "lar","ler",
        "uz","üz",
        "um","üm","ım","im",
        # Possessive + case
        "ımız","imiz","umuz","ümüz",
        "ınız","iniz","unuz","ünüz",
        "ım","im","um","üm",
        "ın","in","un","ün",
        # Present continuous (longer before shorter)
        "iyor","ıyor","uyor","üyor",
        # Past tense + 1st plural (3 chars, before 2-char past)
        "dık","dik","duk","dük",
        "tık","tik","tuk","tük",
        # Copula -dir (3 chars)
        "dır","dir","dur","dür",
        "tır","tir","tur","tür",
        # Past tense simple (2 chars)
        "dı","di","du","dü",
        "tı","ti","tu","tü",
        # Case suffixes
        "ndan","nden","ntan","nten",
        "dan","den","tan","ten",
        "nda","nde","nta","nte",
        "da","de","ta","te",
        "nın","nin","nun","nün",
        "nı","ni","nu","nü",
        "na","ne","ya","ye",
        "yı","yi","yu","yü",
        "ı","i","u","ü",
        "a","e",
    )

    def __init__(self) -> None:
        with open(_WORDLIST_PATH, encoding="utf-8") as fh:
            self._wordlist: List[str] = json.load(fh)
        self._wordlist_set: frozenset = frozenset(self._wordlist)

    _TURKISH_VOWELS = frozenset("aeıioöuü")

    def _has_known_stem(self, token: str) -> bool:
        """Return True if stripping a common suffix leaves a known stem."""
        for suffix in self._SUFFIXES:
            if token.endswith(suffix) and len(token) > len(suffix) + 1:
                stem = token[: -len(suffix)]
                if stem in self._wordlist_set:
                    return True
        # Special case: past/present tense + 1st person '-m' attaches directly
        # to a vowel-final tense stem (çalıştı+m, geliyor+um stripped earlier).
        if token.endswith("m") and len(token) > 2:
            stem = token[:-1]
            if stem in self._wordlist_set and stem[-1] in self._TURKISH_VOWELS:
                return True
        return False

    def check(self, sentence: str, tokens: List[str]) -> List[DetectedError]:
        errors: List[DetectedError] = []
        for token in tokens:
            if len(token) < 3:
                continue
            if token in self._wordlist_set:
                continue
            # Skip capitalised tokens -- likely proper nouns, not misspellings.
            if token[0].upper() + token[1:] in sentence:
                continue
            # Skip valid inflected forms (gidiyorum, arkadaşım, evlerde…).
            if self._has_known_stem(token):
                continue

            suggestion = None
            for ref in self._wordlist:
                if levenshtein(token, ref) == 1:
                    suggestion = ref
                    break

            if suggestion is None and len(token) >= 7:
                for ref in self._wordlist:
                    if levenshtein(token, ref) == 2:
                        suggestion = ref
                        break

            if suggestion is not None:
                errors.append(DetectedError(
                    sentence=sentence,
                    error_type="PossibleSpelling",
                    message=(
                        f"[HEURISTIC] '{token}' yanlis yazilmis olabilir -- "
                        f"'{suggestion}' mi demek istediniz?"
                    ),
                ))
        return errors
