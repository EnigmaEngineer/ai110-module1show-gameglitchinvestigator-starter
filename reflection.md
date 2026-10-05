# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

At first the game looked fine: a text box, a Submit button, and a difficulty picker in the sidebar. Then I started playing and it felt off. The hints were backwards, so guessing 3, 2, 1 when the secret was 64 kept telling me to go lower. It also let me guess 0, and it ended the game after 7 guesses even though Normal says 8. Looking through app.py, I found the swapped hint messages, no range check on guesses, and the secret getting turned into a string on every other attempt. The attempt counter started at 1 instead of 0.

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input Used | Expected Behavior | Actual Behavior | Console Error / Output | Suspected Code Location |
|------------|-------------------|-----------------|------------------------|-------------------------|
| Guess 3, 2, 1 (secret 64, Normal) | "Go HIGHER" each time | "Go LOWER" each time | None | `check_guess`, the two hint messages were swapped |
| Guess 0 | Error, and no attempt used | Accepted and counted as a guess | None | `parse_guess` never checked the range |
| Play a full Normal game | 8 guesses | Game over after 7 | None | `attempts` started at 1 instead of 0 |
| Guess on an even-numbered attempt | Normal number comparison | Wrong hints, because the secret was a string | None | The submit code in app.py converted `secret` to `str` on even attempts |
| Switch to Easy or Hard | Prompt shows 1-20 or 1-50 | Prompt always said 1-100, and New Game picked from 1-100 | None | Hardcoded text in the info box and `randint(1, 100)` in the New Game block |
| Win or lose, then click New Game | Fresh game | Stuck on "Game over", old score and history kept | None | New Game only reset `attempts` and `secret` |

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion you did not accept as written (including what the AI suggested, why you rejected or changed it, and how you verified your version). It does not have to be a suggestion that was wrong: over-engineered, out of scope, harder to read, or a poor fit for this codebase all count.

I used Claude Code in VS Code in agent mode. It moved `check_guess` into `logic_utils.py`, and I reviewed the diff for every file it touched before trusting it.

**Correct suggestion:** Claude Code said the `str(secret)` conversion on even-numbered attempts in `app.py` was a real bug, and that the `try/except TypeError` fallback in the original `check_guess` was only there to hide it. It removed both and passed the integer secret straight into `check_guess`. This was correct because comparing an int to a string either raised `TypeError` or fell back to comparing text, where "9" > "10". I checked it by guessing several times in a row, including on even attempts, and the hints stayed consistent.

**Not accepted as written:** After moving `check_guess`, Claude Code offered to also move `get_range_for_difficulty`, `parse_guess` and `update_score` into `logic_utils.py`. I kept this task to `check_guess` and the high/low fix. The stub `parse_guess` in `logic_utils.py` also had a different signature from the one in `app.py`, since it had no `low`/`high` arguments. Moving everything at once would have mixed refactoring with behavior changes, and it makes the diff harder to review. I checked my smaller version by confirming the `app.py` diff only removed `check_guess` and added the import.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

I counted a bug as fixed only after I saw the changed behavior in the running app, not just in the diff. Claude Code ran `streamlit run app.py` (the server reported healthy) and drove the real `app.py` with Streamlit's AppTest, using a fixed secret of 50 on Normal. Guessing 10 gave "Go HIGHER!" and 90 gave "Go LOWER!". A second guess of 10 on attempt 3 still gave "Go HIGHER!". Guess 0 gave "Guess must be between 1 and 100." and "abc" gave "That is not a number.", and neither used an attempt. Guessing 50 won with the attempt counter at 4. New Game reset status, attempts, score and history.

AI helped me design this check and explained why AppTest works: it runs the same script without a browser. It is not a real browser click-through, so I should still play the game by hand. I have not run pytest or tested the Easy/Hard difficulty switch, and the secret is not regenerated when difficulty changes until New Game is clicked.

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
