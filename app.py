import random

import pandas as pd
import streamlit as st

# FIX: Game logic now lives in logic_utils.py. Claude Code moved it in agent
# mode.
from logic_utils import (
    check_guess,
    get_range_for_difficulty,
    get_temperature,
    load_high_scores,
    parse_guess,
    save_high_score,
    update_score,
)

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

# FEATURE (Challenge 2): Best score per difficulty, saved to highscores.json.
# Claude Code wrote it, and the placeholder lets the sidebar update after a
# win.
high_score_box = st.sidebar.empty()


def show_high_score():
    best = load_high_scores().get(difficulty)
    high_score_box.metric(
        f"🏆 Best score ({difficulty})",
        "None yet" if best is None else best,
    )


show_high_score()

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

if "attempts" not in st.session_state:
    # FIX: Attempts started at 1, so Normal ended after 7 guesses. Claude Code
    # spotted the off-by-one.
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

if "rows" not in st.session_state:
    st.session_state.rows = []

# FIX: A difficulty change kept the old secret and range. Found while testing
# with Claude Code; a switch now starts a fresh game.
if st.session_state.get("difficulty") != difficulty:
    st.session_state.difficulty = difficulty
    st.session_state.secret = random.randint(low, high)
    st.session_state.attempts = 0
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.rows = []

st.subheader("Make a guess")

st.info(
    # FIX: The prompt was hardcoded to 1-100. It now uses the difficulty's
    # range (applied by Claude Code).
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input("Enter your guess:", key=f"guess_input_{difficulty}")

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

# FEATURE (Challenge 4): Attempts bar and a table of this game's guesses with
# hot/cold labels. Written by Claude Code and checked by playing it in the
# browser.
summary_box = st.empty()


def show_summary():
    """Draw the attempts progress bar and the guess-by-guess session table."""
    with summary_box.container():
        used = st.session_state.attempts
        st.progress(
            min(used / attempt_limit, 1.0),
            text=f"Attempts used: {used} / {attempt_limit}",
        )
        if st.session_state.rows:
            table = pd.DataFrame(st.session_state.rows)
            if not show_hint:
                table = table[["#", "Guess"]]
            st.dataframe(table, hide_index=True, width="stretch")


def format_temperature(temperature):
    """Return the temperature text for display; Burning hot shows only 🔥."""
    emoji, label = temperature
    return emoji if label == "Burning hot" else f"{emoji} {label}"


def show_hint_message(outcome, message, temperature):
    """Show a color-coded hint: red for too high, blue for too low."""
    text = f"{message}  {format_temperature(temperature)}"
    if outcome == "Win":
        st.success(message)
    elif outcome == "Too High":
        st.error(text)
    else:
        st.info(text)


show_summary()

if new_game:
    st.session_state.attempts = 0
    # FIX: New Game ignored the difficulty range and kept the old status, score
    # and history. Claude Code rewrote it, and the reset was checked in the
    # browser.
    st.session_state.secret = random.randint(low, high)
    st.session_state.status = "playing"
    st.session_state.score = 0
    st.session_state.history = []
    st.session_state.rows = []
    st.success("New game started.")
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

if submit:
    ok, guess_int, err = parse_guess(raw_guess, low, high)

    if not ok:
        # FIX: Invalid input used to be added to history. Claude Code removed
        # that append, so a bad guess now only shows the error.
        st.error(err)
    else:
        # FIX: Only valid guesses count as attempts, and the secret is passed
        # as a real int with no str() conversion. Edited by Claude Code.
        st.session_state.attempts += 1
        st.session_state.history.append(guess_int)

        outcome, message = check_guess(guess_int, st.session_state.secret)
        temperature = get_temperature(
            guess_int, st.session_state.secret, low, high
        )
        st.session_state.rows.append(
            {
                "#": st.session_state.attempts,
                "Guess": guess_int,
                "Result": {
                    "Too High": "📉 Too high",
                    "Too Low": "📈 Too low",
                    "Win": "🎉 Correct",
                }[outcome],
                "Temperature": format_temperature(temperature),
            }
        )

        if show_hint:
            show_hint_message(outcome, message, temperature)

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            if save_high_score(difficulty, st.session_state.score):
                show_high_score()
                st.success("🏆 New high score!")
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

        show_summary()

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
