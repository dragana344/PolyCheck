#!/usr/bin/env python3
"""
run_benchmarks.py — Performance benchmark with selectable execution mode.

Run from the project root:
    python benchmarks/run_benchmarks.py                        # parallel only (default)
    python benchmarks/run_benchmarks.py --mode sequential      # sequential only
    python benchmarks/run_benchmarks.py --mode both            # side-by-side comparison
    python benchmarks/run_benchmarks.py --language mk --workers 8
    python benchmarks/run_benchmarks.py --sizes 1000 5000 25000
    python benchmarks/run_benchmarks.py --runs 5               # average over 5 repetitions
"""

from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path
from typing import List, Optional

# ── ensure project root is importable ────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent))

import analyzer  # noqa: F401, E402 — trigger CheckerFactory registration

from benchmarks.dataset_generator import BENCHMARK_SIZES, generate
from analyzer.execution import run_parallel, run_sequential


# ─────────────────────────────────────────────────────────────────────────────
# Core benchmark logic
# ─────────────────────────────────────────────────────────────────────────────

def _separator(widths: List[int], char: str = "-", join: str = "--+--") -> str:
    return join.join(char * w for w in widths)


def _fmt_time(mean: float, std: float) -> str:
    """Format 'mean ± std' compactly, e.g. '1.2345 ± 0.0123'."""
    return f"{mean:.4f} ±{std:.4f}"


def _warmup(language: str, mode: str, workers: int, chunk_size: int) -> None:
    """Run a small dataset once to warm up worker processes and OS file cache."""
    warmup_sentences = generate(language, 200, seed=0)
    if mode in ("sequential", "both"):
        run_sequential(warmup_sentences, language)
    if mode in ("parallel", "both"):
        run_parallel(warmup_sentences, language, workers=workers, chunk_size=chunk_size)


