#!/usr/bin/env python3
"""
accuracy_eval.py — Precision/recall evaluation of the rule-based checkers.

Ground truth comes from benchmarks/dataset_generator.generate_labeled():
every sentence pool was hand-written to contain exactly one kind of error
(or none, for the *_CORRECT pool), so the pool a sentence was drawn from
is itself the ground-truth label. No external annotation is needed.

Matching rule
-------------
For a sentence built for error type E:
    - TP[E] += 1 if the checker flags E on that sentence.
    - FN[E] += 1 if it does not.
    (Any *other* error types the checker also flags on this sentence are
    ignored — they are not evaluated as false positives, since the
    sentence is not guaranteed to be clean of unrelated issues.)
For a clean (_CORRECT) sentence:
    - Every error_type the checker flags counts as FP[that type].
    - TN += 1 if nothing is flagged.

This means precision/recall are measured against the templates each rule
was designed to catch, not against an independent, human-annotated corpus.
That is a real limitation worth stating explicitly wherever these numbers
are reported.

Usage:
    python benchmarks/accuracy_eval.py --language en --size 3000
    python benchmarks/accuracy_eval.py --language en --language mk --language tr
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

import analyzer  # noqa: F401, E402 — trigger CheckerFactory registration

from analyzer.factory import CheckerFactory  # noqa: E402
from benchmarks.dataset_generator import generate_labeled  # noqa: E402


def evaluate(language: str, size: int, seed: int) -> None:
    checker = CheckerFactory.get(language)
    dataset = generate_labeled(language, size, seed=seed)

    tp: Dict[str, int] = defaultdict(int)
    fp: Dict[str, int] = defaultdict(int)
    fn: Dict[str, int] = defaultdict(int)
    tn = 0

    for sentence, expected in dataset:
        flagged = {e.error_type for e in checker.check_sentence(sentence)}

        if expected is None:
            if flagged:
                for etype in flagged:
                    fp[etype] += 1
            else:
                tn += 1
        else:
            if expected in flagged:
                tp[expected] += 1
            else:
                fn[expected] += 1

    rule_names = sorted(set(tp) | set(fp) | set(fn))

    col_widths = [30, 6, 6, 6, 10, 10, 10]
    headers = ["Rule", "TP", "FP", "FN", "Precision", "Recall", "F1"]

    print()
    print(f"  Language : {language}")
    print(f"  Dataset  : {size} sentences (seed={seed})")
    print()
    print("  " + "  |  ".join(h.ljust(w) if i == 0 else h.rjust(w) for i, (h, w) in enumerate(zip(headers, col_widths))))
    print("  " + "--+--".join("-" * w for w in col_widths))

    total_tp = total_fp = total_fn = 0
    for rule in rule_names:
        t, f, n = tp[rule], fp[rule], fn[rule]
        total_tp += t
        total_fp += f
        total_fn += n
        precision = t / (t + f) if (t + f) > 0 else float("nan")
        recall = t / (t + n) if (t + n) > 0 else float("nan")
        f1 = (2 * precision * recall / (precision + recall)
              if (t + f) > 0 and (t + n) > 0 and (precision + recall) > 0
              else float("nan"))
        row = [
            rule.ljust(col_widths[0]),
            str(t).rjust(col_widths[1]),
            str(f).rjust(col_widths[2]),
            str(n).rjust(col_widths[3]),
            (f"{precision:.3f}" if precision == precision else "N/A").rjust(col_widths[4]),
            (f"{recall:.3f}" if recall == recall else "N/A").rjust(col_widths[5]),
            (f"{f1:.3f}" if f1 == f1 else "N/A").rjust(col_widths[6]),
        ]
        print("  " + "  |  ".join(row))

    print("  " + "--+--".join("-" * w for w in col_widths))

    overall_p = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else float("nan")
    overall_r = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else float("nan")
    overall_f1 = (2 * overall_p * overall_r / (overall_p + overall_r)
                  if overall_p == overall_p and overall_r == overall_r and (overall_p + overall_r) > 0
                  else float("nan"))
    clean_total = tn + sum(fp.values())
    fp_rate = sum(fp.values()) / clean_total if clean_total > 0 else float("nan")

    print(f"  Overall (micro-averaged): Precision={overall_p:.3f}  Recall={overall_r:.3f}  F1={overall_f1:.3f}")
    print(f"  Clean-sentence false-positive rate: {fp_rate:.3f}  (TN={tn}, FP on clean={sum(fp.values())})")
    print()


def _build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Precision/recall evaluation of the rule-based checkers.")
    ap.add_argument("--language", action="append", dest="languages", default=None, metavar="LANG",
                     help="Language to evaluate (repeatable). Default: en mk tr.")
    ap.add_argument("--size", type=int, default=30000, help="Number of sentences to evaluate. Default: 30000.")
    ap.add_argument("--seed", type=int, default=42, help="Random seed. Default: 42.")
    return ap


def main() -> None:
    args = _build_parser().parse_args()
    languages = args.languages or ["en", "mk", "tr"]

    print("=" * 70)
    print("  RULE-BASED CHECKER — PRECISION / RECALL EVALUATION")
    print("=" * 70)

    for lang in languages:
        evaluate(lang, args.size, args.seed)

    print("=" * 70)


if __name__ == "__main__":
    main()
