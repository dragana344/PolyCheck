"""
Unit tests for individual rules, tested in isolation.

Rules are instantiated directly and called with .check(sentence, tokens).
This bypasses the checker pipeline so we can verify each rule's behaviour
independently of tokenization and rule ordering.

The token list is left empty ([]) for rules that use raw-sentence regex
patterns.  Rules that depend on tokens receive a realistic token list.
"""

import pytest

from analyzer.languages.shared.double_space_rule import DoubleSpaceRule
from analyzer.languages.shared.missing_end_punctuation_rule import MissingEndPunctuationRule
from analyzer.languages.shared.repeated_word_rule import RepeatedWordRule
from analyzer.languages.shared.sentence_capitalization_rule import SentenceCapitalizationRule
from analyzer.languages.shared.space_before_punctuation_rule import SpaceBeforePunctuationRule
from analyzer.languages.shared.consecutive_punctuation_rule import ConsecutivePunctuationRule
from analyzer.languages.shared.unbalanced_quotes_rule import UnbalancedQuotesRule
from analyzer.languages.shared.unbalanced_parentheses_rule import UnbalancedParenthesesRule
from analyzer.languages.english.rules.levenshtein_spell_rule import LevenshteinSpellRule
from analyzer.languages.english.rules.article_before_vowel_rule import ArticleBeforeVowelRule
from analyzer.languages.english.rules.common_confusion_rule import CommonConfusionRule
from analyzer.languages.english.rules.apostrophe_rule import ApostropheRule
from analyzer.languages.english.rules.double_negation_rule import DoubleNegationRule
from analyzer.languages.english.rules.comma_after_introductory_phrase_rule import CommaAfterIntroductoryPhraseRule
from analyzer.languages.macedonian.rules.mixed_script_rule import MixedScriptRule
from analyzer.languages.macedonian.rules.cyrillic_spell_rule import CyrillicSpellRule
from analyzer.languages.macedonian.rules.cyrillic_vowel_rule import CyrillicVowelRule
from analyzer.languages.macedonian.rules.homoglyph_rule import HomoglyphRule


# ─── DoubleSpaceRule ──────────────────────────────────────────────────────────

class TestDoubleSpaceRule:
    rule = DoubleSpaceRule()

    def test_detects_two_spaces(self):
        errors = self.rule.check("Hello  world.", [])
        assert len(errors) == 1
        assert errors[0].error_type == "DoubleSpace"

    def test_detects_three_spaces(self):
        errors = self.rule.check("Hello   world.", [])
        assert len(errors) >= 1

    def test_no_error_single_space(self):
        assert self.rule.check("Hello world.", []) == []

    def test_no_error_empty_string(self):
        assert self.rule.check("", []) == []

    def test_message_has_heuristic_label(self):
        errors = self.rule.check("A  B", [])
        assert "[HEURISTIC]" in errors[0].message

    def test_reports_once_not_per_character(self):
        # Even if there are 5 consecutive spaces, at most one error is reported.
        errors = self.rule.check("A     B", [])
        assert len(errors) == 1


# ─── SpaceBeforePunctuationRule ───────────────────────────────────────────────

class TestSpaceBeforePunctuationRule:
    rule = SpaceBeforePunctuationRule()

    def test_detects_space_before_comma(self):
        errors = self.rule.check("Hello ,world.", [])
        assert any(e.error_type == "SpaceBeforePunctuation" for e in errors)

    def test_detects_space_before_period(self):
        errors = self.rule.check("Hello world .", [])
        assert any(e.error_type == "SpaceBeforePunctuation" for e in errors)

    def test_detects_space_before_exclamation(self):
        errors = self.rule.check("Wow !", [])
        assert len(errors) >= 1

    def test_detects_space_before_question_mark(self):
        errors = self.rule.check("Really ?", [])
        assert len(errors) >= 1

    def test_detects_space_before_semicolon(self):
        errors = self.rule.check("Done ;next.", [])
        assert len(errors) >= 1

    def test_no_error_for_correct_spacing(self):
        assert self.rule.check("Hello, world.", []) == []

    def test_multiple_errors_reported(self):
        errors = self.rule.check("Hello ,world .done", [])
        assert len(errors) >= 2


# ─── MissingEndPunctuationRule ────────────────────────────────────────────────