def run_benchmark(
    language: str,
    mode: str,
    workers: int,
    chunk_size: int,
    sizes: Optional[List[int]] = None,
    seed: int = 42,
    runs: int = 3,
) -> None:
    if sizes is None:
        sizes = BENCHMARK_SIZES

    # Build columns based on mode
    if mode == "sequential":
        col_widths = [8, 22, 8]
        headers    = ["Size", "Seq (s) mean±std", "Errors"]
    elif mode == "parallel":
        col_widths = [8, 22, 8]
        headers    = ["Size", "Par (s) mean±std", "Errors"]
    else:  # both
        col_widths = [8, 22, 22, 10, 8]
        headers    = ["Size", "Seq (s) mean±std", "Par (s) mean±std", "Speedup", "Errors"]

    print()
    print(f"  Language : {language}")
    print(f"  Mode     : {mode}")
    if mode in ("parallel", "both"):
        print(f"  Workers  : {workers}")
        print(f"  Chunks   : {chunk_size} sentences/chunk")
    print(f"  Seed     : {seed}")
    print(f"  Runs     : {runs} (mean ± std reported)")
    print()

    print("  Warming up ...", flush=True)
    _warmup(language, mode, workers, chunk_size)
    print("  Warmup done.")
    print()

    print("  " + "  |  ".join(h.rjust(w) for h, w in zip(headers, col_widths)))
    print("  " + _separator(col_widths))

    for size in sizes:
        sentences = generate(language, size, seed=seed)

        if mode == "sequential":
            times = [run_sequential(sentences, language)[1] for _ in range(runs)]
            errors = run_sequential(sentences, language)[0]
            row = [
                str(size).rjust(col_widths[0]),
                _fmt_time(statistics.mean(times), statistics.stdev(times) if runs > 1 else 0.0).rjust(col_widths[1]),
                str(len(errors)).rjust(col_widths[2]),
            ]

        elif mode == "parallel":
            times = [run_parallel(sentences, language, workers=workers, chunk_size=chunk_size)[1] for _ in range(runs)]
            errors = run_parallel(sentences, language, workers=workers, chunk_size=chunk_size)[0]
            row = [
                str(size).rjust(col_widths[0]),
                _fmt_time(statistics.mean(times), statistics.stdev(times) if runs > 1 else 0.0).rjust(col_widths[1]),
                str(len(errors)).rjust(col_widths[2]),
            ]

        else:  # both
            seq_times = [run_sequential(sentences, language)[1] for _ in range(runs)]
            par_results = [run_parallel(sentences, language, workers=workers, chunk_size=chunk_size) for _ in range(runs)]
            par_times = [r[1] for r in par_results]
            errors = par_results[-1][0]
            seq_mean = statistics.mean(seq_times)
            par_mean = statistics.mean(par_times)
            speedup = seq_mean / par_mean if par_mean > 0 else float("inf")
            row = [
                str(size).rjust(col_widths[0]),
                _fmt_time(seq_mean, statistics.stdev(seq_times) if runs > 1 else 0.0).rjust(col_widths[1]),
                _fmt_time(par_mean, statistics.stdev(par_times) if runs > 1 else 0.0).rjust(col_widths[2]),
                f"{speedup:.2f}x".rjust(col_widths[3]),
                str(len(errors)).rjust(col_widths[4]),
            ]

        print("  " + "  |  ".join(row))

    print()
    print("  Notes:")
    if mode in ("sequential", "both"):
        print("  - 'Seq' = single-process sequential run.")
    if mode in ("parallel", "both"):
        print("  - 'Par' = ProcessPoolExecutor with the specified worker count.")
    if mode == "both":
        print("  - 'Speedup' < 1x at small sizes is expected (process-spawn overhead).")
    print("  - 'Errors' counts all heuristic flags, not only true errors.")
    print(f"  - Times are mean ± std over {runs} runs after a warmup pass.")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="Performance benchmark with selectable execution mode.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python benchmarks/run_benchmarks.py                          # parallel (default)
  python benchmarks/run_benchmarks.py --mode sequential        # sequential only
  python benchmarks/run_benchmarks.py --mode both              # compare side-by-side
  python benchmarks/run_benchmarks.py --mode parallel --workers 8
  python benchmarks/run_benchmarks.py --language mk --sizes 1000 5000 25000
  python benchmarks/run_benchmarks.py --runs 5                 # 5 repetitions per size
""",
    )
    ap.add_argument(
        "--mode",
        choices=["sequential", "parallel", "both"],
        default="parallel",
        help="Execution mode to benchmark. Default: parallel.",
    )
    ap.add_argument(
        "--language",
        choices=["en", "mk"],
        action="append",
        dest="languages",
        default=None,
        metavar="LANG",
        help="Language to benchmark (repeatable). Default: en mk.",
    )
    ap.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Worker process count for parallel mode. Default: 4.",
    )
    ap.add_argument(
        "--chunk-size",
        type=int,
        default=200,
        metavar="N",
        help="Sentences per chunk. Default: 200.",
    )
    ap.add_argument(
        "--sizes",
        type=int,
        nargs="+",
        default=None,
        metavar="N",
        help=f"Override default dataset sizes. Default: {BENCHMARK_SIZES}",
    )
    ap.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for dataset generation. Default: 42.",
    )
    ap.add_argument(
        "--runs",
        type=int,
        default=3,
        help="Number of timed repetitions per size (mean ± std reported). Default: 3.",
    )
    return ap


def main() -> None:
    args = _build_parser().parse_args()
    languages = args.languages or ["en", "mk"]
    sizes     = args.sizes or BENCHMARK_SIZES

    print("=" * 60)
    print("  MULTILINGUAL CHECKER — PERFORMANCE BENCHMARK")
    print("=" * 60)

    for lang in languages:
        print(f"\n{'─' * 60}")
        run_benchmark(
            language=lang,
            mode=args.mode,
            workers=args.workers,
            chunk_size=args.chunk_size,
            sizes=sizes,
            seed=args.seed,
            runs=args.runs,
        )

    print("=" * 60)
    print("  Done.")
    print("=" * 60)


if __name__ == "__main__":
    main()
