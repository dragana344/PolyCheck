from __future__ import annotations

import re
from typing import List

from analyzer.base_checker import BaseLanguageChecker
from analyzer.base_rule import BaseRule

# Language-specific rules
from analyzer.languages.english.rules.article_before_vowel_rule import ArticleBeforeVowelRule
from analyzer.languages.english.rules.apostrophe_rule import ApostropheRule
from analyzer.languages.english.rules.comma_after_introductory_phrase_rule import CommaAfterIntroductoryPhraseRule
from analyzer.languages.english.rules.common_confusion_rule import CommonConfusionRule
from analyzer.languages.english.rules.double_negation_rule import DoubleNegationRule
from analyzer.languages.english.rules.levenshtein_spell_rule import LevenshteinSpellRule

# Shared structural rules (language-agnostic)
from analyzer.languages.shared.consecutive_punctuation_rule import ConsecutivePunctuationRule
from analyzer.languages.shared.double_space_rule import DoubleSpaceRule
from analyzer.languages.shared.missing_end_punctuation_rule import MissingEndPunctuationRule
from analyzer.languages.shared.repeated_word_rule import RepeatedWordRule
from analyzer.languages.shared.sentence_capitalization_rule import SentenceCapitalizationRule
from analyzer.languages.shared.space_before_punctuation_rule import SpaceBeforePunctuationRule
from analyzer.languages.shared.unbalanced_parentheses_rule import UnbalancedParenthesesRule
from analyzer.languages.shared.unbalanced_quotes_rule import UnbalancedQuotesRule


class EnglishChecker(BaseLanguageChecker):
    """
    Checker for English (Latin-script) text.

    Tokenizer: pure ASCII letters, 3+ characters, lowercased.
    Digits and punctuation are excluded — they add noise to spell checking
    without contributing meaningful signal.

    Rule pipeline (order matters — structural checks run before spelling):
        1.  SentenceCapitalizationRule       [HEURISTIC] first alpha char uppercase
        2.  DoubleSpaceRule                  [HEURISTIC] two or more consecutive spaces
        3.  SpaceBeforePunctuationRule       [HEURISTIC] space before , . ! ? ; :
        4.  MissingEndPunctuationRule        [HEURISTIC] sentence ends with . ! ?
        5.  RepeatedWordRule                 [HEURISTIC] consecutive identical words
        6.  ConsecutivePunctuationRule       [HEURISTIC] two or more punctuation chars
        7.  UnbalancedQuotesRule             [HEURISTIC] odd number of double quotes
        8.  UnbalancedParenthesesRule        [HEURISTIC] mismatched parentheses
        9.  ArticleBeforeVowelRule           [HEURISTIC] 'a' before vowel-starting word
        10. CommonConfusionRule              [HEURISTIC] commonly confused word pairs
        11. ApostropheRule                   [HEURISTIC] contractions missing apostrophe
        12. DoubleNegationRule               [HEURISTIC] double negation pattern
        13. CommaAfterIntroductoryPhraseRule [HEURISTIC] missing comma after intro word
        14. LevenshteinSpellRule             [HEURISTIC] 1-edit-distance from common word
    """

    @property
    def language_code(self) -> str:
        return "en"

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
            ArticleBeforeVowelRule(),
            CommonConfusionRule(),
            ApostropheRule(),
            DoubleNegationRule(),
            CommaAfterIntroductoryPhraseRule(),
            LevenshteinSpellRule(),
        ]

    def tokenize(self, sentence: str) -> List[str]:
        return re.findall(r"[A-Za-z]{3,}", sentence.lower())
