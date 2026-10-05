"""Pure game logic for the number guessing game.

Nothing here imports Streamlit, so every function can be unit tested directly.
The Streamlit front end lives in ``app.py``.
"""

import json

HIGH_SCORE_FILE = "highscores.json"


def get_range_for_difficulty(difficulty: str) -> tuple[int, int]:
    """Return the inclusive guessing range for a difficulty level.

    Args:
        difficulty: One of ``"Easy"``, ``"Normal"`` or ``"Hard"``.

    Returns:
        A ``(low, high)`` tuple. ``"Easy"`` is (1, 20), ``"Normal"`` is
        (1, 100) and ``"Hard"`` is (1, 50). Any unrecognised value falls
        back to the Normal range, (1, 100).
    """
    # FIX: Moved here from app.py so it can be tested without Streamlit. Claude
    # Code did the move.
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100


def parse_guess(
    raw: str | None, low: int = 1, high: int = 100
) -> tuple[bool, int | None, str | None]:
    """Parse and validate the raw text a player typed as a guess.

    Surrounding whitespace is ignored. Text containing a decimal point is
    accepted and truncated toward zero, so ``"3.7"`` becomes 3. Anything that
    cannot be read as a number, including ``"inf"``, ``"nan"`` and scientific
    notation such as ``"1e5"``, is rejected rather than raising.

    Args:
        raw: The text entered by the player, or ``None`` if nothing was
            entered.
        low: The smallest allowed guess (inclusive).
        high: The largest allowed guess (inclusive).

    Returns:
        A ``(ok, guess, error)`` tuple. When the guess is valid, ``ok`` is
        ``True``, ``guess`` is the integer value and ``error`` is ``None``.
        Otherwise ``ok`` is ``False``, ``guess`` is ``None`` and ``error`` is
        a message suitable for showing to the player.
    """
    # FIX: Moved from app.py with the range check kept, so 0 and negative
    # guesses are rejected. Claude Code did the move, and the tests and the
    # running game confirm it.
    if raw is None:
        return False, None, "Enter a guess."

    raw = raw.strip()
    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except (ValueError, OverflowError):
        return False, None, "That is not a number."

    if value < low or value > high:
        return False, None, f"Guess must be between {low} and {high}."

    return True, value, None


def check_guess(guess: int, secret: int) -> tuple[str, str]:
    """Compare a guess with the secret number and build a hint.

    Args:
        guess: The player's guess.
        secret: The number the player is trying to find.

    Returns:
        An ``(outcome, message)`` tuple. ``outcome`` is ``"Win"`` when the
        guess equals the secret, ``"Too High"`` when it is above the secret
        and ``"Too Low"`` when it is below. ``message`` is the hint text to
        show the player, which points toward the secret.
    """
    # FIX: The hint messages were swapped. Claude Code moved this function here
    # in agent mode and corrected them, and the hint tests and the running game
    # confirm it.
    if guess == secret:
        return "Win", "🎉 Correct!"

    if guess > secret:
        return "Too High", "📉 Go LOWER!"
    return "Too Low", "📈 Go HIGHER!"


def get_temperature(
    guess: int, secret: int, low: int, high: int
) -> tuple[str, str]:
    """Describe how close a guess is to the secret as a hot/cold label.

    Closeness is the distance between the guess and the secret as a share of
    the whole range, so the same label means the same thing on every
    difficulty. This is display only; it never changes the outcome or score.

    Args:
        guess: The player's guess.
        secret: The number the player is trying to find.
        low: The smallest number in the range (inclusive).
        high: The largest number in the range (inclusive).

    Returns:
        An ``(emoji, label)`` tuple: ``"Correct"`` for an exact match, then
        ``"Burning hot"`` (within 5% of the range), ``"Hot"`` (15%),
        ``"Warm"`` (30%), ``"Cool"`` (50%) and ``"Cold"`` beyond that.
    """
    # FEATURE (Challenge 4): Hot/Cold labels for the UI. Claude Code wrote it,
    # and the temperature tests cover the thresholds.
    distance = abs(guess - secret)
    if distance == 0:
        return "🎯", "Correct"

    closeness = distance / max(high - low, 1)
    if closeness <= 0.05:
        return "🔥", "Burning hot"
    if closeness <= 0.15:
        return "🌶️", "Hot"
    if closeness <= 0.30:
        return "🌤️", "Warm"
    if closeness <= 0.50:
        return "❄️", "Cool"
    return "🧊", "Cold"


def update_score(current_score: int, outcome: str, attempt_number: int) -> int:
    """Return the new score after a guess has been judged.

    A win awards ``100 - 10 * attempt_number`` points, but never fewer than
    10, so earlier wins are worth more. A wrong guess ("Too High" or
    "Too Low") costs 5 points. Any other outcome leaves the score unchanged.

    Args:
        current_score: The score before this guess.
        outcome: The outcome from :func:`check_guess`.
        attempt_number: The 1-based number of the guess just made.

    Returns:
        The updated score. It can be negative after several wrong guesses.
    """
    # FIX: The win bonus was one attempt short, and "Too High" gave +5 on even
    # attempts. Claude Code proposed the fix, and test_update_score covers it.
    if outcome == "Win":
        points = 100 - 10 * attempt_number
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score


def load_high_scores(path: str = HIGH_SCORE_FILE) -> dict[str, int]:
    """Load the saved best score for each difficulty.

    The file is treated as untrusted. A missing or unreadable file, invalid
    JSON, or JSON that is not an object all give an empty result, and any
    entry whose value is not an integer is dropped.

    Args:
        path: Location of the JSON file holding the scores.

    Returns:
        A mapping of difficulty name to best score, for example
        ``{"Normal": 90}``. Empty if nothing valid could be loaded.
    """
    # FEATURE (Challenge 2): High score tracker, written by Claude Code in
    # agent mode. A missing or corrupt file returns {}, and the corrupt-file
    # tests cover that.
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {
        key: value
        for key, value in data.items()
        if isinstance(value, int) and not isinstance(value, bool)
    }


def save_high_score(
    difficulty: str, score: int, path: str = HIGH_SCORE_FILE
) -> bool:
    """Record a score if it beats the stored best for that difficulty.

    Scores for other difficulties are preserved. Matching the current best is
    not a new record, and the file is left untouched in that case.

    Args:
        difficulty: The difficulty the score was earned on.
        score: The score to consider saving.
        path: Location of the JSON file holding the scores.

    Returns:
        ``True`` if a new record was saved. ``False`` if the score did not
        beat the stored best or the file could not be written.
    """
    scores = load_high_scores(path)
    if difficulty in scores and score <= scores[difficulty]:
        return False
    scores[difficulty] = score
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2)
    except OSError:
        return False
    return True
