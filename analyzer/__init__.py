"""
analyzer package

Importing this package bootstraps the entire system:
  from . import languages
causes Python to run analyzer/languages/__init__.py which imports each
language sub-package, each of which calls CheckerFactory.register().

After this one import, CheckerFactory.get("en") and CheckerFactory.get("mk")
are available anywhere in the process — including inside ProcessPoolExecutor
worker processes, because workers import analyzer.execution which causes
Python to load the parent package analyzer, re-executing this file.
"""

from . import languages  # noqa: F401 — side-effect: registers all checkers
