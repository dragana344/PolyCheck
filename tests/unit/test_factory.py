"""
Unit tests for CheckerFactory.

Verifies:
  - Correct checker returned for registered language codes
  - ValueError raised for unregistered language codes
  - Factory returns a fresh instance on each call
  - available_languages() lists all registered codes
"""

import pytest

from analyzer.factory import CheckerFactory


class TestCheckerFactoryRetrieval:
    def test_get_english_checker(self):
        checker = CheckerFactory.get("en")
        assert checker.language_code == "en"

    def test_get_macedonian_checker(self):
        checker = CheckerFactory.get("mk")
        assert checker.language_code == "mk"

    def test_language_code_is_case_insensitive(self):
        checker = CheckerFactory.get("EN")
        assert checker.language_code == "en"

    def test_unsupported_language_raises_value_error(self):
        with pytest.raises(ValueError, match="No checker registered"):
            CheckerFactory.get("zz")

    def test_unsupported_language_error_lists_available(self):
        """Error message should name the languages that ARE available."""
        with pytest.raises(ValueError) as exc_info:
            CheckerFactory.get("xx")
        msg = str(exc_info.value)
        assert "en" in msg
        assert "mk" in msg


class TestCheckerFactoryInstances:
    def test_returns_fresh_instance_each_call(self):
        a = CheckerFactory.get("en")
        b = CheckerFactory.get("en")
        assert a is not b

    def test_available_languages_includes_en_and_mk(self):
        langs = CheckerFactory.available_languages()
        assert "en" in langs
        assert "mk" in langs

    def test_available_languages_returns_sorted_list(self):
        langs = CheckerFactory.available_languages()
        assert langs == sorted(langs)
