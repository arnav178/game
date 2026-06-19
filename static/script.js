const difficultyScreen = document.getElementById("difficultyScreen");
const gameScreen = document.getElementById("gameScreen");
const difficultyButtons = document.querySelectorAll(".difficulty-btn");

const guessInput = document.getElementById("guessInput");
const guessBtn = document.getElementById("guessBtn");
const newGameBtn = document.getElementById("newGameBtn");
const messageEl = document.getElementById("message");
const attemptsEl = document.getElementById("attempts");
const historyEl = document.getElementById("history");
const rangeText = document.getElementById("rangeText");

function renderHistory(history) {
  historyEl.innerHTML = "";
  history.forEach((item) => {
    const li = document.createElement("li");
    li.className = item.result;
    li.textContent = `Guessed ${item.guess} — ${item.result}`;
    historyEl.appendChild(li);
  });
}

function showGameScreen() {
  difficultyScreen.classList.add("hidden");
  gameScreen.classList.remove("hidden");
}

function showDifficultyScreen() {
  gameScreen.classList.add("hidden");
  difficultyScreen.classList.remove("hidden");
}

async function startNewGame(difficulty) {
  const response = await fetch("/new_game", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ difficulty }),
  });
  const data = await response.json();

  messageEl.textContent = data.message;
  attemptsEl.textContent = data.attempts_left;
  rangeText.textContent = `I'm thinking of a number between ${data.min_number} and ${data.max_number}.`;
  guessInput.min = data.min_number;
  guessInput.max = data.max_number;
  renderHistory(data.history);
  guessInput.disabled = false;
  guessBtn.disabled = false;
  guessInput.value = "";

  showGameScreen();
  guessInput.focus();
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

// Difficulty buttons start a new game with the chosen difficulty
difficultyButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    startNewGame(btn.dataset.difficulty);
  });
});

// "Change Difficulty" button takes the user back to the difficulty screen
newGameBtn.addEventListener("click", showDifficultyScreen);

guessBtn.addEventListener("click", submitGuess);
guessInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") submitGuess();
});