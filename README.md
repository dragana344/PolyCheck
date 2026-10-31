# PolyCheck

[![tests](https://github.com/dragana344/PolyCheck/actions/workflows/tests.yml/badge.svg)](https://github.com/dragana344/PolyCheck/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)

A rule-based grammar and spelling checker for **English**, **Turkish** and **Macedonian**, built to study how much a CPU-bound text-checking workload gains from multiprocess parallelism.

- **25 rules across 3 languages:** 8 shared structural rules plus 17 language-specific rules (Turkish apostrophe and suffix rules, Cyrillic/Latin homoglyph detection for Macedonian, and others)
- **Sequential and parallel execution modes:** the parallel mode splits sentences into chunks across a `ProcessPoolExecutor`, giving a **~5.4× speedup** on 30,000 sentences with 10 workers
- **Pluggable architecture:** add a language or rule without touching the core
- **No runtime dependencies:** standard library only, 212 unit tests

> **Note:** PolyCheck is a heuristic checker, not an NLP model or full grammar parser. Every approximate rule labels its output `[HEURISTIC]`, and some false positives are expected.

---

## Quick start

```bash
git clone https://github.com/dragana344/PolyCheck.git
cd PolyCheck
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # only pytest, for the test suite

python main.py --mode sequential --input sample.txt --language en
```

Example output:

```
=== RUN SUMMARY ===
Mode:            sequential
Language:        en
Workers:         1
Sentences:       3
Detected errors: 8
Elapsed (s):     0.000108

=== DETECTED ERRORS (first 20) ===
  [ArticleBeforeVowel] [HEURISTIC] 'a example' — use 'an' before a vowel sound.
    in: 'This is a example sentence.'
  [CommonConfusion] [HEURISTIC] 'their is/are/was/were' is commonly confused — did you mean 'there'?
    in: 'I cant believe their is a error here  .'
  [MissingApostrophe] [HEURISTIC] 'cant' looks like a contraction missing an apostrophe.
    in: 'I cant believe their is a error here  .'
  [RepeatedWord] [HEURISTIC] Word 'the' appears twice consecutively.
    in: 'She went to the the store'
  ...
```

### CLI options

| Argument | Default | Description |
|---|---|---|
| `--mode` | required | `sequential` or `parallel` |
| `--input` | required | A `.txt` file, or a directory of `.txt` files |
| `--language` | `en` | `en`, `tr` or `mk` |
| `--workers` | `4` | Number of worker processes (parallel mode only) |
| `--chunk-size` | `200` | Sentences per work chunk (parallel mode only) |

```bash
python main.py --mode parallel --input corpus.txt --language tr --workers 8 --chunk-size 100
```

---

## Architecture

```
main.py              CLI
   │
io_utils.py          read files, split into sentences
   │
execution.py         run_sequential() / run_parallel()  ── ProcessPoolExecutor
   │
core.py              TextAnalyzer.analyze(sentences)
   │
base_checker.py      tokenize() → run every rule on each sentence
   │
base_rule.py         BaseRule.check() → List[DetectedError]
```

Design decisions:

- **Processes, not threads.** Rule checking is CPU-bound, so threads would serialize on the GIL. The worker function is a top-level function so it can be pickled.
- **Stateless workers.** Each worker builds its own checker from the `CheckerFactory` registry, so no checker object is ever sent between processes.
- **Factory registry.** Each language package registers its checker when it is imported, so the core code never names a specific language.
- **One data model.** `DetectedError` is the only type passed between layers.

```
analyzer/
├── core.py, execution.py, factory.py, ...   core framework
└── languages/
    ├── shared/        language-agnostic rules
    ├── english/       checker + rules + wordlist
    ├── turkish/       checker + rules + wordlist
    └── macedonian/    checker + rules + wordlist
benchmarks/            dataset generator, timing and accuracy evaluation
tests/unit/            pytest suite
```

---

## Rules

### Shared (structural)

| Rule | Detects |
|---|---|
| `SentenceCapitalizationRule` | First letter of the sentence is not uppercase |
| `DoubleSpaceRule` | Two or more consecutive spaces |
| `SpaceBeforePunctuationRule` | Space before `, . ! ? ; :` |
| `MissingEndPunctuationRule` | Sentence does not end with `. ! ?` |
| `RepeatedWordRule` | Same word twice in a row (not used for Turkish, where reduplication such as *yavaş yavaş* is valid) |
| `ConsecutivePunctuationRule` | Two or more punctuation characters in a row |
| `UnbalancedQuotesRule` | Unmatched straight or curly quotes |
| `UnbalancedParenthesesRule` | Mismatched parentheses |

### English

| Rule | Detects |
|---|---|
| `ArticleBeforeVowelRule` | *a* before a vowel sound (*a example*), with exceptions like *a university* |
| `CommonConfusionRule` | Commonly confused pairs (*their/there*, *your/you're*, …) |
| `ApostropheRule` | Contractions missing an apostrophe (*cant*, *dont*) |
| `DoubleNegationRule` | Double negatives |
| `CommaAfterIntroductoryPhraseRule` | Missing comma after *However*, *Therefore*, … |
| `LevenshteinSpellRule` | Word 1–2 edits away from a common English word |

An optional `EnhancedSpellRule` (frequency-weighted, based on `pyspellchecker`) can be swapped in for `LevenshteinSpellRule`.

### Turkish

| Rule | Detects |
|---|---|
| `ProperNounApostropheRule` | Missing apostrophe before a suffix on a proper noun (*Ankarada* → *Ankara'da*) |
| `QuestionParticleRule` | Question particle *mı/mi/mu/mü* written attached to the previous word |
| `NumberSuffixRule` | Missing apostrophe before a suffix on a number (*2024te* → *2024'te*) |
| `BircokRule` | *bir çok* → *birçok*, *birşey* → *bir şey* |
| `HerSeyRule` | *herşey* → *her şey* |
| `LevenshteinSpellRule` | Misspellings, with suffix stripping to handle Turkish agglutination |

### Macedonian

| Rule | Detects |
|---|---|
| `CyrillicSpellRule` | Misspellings, recognizing definite-article suffixes |
| `MixedScriptRule` | Latin letters inside Cyrillic text |
| `HomoglyphRule` | Latin characters that look identical to Cyrillic ones (e.g. Latin `a` vs Cyrillic `а`) |
| `CyrillicVowelRule` | Vowelless words, except valid ones with syllabic *р* (*крв*, *мрк*) |
| `CommaBeforeConjunctionRule` | Missing comma before *но*, *ама*, *туку* |

---

## Benchmarks

```bash
python benchmarks/run_benchmarks.py                          # parallel, all languages
python benchmarks/run_benchmarks.py --mode both --language en  # sequential vs parallel
python benchmarks/run_benchmarks.py --workers 2 --runs 1 --sizes 1000 5000
```

Each benchmark dataset is sampled from hand-written sentence pools; each pool contains either correct sentences or one specific kind of error. Datasets range from 100 to 30,000 sentences.

| Dataset size | Behaviour |
|---|---|
| ≤ 500 sentences | Parallel is slower, because starting worker processes costs more than it saves |
| 1,000 – 5,000 | Break-even point; depends on the machine |
| ≥ 10,000 | Clear speedup, reaching **5.35× – 5.52×** at 30,000 sentences with 10 workers (consistent across all three languages) |

### Accuracy evaluation

```bash
python benchmarks/accuracy_eval.py --language en --size 3000
```

Reports precision and recall per error type, using the sentence pool each sentence came from as its label. These numbers measure each rule against the templates it was designed for, not against an independent human-annotated corpus.

---

## Tests

```bash
pytest        # 212 tests
pytest -v tests/unit/test_turkish_checker.py
```

The suite covers the factory, every rule in isolation, each language checker with positive and negative cases, and a check that sequential and parallel runs detect the same number of errors.

---

## Extending

**Add a language:** create `analyzer/languages/<lang>/checker.py` with a subclass of `BaseLanguageChecker` that sets `language_code`, implements `_build_rules()` and optionally overrides `tokenize()`. Register it in `<lang>/__init__.py` with `CheckerFactory.register(YourChecker)`, then add `from . import <lang>` to `analyzer/languages/__init__.py`.

**Add a rule:** subclass `BaseRule`, implement `check(sentence, tokens) -> List[DetectedError]`, prefix approximate messages with `[HEURISTIC]`, and add the rule to the relevant checker's `_build_rules()`.

