import os
import random
from flask import Flask, render_template, request, session, jsonify

app = Flask(__name__)
# secret_key is required by Flask to securely sign the session cookie.
# In production, this comes from an environment variable (set on Render).
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

# Each difficulty defines its own range and attempt budget.
DIFFICULTIES = {
    "easy":   {"min": 1, "max": 50,  "attempts": 10, "label": "Easy (1–50, 10 tries)"},
    "medium": {"min": 1, "max": 100, "attempts": 7,  "label": "Medium (1–100, 7 tries)"},
    "hard":   {"min": 1, "max": 200, "attempts": 6,  "label": "Hard (1–200, 6 tries)"},
}
DEFAULT_DIFFICULTY = "medium"


def start_new_game(difficulty):
    """Resets the game state stored in the user's session for the chosen difficulty."""
    if difficulty not in DIFFICULTIES:
        difficulty = DEFAULT_DIFFICULTY

    config = DIFFICULTIES[difficulty]
    session["difficulty"] = difficulty
    session["min_number"] = config["min"]
    session["max_number"] = config["max"]
    session["target"] = random.randint(config["min"], config["max"])
    session["attempts_left"] = config["attempts"]
    session["game_over"] = False
    session["history"] = []  # list of past guesses, for display


@app.route("/")
def home():
    """Renders the main page. No game is started until the user picks a difficulty."""
    has_active_game = "target" in session
    return render_template(
        "index.html",
        has_active_game=has_active_game,
        attempts_left=session.get("attempts_left"),
        history=session.get("history", []),
        game_over=session.get("game_over", False),
        min_number=session.get("min_number"),
        max_number=session.get("max_number"),
        difficulties=DIFFICULTIES,
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

    min_number = session["min_number"]
    max_number = session["max_number"]

    if user_guess < min_number or user_guess > max_number:
        return jsonify({
            "error": f"Please guess a number between {min_number} and {max_number}."
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
    """Starts a brand new game using the difficulty sent from the frontend."""
    data = request.get_json(silent=True) or {}
    difficulty = data.get("difficulty", session.get("difficulty", DEFAULT_DIFFICULTY))
    start_new_game(difficulty)
    return jsonify({
        "message": f"New game started on {DIFFICULTIES[session['difficulty']]['label']}! Guess a number.",
        "difficulty": session["difficulty"],
        "min_number": session["min_number"],
        "max_number": session["max_number"],
        "attempts_left": session["attempts_left"],
        "game_over": False,
        "history": [],
    })


if __name__ == "__main__":
    # debug=True is only for local development — Render will use gunicorn instead.
    app.run(debug=True, host="0.0.0.0", port=5000)