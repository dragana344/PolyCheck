#!/usr/bin/env python3
"""
main.py — CLI entry point for the multilingual grammar/spell checker.

Preserves the original CLI surface (--mode, --input, --workers, --chunk-size)
and adds --language so the user can select the language checker.

Usage examples:
    python main.py --mode sequential --input corpus.txt --language en
    python main.py --mode parallel   --input texts/    --language mk --workers 4
    python main.py --mode parallel   --input corpus.txt --language en --workers 8 --chunk-size 100
"""

import argparse
import sys
from pathlib import Path

# Importing analyzer triggers CheckerFactory registration for all languages.
import analyzer  # noqa: F401
from analyzer.execution import run_parallel, run_sequential
from analyzer.factory import CheckerFactory
from analyzer.io_utils import read_texts, split_sentences


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="Multilingual rule-based text checker with parallel execution.",
    )
    ap.add_argument(
        "--mode",
        choices=["sequential", "parallel"],
        required=True,
        help="Run analysis sequentially or in parallel (ProcessPoolExecutor).",
    )
    ap.add_argument(
        "--input",
        required=True,
        metavar="PATH",
        help="Path to a .txt file or a directory of .txt files.",
    )
    ap.add_argument(
        "--language",
        default="en",
        metavar="LANG",
        help=(
            f"ISO 639-1 language code for the checker to use. "
            f"Available: {', '.join(CheckerFactory.available_languages())}. "
            f"Default: en"
        ),
    )
    ap.add_argument(
        "--workers",
        type=int,
        default=4,
        metavar="N",
        help="Number of worker processes (parallel mode only). Default: 4.",
    )
    ap.add_argument(
        "--chunk-size",
        type=int,
        default=200,
        metavar="N",
        help="Sentences per work chunk sent to each worker. Default: 200.",
    )
    return ap


def main() -> None:
    args = build_parser().parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: input path does not exist: {input_path}", file=sys.stderr)
        sys.exit(1)

    texts = read_texts(input_path)
    sentences = split_sentences(texts)

    if not sentences:
        print("No sentences found in input.  Nothing to analyse.")
        return

    if args.mode == "sequential":
        errors, elapsed = run_sequential(sentences, args.language)
        actual_workers = 1
    else:
        errors, elapsed = run_parallel(
            sentences, args.language, args.workers, args.chunk_size
        )
        actual_workers = args.workers

    print("\n=== RUN SUMMARY ===")
    print(f"Mode:            {args.mode}")
    print(f"Language:        {args.language}")
    print(f"Workers:         {actual_workers}")
    print(f"Sentences:       {len(sentences)}")
    print(f"Detected errors: {len(errors)}")
    print(f"Elapsed (s):     {elapsed:.6f}")

    if errors:
        print("\n=== DETECTED ERRORS (first 20) ===")
        for err in errors[:20]:
            print(f"  [{err.error_type}] {err.message}")
            print(f"    in: {err.sentence[:80]!r}")


if __name__ == "__main__":
    main()
