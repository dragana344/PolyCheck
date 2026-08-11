# PolyCheck — Multilingual Heuristic Text Checker

A modular, rule-based multilingual text checker with sequential and parallel
(multiprocess) execution modes. Supports English, Turkish, and Macedonian out of the box.

> **Honesty disclaimer:**  
> This is a **heuristic rule-based checker**, not a full grammar parser or NLP model.
> Every rule that approximates correctness is explicitly labelled `[HEURISTIC]`
> in its output message. False positives are expected and are normal.

---

## Project structure

```
paralelno test/
├── main.py                          CLI entry point
├── requirements.txt
├── pytest.ini
├── conftest.py                      pytest root conftest (path + registration)
├── README.md
│
├── analyzer/
│   ├── __init__.py                  bootstraps CheckerFactory registration
│   ├── models.py                    DetectedError dataclass
│   ├── base_rule.py                 BaseRule abstract class
│   ├── base_checker.py              BaseLanguageChecker abstract class
│   ├── factory.py                   CheckerFactory registry
│   ├── core.py                      TextAnalyzer orchestrator
│   ├── execution.py                 sequential + parallel runners
│   ├── io_utils.py                  file reading + sentence splitting
│   ├── utils.py                     shared algorithms (Levenshtein)
│   └── languages/
│       ├── __init__.py              imports all language packages
│       ├── shared/                  language-agnostic rules
│       │   ├── consecutive_punctuation_rule.py
│       │   ├── double_space_rule.py
│       │   ├── missing_end_punctuation_rule.py
│       │   ├── repeated_word_rule.py
│       │   ├── sentence_capitalization_rule.py
│       │   ├── space_before_punctuation_rule.py
│       │   ├── unbalanced_parentheses_rule.py
│       │   └── unbalanced_quotes_rule.py
│       ├── english/
│       │   ├── checker.py           EnglishChecker
│       │   └── rules/
│       │       ├── apostrophe_rule.py
│       │       ├── article_before_vowel_rule.py
│       │       ├── comma_after_introductory_phrase_rule.py
│       │       ├── common_confusion_rule.py
│       │       ├── double_negation_rule.py
│       │       ├── enhanced_spell_rule.py   (optional, requires pyspellchecker)
│       │       ├── levenshtein_spell_rule.py
│       │       └── wordlist.json
│       ├── turkish/
│       │   ├── checker.py           TurkishChecker
│       │   └── rules/
│       │       ├── bircok_rule.py
│       │       ├── her_sey_rule.py
│       │       ├── levenshtein_spell_rule.py
│       │       ├── number_suffix_rule.py
│       │       ├── proper_noun_apostrophe_rule.py
│       │       ├── question_particle_rule.py
│       │       └── wordlist.json
│       └── macedonian/
│           ├── checker.py           MacedonianChecker
│           └── rules/
│               ├── comma_before_conjunction_rule.py
│               ├── cyrillic_spell_rule.py
│               ├── cyrillic_vowel_rule.py
│               ├── homoglyph_rule.py
│               ├── mixed_script_rule.py
│               └── common_words.json
│
├── tests/
│   └── unit/
│       ├── test_factory.py
│       ├── test_english_checker.py
│       ├── test_macedonian_checker.py
│       ├── test_turkish_checker.py
│       ├── test_analyzer.py
│       └── test_rules.py
│
└── benchmarks/
    ├── dataset_generator.py         sentence pool generator
    └── run_benchmarks.py            sequential vs parallel timing table
```

---

## Installation

```bash
# Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt
```

No third-party packages are required at runtime — only `pytest` for testing.

---

## Running the checker

```bash
# Sequential mode, English
python main.py --mode sequential --input path/to/file.txt --language en

# Parallel mode, Turkish, 4 workers
python main.py --mode parallel --input path/to/file.txt --language tr --workers 4

# Parallel mode, Macedonian, 8 workers
python main.py --mode parallel --input path/to/texts/ --language mk --workers 8

# Adjust chunk size for parallel mode
python main.py --mode parallel --input corpus.txt --language en \
    --workers 8 --chunk-size 100
```

