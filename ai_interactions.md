# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF8)

> Challenge 2: Feature Expansion, a High Score tracker.

**What task did you give the agent?**

"Use your AI coding assistant agentically to plan and implement a meaningful new feature, such as a High Score tracker that saves your best score to a file or a Guess History sidebar." The agent chose the High Score tracker and planned it before editing: keep the file logic in `logic_utils.py` so it is testable without Streamlit, track one best score per difficulty, and show it in the sidebar.

**What did the agent do?**

1. Read `app.py` to see where the win happens and where the sidebar is built.
2. `logic_utils.py`: added `load_high_scores` and `save_high_score` (JSON file `highscores.json`). A missing, unreadable or malformed file returns `{}`, and a tie is not a new record.
3. `app.py`: imported the new functions, added a sidebar "Best score" metric, and on a win calls `save_high_score` and shows "New high score!".
4. `tests/test_game_logic.py`: added tests for saving and beating a score, per-difficulty tracking, a negative first score, and four corrupt-file contents.
5. `.gitignore`: added `highscores.json` so local game data is not committed.
6. Ran `python -m pytest` (31 passed), then drove the real `app.py` with Streamlit AppTest in a temp folder: the sidebar started at "None yet", a win with score 90 showed "New high score!" and updated the sidebar to 90, an identical second win did not show the message, and `highscores.json` contained `{"Normal": 90}`.

**Files modified:** `logic_utils.py`, `app.py`, `tests/test_game_logic.py`, `.gitignore`, `README.md` (test output and stretch feature note), `ai_interactions.md`.

**What did you have to verify or fix manually?**

- Design choice rather than a bug fix: the sidebar is drawn before the game logic runs, so the best-score metric goes into an `st.sidebar.empty()` placeholder that is refreshed after a win. Without it the sidebar would show the old score until the next click. The agent also added `highscores.json` to `.gitignore` so local scores are not committed.
- `python -m pytest` was re-run after the change (31 passed). I made no manual edits to the agent's code.
- Played the game in the browser on Normal and Easy: hint boxes and temperature labels, the progress bar and session table, rejected input (`abc`, `0`, `-5`) adding no row, `3.7` counted as 3, Show hint off hiding the hint columns, a win giving balloons and an immediate sidebar update, "You already won" on a second submit, and New Game resetting everything.
- High score checks in the browser: a win scoring 0 was saved, a later first-attempt win scoring 90 replaced it, switching to Easy showed "None yet", and a loss on Easy (score -30) saved nothing. `highscores.json` ended up as `{"Normal": 90}`.
- Not checked by hand: a win that scores lower than the saved best (the pytest high-score tests cover it) and the Hard difficulty.

---

## Test Generation (SF7)

> Document how you used AI to help generate or improve tests.

| Edge Case | Prompt Used | AI-Suggested Test | Did It Pass? | Your Reasoning |
|-----------|-------------|-------------------|--------------|----------------|
| Negative numbers (`-5`, `-0`, `-0.5`, `-999999`) | "Use your AI coding assistant to identify three potential 'edge case' inputs (e.g., negative numbers, decimals, or extremely large values) that might still break your game. Use your AI coding assistant to generate a suite of pytest cases that verify your game handles these inputs gracefully." | `test_parse_guess_rejects_negative_numbers` | Yes | A leading minus sign is valid for `int()`, so only the range check stands between a negative guess and the game; `-0.5` also truncates to 0. |
| Decimals (`3.7`, `42.0`, `100.9`, `0.9`, `101.0`) | Same prompt as above | `test_parse_guess_truncates_decimals_in_range`, `test_parse_guess_rejects_decimals_that_land_out_of_range` | Yes | `parse_guess` does `int(float(raw))`, which truncates instead of rounding, so `100.9` is accepted as 100 and `0.9` becomes an out-of-range 0. |
| Extremely large values (20-digit int, 5000-digit int, `1e5`, `1.0e999`, `inf`, `nan`) | Same prompt as above | `test_parse_guess_handles_extremely_large_values_without_crashing` | Yes | Huge digit strings, float overflow to infinity and `nan` could raise an uncaught exception and crash the Streamlit app instead of showing an error message. |

---

## Linting & Style (SF9)

> Challenge 3: Professional Documentation and Linting.

**Prompt used:**

```
Add professional grade docstrings to every function in logic_utils.py. Then
review your code for PEP 8 style compliance and apply fixes to resolve any
formatting or naming issues it identifies.
```

**Linting output before:**

