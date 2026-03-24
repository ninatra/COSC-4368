# Connect Four

A polished Connect Four game built with Python and Pygame. Play locally with a friend or go up against an AI — choose between a pure Minimax or Minimax with Alpha-Beta Pruning to compare performance.

---

## Requirements

- Python **3.12** or **3.11** (Python 3.13+ is not yet supported by Pygame)

---

## Setup

### 1. Install Python 3.12

If you don't have Python 3.12, install it via Homebrew (macOS):

```bash
brew install python@3.12
```

---

### 2. Clone the repo

```bash
git clone <your-repo-url>
cd <repo-folder>
```

---

### 3. Create and activate a virtual environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

You'll know it's active when you see `(.venv)` at the start of your terminal prompt.

---

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Game

Make sure your virtual environment is active, then run:

```bash
python connect_four.py
```

> You'll need to activate the venv each time you open a new terminal session:
> ```bash
> source .venv/bin/activate
> ```

---

## Game Modes

On launch, choose one of three modes:

| Mode | Description |
|---|---|
| **2 Players** | Local two-player, take turns on the same machine |
| **vs AI — Minimax** | Play against an AI using pure Minimax (no pruning) |
| **vs AI — Minimax + Alpha-Beta** | Play against an AI using Minimax with Alpha-Beta Pruning |

The two AI modes use the same heuristic and depth, making them useful for directly comparing efficiency.

---

## How to Play

- Click a column to drop your piece into it
- Pieces fall to the lowest available row
- First to connect **4 in a row** (horizontally, vertically, or diagonally) wins
- If the board fills with no winner, the game ends in a **draw**

### Controls

| Key / Action | Effect |
|---|---|
| Mouse move | Preview where your piece will drop |
| Left click | Drop piece into that column |
| `R` | Restart the round (scores are kept) |
| `ESC` | Quit the game |

Wins are tracked in the score bar across rounds.

---

## Project Structure

```
connect_four.py      # Main game file — run this
requirements.txt     # Python dependencies
README.md            # This file
```

---

## Adjusting AI Difficulty

In `connect_four.py`, find this line near the top:

```python
AI_DEPTH = 5
```

| Value | Effect |
|---|---|
| `3` | Easy — fast response |
| `5` | Default — balanced |
| `6+` | Hard — slower, especially for pure Minimax |

> Note: Pure Minimax gets significantly slower at higher depths compared to Alpha-Beta. This is expected and is the whole point of the comparison.
