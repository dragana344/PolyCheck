# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies (only pytest is required)
pip install -r requirements.txt

# Run all tests
pytest

# Run a single test file
pytest tests/unit/test_factory.py -v

# Run the checker (sequential)
python main.py --mode sequential --input corpus.txt --language en

# Run the checker (parallel, 4 workers)
python main.py --mode parallel --input corpus.txt --language en --workers 4 --chunk-size 200

# Run benchmarks (default: parallel mode, both languages, all 9 sizes)
python benchmarks/run_benchmarks.py
python benchmarks/run_benchmarks.py --language en --workers 8
# Fast iteration: 2 workers, 1 run, small sizes
python benchmarks/run_benchmarks.py --workers 2 --runs 1 --sizes 1000 5000
# Compare sequential vs parallel side-by-side
python benchmarks/run_benchmarks.py --mode both --language en
```

## Architecture

The project is a modular, rule-based multilingual text checker with sequential and parallel execution modes. All rules are heuristics — error messages are prefixed with `[HEURISTIC]`.

**Execution flow:**

```
main.py (CLI) → io_utils.py (read files, split sentences)
    → execution.py: run_sequential() / run_parallel()
        → core.py: TextAnalyzer.analyze(sentences)
            → base_checker.py: BaseLanguageChecker.check_sentence()
                → base_rule.py: BaseRule.check() → List[DetectedError]
```

**Key design points:**

- `CheckerFactory` (`analyzer/factory.py`) is a class-level registry mapping ISO 639-1 codes to checker classes. Language registration happens automatically at import time via `analyzer/__init__.py` → `analyzer/languages/__init__.py`.
- Parallelism uses `ProcessPoolExecutor` (not threads) because rule checking is CPU-bound. Worker function `_analyze_chunk` is a top-level function so it is picklable. Each worker recreates its own checker instance — checkers must never cross process boundaries.
- `TextAnalyzer` (`core.py`) is deliberately thin: it knows nothing about files, CLI, parallelism, or language selection.
- `DetectedError` (`models.py`) is the single data model passed between all layers.

**Adding a new language:** create `analyzer/languages/<lang>/checker.py` extending `BaseLanguageChecker` (set `language_code`, implement `_build_rules()`, optionally override `tokenize()`). Add a `__init__.py` that calls `CheckerFactory.register(YourChecker)`, then add `from . import <lang>` to `analyzer/languages/__init__.py`. No other files need changes.

**Adding a new rule:** extend `BaseRule`, implement `check(sentence, tokens) -> List[DetectedError]`, prefix heuristic messages with `[HEURISTIC]`, and add it to `_build_rules()` in the relevant checker. Shared rules live in `analyzer/languages/shared/`.

**Current rule sets (as of checkers, not README):**

Shared (both languages): `SentenceCapitalizationRule`, `DoubleSpaceRule`, `SpaceBeforePunctuationRule`, `MissingEndPunctuationRule`, `RepeatedWordRule`, `ConsecutivePunctuationRule`, `UnbalancedQuotesRule`, `UnbalancedParenthesesRule`

English-specific (14 rules total): `ArticleBeforeVowelRule`, `CommonConfusionRule`, `ApostropheRule`, `DoubleNegationRule`, `CommaAfterIntroductoryPhraseRule`, `LevenshteinSpellRule` (uses `wordlist.json`). `EnhancedSpellRule` exists but is commented out in `_build_rules()` — it's a pyspellchecker-based alternative with frequency weighting and distance-2 matching.

Macedonian-specific (12 rules total): `CyrillicSpellRule` (uses `common_words.json`), `MixedScriptRule`, `CyrillicVowelRule`, `HomoglyphRule`. Tokenizer matches `[Ѐ-ӿ]{2,}` (Cyrillic block, min 2 chars) because Macedonian has many meaningful 2-character words.
