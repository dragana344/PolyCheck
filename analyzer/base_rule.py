from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from .models import DetectedError


class BaseRule(ABC):
    """
    Abstract base for every language rule.

    Each rule receives both the raw sentence and a pre-tokenized list of
    tokens (produced by the language checker's tokenizer).  Rules should
    not re-tokenize; use the tokens list for word-level checks and the raw
    sentence for pattern-level checks.

    Contract:
        - Return [] when no errors are found (never return None).
        - Prefix the message with "[HEURISTIC]" when the rule is
          approximation-based rather than grammar-spec-based.
    """

    #: Short, human-readable identifier for the rule.
    name: str = ""

    @abstractmethod
    def check(self, sentence: str, tokens: List[str]) -> List[DetectedError]:
        """Analyze one sentence and return any detected errors."""
        ...
