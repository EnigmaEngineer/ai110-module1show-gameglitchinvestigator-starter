# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the app: `python -m streamlit run app.py`
3. Run the tests: `python -m pytest -v`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

**Purpose**

A number guessing game in Streamlit. The game picks a secret number in a range set by the difficulty (Easy 1-20, Normal 1-100, Hard 1-50). You get a limited number of attempts (6, 8 or 5), every guess gets a Higher/Lower hint, and winning in fewer attempts scores more. The best score for each difficulty is saved to a file. The starter code came with deliberate bugs, and the job was to find and fix them with an AI assistant and check its work.

**Bugs found**

| Bug | What happened |
|-----|---------------|
| Backwards hints | A guess above the secret said "Go HIGHER" and one below said "Go LOWER". |
| Secret turned into a string | On even-numbered attempts the secret was converted to text, so numbers were compared like words (`"9" > "10"` is true). |
| No range check | A guess of 0 (or a negative number) was accepted and used an attempt. |
| Off-by-one attempts | The attempt counter started at 1, so Normal ended after 7 guesses instead of 8. |
| Wrong range text and New Game | The prompt always said 1-100 and New Game always picked from 1-100, whatever the difficulty. |
| Old state left behind | After a win or loss the game stayed on "Game over" with the old score and history. Changing difficulty kept the old secret. |
| Invalid input stored in history | Text like `abc` was added to the guess history. |
| Score errors | The win bonus was one attempt short, and "Too High" gave +5 on even attempts. |

**Fixes**

- Moved the game logic from `app.py` into `logic_utils.py` so it can be tested without Streamlit.
- Fixed the hints, and removed the `str(secret)` conversion and the `try/except TypeError` that was hiding it.
- Added the range check to `parse_guess`, started attempts at 0, and stopped counting or storing invalid input.
- Made the prompt and New Game use the difficulty's range, made New Game reset everything, and made a difficulty change start a fresh game.
- Fixed `update_score` (a win gives `100 - 10 * attempt`, minimum 10; a wrong guess costs 5) and rewrote the starter tests, which compared a tuple to a string and could never pass.
- Did the five extra challenges: edge-case tests, a saved high score, docstrings and PEP 8 cleanup, a nicer UI, and a comparison of four AI models. Details are in the sections below and in `ai_interactions.md`. The `# FIX:` comments in the code say what changed and how the AI was involved.

## 📸 Demo Walkthrough

A sample game on **Normal** (range 1-100, 8 attempts) where the secret happens to be **50**. You can see the secret in "Developer Debug Info".

1. The game starts with "Guess a number between 1 and 100. Attempts left: 8", an empty attempts bar (`0 / 8`), and the sidebar showing "Best score (Normal): None yet".
2. You enter **80** and click Submit. The outcome is "Too High", so a **red** box says `Go LOWER!  ❄️ Cool`. The table gets row 1 (`80`, `📉 Too high`, `❄️ Cool`), the bar reads `1 / 8`, and the score drops to **-5**.
3. You enter **30**. The outcome is "Too Low", so a **blue** box says `Go HIGHER!  🌤️ Warm`. Row 2 is added and the score is **-10**.
4. You enter **abc**. The game shows "That is not a number." No row is added, the bar stays at `2 / 8`, and the score does not change. Entering **0** shows "Guess must be between 1 and 100." with the same result.
5. You enter **55**. The outcome is "Too High", so the red box says `Go LOWER!  🌶️ Hot`. Row 3 is added and the score is **-15**.
6. You enter **50**. The outcome is "Win": balloons appear and the green box says `Correct!`. Row 4 shows `🎉 Correct` and `🎯 Correct`. A win on attempt 4 earns `100 - 40 = 60` points, so the final score is **45** (-15 + 60).
7. 45 beats the saved best, so the game shows "New high score!" and the sidebar changes to "Best score (Normal): 45". The score is also written to `highscores.json`.
8. The game is over. Clicking Submit again shows "You already won. Start a new game to play again." Clicking **New Game** picks a new secret and resets the table, attempts bar, score and history, but keeps the saved best score.
9. Had you used all 8 attempts without guessing 50, the game would end with "Out of attempts! The secret was 50." and no score would be saved.

