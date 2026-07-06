"""
Unit tests for MacedonianChecker.

All test sentences use real Macedonian Cyrillic text.  Each test targets
one specific error type.  Mixed-script tests are in their own class because
MixedScriptRule is uniquely Macedonian (it has no English counterpart).
"""

import pytest

from analyzer.factory import CheckerFactory


@pytest.fixture(scope="module")
def mk():
    return CheckerFactory.get("mk")


# ─── Sentence capitalization ──────────────────────────────────────────────────

class TestMacedonianCapitalization:
    def test_detects_lowercase_cyrillic_start(self, mk):
        errors = mk.check_sentence("лисицата брзо скокна преку мрзливото куче.")
        types = [e.error_type for e in errors]
        assert "Capitalization" in types

    def test_no_error_for_uppercase_cyrillic_start(self, mk):
        errors = mk.check_sentence("Лисицата брзо скокна преку мрзливото куче.")
        cap = [e for e in errors if e.error_type == "Capitalization"]
        assert cap == []

    def test_message_contains_heuristic_label(self, mk):
        errors = mk.check_sentence("таа отиде на пазар.")
        cap = [e for e in errors if e.error_type == "Capitalization"]
        assert cap and "[HEURISTIC]" in cap[0].message


# ─── Double space ─────────────────────────────────────────────────────────────

class TestMacedonianDoubleSpace:
    def test_detects_double_space(self, mk):
        errors = mk.check_sentence("Лисицата брзо  скокна преку куче.")
        types = [e.error_type for e in errors]
        assert "DoubleSpace" in types

    def test_no_error_for_single_spaces(self, mk):
        errors = mk.check_sentence("Лисицата брзо скокна преку куче.")
        ds = [e for e in errors if e.error_type == "DoubleSpace"]
        assert ds == []


# ─── Space before punctuation ─────────────────────────────────────────────────

class TestMacedonianSpaceBeforePunctuation:
    def test_detects_space_before_comma(self, mk):
        errors = mk.check_sentence("Таа купи јаболки ,портокали и банани.")
        types = [e.error_type for e in errors]
        assert "SpaceBeforePunctuation" in types

    def test_no_error_for_correct_punctuation(self, mk):
        errors = mk.check_sentence("Таа купи јаболки, портокали и банани.")
        sbp = [e for e in errors if e.error_type == "SpaceBeforePunctuation"]
        assert sbp == []


# ─── Missing end punctuation ──────────────────────────────────────────────────

class TestMacedonianMissingEndPunctuation:
    def test_detects_missing_period(self, mk):
        errors = mk.check_sentence("Лисицата брзо скокна преку куче")
        types = [e.error_type for e in errors]
        assert "MissingEndPunctuation" in types

    def test_no_error_with_period(self, mk):
        errors = mk.check_sentence("Лисицата брзо скокна преку куче.")
        ep = [e for e in errors if e.error_type == "MissingEndPunctuation"]
        assert ep == []

    def test_no_error_with_question_mark(self, mk):
        errors = mk.check_sentence("Зошто лисицата скокна?")
        ep = [e for e in errors if e.error_type == "MissingEndPunctuation"]
        assert ep == []


# ─── Repeated words ───────────────────────────────────────────────────────────

class TestMacedonianRepeatedWords:
    def test_detects_repeated_cyrillic_word(self, mk):
        errors = mk.check_sentence("Таа таа отиде на пазар.")
        types = [e.error_type for e in errors]
        assert "RepeatedWord" in types

    def test_detects_repeated_word_in_middle(self, mk):
        errors = mk.check_sentence("Времето денес е е многу убаво.")
        types = [e.error_type for e in errors]
        assert "RepeatedWord" in types

    def test_no_error_for_unique_words(self, mk):
        errors = mk.check_sentence("Лисицата брзо скокна преку куче.")
        rw = [e for e in errors if e.error_type == "RepeatedWord"]
        assert rw == []


# ─── Mixed script ─────────────────────────────────────────────────────────────

class TestMacedonianMixedScript:
    def test_detects_latin_word_in_cyrillic_text(self, mk):
        errors = mk.check_sentence("Таа отиде на pazar да купи зеленчук.")
        types = [e.error_type for e in errors]
        assert "MixedScript" in types

    def test_detects_multiple_latin_words(self, mk):
        errors = mk.check_sentence("Тој е mnogu добар student.")
        mixed = [e for e in errors if e.error_type == "MixedScript"]
        assert len(mixed) >= 2

    def test_no_mixed_script_in_pure_cyrillic(self, mk):
        errors = mk.check_sentence("Лисицата брзо скокна преку мрзливото куче.")
        mixed = [e for e in errors if e.error_type == "MixedScript"]
        assert mixed == []

    def test_mixed_script_message_contains_heuristic_label(self, mk):
        errors = mk.check_sentence("Таа отиде на pazar.")
        mixed = [e for e in errors if e.error_type == "MixedScript"]
        assert mixed and "[HEURISTIC]" in mixed[0].message


# ─── Clean sentences ──────────────────────────────────────────────────────────

class TestMacedonianCleanSentence:
    STRUCTURAL_TYPES = {
        "DoubleSpace", "RepeatedWord", "MissingEndPunctuation",
        "SpaceBeforePunctuation", "Capitalization", "MixedScript",
    }

    def test_clean_sentence_no_structural_errors(self, mk):
        errors = mk.check_sentence(
            "Лисицата брзо скокна преку мрзливото куче."
        )
        structural = [e for e in errors if e.error_type in self.STRUCTURAL_TYPES]
        assert structural == []

    def test_check_sentence_always_returns_list(self, mk):
        result = mk.check_sentence("Здраво свет.")
        assert isinstance(result, list)
