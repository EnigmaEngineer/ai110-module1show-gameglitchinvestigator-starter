import pytest

from logic_utils import (
    check_guess,
    get_range_for_difficulty,
    get_temperature,
    load_high_scores,
    parse_guess,
    save_high_score,
    update_score,
)

# FIX: The starter tests compared the (outcome, message) tuple to a bare
# string, so they could never pass. Claude Code rewrote them and added more
# cases.


def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"


def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High" and say go
    # lower
    outcome, message = check_guess(60, 50)
    assert outcome == "Too High"
    assert "LOWER" in message


def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low" and say go
    # higher
    outcome, message = check_guess(40, 50)
    assert outcome == "Too Low"
    assert "HIGHER" in message


def test_hints_point_toward_secret_regression():
    # Regression: hints used to be backwards (a guess above the secret said
    # "go higher").
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


# Challenge 1: edge-case inputs for parse_guess (negatives, decimals, huge
# values).


@pytest.mark.parametrize("raw", ["-5", "-1", "-0", "-0.5", "-999999"])
def test_parse_guess_rejects_negative_numbers(raw):
    ok, value, error = parse_guess(raw, 1, 100)
    assert ok is False
    assert value is None
    assert "between 1 and 100" in error


@pytest.mark.parametrize(
    "raw, expected", [("3.7", 3), ("42.0", 42), ("100.9", 100)]
)
def test_parse_guess_truncates_decimals_in_range(raw, expected):
    # Decimals are accepted but truncated toward zero, never rounded up.
    assert parse_guess(raw, 1, 100) == (True, expected, None)


@pytest.mark.parametrize("raw", ["0.9", "0.0", "101.0"])
def test_parse_guess_rejects_decimals_that_land_out_of_range(raw):
    ok, value, _ = parse_guess(raw, 1, 100)
    assert ok is False
    assert value is None


@pytest.mark.parametrize(
    "raw",
    [
        "99999999999999999999",  # far above the range, still a valid int
        "9" * 5000,  # exceeds Python's int-string digit limit
        "1e5",
        "1.0e999",  # scientific notation / float overflow to inf
        "inf",
        "nan",
    ],
    ids=[
        "20-digit-int",
        "5000-digit-int",
        "sci-notation",
        "float-overflow",
        "inf",
        "nan",
    ],
)
def test_parse_guess_handles_extremely_large_values_without_crashing(raw):
    ok, value, error = parse_guess(raw, 1, 100)
    assert ok is False
    assert value is None
    assert isinstance(error, str) and error


# Challenge 2: High Score tracker.


def test_high_score_saved_and_only_beaten_by_higher(tmp_path):
    path = str(tmp_path / "scores.json")
    assert load_high_scores(path) == {}
    assert save_high_score("Normal", 70, path) is True
    assert save_high_score("Normal", 70, path) is False  # tie is not a record
    assert save_high_score("Normal", 40, path) is False
    assert save_high_score("Normal", 90, path) is True
    # Each difficulty is tracked separately.
    assert save_high_score("Easy", 10, path) is True
    assert load_high_scores(path) == {"Normal": 90, "Easy": 10}


def test_high_score_negative_first_score_is_recorded(tmp_path):
    path = str(tmp_path / "scores.json")
    assert save_high_score("Hard", -15, path) is True
    assert load_high_scores(path) == {"Hard": -15}


@pytest.mark.parametrize(
    "content", ["", "not json", "[1, 2]", '{"Normal": "high"}']
)
def test_high_score_corrupt_file_is_ignored(tmp_path, content):
    path = tmp_path / "scores.json"
    path.write_text(content, encoding="utf-8")
    assert load_high_scores(str(path)) == {}
    assert save_high_score("Normal", 50, str(path)) is True


# Challenge 4: hot/cold labels (display only).


@pytest.mark.parametrize(
    "guess, label",
    [
        (50, "Correct"),
        (52, "Burning hot"),  # 2% of the range
        (60, "Hot"),  # 10%
        (70, "Warm"),  # 20%
        (85, "Cool"),  # 35%
        (1, "Cool"),  # 49.5%
        (100, "Cold"),  # 50.5%
    ],
)
def test_temperature_labels_on_normal_range(guess, label):
    assert get_temperature(guess, 50, 1, 100)[1] == label


def test_temperature_scales_with_range_size():
    # Being 2 away is "Hot" on Easy (1-20) but "Burning hot" on Normal.
    assert get_temperature(12, 10, 1, 20)[1] == "Hot"
    assert get_temperature(52, 50, 1, 100)[1] == "Burning hot"


def test_temperature_is_symmetric_and_has_emoji():
    assert get_temperature(40, 50, 1, 100) == get_temperature(60, 50, 1, 100)
    emoji, label = get_temperature(40, 50, 1, 100)
    assert emoji and label


def test_temperature_does_not_change_check_guess():
    # The UI helper is independent of the core outcome.
    assert check_guess(60, 50)[0] == "Too High"
    assert get_temperature(60, 50, 1, 100)[1] == "Hot"


def test_temperature_handles_degenerate_range():
    assert get_temperature(5, 5, 5, 5) == ("🎯", "Correct")