Unticking **Show hint** hides the hint boxes and drops the table to just `#` and `Guess`. A guess within 5% of the secret shows only 🔥 in the Temperature column.

## 🧪 Test Results

Includes the Challenge 1 edge-case suite (negative numbers, decimals, extremely large values) the Challenge 2 high score tests and the Challenge 4 hot/cold tests.

```
$ python -m pytest -v
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.0, pluggy-1.6.0 -- C:\Users\syeds\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe
cachedir: .pytest_cache
collecting ... collected 42 items

tests/test_game_logic.py::test_winning_guess PASSED                      [  2%]
tests/test_game_logic.py::test_guess_too_high PASSED                     [  4%]
tests/test_game_logic.py::test_guess_too_low PASSED                      [  7%]
tests/test_game_logic.py::test_hints_point_toward_secret_regression PASSED [  9%]
tests/test_game_logic.py::test_range_for_difficulty PASSED               [ 11%]
tests/test_game_logic.py::test_parse_guess_valid PASSED                  [ 14%]
tests/test_game_logic.py::test_parse_guess_rejects_out_of_range_and_junk PASSED [ 16%]
tests/test_game_logic.py::test_update_score PASSED                       [ 19%]
tests/test_game_logic.py::test_parse_guess_rejects_negative_numbers[-5] PASSED [ 21%]
tests/test_game_logic.py::test_parse_guess_rejects_negative_numbers[-1] PASSED [ 23%]
tests/test_game_logic.py::test_parse_guess_rejects_negative_numbers[-0] PASSED [ 26%]
tests/test_game_logic.py::test_parse_guess_rejects_negative_numbers[-0.5] PASSED [ 28%]
tests/test_game_logic.py::test_parse_guess_rejects_negative_numbers[-999999] PASSED [ 30%]
tests/test_game_logic.py::test_parse_guess_truncates_decimals_in_range[3.7-3] PASSED [ 33%]
tests/test_game_logic.py::test_parse_guess_truncates_decimals_in_range[42.0-42] PASSED [ 35%]
tests/test_game_logic.py::test_parse_guess_truncates_decimals_in_range[100.9-100] PASSED [ 38%]
tests/test_game_logic.py::test_parse_guess_rejects_decimals_that_land_out_of_range[0.9] PASSED [ 40%]
tests/test_game_logic.py::test_parse_guess_rejects_decimals_that_land_out_of_range[0.0] PASSED [ 42%]
tests/test_game_logic.py::test_parse_guess_rejects_decimals_that_land_out_of_range[101.0] PASSED [ 45%]
tests/test_game_logic.py::test_parse_guess_handles_extremely_large_values_without_crashing[20-digit-int] PASSED [ 47%]
tests/test_game_logic.py::test_parse_guess_handles_extremely_large_values_without_crashing[5000-digit-int] PASSED [ 50%]
tests/test_game_logic.py::test_parse_guess_handles_extremely_large_values_without_crashing[sci-notation] PASSED [ 52%]
tests/test_game_logic.py::test_parse_guess_handles_extremely_large_values_without_crashing[float-overflow] PASSED [ 54%]
tests/test_game_logic.py::test_parse_guess_handles_extremely_large_values_without_crashing[inf] PASSED [ 57%]
tests/test_game_logic.py::test_parse_guess_handles_extremely_large_values_without_crashing[nan] PASSED [ 59%]
tests/test_game_logic.py::test_high_score_saved_and_only_beaten_by_higher PASSED [ 61%]
tests/test_game_logic.py::test_high_score_negative_first_score_is_recorded PASSED [ 64%]
tests/test_game_logic.py::test_high_score_corrupt_file_is_ignored[] PASSED [ 66%]
tests/test_game_logic.py::test_high_score_corrupt_file_is_ignored[not json] PASSED [ 69%]
tests/test_game_logic.py::test_high_score_corrupt_file_is_ignored[[1, 2]] PASSED [ 71%]
tests/test_game_logic.py::test_high_score_corrupt_file_is_ignored[{"Normal": "high"}] PASSED [ 73%]
tests/test_game_logic.py::test_temperature_labels_on_normal_range[50-Correct] PASSED [ 76%]
tests/test_game_logic.py::test_temperature_labels_on_normal_range[52-Burning hot] PASSED [ 78%]
tests/test_game_logic.py::test_temperature_labels_on_normal_range[60-Hot] PASSED [ 80%]
tests/test_game_logic.py::test_temperature_labels_on_normal_range[70-Warm] PASSED [ 83%]
tests/test_game_logic.py::test_temperature_labels_on_normal_range[85-Cool] PASSED [ 85%]
tests/test_game_logic.py::test_temperature_labels_on_normal_range[1-Cool] PASSED [ 88%]
tests/test_game_logic.py::test_temperature_labels_on_normal_range[100-Cold] PASSED [ 90%]
tests/test_game_logic.py::test_temperature_scales_with_range_size PASSED [ 92%]
tests/test_game_logic.py::test_temperature_is_symmetric_and_has_emoji PASSED [ 95%]
tests/test_game_logic.py::test_temperature_does_not_change_check_guess PASSED [ 97%]
tests/test_game_logic.py::test_temperature_handles_degenerate_range PASSED [100%]

============================= 42 passed in 0.11s ==============================
```

