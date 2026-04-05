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
python connect4.py
```

> You'll need to activate the venv each time you open a new terminal session:
>
> ```bash
> source .venv/bin/activate
> ```

---

## Game Modes

On launch, choose one of three modes:

| Mode                          | Description                                              |
| ----------------------------- | -------------------------------------------------------- |
| **2 Players**                 | Local two-player, take turns on the same machine         |
| **AI — Minimax**              | Play against an AI using pure Minimax (no pruning)       |
| **AI — Minimax + Alpha-Beta** | Play against an AI using Minimax with Alpha-Beta Pruning |

The two AI modes use the same heuristic and depth, making them useful for directly comparing efficiency.

---

## How to Play

- Click a column to drop your piece into it
- Pieces fall to the lowest available row
- First to connect **4 in a row** (horizontally, vertically, or diagonally) wins
- If the board fills with no winner, the game ends in a **draw**

### Controls

| Key / Action | Effect                              |
| ------------ | ----------------------------------- |
| Mouse move   | Preview where your piece will drop  |
| Left click   | Drop piece into that column         |
| `R`          | Restart the round (scores are kept) |
| `ESC`        | Quit the game                       |

Wins are tracked in the score bar across rounds.

---

## Project Structure

```
connect4.py      # Main game file — run this
requirements.txt     # Python dependencies
README.md            # This file
```

---

## Adjusting AI Difficulty

In `connect4.py`, find this line near the top:

```python
AI_DEPTH = 5
```

| Value | Effect                                     |
| ----- | ------------------------------------------ |
| `3`   | Easy — fast response                       |
| `5`   | Default — balanced                         |
| `6+`  | Hard — slower, especially for pure Minimax |

> Note: Pure Minimax gets significantly slower at higher depths compared to Alpha-Beta. This is expected and is the whole point of the comparison.

---

## Measuring AI Performance

The game now prints performance metrics to the terminal for every AI move (in both AI modes).

Example output:

```text
[AI:minimax] depth=5 col=3 score=12 nodes=19231 cutoffs=0 time_ms=84.17
[AI:alpha-beta] depth=5 col=3 score=12 nodes=5321 cutoffs=714 time_ms=20.44
```

Fields:

- `time_ms`: wall-clock time for the search call
- `nodes`: number of search nodes expanded
- `cutoffs`: number of alpha-beta pruning cutoffs (always `0` for pure minimax)

For a fair comparison:

1. Use the same `AI_DEPTH`.
2. Compare positions of similar complexity (opening, midgame, endgame).
3. Collect multiple moves and average results.
4. Report both runtime and node count.

### Benchmark Setups

Two benchmark workflows are included so the project can measure both direct head-to-head performance and scaling behavior.

#### 1. Fixed-Scenario Benchmark

This benchmark compares minimax and alpha-beta on the same preset board states. It is the main report-ready comparison because both algorithms start from identical positions.

You can run an automatic side-by-side benchmark without opening the game window:

```bash
python connect4.py --benchmark --depth 5 --repeats 5
```

This command writes the fixed-scenario results to `fixed_scenarios_benchmark.csv` by default.

To save the CSV under a different name or location:

```bash
python connect4.py --benchmark --depth 5 --repeats 5 --csv fixed_scenarios_benchmark.csv
```

Optional flags:

- `--depth N`: search depth (default: `5`)
- `--repeats N`: repetitions per scenario and algorithm (default: `5`)
- `--csv PATH`: CSV export path, default is `fixed_scenarios_benchmark.csv`

#### 2. Depth-Scaling Benchmark

The separate depth benchmark in `benchmark.py` tests both algorithms at depths 2 through 6 on randomly generated mid-game boards. It is useful for showing how the runtime and node count grow as search depth increases.

Run it with:

```bash
python benchmark.py
```

It writes the depth-scaling results to `depth_scaling_benchmark.csv`.

The benchmark prints a table with:

- average runtime (`Avg ms`)
- average node expansions (`Avg nodes`)
- average pruning events (`Avg cutoffs`)
- chosen move and score
- per-scenario speedup and node-reduction summary
