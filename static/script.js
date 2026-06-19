const guessInput = document.getElementById("guessInput");
const guessBtn = document.getElementById("guessBtn");
const newGameBtn = document.getElementById("newGameBtn");
const messageEl = document.getElementById("message");
const attemptsEl = document.getElementById("attempts");
const historyEl = document.getElementById("history");

function renderHistory(history) {
  historyEl.innerHTML = "";
  history.forEach((item) => {
    const li = document.createElement("li");
    li.className = item.result;
    li.textContent = `Guessed ${item.guess} — ${item.result}`;
    historyEl.appendChild(li);
  });
}

async function submitGuess() {
  const value = guessInput.value;
  if (value === "") {
    messageEl.textContent = "Please enter a number first.";
    return;
  }

  const response = await fetch("/guess", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ guess: value }),
  });
  const data = await response.json();

  if (!response.ok) {
    messageEl.textContent = data.error;
    return;
  }

  messageEl.textContent = data.message;
  attemptsEl.textContent = data.attempts_left;
  renderHistory(data.history);
  guessInput.value = "";

  if (data.game_over) {
    guessInput.disabled = true;
    guessBtn.disabled = true;
  }
}

async function startNewGame() {
  const response = await fetch("/new_game", { method: "POST" });
  const data = await response.json();

  messageEl.textContent = data.message;
  attemptsEl.textContent = data.attempts_left;
  renderHistory(data.history);
  guessInput.disabled = false;
  guessBtn.disabled = false;
  guessInput.value = "";
  guessInput.focus();
}

guessBtn.addEventListener("click", submitGuess);
newGameBtn.addEventListener("click", startNewGame);
guessInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") submitGuess();
});