### CLI arguments

| Argument | Default | Description |
|---|---|---|
| `--mode` | required | `sequential` or `parallel` |
| `--input` | required | Path to `.txt` file or directory of `.txt` files |
| `--language` | `en` | ISO 639-1 language code (`en`, `tr`, `mk`) |
| `--workers` | `4` | Number of worker processes (parallel mode only) |
| `--chunk-size` | `200` | Sentences per work chunk (parallel mode only) |

---

## Running tests

```bash
# Run all unit tests from the project root
pytest

# Verbose output
pytest -v

# Run a single test file
pytest tests/unit/test_factory.py -v
pytest tests/unit/test_english_checker.py -v
pytest tests/unit/test_turkish_checker.py -v
pytest tests/unit/test_macedonian_checker.py -v
pytest tests/unit/test_analyzer.py -v
pytest tests/unit/test_rules.py -v
```

### What the tests cover

| File | Tests |
|---|---|
| `test_factory.py` | CheckerFactory: correct checker returned, ValueError for unknown language, fresh instances, sorted language list |
| `test_english_checker.py` | English-specific rules tested with positive and negative cases |
| `test_turkish_checker.py` | Turkish-specific rules including suffix handling and agglutinative morphology cases |
| `test_macedonian_checker.py` | Macedonian rules including Cyrillic-specific, vowel, and mixed-script cases |
| `test_analyzer.py` | TextAnalyzer, run_sequential, run_parallel — type checks, empty input, seq/par count equality |
| `test_rules.py` | Shared rules and language-specific rules tested in isolation |

---

## Running benchmarks

```bash
# Default: all languages, parallel mode, all dataset sizes
python benchmarks/run_benchmarks.py

# English only, 8 workers
python benchmarks/run_benchmarks.py --language en --workers 8

# Compare sequential vs parallel side by side
python benchmarks/run_benchmarks.py --mode both --language en

# Fast iteration: 2 workers, 1 run, small sizes
python benchmarks/run_benchmarks.py --workers 2 --runs 1 --sizes 1000 5000

# Specific sizes for Turkish
python benchmarks/run_benchmarks.py --language tr --sizes 1000 5000 10000 30000
```

### Dataset sizes

`100 · 200 · 300 · 400 · 500 · 1000 · 1500 · 2000 · 2500 · 5000 · 10000 · 15000 · 20000 · 25000 · 30000`

Sentences are generated by weighted random sampling from template pools:

| Category | English | Turkish | Macedonian |
|---|---|---|---|
| Correct sentences | 35 % | 35 % | 30 % |
| Double space | 10 % | 10 % | 10 % |
| Repeated word | 10 % | 10 % | 10 % |
| Missing end punctuation | 15 % | 15 % | 15 % |
| Space before punctuation | 10 % | 10 % | 10 % |
| Typos / spelling errors | 12 % | 6 % | — |
| No capitalization | 8 % | 8 % | 10 % |
| Unbalanced quotes | — | 6 % | — |
| Mixed script (Latin in Cyrillic) | — | — | 15 % |

### Expected benchmark behaviour

- **Small datasets (≤ 300–500 sentences):** Parallel is usually *slower* than sequential due to process-spawn overhead. This is normal and expected and consistent across all three languages.
- **Medium datasets (1 000–5 000):** Breakeven zone; results vary by machine and CPU core count.
- **Large datasets (≥ 10 000):** Parallel speedup becomes clearly visible, reaching approximately 5.35×–5.52× at 30,000 sentences with 10 workers across all three languages.

---

## Rules implemented

### Shared rules (all languages)

| Rule | Description |
|---|---|
| `SentenceCapitalizationRule` | First alphabetic character must be uppercase |
| `DoubleSpaceRule` | Two or more consecutive spaces |
| `SpaceBeforePunctuationRule` | Space immediately before `, . ! ? ; :` |
| `MissingEndPunctuationRule` | Sentence does not end with `. ! ?` |
| `RepeatedWordRule` | Same word appears twice consecutively |
| `ConsecutivePunctuationRule` | Two or more punctuation characters in a row |
| `UnbalancedQuotesRule` | Odd number of double quotes |
| `UnbalancedParenthesesRule` | Mismatched parentheses |

