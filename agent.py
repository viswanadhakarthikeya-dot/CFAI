"""
agent.py - AI Agent using Minimax with Alpha-Beta Pruning

The MinimaxAgent explores the game tree to find the optimal move,
using alpha-beta pruning to skip branches that can't affect the result.
"""

import math
from typing import Optional, Tuple
from game import Game


class Agent:
    """Base class for all game-playing agents."""

    def choose_move(self, game: Game) -> int:
        raise NotImplementedError


class MinimaxAgent(Agent):
    """
    Minimax Agent with Alpha-Beta Pruning.

    - Maximizes score for `player_symbol`
    - Minimizes score for `opponent_symbol`
    - Prunes branches using alpha-beta to improve efficiency
    """

    def __init__(self, player_symbol: str, opponent_symbol: str, max_depth: float = math.inf, difficulty: str = "hard"):
        self.player = player_symbol
        self.opponent = opponent_symbol
        self.max_depth = max_depth
        self.difficulty = difficulty.lower()

    def choose_move(self, game: Game) -> int:
        """Returns the best move index for the current game state."""
        import random

        legal_moves = game.get_legal_moves()
        if not legal_moves:
            return None

        # Check difficulty for random choices to make games feel easier
        if self.difficulty == "easy":
            # 50% chance of random move
            if random.random() < 0.50:
                return random.choice(legal_moves)
        elif self.difficulty == "medium":
            # 15% chance of random move
            if random.random() < 0.15:
                return random.choice(legal_moves)

        best_score = -math.inf
        best_moves = []

        for move in legal_moves:
            game.make_move(move, self.player)
            score = self._minimax(
                game, depth=0, is_maximizing=False,
                alpha=-math.inf, beta=math.inf
            )
            game.undo_move(move)

            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)

        return random.choice(best_moves) if best_moves else None

    def _minimax(
        self,
        game: Game,
        depth: int,
        is_maximizing: bool,
        alpha: float,
        beta: float
    ) -> int:
        """
        Recursive Minimax with Alpha-Beta pruning.

        Args:
            game: Current game state
            depth: Current depth in the tree
            is_maximizing: True if it's the maximizing player's turn
            alpha: Best score the maximizer can guarantee
            beta: Best score the minimizer can guarantee

        Returns:
            The evaluated score of the position
        """
        if game.is_terminal() or depth >= self.max_depth:
            score = game.evaluate(self.player, self.opponent)
            if game.is_terminal():
                # Prefer faster wins / slower losses
                return score - depth if score > 0 else score + depth
            return score

        if is_maximizing:
            max_eval = -math.inf
            for move in game.get_legal_moves():
                game.make_move(move, self.player)
                eval_score = self._minimax(game, depth + 1, False, alpha, beta)
                game.undo_move(move)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cutoff
            return max_eval
        else:
            min_eval = math.inf
            for move in game.get_legal_moves():
                game.make_move(move, self.opponent)
                eval_score = self._minimax(game, depth + 1, True, alpha, beta)
                game.undo_move(move)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha cutoff
            return min_eval


class Player:
    """Base class for a game player."""

    def __init__(self, symbol: str):
        self.symbol = symbol

    def get_move(self, game: Game) -> int:
        raise NotImplementedError

    def __str__(self):
        return f"Player({self.symbol})"


class HumanPlayer(Player):
    """Gets move input from the human user."""

    def get_move(self, game: Game) -> int:
        legal = game.get_legal_moves()
        is_chess = False
        if legal and hasattr(legal[0], "uci"):
            is_chess = True

        if is_chess:
            print(f"Legal moves: {[m.uci() for m in legal]}")
        else:
            print(f"Legal moves: {legal}")

        while True:
            try:
                user_input = input("Enter your move: ").strip()
                if is_chess:
                    import chess
                    try:
                        move = chess.Move.from_uci(user_input)
                        # Check promotion if input lacks q (e.g., e7e8)
                        if move not in legal:
                            move = chess.Move.from_uci(user_input + "q")
                    except Exception:
                        print("Invalid UCI move format (e.g., e2e4).")
                        continue
                else:
                    move = int(user_input)

                if move in legal:
                    return move
                else:
                    if is_chess:
                        print(f"Invalid! Choose from {[m.uci() for m in legal]}.")
                    else:
                        print(f"Invalid! Choose from {legal}.")
            except ValueError:
                print("Please enter a valid input.")

    def __str__(self):
        return f"Human({self.symbol})"


class AIPlayer(Player):
    """Selects moves using an AI agent."""

    def __init__(self, symbol: str, agent: Agent):
        super().__init__(symbol)
        self.agent = agent

    def get_move(self, game: Game) -> int:
        print("AI is thinking...")
        move = self.agent.choose_move(game)
        print(f"AI chose: {move}")
        return move

    def __str__(self):
        return f"AI({self.symbol})"


