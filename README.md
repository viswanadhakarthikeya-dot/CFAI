# Board Game Playing Agent

A modular Python framework for board games with an AI agent powered by **Minimax + Alpha-Beta Pruning**.

## Project Structure

```
board_game_agent/
├── main.py      # Entry point — launches the GUI (or CLI fallback)
├── game.py      # Game logic (Tic-Tac-Toe, Connect Four, Chess)
├── agent.py     # AI MinimaxAgent and Player classes
├── gui.py       # Modern Tkinter desktop GUI
└── tests.py     # Unit tests
```

## How to Run

```bash
# Launch the Tkinter GUI (Default)
python main.py

# Launch the console CLI mode
python main.py --cli

# Run tests
python tests.py
```

## Game Modes

| Mode | Description |
|------|-------------|
| Human vs AI | You play against the Minimax agent |
| AI vs AI | Watch two agents play each other |
| Human vs Human | Local two-player game |

## How the AI Works

The `MinimaxAgent` uses the **Minimax algorithm** — it explores all possible future game states and picks the move that maximizes its score while assuming the opponent plays optimally.

**Alpha-Beta Pruning** speeds this up by skipping branches that can't possibly affect the final decision.

```
Score:  +10 = AI wins
         0  = Draw
        -10 = Opponent wins
```

## Extending to Other Games

1. Create a new class in `game.py` inheriting from `Game`
2. Implement all abstract methods: `get_legal_moves`, `make_move`, `undo_move`, `is_terminal`, `get_winner`, `evaluate`, `display`, `clone`
3. Plug it into `main.py`

The `MinimaxAgent` works with **any** game that implements the `Game` interface.

## Requirements

- Python 3.7+
- No external dependencies
