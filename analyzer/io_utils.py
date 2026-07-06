"""
File I/O and sentence splitting.

Kept separate from core.py so that the TextAnalyzer (and the parallel worker
function) never need to import pathlib or touch the filesystem — clean
separation between I/O and computation.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List


def read_texts(path: Path) -> List[str]:
    """
    Return a list of raw text strings.
    - If path is a file, return a single-element list.
    - If path is a directory, recursively find all *.txt files and return
      one string per file (sorted by path for reproducibility).
    """
    if path.is_file():
        return [path.read_text(encoding="utf-8", errors="ignore")]

    texts: List[str] = []
    for p in sorted(path.rglob("*.txt")):
        texts.append(p.read_text(encoding="utf-8", errors="ignore"))
    return texts


def split_sentences(texts: List[str]) -> List[str]:
    """
    Split each text into sentences on newlines and on '.', '!', or '?'
    followed by whitespace.  Empty/whitespace-only strings are dropped.
    """
    sentences: List[str] = []
    for text in texts:
        for line in text.splitlines():
            sentences.extend(re.split(r"(?<=[.!?])\s+", line))
    return [s.strip() for s in sentences if s.strip()]