class TestMissingEndPunctuationRule:
    rule = MissingEndPunctuationRule()

    def test_flags_sentence_without_punct(self):
        errors = self.rule.check("The dog barked", [])
        assert len(errors) == 1
        assert errors[0].error_type == "MissingEndPunctuation"

    def test_no_error_for_period(self):
        assert self.rule.check("The dog barked.", []) == []

    def test_no_error_for_exclamation(self):
        assert self.rule.check("The dog barked!", []) == []

    def test_no_error_for_question_mark(self):
        assert self.rule.check("Did the dog bark?", []) == []

    def test_no_error_for_ellipsis(self):
        assert self.rule.check("And then…", []) == []

    def test_no_error_for_period_inside_quote(self):
        assert self.rule.check('He said "hello."', []) == []

    def test_empty_string_no_error(self):
        assert self.rule.check("", []) == []

    def test_very_short_fragment_skipped(self):
        # Fragments under 4 chars are not full sentences — skip them.
        assert self.rule.check("OK", []) == []

    def test_message_has_heuristic_label(self):
        errors = self.rule.check("The dog barked", [])
        assert "[HEURISTIC]" in errors[0].message


# ─── RepeatedWordRule ─────────────────────────────────────────────────────────

class TestRepeatedWordRule:
    rule = RepeatedWordRule()

    def test_detects_repeated_word_at_start(self):
        errors = self.rule.check("The the dog.", [])
        assert any(e.error_type == "RepeatedWord" for e in errors)

    def test_detects_repeated_word_in_middle(self):
        errors = self.rule.check("She went to to the store.", [])
        assert len(errors) >= 1

    def test_detects_case_insensitive(self):
        errors = self.rule.check("She She went home.", [])
        assert len(errors) >= 1

    def test_no_error_for_non_consecutive_same_word(self):
        # "the" appears twice but not consecutively
        assert self.rule.check("The cat and the dog.", []) == []

    def test_no_error_for_unique_words(self):
        assert self.rule.check("The dog barked.", []) == []

    def test_detects_cyrillic_repeated_word(self):
        errors = self.rule.check("Таа таа отиде.", [])
        assert len(errors) >= 1

    def test_detects_short_word_repetition(self):
        # "to to" — short words are not excluded by this rule
        errors = self.rule.check("She went to to the store.", [])
        assert len(errors) >= 1

    def test_message_has_heuristic_label(self):
        errors = self.rule.check("The the dog.", [])
        assert "[HEURISTIC]" in errors[0].message


# ─── SentenceCapitalizationRule ───────────────────────────────────────────────

class TestSentenceCapitalizationRule:
    rule = SentenceCapitalizationRule()

    def test_detects_lowercase_latin_start(self):
        errors = self.rule.check("the dog barked.", [])
        assert len(errors) == 1
        assert errors[0].error_type == "Capitalization"

    def test_no_error_for_uppercase_latin_start(self):
        assert self.rule.check("The dog barked.", []) == []

    def test_detects_lowercase_cyrillic_start(self):
        errors = self.rule.check("лисицата скокна.", [])
        assert len(errors) == 1

    def test_no_error_for_uppercase_cyrillic_start(self):
        assert self.rule.check("Лисицата скокна.", []) == []

    def test_empty_string_no_error(self):
        assert self.rule.check("", []) == []

    def test_whitespace_only_no_error(self):
        assert self.rule.check("   ", []) == []

    def test_sentence_starting_with_digit_does_not_crash(self):
        result = self.rule.check("3 dogs barked.", [])
        assert isinstance(result, list)

    def test_message_has_heuristic_label(self):
        errors = self.rule.check("hello world.", [])
        assert "[HEURISTIC]" in errors[0].message


# ─── LevenshteinSpellRule (English, language-specific) ───────────────────────

