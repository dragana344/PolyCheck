"""
Unit tests for EnglishChecker.

Each test targets one specific error type.  Structural-rule tests are
kept separate from spell-check tests because LevenshteinSpellRule is
heuristic and can produce false positives on ordinary words.
"""

import pytest

from analyzer.factory import CheckerFactory


@pytest.fixture(scope="module")
def en():
    return CheckerFactory.get("en")


# ─── Sentence capitalization ──────────────────────────────────────────────────

class TestEnglishCapitalization:
    def test_detects_lowercase_start(self, en):
        errors = en.check_sentence("the dog barked at the stranger.")
        types = [e.error_type for e in errors]
        assert "Capitalization" in types

    def test_no_error_for_uppercase_start(self, en):
        errors = en.check_sentence("The dog barked at the stranger.")
        cap = [e for e in errors if e.error_type == "Capitalization"]
        assert cap == []

    def test_message_contains_heuristic_label(self, en):
        errors = en.check_sentence("she went to the market.")
        cap = [e for e in errors if e.error_type == "Capitalization"]
        assert cap and "[HEURISTIC]" in cap[0].message


# ─── Double space ─────────────────────────────────────────────────────────────

class TestEnglishDoubleSpace:
    def test_detects_double_space(self, en):
        errors = en.check_sentence("The quick  brown fox jumps.")
        types = [e.error_type for e in errors]
        assert "DoubleSpace" in types

    def test_no_error_for_single_spaces(self, en):
        errors = en.check_sentence("The quick brown fox jumps.")
        ds = [e for e in errors if e.error_type == "DoubleSpace"]
        assert ds == []


# ─── Space before punctuation ─────────────────────────────────────────────────

class TestEnglishSpaceBeforePunctuation:
    def test_detects_space_before_comma(self, en):
        errors = en.check_sentence("She bought apples ,oranges and bananas.")
        types = [e.error_type for e in errors]
        assert "SpaceBeforePunctuation" in types

    def test_detects_space_before_period(self, en):
        errors = en.check_sentence("He said hello .")
        types = [e.error_type for e in errors]
        assert "SpaceBeforePunctuation" in types

    def test_no_error_for_correct_punctuation(self, en):
        errors = en.check_sentence("She bought apples, oranges, and bananas.")
        sbp = [e for e in errors if e.error_type == "SpaceBeforePunctuation"]
        assert sbp == []


# ─── Missing end punctuation ──────────────────────────────────────────────────

class TestEnglishMissingEndPunctuation:
    def test_detects_missing_period(self, en):
        errors = en.check_sentence("The cat sat on the mat")
        types = [e.error_type for e in errors]
        assert "MissingEndPunctuation" in types

    def test_no_error_for_period(self, en):
        errors = en.check_sentence("The cat sat on the mat.")
        ep = [e for e in errors if e.error_type == "MissingEndPunctuation"]
        assert ep == []

    def test_no_error_for_exclamation(self, en):
        errors = en.check_sentence("The dog barked!")
        ep = [e for e in errors if e.error_type == "MissingEndPunctuation"]
        assert ep == []

    def test_no_error_for_question_mark(self, en):
        errors = en.check_sentence("Did the dog bark?")
        ep = [e for e in errors if e.error_type == "MissingEndPunctuation"]
        assert ep == []


# ─── Repeated words ───────────────────────────────────────────────────────────

class TestEnglishRepeatedWords:
    def test_detects_repeated_word_at_start(self, en):
        errors = en.check_sentence("The the dog barked loudly.")
        types = [e.error_type for e in errors]
        assert "RepeatedWord" in types

    def test_detects_repeated_word_in_middle(self, en):
        errors = en.check_sentence("She went to to the store.")
        types = [e.error_type for e in errors]
        assert "RepeatedWord" in types

    def test_detects_case_insensitive_repetition(self, en):
        errors = en.check_sentence("She She went home.")
        types = [e.error_type for e in errors]
        assert "RepeatedWord" in types

    def test_no_error_for_unique_words(self, en):
        errors = en.check_sentence("The cat sat on the mat.")
        rw = [e for e in errors if e.error_type == "RepeatedWord"]
        assert rw == []


# ─── Spell checking (heuristic Levenshtein) ───────────────────────────────────

class TestEnglishSpellHeuristic:
    def test_detects_single_char_typo(self, en):
        # "thnk" is 1 edit away from "think"
        errors = en.check_sentence("I thnk this is correct.")
        types = [e.error_type for e in errors]
        assert "PossibleSpelling" in types

    def test_detects_multiple_typos(self, en):
        errors = en.check_sentence("She woud like to come tomrrow.")
        spell = [e for e in errors if e.error_type == "PossibleSpelling"]
        assert len(spell) >= 1

    def test_exact_common_word_not_flagged(self, en):
        # "think" is in the wordlist — exact match should not be flagged
        errors = en.check_sentence("I think this is correct.")
        spell = [e for e in errors if e.error_type == "PossibleSpelling"]
        flagged_words = [e.message for e in spell]
        # "think" itself should not appear as a suspected misspelling
        assert not any("'think'" in m and "close to 'think'" in m for m in flagged_words)


# ─── Clean sentences ──────────────────────────────────────────────────────────

class TestEnglishCleanSentence:
    STRUCTURAL_TYPES = {
        "DoubleSpace", "RepeatedWord", "MissingEndPunctuation",
        "SpaceBeforePunctuation", "Capitalization",
    }

    def test_clean_sentence_no_structural_errors(self, en):
        errors = en.check_sentence(
            "She studied hard for the final examination."
        )
        structural = [e for e in errors if e.error_type in self.STRUCTURAL_TYPES]
        assert structural == []

    def test_check_sentence_always_returns_list(self, en):
        result = en.check_sentence("Hello world.")
        assert isinstance(result, list)
