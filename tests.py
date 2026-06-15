"""
tests.py - Unit tests for Board Game Playing Agent
Run with: python tests.py
"""

import unittest
from game import TicTacToe, ConnectFour, Chess
import chess
from agent import MinimaxAgent


class TestTicTacToe(unittest.TestCase):

    def setUp(self):
        self.game = TicTacToe()

    def test_initial_board_is_empty(self):
        self.assertEqual(self.game.get_legal_moves(), list(range(9)))

    def test_make_and_undo_move(self):
        self.game.make_move(4, "X")
        self.assertEqual(self.game.board[4], "X")
        self.game.undo_move(4)
        self.assertIsNone(self.game.board[4])

    def test_winner_detection_row(self):
        for i in range(3):
            self.game.make_move(i, "X")
        self.assertEqual(self.game.get_winner(), "X")

    def test_winner_detection_diagonal(self):
        for i in [0, 4, 8]:
            self.game.make_move(i, "O")
        self.assertEqual(self.game.get_winner(), "O")

    def test_draw_detection(self):
        # X O X
        # X X O
        # O X O
        moves = [(0, "X"), (1, "O"), (2, "X"),
                 (3, "X"), (4, "X"), (5, "O"),
                 (6, "O"), (7, "X"), (8, "O")]
        for pos, p in moves:
            self.game.make_move(pos, p)
        self.assertIsNone(self.game.get_winner())
        self.assertTrue(self.game.is_terminal())

    def test_evaluate_win(self):
        for i in range(3):
            self.game.make_move(i, "X")
        self.assertEqual(self.game.evaluate("X", "O"), 10)
        self.assertEqual(self.game.evaluate("O", "X"), -10)

    def test_clone_independence(self):
        self.game.make_move(0, "X")
        clone = self.game.clone()
        clone.make_move(1, "O")
        self.assertIsNone(self.game.board[1])  # Original unchanged


class TestMinimaxAgent(unittest.TestCase):

    def setUp(self):
        self.agent = MinimaxAgent(player_symbol="O", opponent_symbol="X")

    def test_agent_blocks_winning_move(self):
        """AI should block X from winning at position 2."""
        game = TicTacToe()
        game.make_move(0, "X")
        game.make_move(1, "X")
        # X X _ -> AI (O) must play 2 to block
        move = self.agent.choose_move(game)
        self.assertEqual(move, 2)

    def test_agent_takes_winning_move(self):
        """AI should take position 8 to win."""
        game = TicTacToe()
        game.make_move(0, "O")
        game.make_move(4, "O")
        # O _ _
        # _ O _
        # _ _ _  -> AI should play 8 to win diagonally
        move = self.agent.choose_move(game)
        self.assertEqual(move, 8)

    def test_agent_returns_valid_move(self):
        """Agent always returns a legal move."""
        game = TicTacToe()
        for _ in range(3):
            move = self.agent.choose_move(game)
            self.assertIn(move, game.get_legal_moves())
            game.make_move(move, "O")
            if not game.is_terminal():
                remaining = game.get_legal_moves()
                game.make_move(remaining[0], "X")

    def test_easy_agent_makes_suboptimal_choices(self):
        """Easy AI should occasionally fail to block a winning move due to random play."""
        easy_agent = MinimaxAgent(player_symbol="O", opponent_symbol="X", max_depth=1, difficulty="easy")
        game = TicTacToe()
        game.make_move(0, "X")
        game.make_move(1, "X")
        # X X _ -> O should block at 2 under hard difficulty.
        # But easy agent has 50% chance to play randomly.
        moves = set()
        for _ in range(50):
            moves.add(easy_agent.choose_move(game))
        # It should play multiple different moves, not just 2.
        self.assertTrue(len(moves) > 1)

    def test_medium_agent_makes_suboptimal_choices(self):
        """Medium AI should also occasionally play randomly."""
        medium_agent = MinimaxAgent(player_symbol="O", opponent_symbol="X", max_depth=3, difficulty="medium")
        game = TicTacToe()
        game.make_move(0, "X")
        game.make_move(1, "X")
        moves = set()
        for _ in range(100):
            moves.add(medium_agent.choose_move(game))
        self.assertTrue(len(moves) > 1)


class TestConnectFour(unittest.TestCase):

    def setUp(self):
        self.game = ConnectFour()

    def test_initial_board(self):
        self.assertEqual(len(self.game.get_legal_moves()), 7)
        self.assertTrue(all(x is None for x in self.game.board))

    def test_make_move_drops_to_bottom(self):
        self.game.make_move(3, "X")
        # Column 3 bottom cell is 5 * 7 + 3 = 38
        self.assertEqual(self.game.board[38], "X")
        # Next move in col 3 should land at 4 * 7 + 3 = 31
        self.game.make_move(3, "O")
        self.assertEqual(self.game.board[31], "O")

    def test_column_full_error(self):
        for _ in range(6):
            self.game.make_move(0, "X")
        with self.assertRaises(ValueError):
            self.game.make_move(0, "O")

    def test_horizontal_win(self):
        for col in range(4):
            self.game.make_move(col, "X")
        self.assertEqual(self.game.get_winner(), "X")

    def test_vertical_win(self):
        for _ in range(4):
            self.game.make_move(0, "O")
        self.assertEqual(self.game.get_winner(), "O")

    def test_undo_move(self):
        self.game.make_move(5, "X")
        self.assertEqual(self.game.board[40], "X")
        self.game.undo_move(5)
        self.assertIsNone(self.game.board[40])


class TestChess(unittest.TestCase):

    def setUp(self):
        self.game = Chess()

    def test_initial_setup(self):
        # 20 legal moves for White at start position
        self.assertEqual(len(self.game.get_legal_moves()), 20)
        self.assertEqual(self.game.current_player, "X")

    def test_make_move_updates_state(self):
        # White plays e2e4 (represented as chess.Move.from_uci("e2e4"))
        move = chess.Move.from_uci("e2e4")
        self.game.make_move(move, "X")
        # Turn should switch to Black ("O")
        self.assertEqual(self.game.current_player, "O")
        # Check piece is actually on e4
        self.assertEqual(self.game.board.piece_at(chess.E4).symbol(), "P")

    def test_undo_restores_state(self):
        initial_fen = self.game.board.fen()
        move = chess.Move.from_uci("g1f3")
        self.game.make_move(move, "X")
        self.game.undo_move(move)
        self.assertEqual(self.game.board.fen(), initial_fen)
        self.assertEqual(self.game.current_player, "X")

    def test_fool_mate_checkmate_detection(self):
        # Fool's mate: 1. f3 e5 2. g4 Qh4#
        moves = ["f2f3", "e7e5", "g2g4", "d8h4"]
        players = ["X", "O", "X", "O"]
        for m_str, p in zip(moves, players):
            move = chess.Move.from_uci(m_str)
            self.game.make_move(move, p)
        self.assertTrue(self.game.is_terminal())
        self.assertEqual(self.game.get_winner(), "O")  # Black ("O") wins


if __name__ == "__main__":
    unittest.main(verbosity=2)