class TestLevenshteinSpellRule:
    rule = LevenshteinSpellRule()

    def test_detects_one_char_typo(self):
        # "thnk" → "think" (delete 'i')
        errors = self.rule.check("I thnk this is correct.", ["thnk", "this", "correct"])
        assert any(e.error_type == "PossibleSpelling" for e in errors)

    def test_exact_match_not_flagged(self):
        # "think" is in the wordlist — should be skipped
        errors = self.rule.check("I think this is correct.", ["think", "this", "correct"])
        flagged = [e for e in errors if "'think'" in e.message and "close to 'think'" in e.message]
        assert flagged == []

    def test_short_tokens_skipped(self):
        # Tokens under 3 chars must not be checked (too noisy)
        errors = self.rule.check("Go.", ["go"])
        assert errors == []

    def test_message_has_heuristic_label(self):
        errors = self.rule.check("I thnk so.", ["thnk", "so"])
        spell = [e for e in errors if e.error_type == "PossibleSpelling"]
        if spell:
            assert "[HEURISTIC]" in spell[0].message


# ─── MixedScriptRule (Macedonian, language-specific) ─────────────────────────

class TestMixedScriptRule:
    rule = MixedScriptRule()

    def test_detects_latin_word_in_cyrillic_text(self):
        errors = self.rule.check("Таа отиде на pazar.", [])
        assert any(e.error_type == "MixedScript" for e in errors)

    def test_no_error_for_pure_cyrillic(self):
        assert self.rule.check("Лисицата скокна.", []) == []

    def test_detects_multiple_latin_sequences(self):
        errors = self.rule.check("Тој е mnogu добар student.", [])
        mixed = [e for e in errors if e.error_type == "MixedScript"]
        assert len(mixed) >= 2

    def test_single_latin_char_not_flagged(self):
        # Rule requires 2+ consecutive Latin chars to reduce noise
        errors = self.rule.check("Таа е x добра.", [])
        assert errors == []

    def test_message_has_heuristic_label(self):
        errors = self.rule.check("Тој е ok.", [])
        mixed = [e for e in errors if e.error_type == "MixedScript"]
        if mixed:
            assert "[HEURISTIC]" in mixed[0].message


# ─── ConsecutivePunctuationRule ───────────────────────────────────────────────

class TestConsecutivePunctuationRule:
    rule = ConsecutivePunctuationRule()

    def test_detects_double_exclamation(self):
        errors = self.rule.check("What!!", [])
        assert any(e.error_type == "ConsecutivePunctuation" for e in errors)

    def test_detects_double_question(self):
        errors = self.rule.check("Really??", [])
        assert len(errors) >= 1

    def test_detects_period_comma(self):
        errors = self.rule.check("Hello.,world", [])
        assert len(errors) >= 1

    def test_detects_double_period(self):
        errors = self.rule.check("Hello..world", [])
        assert len(errors) >= 1

    def test_ellipsis_not_flagged(self):
        assert self.rule.check("And then...", []) == []

    def test_no_error_for_clean_sentence(self):
        assert self.rule.check("Hello, world!", []) == []

    def test_message_has_heuristic_label(self):
        errors = self.rule.check("What!!", [])
        assert "[HEURISTIC]" in errors[0].message


# ─── UnbalancedQuotesRule ─────────────────────────────────────────────────────

class TestUnbalancedQuotesRule:
    rule = UnbalancedQuotesRule()

    def test_detects_single_quote(self):
        errors = self.rule.check('He said "hello.', [])
        assert any(e.error_type == "UnbalancedQuotes" for e in errors)

    def test_no_error_for_balanced_quotes(self):
        assert self.rule.check('He said "hello."', []) == []

    def test_no_error_for_no_quotes(self):
        assert self.rule.check("The dog barked.", []) == []

    def test_detects_three_quotes(self):
        errors = self.rule.check('"Hello" he said "goodbye.', [])
        assert len(errors) >= 1

    def test_balanced_two_pairs_no_error(self):
        assert self.rule.check('"Hi" and "bye."', []) == []

    def test_message_has_heuristic_label(self):
        errors = self.rule.check('"unmatched', [])
        assert "[HEURISTIC]" in errors[0].message


# ─── UnbalancedParenthesesRule ────────────────────────────────────────────────