Run with `ruff check --select E,W,F,N,D,I --ignore D203,D213 --output-format concise app.py logic_utils.py tests/test_game_logic.py` (E/W = pycodestyle, F = pyflakes, N = pep8-naming, D = pydocstyle, I = import order; ruff's default 88-column limit).

```
app.py:1:1: D100 Missing docstring in public module
app.py:1:1: I001 [*] Import block is un-sorted or un-formatted
app.py:3:89: E501 Line too long (108 > 88)
app.py:38:89: E501 Line too long (158 > 88)
app.py:42:5: D103 Missing docstring in public function
app.py:44:88: E501 Line too long (96 > 88)
app.py:53:89: E501 Line too long (105 > 88)
app.py:65:89: E501 Line too long (136 > 88)
app.py:77:89: E501 Line too long (102 > 88)
app.py:104:89: E501 Line too long (125 > 88)
app.py:123:89: E501 Line too long (119 > 88)
app.py:126:89: E501 Line too long (139 > 88)
logic_utils.py:1:1: D100 Missing docstring in public module
logic_utils.py:2:8: F401 [*] `os` imported but unused
logic_utils.py:9:89: E501 Line too long (130 > 88)
logic_utils.py:20:5: D212 [*] Multi-line docstring summary should start at the first line
logic_utils.py:25:89: E501 Line too long (115 > 88)
logic_utils.py:48:5: D212 [*] Multi-line docstring summary should start at the first line
logic_utils.py:53:89: E501 Line too long (138 > 88)
logic_utils.py:64:89: E501 Line too long (142 > 88)
logic_utils.py:82:89: E501 Line too long (131 > 88)
logic_utils.py:90:89: E501 Line too long (92 > 88)
logic_utils.py:94:89: E501 Line too long (99 > 88)
tests/test_game_logic.py:1:1: D100 Missing docstring in public module
tests/test_game_logic.py:12:89: E501 Line too long (164 > 88)
tests/test_game_logic.py:14:5: D103 Missing docstring in public function
tests/test_game_logic.py:19:5: D103 Missing docstring in public function
tests/test_game_logic.py:25:5: D103 Missing docstring in public function
tests/test_game_logic.py:31:5: D103 Missing docstring in public function
tests/test_game_logic.py:46:5: D103 Missing docstring in public function
tests/test_game_logic.py:51:5: D103 Missing docstring in public function
tests/test_game_logic.py:54:5: D103 Missing docstring in public function
tests/test_game_logic.py:62:5: D103 Missing docstring in public function
tests/test_game_logic.py:72:5: D103 Missing docstring in public function
tests/test_game_logic.py:79:5: D103 Missing docstring in public function
tests/test_game_logic.py:84:5: D103 Missing docstring in public function
tests/test_game_logic.py:94:89: E501 Line too long (90 > 88)
tests/test_game_logic.py:95:5: D103 Missing docstring in public function
tests/test_game_logic.py:104:5: D103 Missing docstring in public function
tests/test_game_logic.py:114:5: D103 Missing docstring in public function
tests/test_game_logic.py:120:5: D103 Missing docstring in public function
Found 41 errors.
[*] 4 fixable with the `--fix` option.
```

**Linting output after:**

Run with `--line-length 79` (PEP 8's limit) and `--ignore D203,D213,D413`. The 18 remaining findings are all missing docstrings (D100/D103), none in `logic_utils.py`; see below.

```
$ python -m ruff check --select E,W,F,N,I --line-length 79 app.py logic_utils.py tests/test_game_logic.py
All checks passed!

$ python -m ruff check --select E,W,F,N,D,I --ignore D203,D213,D413 --line-length 79 --output-format concise logic_utils.py
All checks passed!

$ python -m ruff check --select E,W,F,N,D,I --ignore D203,D213,D413 --line-length 79 --output-format concise app.py tests/test_game_logic.py
app.py:1:1: D100 Missing docstring in public module
app.py:47:5: D103 Missing docstring in public function
tests/test_game_logic.py:1:1: D100 Missing docstring in public module
tests/test_game_logic.py:17:5: D103 Missing docstring in public function
tests/test_game_logic.py:23:5: D103 Missing docstring in public function
tests/test_game_logic.py:31:5: D103 Missing docstring in public function
tests/test_game_logic.py:39:5: D103 Missing docstring in public function
tests/test_game_logic.py:56:5: D103 Missing docstring in public function
tests/test_game_logic.py:62:5: D103 Missing docstring in public function
tests/test_game_logic.py:66:5: D103 Missing docstring in public function
tests/test_game_logic.py:75:5: D103 Missing docstring in public function
tests/test_game_logic.py:87:5: D103 Missing docstring in public function
tests/test_game_logic.py:97:5: D103 Missing docstring in public function
tests/test_game_logic.py:103:5: D103 Missing docstring in public function
tests/test_game_logic.py:128:5: D103 Missing docstring in public function
tests/test_game_logic.py:138:5: D103 Missing docstring in public function
tests/test_game_logic.py:150:5: D103 Missing docstring in public function
tests/test_game_logic.py:159:5: D103 Missing docstring in public function
Found 18 errors.

$ python -m pytest -q
31 passed
```

**Changes applied:**

Applied:
- Added a module docstring and Google-style docstrings (summary, Args, Returns) to all 6 functions in `logic_utils.py`. This also fixed the two docstrings whose summary started on the second line (D212).
- Removed the unused `import os` (F401).
- Wrapped about 20 lines longer than 79 characters, mostly the long `FIX` comments, in `logic_utils.py`, `app.py` and the tests. The comment wording did not change.
- Added return type hints so the signatures match the docstrings.
- Changed `parse_guess` to catch `(ValueError, OverflowError)` instead of a bare `Exception`. Those are the errors `int()` and `float()` can raise here, and the edge-case tests still pass.
- Ran `ruff format`, which added the two blank lines between test functions and rewrapped a few long calls, and sorted the imports in `app.py`.
- The naming check (N) found nothing. Names were already snake_case and UPPER_CASE.

Not applied:
- D413 (blank line after the last docstring section). It is a strict pydocstyle rule that is not in PEP 257 or the Google convention.
- D100/D103 (missing docstrings) in `app.py` and the tests. The task was docstrings for `logic_utils.py`, and the test names already say what they check, so about 16 one-line docstrings would be noise.

---

## Model Comparison (SF11)

> Challenge 5: AI Model Comparison. Four models, each given the identical prompt in a fresh chat: **ChatGPT (Free version)**, **Google Gemini 3.1 Pro**, **Microsoft Copilot (Chat, basic)** and **Claude Opus 5.5**. An extra Claude Haiku 4.5 run is at the bottom.

**Task given to all models:**

The "wrong hints on even attempts" bug from Phase 1. The prompt contained the original buggy `app.py` submit block (which set `secret = str(st.session_state.secret)` on even attempts) and the original `check_guess` (with its `try/except TypeError` string fallback), described the symptom (guessing 9 against a secret of 10 says "Go LOWER"), and asked: "Please fix this bug. Give (1) the corrected code, and (2) an explanation of why it was happening. Keep the whole answer under 300 words."

Each model's `check_guess` was run for every guess from 1 to 100 against a secret of 50, checking the outcome and hint direction, plus 9 vs 10. Each was also checked with `ruff --select RET` (return-statement style).

| | ChatGPT (Free) | Google Gemini 3.1 Pro | Microsoft Copilot (Chat, basic) | Claude Opus 5.5 |
|-|---------|---------------|-------------------|-----------------|
| **Fix summary** | Removed the string conversion and fallback, fixed hint text, added `int()` casts in `check_guess`, and returned a full replacement submit block. | Removed the string conversion and fallback, fixed hint text. Minimal submit block with a comment. | Removed the string conversion and fallback, fixed hint text. Minimal submit block with a comment. | Removed the string conversion and fallback, fixed hint text. Minimal changes, no casts. |
| **Hint tests (guesses 1-100, secret 50)** | 0 wrong | 0 wrong | 0 wrong | 0 wrong |
| **More Pythonic?** | Weakest. The `int()` casts hide the cause, `check_guess("abc", 10)` raises `ValueError`, and `📈 Go LOWER!` pairs a rising-chart emoji with a "lower" hint. | Good. Matching emoji, helpful comments, but uses `elif` after `return` (RET505). | Good. Matching emoji, but uses `else` after `return` (RET505) and the answer is formatted as plain text, so code blocks are hard to read. | Best. Flat early returns with no `elif`/`else` after a `return`, matching emoji, no casts. Same shape as the final `check_guess` in `logic_utils.py`. |
| **Explained the "why"** | Clear step-by-step walkthrough of `9 > "10"` raising `TypeError`, the except branch, and `"9" > "10"` being `True`. Mentions the swapped hints only in the last sentence. | Clearest overall. Names the two bugs up front, then traces the exact 9-vs-10 case through both of them. | Names both bugs, quotes the offending code for each, shows `"9" > "10"`. Shorter, no combined trace. | Names both bugs and explains why the symptom looks odd/even-dependent. Also gave `"5" > "40"`. A little dense. |
| **Risk in what it handed back** | Its submit block appends raw invalid input to `history` and counts an attempt before validating, which brings back two bugs fixed earlier. | None found. | None found. | None found. |

**Which did you prefer and why?**

Claude Opus for the code and Gemini for the explanation. All four fixed the actual bugs and passed the hint checks, so they differ in quality, not correctness. Opus's `check_guess` was the most Pythonic: early returns and no `else` after a `return`. Gemini and Copilot were close behind. Gemini explained the "why" best by tracing the 9-vs-10 case through both bugs instead of listing them separately. ChatGPT came last. Its `int()` casts treat the symptom, and its extra submit-block rewrite brought back two bugs already fixed in this project (`history.append(raw_guess)` on bad input, and `attempts += 1` before validation). Its `check_guess` still passed the tests, and the two regressions only showed up when reading the code. When a model rewrites more than was asked, the extra code needs checking against the earlier fixes.

Limits: this is one bug and one run per model, so it says how they did on this task and nothing more. The ChatGPT (Free), Gemini 3.1 Pro and Copilot (Chat, basic) answers are pasted exactly as returned. The tiers differ (free and basic tiers against Gemini Pro and Opus), so the comparison is not like-for-like.

### Extra: Claude Haiku 4.5

Run as a separate tool-less sub-agent with the same prompt. It removed the string conversion and said `check_guess` could stay unchanged. That is incomplete: the swapped hint text stays, so a guess that is too high would still say "Go HIGHER", and `test_hints_point_toward_secret_regression` would fail.
