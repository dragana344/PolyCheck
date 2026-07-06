from __future__ import annotations

import re
from typing import List

from analyzer.base_rule import BaseRule
from analyzer.models import DetectedError

# Matches capitalized tokens in the raw sentence (preserving original casing).
# Two forms:
#   - Title case: Ankara, İstanbul, Boğaziçi
#   - All-caps with optional lowercase suffix: TBMM, ODTÜde
_CAPITALIZED = re.compile(
    r"[A-ZÇĞİÖŞÜ][A-Za-zÇĞİÖŞÜçğışöü]+"
    r"|[A-ZÇĞİÖŞÜ]{2,}[a-zçğışöü]*"
)


class ProperNounApostropheRule(BaseRule):
    """
    [HEURISTIC] Flags proper nouns that have an inflectional suffix attached
    without an apostrophe (e.g. 'Ankaraya' should be 'Ankara'ya').

    Works on the raw sentence (not the lowercased token list) so that
    capitalisation can be used to identify proper nouns.
    """

    name = "ProperNounApostrophe"

    # Suffixes that require an apostrophe when attached to a proper noun.
    # Ordered longest-first at init time so we don't match '-a' inside '-ya'.
    _SUFFIXES = (
        "daki", "deki", "taki", "teki",
        "dan", "den", "tan", "ten",
        "yla", "yle",
        "la", "le",
        "yı", "yi", "yu", "yü",
        "nın", "nin", "nun", "nün",
        "ın", "in", "un", "ün",
        "na", "ne",
        "ya", "ye",
        "da", "de", "ta", "te",
        "a", "e",
        "ı", "i", "u", "ü",
    )

    # Derivational/adjectival suffixes that attach WITHOUT an apostrophe even
    # on proper nouns (e.g. Ankaralı, Türkiyeli, Türkçe, Amerikalılar).
    _NON_APOSTROPHE_SUFFIXES = (
        "li", "lı", "lu", "lü",
        "lik", "lık", "luk", "lük",
        "ler", "lar",
        "gil",
        "cı", "ci", "cu", "cü",
        "ca", "ce",
        "ça", "çe",
    )

    _PROPER_NOUNS = {
        # Cities
        "ankara", "istanbul", "izmir", "adana", "antalya",
        "bursa", "konya", "eskişehir", "trabzon",
        "samsun", "gaziantep", "kayseri", "kocaeli",
        # Countries / regions
        "türkiye", "almanya", "fransa", "ingiltere",
        "amerika", "abd", "kanada", "japonya",
        "çin", "italya", "ispanya", "rusya",
        # Universities
        "odtü", "itü", "ytü", "boğaziçi",
        "hacettepe", "bilkent", "koç", "sabancı",
        # Institutions / abbreviations
        "tbmm", "tdk", "tüik", "sgk",
        "ösym", "yök", "tübitak",
        "ibb", "abb", "trt", "thy",
        # Common first names
        "ahmet", "mehmet", "mustafa", "ali",
        "veli", "hasan", "hüseyin", "ibrahim",
        "emre", "mert", "kerem", "berk",
        "kaan", "can", "burak", "enes",
        "onur", "serkan", "selim", "murat",
        "ayşe", "fatma", "zeynep", "elif",
        "ece", "selin", "melis", "buse",
        "esra", "gamze", "merve", "sena",
        "hilal", "naz", "damla",
        # Historical / cultural figures
        "atatürk", "fatih", "kanuni",
        "mevlana", "yunusemre",
        # Tech companies
        "google", "microsoft", "apple",
        "amazon", "meta", "openai",
        "tesla", "nvidia", "samsung",
    }

    # Abbreviations that collide with ordinary Turkish words when lowercased
    # ('ab' is the start of 'abla', 'aba', 'abi'…).  These are only treated
    # as proper nouns when the stem appears in ALL CAPS in the sentence
    # (e.g. 'ABye' is flagged, 'Abla' is not).
    _CAPS_ONLY_ABBREVIATIONS = {
        "ab",
    }

    def __init__(self) -> None:
        # Pre-sort once so check() does not pay the cost on every sentence.
        self._sorted_suffixes = sorted(self._SUFFIXES, key=len, reverse=True)

    def check(self, sentence: str, tokens: List[str]) -> List[DetectedError]:
        errors: List[DetectedError] = []

        for match in _CAPITALIZED.finditer(sentence):
            token = match.group()

            # Already has an apostrophe — correctly written.
            if "'" in token or "’" in token:
                continue

            normalized = token.lower()

            # Derivational suffixes never need an apostrophe; skip them.
            if normalized.endswith(self._NON_APOSTROPHE_SUFFIXES):
                continue

            for suffix in self._sorted_suffixes:
                if not normalized.endswith(suffix):
                    continue
                stem = normalized[: -len(suffix)]
                if len(stem) < 2:
                    continue
                is_known = stem in self._PROPER_NOUNS or (
                    stem in self._CAPS_ONLY_ABBREVIATIONS
                    and token[: len(stem)].isupper()
                )
                if is_known:
                    errors.append(DetectedError(
                        sentence=sentence,
                        error_type=self.name,
                        message=(
                            f"[HEURISTIC] '{token}' looks like a proper noun "
                            f"with a suffix but is missing an apostrophe "
                            f"(e.g. '{token[: len(stem)]}'{suffix}')."
                        ),
                    ))
                    break

        return errors