class TestUnbalancedParenthesesRule:
    rule = UnbalancedParenthesesRule()

    def test_detects_unclosed_paren(self):
        errors = self.rule.check("See the example (below.", [])
        assert any(e.error_type == "UnbalancedParentheses" for e in errors)

    def test_detects_extra_closing_paren(self):
        errors = self.rule.check("See the example below).", [])
        assert len(errors) >= 1

    def test_no_error_for_balanced(self):
        assert self.rule.check("See the example (below).", []) == []

    def test_no_error_for_no_parens(self):
        assert self.rule.check("The dog barked.", []) == []

    def test_detects_nested_imbalance(self):
        errors = self.rule.check("A (B (C) D.", [])
        assert len(errors) >= 1

    def test_balanced_nested_no_error(self):
        assert self.rule.check("A (B (C) D).", []) == []

    def test_message_has_heuristic_label(self):
        errors = self.rule.check("Open (paren.", [])
        assert "[HEURISTIC]" in errors[0].message


# ─── ArticleBeforeVowelRule ───────────────────────────────────────────────────

class TestArticleBeforeVowelRule:
    rule = ArticleBeforeVowelRule()

    def test_detects_a_before_apple(self):
        errors = self.rule.check("She ate a apple.", [])
        assert any(e.error_type == "ArticleBeforeVowel" for e in errors)

    def test_detects_a_before_umbrella(self):
        errors = self.rule.check("It was a umbrella.", [])
        assert len(errors) >= 1

    def test_detects_a_before_elephant(self):
        errors = self.rule.check("I saw a elephant.", [])
        assert len(errors) >= 1

    def test_no_error_for_an_before_vowel(self):
        assert self.rule.check("She ate an apple.", []) == []

    def test_no_error_for_a_before_consonant(self):
        assert self.rule.check("She has a dog.", []) == []

    def test_case_insensitive(self):
        errors = self.rule.check("A apple fell down.", [])
        assert len(errors) >= 1

    def test_message_has_heuristic_label(self):
        errors = self.rule.check("a apple", [])
        assert "[HEURISTIC]" in errors[0].message


# ─── CommonConfusionRule ──────────────────────────────────────────────────────

class TestCommonConfusionRule:
    rule = CommonConfusionRule()

    def test_detects_should_of(self):
        errors = self.rule.check("You should of called.", [])
        assert any(e.error_type == "CommonConfusion" for e in errors)

    def test_detects_would_of(self):
        errors = self.rule.check("I would of gone.", [])
        assert len(errors) >= 1

    def test_detects_could_of(self):
        errors = self.rule.check("She could of helped.", [])
        assert len(errors) >= 1

    def test_detects_must_of(self):
        errors = self.rule.check("He must of forgotten.", [])
        assert len(errors) >= 1

    def test_detects_your_welcome(self):
        errors = self.rule.check("Your welcome.", [])
        assert len(errors) >= 1

    def test_detects_their_is(self):
        errors = self.rule.check("Their is a problem.", [])
        assert len(errors) >= 1

    def test_no_error_for_correct_should_have(self):
        assert self.rule.check("You should have called.", []) == []

    def test_no_error_for_correct_you_are_welcome(self):
        assert self.rule.check("You're welcome.", []) == []

    def test_message_has_heuristic_label(self):
        errors = self.rule.check("I should of known.", [])
        assert "[HEURISTIC]" in errors[0].message


# ─── ApostropheRule ───────────────────────────────────────────────────────────

class TestApostropheRule:
    rule = ApostropheRule()

    def test_detects_dont(self):
        errors = self.rule.check("I dont know.", [])
        assert any(e.error_type == "MissingApostrophe" for e in errors)

    def test_detects_doesnt(self):
        errors = self.rule.check("She doesnt care.", [])
        assert len(errors) >= 1

    def test_detects_cant(self):
        errors = self.rule.check("I cant go.", [])
        assert len(errors) >= 1

    def test_detects_theyre(self):
        errors = self.rule.check("Theyre coming.", [])
        assert len(errors) >= 1

    def test_detects_wont(self):
        errors = self.rule.check("He wont help.", [])
        assert len(errors) >= 1

    def test_no_error_for_correct_contraction(self):
        assert self.rule.check("I don't know.", []) == []

    def test_no_error_for_clean_sentence(self):
        assert self.rule.check("The dog barked.", []) == []

    def test_message_has_heuristic_label(self):
        errors = self.rule.check("I cant go.", [])
        assert "[HEURISTIC]" in errors[0].message


# ─── DoubleNegationRule ───────────────────────────────────────────────────────

