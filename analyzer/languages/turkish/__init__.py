"""
Auto-registers TurkishChecker into CheckerFactory when this package is imported.
See analyzer/languages/english/__init__.py for the explanation of when/why
this runs in both the main process and worker processes.
"""

from analyzer.factory import CheckerFactory
from analyzer.languages.turkish.checker import TurkishChecker

CheckerFactory.register(TurkishChecker)
