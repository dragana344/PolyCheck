"""
Unit tests for TextAnalyzer and the execution runners.

Verifies:
  - TextAnalyzer.analyze() returns a list of DetectedError
  - Empty input returns empty list
  - Sequential and parallel modes produce the same error count
  - Elapsed time is positive
  - Return types are correct
"""

import pytest

from analyzer.core import TextAnalyzer
from analyzer.execution import run_parallel, run_sequential
from analyzer.factory import CheckerFactory
from analyzer.models import DetectedError


@pytest.fixture(scope="module")
def en_checker():
    return CheckerFactory.get("en")


@pytest.fixture(scope="module")
def mk_checker():
    return CheckerFactory.get("mk")


# ─── TextAnalyzer ─────────────────────────────────────────────────────────────

class TestTextAnalyzer:
    def test_returns_list(self, en_checker):
        ta = TextAnalyzer(en_checker)
        result = ta.analyze(["The dog barked."])
        assert isinstance(result, list)

    def test_errors_are_detected_error_instances(self, en_checker):
        ta = TextAnalyzer(en_checker)
        result = ta.analyze(["The quick  brown fox."])
        for item in result:
            assert isinstance(item, DetectedError)

    def test_empty_input_returns_empty_list(self, en_checker):
        ta = TextAnalyzer(en_checker)
        assert ta.analyze([]) == []

    def test_multiple_sentences_aggregated(self, en_checker):
        ta = TextAnalyzer(en_checker)
        sentences = [
            "the dog barked.",           # capitalization
            "The quick  brown fox.",     # double space
            "She went to to the store.", # repeated word
        ]
        errors = ta.analyze(sentences)
        types = {e.error_type for e in errors}
        assert "Capitalization" in types
        assert "DoubleSpace" in types
        assert "RepeatedWord" in types

    def test_macedonian_analyzer(self, mk_checker):
        ta = TextAnalyzer(mk_checker)
        errors = ta.analyze(["Таа отиде на pazar да купи зеленчук."])
        types = [e.error_type for e in errors]
        assert "MixedScript" in types


# ─── Sequential runner ────────────────────────────────────────────────────────

class TestRunSequential:
    def test_returns_two_tuple(self):
        result = run_sequential(["Hello world."], "en")
        assert isinstance(result, tuple) and len(result) == 2

    def test_errors_is_list(self):
        errors, _ = run_sequential(["Hello world."], "en")
        assert isinstance(errors, list)

    def test_elapsed_is_positive(self):
        _, elapsed = run_sequential(["The cat sat on the mat."] * 10, "en")
        assert elapsed > 0

    def test_detects_errors_in_sequence(self):
        sentences = ["the cat sat on the mat."] * 5
        errors, _ = run_sequential(sentences, "en")
        types = {e.error_type for e in errors}
        assert "Capitalization" in types


# ─── Parallel runner ──────────────────────────────────────────────────────────

class TestRunParallel:
    def test_returns_two_tuple(self):
        result = run_parallel(["Hello world."], "en", workers=2, chunk_size=1)
        assert isinstance(result, tuple) and len(result) == 2

    def test_errors_is_list(self):
        errors, _ = run_parallel(["Hello world."], "en", workers=2, chunk_size=1)
        assert isinstance(errors, list)

    def test_elapsed_is_positive(self):
        sentences = ["The cat sat on the mat."] * 10
        _, elapsed = run_parallel(sentences, "en", workers=2, chunk_size=5)
        assert elapsed > 0


# ─── Sequential vs parallel consistency ──────────────────────────────────────

class TestSequentialParallelConsistency:
    """
    Both modes must produce the same number of errors for the same input.
    Order is not guaranteed in parallel mode, so only counts are compared.
    """

    _SENTENCES = [
        "The quick  brown fox.",       # double space
        "She went to to the store.",   # repeated word
        "the cat sat on the mat.",     # capitalization
        "The cat sat on the mat",      # missing end punct
        "She bought apples ,oranges.", # space before punct
    ] * 10

    def test_en_counts_match(self):
        seq_errors, _ = run_sequential(self._SENTENCES, "en")
        par_errors, _ = run_parallel(self._SENTENCES, "en", workers=2, chunk_size=10)
        assert len(seq_errors) == len(par_errors)

    def test_mk_counts_match(self):
        sentences = [
            "Таа таа отиде на пазар.",
            "лисицата скокна.",
            "Лисицата брзо  скокна.",
            "Таа отиде на pazar.",
        ] * 5
        seq_errors, _ = run_sequential(sentences, "mk")
        par_errors, _ = run_parallel(sentences, "mk", workers=2, chunk_size=5)
        assert len(seq_errors) == len(par_errors)
