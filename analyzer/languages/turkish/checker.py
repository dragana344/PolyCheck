from __future__ import annotations

import re
from typing import List

from analyzer.base_checker import BaseLanguageChecker
from analyzer.base_rule import BaseRule

from analyzer.languages.turkish.rules.bircok_rule import BircokRule
from analyzer.languages.turkish.rules.her_sey_rule import HerSeyRule
from analyzer.languages.turkish.rules.number_suffix_rule import NumberSuffixRule
from analyzer.languages.turkish.rules.proper_noun_apostrophe_rule import ProperNounApostropheRule
from analyzer.languages.turkish.rules.question_particle_rule import QuestionParticleRule

from analyzer.languages.shared.consecutive_punctuation_rule import ConsecutivePunctuationRule
from analyzer.languages.shared.double_space_rule import DoubleSpaceRule
from analyzer.languages.shared.missing_end_punctuation_rule import MissingEndPunctuationRule
from analyzer.languages.shared.repeated_word_rule import RepeatedWordRule
from analyzer.languages.shared.sentence_capitalization_rule import SentenceCapitalizationRule
from analyzer.languages.shared.space_before_punctuation_rule import SpaceBeforePunctuationRule
from analyzer.languages.shared.unbalanced_parentheses_rule import UnbalancedParenthesesRule
from analyzer.languages.shared.unbalanced_quotes_rule import UnbalancedQuotesRule


class TurkishChecker(BaseLanguageChecker):
    """
    Checker for Turkish (Latin-script with Turkish special characters).

    Tokenizer: sequences of Latin + Turkish letters (Ç/ç Ğ/ğ İ/ı Ö/ö Ş/ş Ü/ü),
    minimum 2 characters, lowercased.

    Rule pipeline:
        1.  SentenceCapitalizationRule  [shared]
        2.  DoubleSpaceRule             [shared]
        3.  SpaceBeforePunctuationRule  [shared]
        4.  MissingEndPunctuationRule   [shared]
        5.  RepeatedWordRule            [shared]
        6.  ConsecutivePunctuationRule  [shared]
        7.  UnbalancedQuotesRule        [shared]
        8.  UnbalancedParenthesesRule   [shared]
        9.  ProperNounApostropheRule    [HEURISTIC] missing apostrophe before suffix
                                        (incl. abbreviations: TBMMde, ABye)
        10. QuestionParticleRule        [HEURISTIC] question particle written without space
        11. HerSeyRule                  [HEURISTIC] 'herşey' should be 'her şey'
        12. BircokRule                  [HEURISTIC] 'bir çok' should be 'birçok';
                                        'birşey' should be 'bir şey'
        13. NumberSuffixRule            [HEURISTIC] number + suffix without apostrophe
    """

    @property
    def language_code(self) -> str:
        return "tr"

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
            ProperNounApostropheRule(),
            QuestionParticleRule(),
            HerSeyRule(),
            BircokRule(),
            NumberSuffixRule(),
        ]

    def tokenize(self, sentence: str) -> List[str]:
        return re.findall(r"[A-Za-zÇĞİÖŞÜçğışöü]{2,}", sentence.lower())
