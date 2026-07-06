"""
Importing this package triggers registration of all language checkers.

To add a new language:
    1. Create  analyzer/languages/<lang>/  with checker.py + rules/
    2. Add     `from . import <lang>`  below
    3. Done — CheckerFactory.get("<lang>") will work everywhere.
"""

from . import english, macedonian, turkish  # noqa: F401
