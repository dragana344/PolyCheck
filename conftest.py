"""
Root-level pytest conftest.

pytest finds this file first, adds its directory (the project root) to
sys.path, and executes it.  Importing `analyzer` here triggers
CheckerFactory registration for all languages before any test runs.
"""

import sys
import os

# Explicitly insert the project root so imports work regardless of how
# pytest is invoked (e.g. from within the tests/ subdirectory).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import analyzer  # noqa: F401, E402 — side-effect: registers all checkers
