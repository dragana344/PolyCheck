from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import List

from .base_rule import BaseRule
from .models import DetectedError


class BaseLanguageChecker(ABC):
    """
    Abstract base for every language checker.

    Subclasses must implement:
        language_code  – ISO 639-1 code, e.g. "en", "mk", "tr"
        _build_rules() – return the list of BaseRule instances for this language

    Subclasses may override:
        tokenize()     – language-specific word splitting
                         (default: Unicode word characters, 2+ chars, lowercased)

    The rules list is built once in __init__ so JSON files are loaded only
    once per checker instance, not on every call to check_sentence().
    """

    def __init__(self) -> None:
        self._rules: List[BaseRule] = self._build_rules()

    @property
    @abstractmethod
    def language_code(self) -> str:
        """ISO 639-1 language code."""
        ...

    @abstractmethod
    def _build_rules(self) -> List[BaseRule]:
        """Instantiate and return all rules for this language."""
        ...

    @property
    def rules(self) -> List[BaseRule]:
        return self._rules

    def tokenize(self, sentence: str) -> List[str]:
        """
        Default tokenizer: Unicode word characters, minimum 2 characters,
        lowercased.  Override this in language subclasses when script or
        morphology requires different splitting logic.
        """
        return re.findall(r"\w{2,}", sentence.lower())

    def check_sentence(self, sentence: str) -> List[DetectedError]:
        """Run all rules against one sentence and return merged errors."""
        tokens = self.tokenize(sentence)
        errors: List[DetectedError] = []
        for rule in self._rules:
            errors.extend(rule.check(sentence, tokens))
        return errors
