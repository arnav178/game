import os
import random
from flask import Flask, render_template, request, session, jsonify

app = Flask(__name__)
# secret_key is required by Flask to securely sign the session cookie.
# In production, this comes from an environment variable (set on Render).
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

MIN_NUMBER = 1
MAX_NUMBER = 100
MAX_ATTEMPTS = 7


def start_new_game():
    """Resets the game state stored in the user's session."""
    session["target"] = random.randint(MIN_NUMBER, MAX_NUMBER)
    session["attempts_left"] = MAX_ATTEMPTS
    session["game_over"] = False
    session["history"] = []  # list of past guesses, for display


@app.route("/")
def home():
    """Renders the main page. Starts a fresh game if none exists yet."""
    if "target" not in session:
        start_new_game()
    return render_template(
        "index.html",
        attempts_left=session["attempts_left"],
        history=session["history"],
        game_over=session["game_over"],
        min_number=MIN_NUMBER,
        max_number=MAX_NUMBER,
    )


@app.route("/guess", methods=["POST"])
def guess():
    """Handles a single guess submitted by the user."""
    if "target" not in session or session.get("game_over"):
        return jsonify({"error": "No active game. Please start a new game."}), 400

    data = request.get_json()
    try:
        user_guess = int(data.get("guess"))
    except (TypeError, ValueError):
        return jsonify({"error": "Please enter a valid whole number."}), 400

    if user_guess < MIN_NUMBER or user_guess > MAX_NUMBER:
        return jsonify({
            "error": f"Please guess a number between {MIN_NUMBER} and {MAX_NUMBER}."
        }), 400

    target = session["target"]
    session["attempts_left"] -= 1

    if user_guess == target:
        message = f"🎉 Correct! The number was {target}."
        session["game_over"] = True
        result = "correct"
    elif session["attempts_left"] <= 0:
        message = f"💀 Out of attempts! The number was {target}."
        session["game_over"] = True
        result = "lost"
    elif user_guess < target:
        message = "📈 Too low! Try a higher number."
        result = "low"
    else:
        message = "📉 Too high! Try a lower number."
        result = "high"

    # Save this guess to history (need to re-assign for Flask to detect the change)
    history = session["history"]
    history.append({"guess": user_guess, "result": result})
    session["history"] = history

    return jsonify({
        "message": message,
        "result": result,
        "attempts_left": session["attempts_left"],
        "game_over": session["game_over"],
        "history": session["history"],
    })


@app.route("/new_game", methods=["POST"])
def new_game():
    """Starts a brand new game (resets session state)."""
    start_new_game()
    return jsonify({
        "message": "New game started! Guess a number.",
        "attempts_left": session["attempts_left"],
        "game_over": False,
        "history": [],
    })


if __name__ == "__main__":
    # debug=True is only for local development — Render will use gunicorn instead.
    app.run(debug=True, host="0.0.0.0", port=5000)