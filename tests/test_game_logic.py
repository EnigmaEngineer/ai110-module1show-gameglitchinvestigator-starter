from logic_utils import check_guess, get_range_for_difficulty, parse_guess, update_score

# FIX: Original tests compared the (outcome, message) tuple to a bare string, so they could never pass; Claude Code corrected them and added coverage, I ran pytest.

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High" and say go lower
    outcome, message = check_guess(60, 50)
    assert outcome == "Too High"
    assert "LOWER" in message

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low" and say go higher
    outcome, message = check_guess(40, 50)
    assert outcome == "Too Low"
    assert "HIGHER" in message

def test_hints_point_toward_secret_regression():
    # Regression: hints used to be backwards (guess above secret said "go higher").
    # Following the hint must always move the guess toward the secret.
    secret = 50
    for guess in range(1, 101):
        outcome, message = check_guess(guess, secret)
        if guess > secret:
            assert outcome == "Too High"
            assert "LOWER" in message and "HIGHER" not in message
        elif guess < secret:
            assert outcome == "Too Low"
            assert "HIGHER" in message and "LOWER" not in message
        else:
            assert outcome == "Win"

def test_range_for_difficulty():
    assert get_range_for_difficulty("Easy") == (1, 20)
    assert get_range_for_difficulty("Normal") == (1, 100)
    assert get_range_for_difficulty("Hard") == (1, 50)

def test_parse_guess_valid():
    assert parse_guess("42") == (True, 42, None)

def test_parse_guess_rejects_out_of_range_and_junk():
    assert parse_guess("0", 1, 100)[0] is False
    assert parse_guess("101", 1, 100)[0] is False
    assert parse_guess("abc")[0] is False
    assert parse_guess("")[0] is False
    assert parse_guess("   ")[0] is False
    assert parse_guess(None)[0] is False

def test_update_score():
    assert update_score(0, "Win", 1) == 90
    assert update_score(0, "Win", 20) == 10  # floor
    assert update_score(10, "Too High", 2) == 5  # no even-attempt bonus
    assert update_score(10, "Too Low", 3) == 5