class TestDoubleNegationRule:
    rule = DoubleNegationRule()

    def test_detects_dont_have_no(self):
        errors = self.rule.check("I don't have no money.", [])
        assert any(e.error_type == "DoubleNegation" for e in errors)

    def test_detects_never_said_nothing(self):
        errors = self.rule.check("She never said nothing.", [])
        assert len(errors) >= 1

    def test_detects_cant_find_nobody(self):
        errors = self.rule.check("I can't find nobody.", [])
        assert len(errors) >= 1

    def test_no_error_for_single_negation(self):
        assert self.rule.check("I don't have any money.", []) == []

    def test_no_error_for_clean_sentence(self):
        assert self.rule.check("She said something.", []) == []

    def test_message_has_heuristic_label(self):
        errors = self.rule.check("I don't know nothing.", [])
        assert "[HEURISTIC]" in errors[0].message


# ─── CommaAfterIntroductoryPhraseRule ─────────────────────────────────────────

class TestCommaAfterIntroductoryPhraseRule:
    rule = CommaAfterIntroductoryPhraseRule()

    def test_detects_however_no_comma(self):
        errors = self.rule.check("However the dog barked.", [])
        assert any(e.error_type == "MissingIntroductoryComma" for e in errors)

    def test_detects_therefore_no_comma(self):
        errors = self.rule.check("Therefore we left early.", [])
        assert len(errors) >= 1

    def test_detects_furthermore_no_comma(self):
        errors = self.rule.check("Furthermore the evidence is clear.", [])
        assert len(errors) >= 1

    def test_no_error_when_comma_present(self):
        assert self.rule.check("However, the dog barked.", []) == []

    def test_no_error_for_therefore_with_comma(self):
        assert self.rule.check("Therefore, we left early.", []) == []

    def test_no_error_for_non_introductory_word(self):
        assert self.rule.check("The dog barked loudly.", []) == []

    def test_detects_thus_no_comma(self):
        errors = self.rule.check("Thus the problem was solved.", [])
        assert len(errors) >= 1

    def test_message_has_heuristic_label(self):
        errors = self.rule.check("However the situation changed.", [])
        assert "[HEURISTIC]" in errors[0].message


# ─── CyrillicVowelRule ────────────────────────────────────────────────────────

class TestCyrillicVowelRule:
    rule = CyrillicVowelRule()

    def test_detects_consonant_only_token(self):
        errors = self.rule.check("Тоа е мрк збор.", [])
        assert any(e.error_type == "CyrillicNoVowel" for e in errors)

    def test_no_error_for_normal_cyrillic_word(self):
        assert self.rule.check("Лисицата скокна.", []) == []

    def test_no_error_for_single_char_token(self):
        assert self.rule.check("А тоа е точно.", []) == []

    def test_detects_multiple_vowelless_tokens(self):
        errors = self.rule.check("Збрв крст.", [])
        vowelless = [e for e in errors if e.error_type == "CyrillicNoVowel"]
        assert len(vowelless) >= 2

    def test_no_error_for_empty_string(self):
        assert self.rule.check("", []) == []

    def test_message_has_heuristic_label(self):
        errors = self.rule.check("Тоа е мрк.", [])
        assert "[HEURISTIC]" in errors[0].message


# ─── HomoglyphRule ────────────────────────────────────────────────────────────

class TestHomoglyphRule:
    rule = HomoglyphRule()

    def test_detects_latin_a_in_cyrillic_word(self):
        sentence = "Тоa е точно."   # 'a' in 'Тоa' is Latin U+0061
        errors = self.rule.check(sentence, [])
        assert any(e.error_type == "Homoglyph" for e in errors)

    def test_detects_latin_o_in_cyrillic_text(self):
        sentence = "Тoj oтиде дома."  # 'o' chars are Latin U+006F
        errors = self.rule.check(sentence, [])
        assert len(errors) >= 1

    def test_no_error_for_pure_cyrillic(self):
        assert self.rule.check("Лисицата скокна.", []) == []

    def test_no_error_for_pure_latin(self):
        assert self.rule.check("The dog barked.", []) == []

    def test_no_error_for_empty_string(self):
        assert self.rule.check("", []) == []

    def test_message_has_heuristic_label(self):
        sentence = "Тоa е точно."
        errors = self.rule.check(sentence, [])
        if errors:
            assert "[HEURISTIC]" in errors[0].message
