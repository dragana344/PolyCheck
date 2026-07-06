"""
Auto-registers EnglishChecker into CheckerFactory when this package is imported.

This runs once per process.  In the main process it happens via:
    analyzer/__init__.py → from . import languages → english/__init__.py

In each ProcessPoolExecutor worker it happens because importing
analyzer.execution causes Python to first load the parent package analyzer,
which re-runs analyzer/__init__.py and reaches this file again.
"""

from analyzer.factory import CheckerFactory
from analyzer.languages.english.checker import EnglishChecker

CheckerFactory.register(EnglishChecker)
