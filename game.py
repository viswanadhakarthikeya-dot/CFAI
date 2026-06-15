"""
game.py - Game logic for Tic-Tac-Toe
Implements the base Game interface for easy extension to other board games.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
import chess


class Game(ABC):
    """Abstract base class for board games."""

    @abstractmethod
    def get_legal_moves(self) -> List:
        pass

    @abstractmethod
    def make_move(self, move, player: str) -> None:
        pass

    @abstractmethod
    def undo_move(self, move) -> None:
        pass

    @abstractmethod
    def is_terminal(self) -> bool:
        pass

    @abstractmethod
    def get_winner(self) -> Optional[str]:
        pass

    @abstractmethod
    def evaluate(self, player: str, opponent: str) -> int:
        pass

    @abstractmethod
    def display(self) -> None:
        pass

    @abstractmethod
    def clone(self) -> "Game":
        pass


class TicTacToe(Game):
    """
    Standard 3x3 Tic-Tac-Toe game.

    Board positions:
        0 | 1 | 2
       -----------
        3 | 4 | 5
       -----------
        6 | 7 | 8
    """

    WIN_CONDITIONS = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Rows
        (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Columns
        (0, 4, 8), (2, 4, 6),             # Diagonals
    ]

    def __init__(self):
        self.board = [None] * 9
        self._move_history = []

    def get_legal_moves(self) -> List[int]:
        return [i for i, cell in enumerate(self.board) if cell is None]

    def make_move(self, move: int, player: str) -> None:
        if self.board[move] is not None:
            raise ValueError(f"Cell {move} is already occupied.")
        self.board[move] = player
        self._move_history.append(move)

    def undo_move(self, move: int) -> None:
        self.board[move] = None
        if self._move_history and self._move_history[-1] == move:
            self._move_history.pop()

    def is_terminal(self) -> bool:
        return self.get_winner() is not None or len(self.get_legal_moves()) == 0

    def get_winner(self) -> Optional[str]:
        for a, b, c in self.WIN_CONDITIONS:
            if self.board[a] and self.board[a] == self.board[b] == self.board[c]:
                return self.board[a]
        return None

    def evaluate(self, player: str, opponent: str) -> int:
        """Returns +10 if player wins, -10 if opponent wins, 0 for draw."""
        winner = self.get_winner()
        if winner == player:
            return 10
        elif winner == opponent:
            return -10
        return 0

    def display(self) -> None:
        symbols = {None: ".", "X": "X", "O": "O"}
        rows = []
        for row in range(3):
            cells = [symbols[self.board[row * 3 + col]] for col in range(3)]
            rows.append(" | ".join(cells))
        print("\n" + "\n---+---+---\n".join(rows) + "\n")

    def clone(self) -> "TicTacToe":
        new_game = TicTacToe()
        new_game.board = self.board.copy()
        new_game._move_history = self._move_history.copy()
        return new_game


class ConnectFour(Game):
    """
    Standard 6x7 Connect Four game.
    Board is a flat list of 42 cells (0-41).
    0 is top-left, 41 is bottom-right.
    """

    def __init__(self):
        self.board = [None] * 42
        self._move_history = []

    def get_legal_moves(self) -> List[int]:
        # A move is a column index (0-6).
        # Column is legal if its top cell (row 0) is empty.
        return [c for c in range(7) if self.board[c] is None]

    def make_move(self, move: int, player: str) -> None:
        # move is column index (0-6)
        if move < 0 or move > 6 or self.board[move] is not None:
            raise ValueError(f"Invalid column index or column {move} is full.")
        
        # Place piece in the lowest empty row of this column
        for r in range(5, -1, -1):
            idx = r * 7 + move
            if self.board[idx] is None:
                self.board[idx] = player
                self._move_history.append(move)
                return

    def undo_move(self, move: int) -> None:
        # move is column index (0-6)
        # Find the top-most piece in this column and remove it
        for r in range(6):
            idx = r * 7 + move
            if self.board[idx] is not None:
                self.board[idx] = None
                break
        if self._move_history and self._move_history[-1] == move:
            self._move_history.pop()

    def is_terminal(self) -> bool:
        return self.get_winner() is not None or len(self.get_legal_moves()) == 0

    def get_winner(self) -> Optional[str]:
        # Check horizontal wins
        for r in range(6):
            for c in range(4):
                idx = r * 7 + c
                if self.board[idx] and self.board[idx] == self.board[idx+1] == self.board[idx+2] == self.board[idx+3]:
                    return self.board[idx]

        # Check vertical wins
        for r in range(3):
            for c in range(7):
                idx = r * 7 + c
                if self.board[idx] and self.board[idx] == self.board[idx+7] == self.board[idx+14] == self.board[idx+21]:
                    return self.board[idx]

        # Check diagonal down-right wins
        for r in range(3):
            for c in range(4):
                idx = r * 7 + c
                if self.board[idx] and self.board[idx] == self.board[idx+8] == self.board[idx+16] == self.board[idx+24]:
                    return self.board[idx]

        # Check diagonal up-right wins
        for r in range(3, 6):
            for c in range(4):
                idx = r * 7 + c
                if self.board[idx] and self.board[idx] == self.board[idx-6] == self.board[idx-12] == self.board[idx-18]:
                    return self.board[idx]

        return None

    def _evaluate_window(self, window: List[Optional[str]], player: str, opponent: str) -> int:
        player_count = window.count(player)
        opponent_count = window.count(opponent)
        empty_count = window.count(None)

        if player_count == 4:
            return 1000
        elif player_count == 3 and empty_count == 1:
            return 50
        elif player_count == 2 and empty_count == 2:
            return 10

        if opponent_count == 4:
            return -1000
        elif opponent_count == 3 and empty_count == 1:
            return -80
        elif opponent_count == 2 and empty_count == 2:
            return -10

        return 0

    def evaluate(self, player: str, opponent: str) -> int:
        winner = self.get_winner()
        if winner == player:
            return 100000
        elif winner == opponent:
            return -100000

        score = 0

        # Center column bonus
        center_count = 0
        for r in range(6):
            if self.board[r * 7 + 3] == player:
                center_count += 1
            elif self.board[r * 7 + 3] == opponent:
                center_count -= 1
        score += center_count * 15

        # Horizontal windows
        for r in range(6):
            for c in range(4):
                window = [self.board[r * 7 + c + i] for i in range(4)]
                score += self._evaluate_window(window, player, opponent)

        # Vertical windows
        for r in range(3):
            for c in range(7):
                window = [self.board[(r + i) * 7 + c] for i in range(4)]
                score += self._evaluate_window(window, player, opponent)

        # Diagonal down-right
        for r in range(3):
            for c in range(4):
                window = [self.board[(r + i) * 7 + (c + i)] for i in range(4)]
                score += self._evaluate_window(window, player, opponent)

        # Diagonal up-right
        for r in range(3, 6):
            for c in range(4):
                window = [self.board[(r - i) * 7 + (c + i)] for i in range(4)]
                score += self._evaluate_window(window, player, opponent)

        return score

    def display(self) -> None:
        symbols = {None: ".", "X": "X", "O": "O"}
        rows = []
        for r in range(6):
            row_str = " | ".join(symbols[self.board[r * 7 + c]] for c in range(7))
            rows.append(row_str)
        print("\n" + "\n".join(rows))
        print("-" * 25)
        print(" 0   1   2   3   4   5   6\n")

    def clone(self) -> "ConnectFour":
        new_game = ConnectFour()
        new_game.board = self.board.copy()
        new_game._move_history = self._move_history.copy()
        return new_game


class Chess(Game):
    """
    Chess game wrapping python-chess library.
    Board is represented internally by a chess.Board instance.
    """

    def __init__(self):
        self.board = chess.Board()
        self._move_history = []

    @property
    def current_player(self) -> str:
        return "X" if self.board.turn == chess.WHITE else "O"

    def get_legal_moves(self) -> List[chess.Move]:
        return list(self.board.legal_moves)

    def make_move(self, move: chess.Move, player: str) -> None:
        self.board.push(move)
        self._move_history.append(move)

    def undo_move(self, move: chess.Move) -> None:
        self.board.pop()
        if self._move_history and self._move_history[-1] == move:
            self._move_history.pop()

    def is_terminal(self) -> bool:
        return self.board.is_game_over()

    def get_winner(self) -> Optional[str]:
        if self.board.is_checkmate():
            return "O" if self.board.turn == chess.WHITE else "X"
        return None

    def evaluate(self, player: str, opponent: str) -> int:
        if self.board.is_checkmate():
            winner = self.get_winner()
            if winner == player:
                return 1000000
            elif winner == opponent:
                return -1000000

        if self.board.is_stalemate() or self.board.is_insufficient_material() or self.board.is_seventyfive_moves() or self.board.is_fivefold_repetition():
            return 0

        player_color = chess.WHITE if player == "X" else chess.BLACK
        opponent_color = chess.BLACK if player == "X" else chess.WHITE

        score = 0
        piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }

        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                val = piece_values[piece.piece_type]
                if piece.color == player_color:
                    score += val
                else:
                    score -= val

        # Simple positional bonus for center control
        center_squares = [chess.D4, chess.D5, chess.E4, chess.E5]
        for sq in center_squares:
            piece = self.board.piece_at(sq)
            if piece:
                if piece.color == player_color:
                    score += 10
                else:
                    score -= 10

        # Mobility bonus
        score += len(list(self.board.legal_moves)) * 2 if self.board.turn == player_color else -len(list(self.board.legal_moves)) * 2

        return score

    def display(self) -> None:
        print(self.board)

    def clone(self) -> "Chess":
        new_game = Chess()
        new_game.board = self.board.copy()
        new_game._move_history = self._move_history.copy()
        return new_game