### English-specific rules

| Rule | Description |
|---|---|
| `ArticleBeforeVowelRule` | `a` used before a vowel-starting word instead of `an` |
| `CommonConfusionRule` | Commonly confused word pairs (their/there, your/you're, etc.) |
| `ApostropheRule` | Contractions missing apostrophe |
| `DoubleNegationRule` | Double negation pattern |
| `CommaAfterIntroductoryPhraseRule` | Missing comma after introductory word or phrase |
| `LevenshteinSpellRule` | Token is 1 edit away from a common English word |

### Turkish-specific rules

| Rule | Description |
|---|---|
| `ProperNounApostropheRule` | Proper nouns must use apostrophe before suffixes |
| `QuestionParticleRule` | Question particle `mı/mi/mu/mü` must be written separately |
| `NumberSuffixRule` | Suffixes attached to numbers must use apostrophe |
| `BircokRule` | `birçok` must be written as one word |
| `HerSeyRule` | `her şey` must be written as two words |
| `LevenshteinSpellRule` | Token is 1 edit away from a common Turkish word (with suffix stripping) |

### Macedonian-specific rules

| Rule | Description |
|---|---|
| `CyrillicSpellRule` | Cyrillic token is 1 edit away from a common Macedonian word |
| `CyrillicVowelRule` | Word of 3+ characters contains no Cyrillic vowels (excluding valid vowelless words) |
| `MixedScriptRule` | Latin characters found inside Cyrillic text |
| `HomoglyphRule` | Visually similar Latin characters used in place of Cyrillic |
| `CommaBeforeConjunctionRule` | Missing comma before coordinating conjunctions |

---

## Adding a new language

1. Create `analyzer/languages/<lang>/` directory.
2. Add `checker.py` with a class extending `BaseLanguageChecker`:
   - Set `language_code = "<lang>"`.
   - Override `_build_rules()` to return a list of rule instances.
   - Optionally override `tokenize()` for language-specific word splitting.
3. Add any language-specific rules in `analyzer/languages/<lang>/rules/`.
4. Create `analyzer/languages/<lang>/__init__.py` that calls:
   ```python
   from analyzer.factory import CheckerFactory
   from analyzer.languages.<lang>.checker import YourChecker
   CheckerFactory.register(YourChecker)
   ```
5. Add `from . import <lang>` to `analyzer/languages/__init__.py`.

No other files need to be changed.

---

## Adding a new rule to an existing language

1. Create a new file in `analyzer/languages/<lang>/rules/` (or in
   `analyzer/languages/shared/` if the rule applies to all languages).
2. Implement a class extending `BaseRule`:
   - Set `name = "RuleName"`.
   - Implement `check(sentence, tokens) -> List[DetectedError]`.
   - Prefix the error message with `[HEURISTIC]` if the rule is approximate.
3. Import and instantiate the rule in `<lang>/checker.py`'s `_build_rules()`.

---

## Architecture overview

```
CLI (main.py)
    │
    ▼
io_utils.py          read files + split sentences
    │
    ▼
execution.py         run_sequential() / run_parallel()
    │                ProcessPoolExecutor — CPU-bound work, no GIL bottleneck
    ▼
core.py              TextAnalyzer.analyze(sentences)
    │
    ▼
base_checker.py      BaseLanguageChecker.check_sentence(sentence)
    │                tokenize() → tokens
    │                for each rule: rule.check(sentence, tokens)
    ▼
base_rule.py         BaseRule.check() → List[DetectedError]
```

Parallelism is at the **sentence chunk** level: the sentence list is split
into fixed-size chunks and each chunk is dispatched to a worker process.
Workers are completely stateless — each recreates its own checker instance
from the CheckerFactory registry.
