"""
main.py - Entry point for the Board Game Playing Agent platform.
Launches the interactive Tkinter GUI by default, with a fallback or command-line
option to run in console CLI mode.
"""

import sys
from game import TicTacToe, ConnectFour, Chess
from agent import MinimaxAgent, HumanPlayer, AIPlayer


def run_cli():
    print("=" * 40)
    print("   ADVANCED BOARD GAME PLAYING AGENT")
    print("=" * 40)
    
    print("\nSelect Game:")
    print("  1. Tic-Tac-Toe")
    print("  2. Connect Four")
    print("  3. Chess")
    game_choice = input("\nEnter game choice (1/2/3): ").strip()

    if game_choice == "2":
        game = ConnectFour()
        game_name = "Connect Four"
    elif game_choice == "3":
        game = Chess()
        game_name = "Chess"
    else:
        game = TicTacToe()
        game_name = "Tic-Tac-Toe"

    print(f"\nPlaying: {game_name}")
    print("\nSelect Mode:")
    print("  1. Human vs AI")
    print("  2. AI vs AI")
    print("  3. Human vs Human")
    mode_choice = input("\nEnter mode choice (1/2/3): ").strip()

    # Determine depth limits based on difficulty and game
    depth = 9  # default for Tic-Tac-Toe
    difficulty = "hard"
    if mode_choice in ["1", "2"]:
        print("\nSelect AI Difficulty:")
        print("  1. Easy")
        print("  2. Medium")
        print("  3. Hard")
        diff_choice = input("\nEnter difficulty choice (1/2/3): ").strip()
        
        difficulty_map = {"1": "easy", "2": "medium", "3": "hard"}
        difficulty = difficulty_map.get(diff_choice, "hard")
        
        if game_name == "Tic-Tac-Toe":
            depths = {"1": 1, "2": 3, "3": 9}
        elif game_name == "Connect Four":
            depths = {"1": 2, "2": 4, "3": 6}
        else: # Chess
            depths = {"1": 1, "2": 2, "3": 3}
        depth = depths.get(diff_choice, 4)

    if mode_choice == "1":
        player_x = HumanPlayer("X")
        player_o = AIPlayer("O", MinimaxAgent(player_symbol="O", opponent_symbol="X", max_depth=depth, difficulty=difficulty))
    elif mode_choice == "2":
        player_x = AIPlayer("X", MinimaxAgent(player_symbol="X", opponent_symbol="O", max_depth=depth, difficulty=difficulty))
        player_o = AIPlayer("O", MinimaxAgent(player_symbol="O", opponent_symbol="X", max_depth=depth, difficulty=difficulty))
    else:
        player_x = HumanPlayer("X")
        player_o = HumanPlayer("O")

    players = {"X": player_x, "O": player_o}
    
    def get_current_player():
        if hasattr(game, "current_player"):
            return game.current_player
        return current_turn

    current_turn = "X"
    print("\n")
    game.display()

    while not game.is_terminal():
        current = get_current_player()
        print(f"\n--- {players[current]}'s turn ({current}) ---")
        
        legal = game.get_legal_moves()
        if not legal:
            print("No legal moves available. Passing turn.")
            current_turn = "O" if current_turn == "X" else "X"
            continue
            
        move = players[current].get_move(game)

        if move not in legal:
            print("Invalid move! Try again.")
            continue

        game.make_move(move, current)
        game.display()
        current_turn = "O" if current_turn == "X" else "X"

    winner = game.get_winner()
    print("\n" + "=" * 40)
    if winner:
        print(f"🎉 Player '{winner}' WINS!")
    else:
        print("🤝 It's a DRAW!")
    
    if game_name == "Chess":
        print(f"Final FEN: {game.board.fen()}")
    print("=" * 40)


def main():
    # If "--cli" argument is passed, force CLI mode
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        run_cli()
        return

    # Attempt to load Tkinter GUI
    try:
        import tkinter as tk
        from gui import BoardGameApp
        
        root = tk.Tk()
        app = BoardGameApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Warning: Could not start GUI ({e})")
        print("Launching console CLI interface instead...")
        run_cli()


if __name__ == "__main__":
    main()