## 🚀 Stretch Features

- [x] **High Score tracker (Challenge 2):** the best score for each difficulty is saved to `highscores.json` (git-ignored) and shown in the sidebar. Winning with a higher score than the saved best shows "New high score!" and updates the sidebar immediately. A missing or corrupt file is treated as no scores.
- [x] **Enhanced UI (Challenge 4):** the game now shows color-coded hints, Hot/Cold emojis and a session summary. Core rules are unchanged: `check_guess` and `update_score` are untouched and the new code only reads their results.

  | What you see | Where it lives | What it outputs |
  |--------------|----------------|-----------------|
  | Hot/Cold label | `get_temperature(guess, secret, low, high)` in `logic_utils.py` | An `(emoji, label)` pair based on the distance as a share of the range: 🎯 Correct, 🔥 Burning hot (within 5%), 🌶️ Hot (15%), 🌤️ Warm (30%), ❄️ Cool (50%), 🧊 Cold (beyond). Because it uses the range, "Hot" means the same on Easy, Normal and Hard. |
  | Display text | `format_temperature(temperature)` in `app.py` | Turns the `(emoji, label)` pair into the text shown in the hint box and the table: `🌶️ Hot`, `❄️ Cool` and so on. For Burning hot it shows only `🔥`, without the words. |
  | Color-coded hint | `show_hint_message(outcome, message, temperature)` in `app.py` | Too high shows in a red box (`st.error`), too low in a blue box (`st.info`), a win in green (`st.success`), each followed by the temperature, e.g. `📉 Go LOWER!  ❄️ Cool`. Only shown when "Show hint" is ticked. |
  | Attempts progress bar | `show_summary()` in `app.py` | A bar reading `Attempts used: 2 / 8` that fills as you guess, using the difficulty's attempt limit. |
  | Session summary table | `show_summary()` in `app.py`, fed by `st.session_state.rows` | One row per valid guess with columns `#`, `Guess`, `Result` (📉 Too high / 📈 Too low / 🎉 Correct) and `Temperature`. Invalid input such as `abc` adds no row. With "Show hint" unticked only `#` and `Guess` are shown, so the table cannot leak hints. |

  `st.session_state.rows` is cleared whenever `history` is, on New Game and on a difficulty change. `history` still holds plain integers, so the debug panel and the existing behavior are unchanged. The summary is drawn into an `st.empty()` placeholder so it updates in the same run as the guess.

  Verified with 11 new pytest cases for `get_temperature` (labels at each threshold, scaling across difficulties, symmetry, a one-number range) and by driving the real `app.py` with Streamlit AppTest: guesses of 90, 45 and `abc` against a secret of 50 gave a red `Go LOWER!  ❄️ Cool`, a blue `Go HIGHER!  🌶️ Hot` and a plain error with no new row, then a winning guess added a third row. I have not yet looked at the colors in a real browser.
