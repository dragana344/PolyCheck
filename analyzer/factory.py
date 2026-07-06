from __future__ import annotations

from typing import Dict, Type

from .base_checker import BaseLanguageChecker


class CheckerFactory:
    """
    Registry that maps ISO 639-1 language codes to checker classes.

    Usage
    -----
    Registration (done once at import time, inside each language's __init__.py):
        CheckerFactory.register(EnglishChecker)

    Retrieval (done at run time, in execution.py):
        checker = CheckerFactory.get("en")

    Adding a new language
    ---------------------
    1. Create  analyzer/languages/<lang>/checker.py  with a class that extends
       BaseLanguageChecker and sets language_code = "<lang>".
    2. Create  analyzer/languages/<lang>/__init__.py  that calls
       CheckerFactory.register(<YourChecker>).
    3. Import the new package in  analyzer/languages/__init__.py.
    That is all — no changes needed in factory.py or execution.py.
    """

    _registry: Dict[str, Type[BaseLanguageChecker]] = {}

    @classmethod
    def register(cls, checker_class: Type[BaseLanguageChecker]) -> None:
        """
        Register a checker class under its own language_code.
        Creates a temporary instance only to read language_code; the instance
        is discarded immediately (no rules are loaded at this point because
        _build_rules() is called in __init__, but the cost is negligible and
        happens only once per process startup).
        """
        code = checker_class().language_code
        cls._registry[code] = checker_class

    @classmethod
    def get(cls, language_code: str) -> BaseLanguageChecker:
        """
        Return a fresh checker instance for *language_code*.
        Raises ValueError if the language has not been registered.
        """
        code = language_code.lower()
        if code not in cls._registry:
            available = ", ".join(sorted(cls._registry)) or "(none registered)"
            raise ValueError(
                f"No checker registered for language '{code}'. "
                f"Available: {available}"
            )
        return cls._registry[code]()

    @classmethod
    def available_languages(cls) -> list[str]:
        return sorted(cls._registry.keys())
