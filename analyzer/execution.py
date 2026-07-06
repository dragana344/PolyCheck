"""
Sequential and parallel execution runners.

Parallelism design notes
------------------------
ProcessPoolExecutor is used (not ThreadPoolExecutor) because the grammar
check is CPU-bound: Levenshtein runs a tight double loop with no I/O.
Threads in CPython are serialised by the GIL for pure-Python CPU work, so
they would give no speedup.  Separate processes sidestep the GIL entirely.

Worker function requirements
-----------------------------
`_analyze_chunk` must be:
  1. A top-level function (not a lambda, closure, or bound method) so that
     the multiprocessing pickler can locate it by module + qualname.
  2. Self-contained: it must re-create the checker inside the worker
     process.  Checker instances hold open file handles / compiled regexes
     that are NOT safely picklable across process boundaries.
  3. Trigger language registration before calling CheckerFactory.get().
     This happens automatically: importing analyzer.execution causes Python
     to first import the parent package analyzer, which runs
     analyzer/__init__.py → `from . import languages`, registering all
     checkers in every worker process.
"""

from __future__ import annotations

import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Tuple

from .core import TextAnalyzer
from .factory import CheckerFactory
from .models import DetectedError


# ---------------------------------------------------------------------------
# Worker function (top-level so it is picklable)
# ---------------------------------------------------------------------------

def _analyze_chunk(sentences: List[str], language_code: str) -> List[DetectedError]:
    """
    Entry point for each worker process.

    Called by ProcessPoolExecutor.  Re-creates the checker here because
    checker instances must not cross process boundaries (regex/file state).
    CheckerFactory is already populated at this point because importing this
    module triggers analyzer/__init__.py which registers all languages.
    """
    checker = CheckerFactory.get(language_code)
    return TextAnalyzer(checker).analyze(sentences)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _chunk_list(items: List[str], size: int) -> List[List[str]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


# ---------------------------------------------------------------------------
# Public runners
# ---------------------------------------------------------------------------

def run_sequential(
    sentences: List[str],
    language_code: str,
) -> Tuple[List[DetectedError], float]:
    checker = CheckerFactory.get(language_code)
    analyzer = TextAnalyzer(checker)
    start = time.perf_counter()
    errors = analyzer.analyze(sentences)
    return errors, time.perf_counter() - start


def run_parallel(
    sentences: List[str],
    language_code: str,
    workers: int,
    chunk_size: int,
) -> Tuple[List[DetectedError], float]:
    """
    Distribute sentences across `workers` processes using ProcessPoolExecutor.

    Each worker receives a chunk of sentences and the language code string
    (a plain str — trivially picklable).  Results are collected as futures
    complete (as_completed preserves no order, which is fine here).
    """
    chunks = _chunk_list(sentences, chunk_size)
    errors: List[DetectedError] = []

    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(_analyze_chunk, chunk, language_code)
            for chunk in chunks
        ]
        for future in as_completed(futures):
            errors.extend(future.result())

    return errors, time.perf_counter() - start
