from __future__ import annotations

import re
from typing import List

from analyzer.base_checker import BaseLanguageChecker
from analyzer.base_rule import BaseRule

# Language-specific rules
from analyzer.languages.macedonian.rules.cyrillic_spell_rule import CyrillicSpellRule
from analyzer.languages.macedonian.rules.cyrillic_vowel_rule import CyrillicVowelRule
from analyzer.languages.macedonian.rules.homoglyph_rule import HomoglyphRule
from analyzer.languages.macedonian.rules.mixed_script_rule import MixedScriptRule

# Shared structural rules (language-agnostic)
from analyzer.languages.shared.consecutive_punctuation_rule import ConsecutivePunctuationRule
from analyzer.languages.shared.double_space_rule import DoubleSpaceRule
from analyzer.languages.shared.missing_end_punctuation_rule import MissingEndPunctuationRule
from analyzer.languages.shared.repeated_word_rule import RepeatedWordRule
from analyzer.languages.shared.sentence_capitalization_rule import SentenceCapitalizationRule
from analyzer.languages.shared.space_before_punctuation_rule import SpaceBeforePunctuationRule
from analyzer.languages.shared.unbalanced_parentheses_rule import UnbalancedParenthesesRule
from analyzer.languages.shared.unbalanced_quotes_rule import UnbalancedQuotesRule


class MacedonianChecker(BaseLanguageChecker):
    """
    Checker for Macedonian (Cyrillic-script) text.

    Tokenizer: sequences of Cyrillic Unicode characters (U+0400–U+04FF),
    minimum 2 characters, lowercased.  The full Cyrillic block covers all
    standard Macedonian letters including Ѓ (U+0403), Ѕ (U+0405), Ј (U+0408),
    Љ (U+0409), Њ (U+040A), Ќ (U+040C), and Џ (U+040F).

    Rule pipeline (order matters — structural checks run before spelling):
        1.  SentenceCapitalizationRule  [HEURISTIC] first alpha char uppercase
        2.  DoubleSpaceRule             [HEURISTIC] two or more consecutive spaces
        3.  SpaceBeforePunctuationRule  [HEURISTIC] space before , . ! ? ; :
        4.  MissingEndPunctuationRule   [HEURISTIC] sentence ends with . ! ?
        5.  RepeatedWordRule            [HEURISTIC] consecutive identical words
        6.  ConsecutivePunctuationRule  [HEURISTIC] two or more punctuation chars
        7.  UnbalancedQuotesRule        [HEURISTIC] odd number of double quotes
        8.  UnbalancedParenthesesRule   [HEURISTIC] mismatched parentheses
        9.  CyrillicSpellRule           [HEURISTIC] 1-edit-distance from common word
        10. MixedScriptRule             [HEURISTIC] Latin chars in Cyrillic text
        11. CyrillicVowelRule           [HEURISTIC] Cyrillic token with no vowel
        12. HomoglyphRule               [HEURISTIC] visually identical Latin/Cyrillic chars
    """

    @property
    def language_code(self) -> str:
        return "mk"

    def _build_rules(self) -> List[BaseRule]:
        return [
            SentenceCapitalizationRule(),
            DoubleSpaceRule(),
            SpaceBeforePunctuationRule(),
            MissingEndPunctuationRule(),
            RepeatedWordRule(),
            ConsecutivePunctuationRule(),
            UnbalancedQuotesRule(),
            UnbalancedParenthesesRule(),
            CyrillicSpellRule(),
            MixedScriptRule(),
            CyrillicVowelRule(),
            HomoglyphRule(),
        ]

    def tokenize(self, sentence: str) -> List[str]:
        # {2,} instead of {3,} because Macedonian has many meaningful
        # 2-character words: на, во, со, од, за, да, се, ги, го, ја …
        return re.findall(r"[Ѐ-ӿ]{2,}", sentence.lower())
