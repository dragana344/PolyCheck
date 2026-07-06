from __future__ import annotations

from typing import List

from .base_checker import BaseLanguageChecker
from .models import DetectedError


class TextAnalyzer:
    """
    Runs a language checker over a flat list of sentences.

    This class is intentionally thin — it knows nothing about files,
    CLI arguments, parallelism, or language selection.  All of that
    lives in execution.py and main.py.

    Keeping it separate means the parallel worker function in execution.py
    can instantiate TextAnalyzer inside each subprocess without dragging
    in CLI or I/O state.
    """

    def __init__(self, checker: BaseLanguageChecker) -> None:
        self._checker = checker

    def analyze(self, sentences: List[str]) -> List[DetectedError]:
        errors: List[DetectedError] = []
        for sentence in sentences:
            errors.extend(self._checker.check_sentence(sentence))
        return errors
