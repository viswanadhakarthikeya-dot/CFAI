"""
gui.py - Modern Tkinter-based GUI for the Board Game Agent platform.
Provides a dark-themed sidebar dashboard and a dynamic interactive board.
"""

import os
import math
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from game import TicTacToe, ConnectFour, Chess
import chess
from agent import MinimaxAgent


class BoardGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GAME HUB - Board Game Platform")
        self.root.geometry("880x620")
        self.root.configure(bg="#121214")
        self.root.resizable(False, False)

        # Style customization
        self.font_family = "Segoe UI" if os.name == "nt" else "Helvetica"
        
        # Configure TTK Styles
        self.setup_styles()

        # Game State
        self.game = None
        self.current_turn = "X"  # Tracks alternating turn for TicTacToe/ConnectFour
        self.ai_thinking = False
        self.hover_cell = None
        self.hover_col = None

        # Scores State
        self.score_x = 0
        self.score_o = 0
        self.score_draws = 0

        # Setup GUI Components
        self.create_widgets()
        
        # Initialize Game
        self.reset_game(reset_scores=True)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Colors
        bg_dark = "#18181C"
        text_light = "#E4E4E7"
        accent_color = "#6366F1"
        
        # Custom frame
        style.configure("TFrame", background=bg_dark)
        
        # Custom Label
        style.configure("TLabel", background=bg_dark, foreground=text_light, font=(self.font_family, 10))
        style.configure("Title.TLabel", font=(self.font_family, 14, "bold"), foreground="#FFFFFF")
        style.configure("Sub.TLabel", font=(self.font_family, 9), foreground="#A1A1AA")
        
        # Custom Button
        style.configure("TButton", 
                        background=accent_color, 
                        foreground="#FFFFFF", 
                        bordercolor=accent_color,
                        font=(self.font_family, 10, "bold"), 
                        focuscolor="none")
        style.map("TButton",
                  background=[("active", "#4F46E5"), ("pressed", "#4338CA")],
                  bordercolor=[("active", "#4F46E5")])
                  
        # Secondary Button
        style.configure("Secondary.TButton", 
                        background="#3F3F46", 
                        foreground=text_light, 
                        bordercolor="#3F3F46",
                        font=(self.font_family, 9, "bold"))
        style.map("Secondary.TButton",
                  background=[("active", "#27272A"), ("pressed", "#18181B")],
                  bordercolor=[("active", "#27272A")])

        # Custom Dropdowns
        style.configure("TCombobox", 
                        fieldbackground="#27272A", 
                        background="#3F3F46", 
                        foreground="#E4E4E7",
                        bordercolor="#3F3F46",
                        lightcolor="#3F3F46",
                        darkcolor="#3F3F46",
                        arrowcolor="#E4E4E7")
        style.map("TCombobox", 
                  fieldbackground=[("readonly", "#27272A")],
                  foreground=[("readonly", "#E4E4E7")])

    def create_widgets(self):
        # ----------------- Main Layout Frames -----------------
        # Sidebar Panel (Left)
        self.sidebar = ttk.Frame(self.root, padding=20)
        self.sidebar.place(x=0, y=0, width=300, height=620)

        # Border separator
        separator = tk.Frame(self.root, bg="#27272A", width=2)
        separator.place(x=300, y=0, height=620)

        # Main Workspace Area (Right)
        self.workspace = tk.Frame(self.root, bg="#121214")
        self.workspace.place(x=302, y=0, width=578, height=620)

        # ----------------- Sidebar Contents -----------------
        # Logo Section
        logo_frame = tk.Frame(self.sidebar, bg="#18181C")
        logo_frame.pack(fill="x", pady=(0, 20))
        
        logo_label = tk.Label(logo_frame, text="🎮 GAME HUB", font=(self.font_family, 16, "bold"), bg="#18181C", fg="#6366F1")
        logo_label.pack(anchor="w")
        
        sub_logo_label = ttk.Label(logo_frame, text="Board Game Playing Platform", style="Sub.TLabel")
        sub_logo_label.pack(anchor="w", pady=(2, 0))

        # Settings Section
        settings_frame = tk.Frame(self.sidebar, bg="#18181C")
        settings_frame.pack(fill="x", pady=10)

        # Game Select
        ttk.Label(settings_frame, text="Select Game").pack(anchor="w", pady=(0, 4))
        self.game_type_var = tk.StringVar(value="tictactoe")
        self.game_select = ttk.Combobox(settings_frame, textvariable=self.game_type_var, state="readonly")
        self.game_select["values"] = ("Tic-Tac-Toe", "Connect Four", "Chess")
        self.game_select.current(0)
        self.game_select.pack(fill="x", pady=(0, 12))
        self.game_select.bind("<<ComboboxSelected>>", self.on_game_change)

        # Game Mode
        ttk.Label(settings_frame, text="Game Mode").pack(anchor="w", pady=(0, 4))
        self.mode_var = tk.StringVar(value="pve")
        self.mode_select = ttk.Combobox(settings_frame, textvariable=self.mode_var, state="readonly")
        self.mode_select["values"] = ("Human vs AI", "AI vs AI", "Human vs Human")
        self.mode_select.current(0)
        self.mode_select.pack(fill="x", pady=(0, 12))
        self.mode_select.bind("<<ComboboxSelected>>", self.on_setting_change)

        # AI Difficulty (only active if AI is playing)
        self.difficulty_label = ttk.Label(settings_frame, text="AI Difficulty")
        self.difficulty_label.pack(anchor="w", pady=(0, 4))
        self.difficulty_var = tk.StringVar(value="medium")
        self.difficulty_select = ttk.Combobox(settings_frame, textvariable=self.difficulty_var, state="readonly")
        self.difficulty_select["values"] = ("Easy", "Medium", "Hard")
        self.difficulty_select.current(1)
        self.difficulty_select.pack(fill="x", pady=(0, 12))
        self.difficulty_select.bind("<<ComboboxSelected>>", self.on_setting_change)

        # Play As Symbol (only active in PvE mode)
        self.play_as_label = ttk.Label(settings_frame, text="Play As")
        self.play_as_label.pack(anchor="w", pady=(0, 4))
        self.play_as_var = tk.StringVar(value="X")
        self.play_as_select = ttk.Combobox(settings_frame, textvariable=self.play_as_var, state="readonly")
        self.play_as_select["values"] = ("X (First)", "O (Second)")
        self.play_as_select.current(0)
        self.play_as_select.pack(fill="x", pady=(0, 12))
        self.play_as_select.bind("<<ComboboxSelected>>", self.on_setting_change)

        # Scoreboard Section
        ttk.Label(self.sidebar, text="SCOREBOARD", style="Title.TLabel").pack(anchor="w", pady=(10, 8))
        
        score_grid = tk.Frame(self.sidebar, bg="#18181C")
        score_grid.pack(fill="x", pady=(0, 10))

        # Setup custom styled tiles for scoreboard
        self.score_x_tile = tk.Frame(score_grid, bg="#27272A", bd=0, highlightthickness=1, highlightbackground="#3F3F46")
        self.score_x_tile.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.lbl_x_title = tk.Label(self.score_x_tile, text="X / Black", bg="#27272A", fg="#A1A1AA", font=(self.font_family, 8, "bold"))
        self.lbl_x_title.pack(pady=(4, 0))
        self.lbl_x_val = tk.Label(self.score_x_tile, text="0", bg="#27272A", fg="#38BDF8", font=(self.font_family, 14, "bold"))
        self.lbl_x_val.pack(pady=(0, 4))

        self.score_o_tile = tk.Frame(score_grid, bg="#27272A", bd=0, highlightthickness=1, highlightbackground="#3F3F46")
        self.score_o_tile.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        self.lbl_o_title = tk.Label(self.score_o_tile, text="O / White", bg="#27272A", fg="#A1A1AA", font=(self.font_family, 8, "bold"))
        self.lbl_o_title.pack(pady=(4, 0))
        self.lbl_o_val = tk.Label(self.score_o_tile, text="0", bg="#27272A", fg="#F43F5E", font=(self.font_family, 14, "bold"))
        self.lbl_o_val.pack(pady=(0, 4))

        self.score_draw_tile = tk.Frame(score_grid, bg="#27272A", bd=0, highlightthickness=1, highlightbackground="#3F3F46")
        self.score_draw_tile.grid(row=0, column=2, sticky="nsew", padx=2, pady=2)
        lbl_draw_title = tk.Label(self.score_draw_tile, text="Draws", bg="#27272A", fg="#A1A1AA", font=(self.font_family, 8, "bold"))
        lbl_draw_title.pack(pady=(4, 0))
        self.lbl_draw_val = tk.Label(self.score_draw_tile, text="0", bg="#27272A", fg="#E4E4E7", font=(self.font_family, 14, "bold"))
        self.lbl_draw_val.pack(pady=(0, 4))

        score_grid.columnconfigure(0, weight=1)
        score_grid.columnconfigure(1, weight=1)
        score_grid.columnconfigure(2, weight=1)

        self.btn_reset_score = ttk.Button(self.sidebar, text="Reset Scores", style="Secondary.TButton", command=self.reset_scores)
        self.btn_reset_score.pack(fill="x", pady=(0, 15))

        # Dynamic Game Rules
        rules_frame = tk.Frame(self.sidebar, bg="#27272A", bd=0, highlightthickness=1, highlightbackground="#3F3F46")
        rules_frame.pack(fill="both", expand=True, pady=(10, 0))
        rules_title = tk.Label(rules_frame, text="📖 How to Play", bg="#27272A", fg="#FFFFFF", font=(self.font_family, 10, "bold"))
        rules_title.pack(anchor="w", padx=10, pady=(8, 4))
        self.rules_label = tk.Label(rules_frame, text="", bg="#27272A", fg="#A1A1AA", font=(self.font_family, 9), wraplength=230, justify="left")
        self.rules_label.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.update_rules()

        # ----------------- Main Workspace Area Contents -----------------
        # Header (Game Title and Current State)
        header_frame = tk.Frame(self.workspace, bg="#121214")
        header_frame.pack(fill="x", padx=30, pady=(25, 15))

        self.lbl_game_title = tk.Label(header_frame, text="Tic-Tac-Toe", font=(self.font_family, 18, "bold"), bg="#121214", fg="#FFFFFF")
        self.lbl_game_title.pack(side="left", anchor="w")

        self.btn_restart = ttk.Button(header_frame, text="Restart Match", command=self.restart_game)
        self.btn_restart.pack(side="right", anchor="e")

        # Game Status indicator label below the header
        self.lbl_status = tk.Label(self.workspace, text="Your turn (Player X)", font=(self.font_family, 11), bg="#121214", fg="#A1A1AA")
        self.lbl_status.pack(anchor="w", padx=30, pady=(0, 15))

        # Interactive Canvas container
        self.canvas_container = tk.Frame(self.workspace, bg="#121214")
        self.canvas_container.pack(expand=True, fill="both", padx=30, pady=(0, 30))

        # Canvas drawing element
        self.canvas = tk.Canvas(self.canvas_container, bg="#18181C", highlightthickness=1, highlightbackground="#27272A")
        self.canvas.pack(expand=True)

        # Bind events to canvas
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Leave>", self.on_mouse_leave)

    def update_rules(self):
        game_choice = self.game_type_var.get()
        if game_choice == "Tic-Tac-Toe":
            rules = "Line up three of your markers (X or O) in a row, column, or diagonal on a 3x3 grid to win. Block your opponent from doing the same!"
            self.lbl_x_title.config(text="X (Blue)")
            self.lbl_o_title.config(text="O (Red)")
        elif game_choice == "Connect Four":
            rules = "Drop colored discs into a 7-column, 6-row grid. The first to form a horizontal, vertical, or diagonal line of four of their own discs wins!"
            self.lbl_x_title.config(text="Red (X)")
            self.lbl_o_title.config(text="Yellow (O)")
        else:
            rules = "Move your pieces strategically to checkmate the opponent's King. Click a piece to select it and see legal moves, then click a target square to move."
            self.lbl_x_title.config(text="White (X)")
            self.lbl_o_title.config(text="Black (O)")
        self.rules_label.config(text=rules)

    # ----------------- Settings & Control Callbacks -----------------
    def on_game_change(self, event=None):
        game_choice = self.game_type_var.get()
        self.lbl_game_title.config(text=game_choice)
        self.update_rules()
        self.reset_game(reset_scores=True)

    def on_setting_change(self, event=None):
        # Update visibility and interactivity of controls depending on current mode
        mode = self.mode_var.get()
        if mode == "Human vs Human":
            self.difficulty_select.config(state="disabled")
            self.play_as_select.config(state="disabled")
        elif mode == "AI vs AI":
            self.difficulty_select.config(state="readonly")
            self.play_as_select.config(state="disabled")
        else:  # Human vs AI
            self.difficulty_select.config(state="readonly")
            self.play_as_select.config(state="readonly")
        
        self.restart_game()

    def reset_scores(self):
        self.score_x = 0
        self.score_o = 0
        self.score_draws = 0
        self.update_scoreboard_display()

    def update_scoreboard_display(self):
        self.lbl_x_val.config(text=str(self.score_x))
        self.lbl_o_val.config(text=str(self.score_o))
        self.lbl_draw_val.config(text=str(self.score_draws))

    # ----------------- Game Control Logic -----------------
    def reset_game(self, reset_scores=False):
        if reset_scores:
            self.reset_scores()
            
        game_choice = self.game_type_var.get()
        if game_choice == "Tic-Tac-Toe":
            self.game = TicTacToe()
            self.canvas.config(width=420, height=420)
        elif game_choice == "Connect Four":
            self.game = ConnectFour()
            self.canvas.config(width=490, height=420)
        else:  # Chess
            self.game = Chess()
            self.canvas.config(width=480, height=540)

        self.current_turn = "X"
        self.ai_thinking = False
        self.hover_cell = None
        self.hover_col = None
        self.selected_square = None

        self.root.update_idletasks()
        self.draw_board()
        self.update_status_label()

        # If starting in AI vs AI or AI plays first, kick off the AI process
        self.check_and_trigger_ai()

    def restart_game(self):
        self.reset_game(reset_scores=False)

    def get_current_player(self):
        if hasattr(self.game, "current_player"):
            return self.game.current_player
        return self.current_turn

    def is_human_turn(self):
        if self.ai_thinking:
            return False
            
        mode = self.mode_var.get()
        if mode == "Human vs Human":
            return True
        if mode == "AI vs AI":
            return False
            
        # Human vs AI
        current_player = self.get_current_player()
        play_as_choice = self.play_as_var.get()
        human_symbol = "X" if "X" in play_as_choice else "O"
        return current_player == human_symbol

    def update_status_label(self):
        if self.game.is_terminal():
            winner = self.game.get_winner()
            if winner:
                game_choice = self.game_type_var.get()
                if game_choice == "Chess":
                    w_name = "White (X)" if winner == "X" else "Black (O)"
                    text = f"Game Over! Checkmate! {w_name} wins!"
                elif game_choice == "Connect Four":
                    w_name = "Red (X)" if winner == "X" else "Yellow (O)"
                    text = f"Game Over! {w_name} wins!"
                else:
                    text = f"Game Over! Player {winner} wins!"
            else:
                if self.game_type_var.get() == "Chess":
                    text = "Game Over! Draw (stalemate/repetition/insufficient material)."
                else:
                    text = "Game Over! It's a draw!"
            self.lbl_status.config(text=text, fg="#10B981")
            return

        if self.ai_thinking:
            self.lbl_status.config(text="AI is thinking...", fg="#F59E0B")
            return

        curr = self.get_current_player()
        mode = self.mode_var.get()
        game_choice = self.game_type_var.get()
        
        # Format human readable player labels
        if game_choice == "Tic-Tac-Toe":
            p_name = "Player X" if curr == "X" else "Player O"
        elif game_choice == "Connect Four":
            p_name = "Red (X)" if curr == "X" else "Yellow (O)"
        else:
            p_name = "White (X)" if curr == "X" else "Black (O)"

        if mode == "Human vs Human":
            self.lbl_status.config(text=f"Your Turn ({p_name})", fg="#A1A1AA")
        elif mode == "AI vs AI":
            self.lbl_status.config(text=f"AI Turn ({p_name})", fg="#A1A1AA")
        else:  # Human vs AI
            human_symbol = "X" if "X" in self.play_as_var.get() else "O"
            if curr == human_symbol:
                self.lbl_status.config(text=f"Your Turn ({p_name})", fg="#A1A1AA")
            else:
                self.lbl_status.config(text=f"AI's Turn ({p_name}) - Calculating...", fg="#A1A1AA")

    # ----------------- Drawing Routines -----------------
    def draw_board(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1 or h <= 1:
            # Fallback to defaults if not yet rendered
            game_choice = self.game_type_var.get()
            if game_choice == "Tic-Tac-Toe":
                w, h = 420, 420
            elif game_choice == "Connect Four":
                w, h = 490, 420
            else:
                w, h = 480, 540

        game_choice = self.game_type_var.get()
        if game_choice == "Tic-Tac-Toe":
            self.draw_tictactoe_board(w, h)
        elif game_choice == "Connect Four":
            self.draw_connectfour_board(w, h)
        else:
            self.draw_chess_board(w, h)

        # Draw Game Over Overlay if terminal
        if self.game.is_terminal():
            self.draw_game_over_overlay(w, h)
        elif self.ai_thinking:
            # Draw tiny thinking status text inside canvas
            self.canvas.create_rectangle(0, h - 30, w, h, fill="#121214", outline="")
            self.canvas.create_text(20, h - 15, text="🤖 AI is calculating moves...", font=(self.font_family, 10, "italic"), fill="#A1A1AA", anchor="w")

    def draw_tictactoe_board(self, w, h):
        cell_w = w / 3
        cell_h = h / 3
        
        # Grid background
        self.canvas.create_rectangle(0, 0, w, h, fill="#18181C", outline="")

        # Draw grid lines
        grid_color = "#3F3F46"
        self.canvas.create_line(cell_w, 20, cell_w, h - 20, fill=grid_color, width=4, capstyle="round")
        self.canvas.create_line(cell_w * 2, 20, cell_w * 2, h - 20, fill=grid_color, width=4, capstyle="round")
        self.canvas.create_line(20, cell_h, w - 20, cell_h, fill=grid_color, width=4, capstyle="round")
        self.canvas.create_line(20, cell_h * 2, w - 20, cell_h * 2, fill=grid_color, width=4, capstyle="round")

        # Draw pieces
        for idx, cell in enumerate(self.game.board):
            r = idx // 3
            c = idx % 3
            cx = c * cell_w + cell_w / 2
            cy = r * cell_h + cell_h / 2
            pad = cell_w * 0.22

            # Hover Preview
            if self.hover_cell == idx and cell is None and self.is_human_turn():
                curr = self.get_current_player()
                if curr == "X":
                    self.canvas.create_line(cx - cell_w/2 + pad, cy - cell_h/2 + pad, cx + cell_w/2 - pad, cy + cell_h/2 - pad, fill="#38BDF8", width=2, dash=(4, 4))
                    self.canvas.create_line(cx + cell_w/2 - pad, cy - cell_h/2 + pad, cx - cell_w/2 + pad, cy + cell_h/2 - pad, fill="#38BDF8", width=2, dash=(4, 4))
                else:
                    self.canvas.create_oval(cx - cell_w/2 + pad, cy - cell_h/2 + pad, cx + cell_w/2 - pad, cy + cell_h/2 - pad, outline="#F43F5E", width=2, dash=(4, 4))

            # Filled cells
            if cell == "X":
                self.canvas.create_line(cx - cell_w/2 + pad, cy - cell_h/2 + pad, cx + cell_w/2 - pad, cy + cell_h/2 - pad, fill="#38BDF8", width=6, capstyle="round")
                self.canvas.create_line(cx + cell_w/2 - pad, cy - cell_h/2 + pad, cx - cell_w/2 + pad, cy + cell_h/2 - pad, fill="#38BDF8", width=6, capstyle="round")
            elif cell == "O":
                self.canvas.create_oval(cx - cell_w/2 + pad, cy - cell_h/2 + pad, cx + cell_w/2 - pad, cy + cell_h/2 - pad, outline="#F43F5E", width=6)

    def draw_connectfour_board(self, w, h):
        cell_w = w / 7
        cell_h = h / 6
        pad = 8

        # Draw Board Frame (Blue plastic board)
        self.canvas.create_rectangle(0, 0, w, h, fill="#1E3A8A", outline="")

        # Draw Cells / Slots
        for r in range(6):
            for c in range(7):
                idx = r * 7 + c
                cell = self.game.board[idx]
                
                cx1 = c * cell_w + pad
                cy1 = r * cell_h + pad
                cx2 = (c + 1) * cell_w - pad
                cy2 = (r + 1) * cell_h - pad

                # Determine fill color
                if cell == "X":
                    fill_color = "#EF4444"  # Red
                    outline_color = "#B91C1C"
                elif cell == "O":
                    fill_color = "#F59E0B"  # Yellow
                    outline_color = "#D97706"
                else:
                    fill_color = "#18181C"  # Empty slot matches background
                    outline_color = "#121214"

                self.canvas.create_oval(cx1, cy1, cx2, cy2, fill=fill_color, outline=outline_color, width=2)

        # Hover Preview Indicator (drawn above the lowest empty cell in column)
        if self.hover_col is not None and self.is_human_turn():
            # Find lowest empty slot in hover_col
            lowest_r = self.get_lowest_empty_row(self.hover_col)
            if lowest_r is not None:
                curr = self.get_current_player()
                preview_color = "#EF4444" if curr == "X" else "#F59E0B"
                
                cx1 = self.hover_col * cell_w + pad
                cy1 = lowest_r * cell_h + pad
                cx2 = (self.hover_col + 1) * cell_w - pad
                cy2 = (lowest_r + 1) * cell_h - pad
                self.canvas.create_oval(cx1, cy1, cx2, cy2, outline=preview_color, width=2, dash=(3, 3))

    def get_lowest_empty_row(self, col):
        for r in range(5, -1, -1):
            if self.game.board[r * 7 + col] is None:
                return r
        return None

    def get_captured_pieces(self):
        import chess
        # Start count
        counts = {
            chess.WHITE: {chess.PAWN: 8, chess.KNIGHT: 2, chess.BISHOP: 2, chess.ROOK: 2, chess.QUEEN: 1},
            chess.BLACK: {chess.PAWN: 8, chess.KNIGHT: 2, chess.BISHOP: 2, chess.ROOK: 2, chess.QUEEN: 1}
        }
        # Decrement for pieces still on board
        for sq in chess.SQUARES:
            piece = self.game.board.piece_at(sq)
            if piece and piece.piece_type != chess.KING:
                counts[piece.color][piece.piece_type] -= 1
        
        # Filter out 0 counts to make drawing easier
        white_cap = {pt: count for pt, count in counts[chess.WHITE].items() if count > 0}
        black_cap = {pt: count for pt, count in counts[chess.BLACK].items() if count > 0}
        return white_cap, black_cap

    def draw_chess_board(self, w, h):
        cell_w = w / 8
        cell_h = (h - 60) / 8  # 30px top and bottom margin for scoreboard
        import chess

        piece_chars = {
            chess.PAWN: "♟",
            chess.KNIGHT: "♞",
            chess.BISHOP: "♝",
            chess.ROOK: "♜",
            chess.QUEEN: "♛",
            chess.KING: "♚"
        }

        # Calculate captured pieces and material differences
        captured_white, captured_black = self.get_captured_pieces()
        
        # Calculate material values
        values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9}
        
        white_material = sum(len(self.game.board.pieces(pt, chess.WHITE)) * val for pt, val in values.items())
        black_material = sum(len(self.game.board.pieces(pt, chess.BLACK)) * val for pt, val in values.items())
        
        diff = white_material - black_material

        # ----------------- Draw Top Scoreboard (Black Profile + Captured White Pieces) -----------------
        self.canvas.create_rectangle(0, 0, w, 30, fill="#18181C", outline="")
        self.canvas.create_text(15, 15, text="Black (O)", font=(self.font_family, 10, "bold"), fill="#A1A1AA", anchor="w")
        
        # Captured White pieces (captured by Black) - drawn in white color
        cap_x = 100
        piece_symbols = {chess.PAWN: "♟", chess.KNIGHT: "♞", chess.BISHOP: "♝", chess.ROOK: "♜", chess.QUEEN: "♛"}
        for pt, count in captured_white.items():
            for _ in range(count):
                self.canvas.create_text(cap_x, 15, text=piece_symbols[pt], font=(self.font_family, 12), fill="#F8FAFC")
                cap_x += 14
        
        # If Black has material advantage
        if diff < 0:
            self.canvas.create_text(cap_x + 5, 15, text=f"+{abs(diff)}", font=(self.font_family, 10, "bold"), fill="#10B981", anchor="w")

        # ----------------- Draw Bottom Scoreboard (White Profile + Captured Black Pieces) -----------------
        self.canvas.create_rectangle(0, h - 30, w, h, fill="#18181C", outline="")
        self.canvas.create_text(15, h - 15, text="White (X)", font=(self.font_family, 10, "bold"), fill="#A1A1AA", anchor="w")
        
        # Captured Black pieces (captured by White) - drawn in dark color with light border
        cap_x = 100
        for pt, count in captured_black.items():
            for _ in range(count):
                self.canvas.create_text(cap_x + 1, h - 14, text=piece_symbols[pt], font=(self.font_family, 12), fill="#E5E5EA")
                self.canvas.create_text(cap_x, h - 15, text=piece_symbols[pt], font=(self.font_family, 12), fill="#18181B")
                cap_x += 14
                
        # If White has material advantage
        if diff > 0:
            self.canvas.create_text(cap_x + 5, h - 15, text=f"+{diff}", font=(self.font_family, 10, "bold"), fill="#10B981", anchor="w")

        # ----------------- Draw Board Squares -----------------
        # Find last move squares for highlighting
        last_move_squares = []
        if len(self.game.board.move_stack) > 0:
            lm = self.game.board.move_stack[-1]
            last_move_squares = [lm.from_square, lm.to_square]

        for r in range(8):
            for c in range(8):
                sq_idx = (7 - r) * 8 + c
                cx1 = c * cell_w
                cy1 = 30 + r * cell_h
                cx2 = (c + 1) * cell_w
                cy2 = 30 + (r + 1) * cell_h
                
                is_light = (r + c) % 2 == 0
                
                # Check if this square is highlighted due to the last move
                if sq_idx in last_move_squares:
                    bg_color = "#BAE6FD" if is_light else "#7DD3FC"  # Soft sky-blue highlights
                else:
                    bg_color = "#F0D9B5" if is_light else "#B58863"
                
                self.canvas.create_rectangle(cx1, cy1, cx2, cy2, fill=bg_color, outline="")

        # Highlight check in red if King is in check
        if self.game.board.is_check():
            king_square = self.game.board.king(self.game.board.turn)
            k_rank = king_square // 8
            k_file = king_square % 8
            k_row = 7 - k_rank
            
            kcx1 = k_file * cell_w
            kcy1 = 30 + k_row * cell_h
            kcx2 = (k_file + 1) * cell_w
            kcy2 = 30 + (k_row + 1) * cell_h
            
            self.canvas.create_rectangle(kcx1, kcy1, kcx2, kcy2, fill="#FECACA", outline="#EF4444", width=3)

        # Highlight hovered cell
        if self.hover_cell is not None and self.is_human_turn() and self.hover_cell < 64:
            hc_row = self.hover_cell // 8
            hc_col = self.hover_cell % 8
            
            hc_x1 = hc_col * cell_w
            hc_y1 = 30 + hc_row * cell_h
            hc_x2 = (hc_col + 1) * cell_w
            hc_y2 = 30 + (hc_row + 1) * cell_h
            self.canvas.create_rectangle(hc_x1, hc_y1, hc_x2, hc_y2, outline="#38BDF8", width=2)

        # Highlight selected square in gold if any
        if self.selected_square is not None:
            sel_rank = self.selected_square // 8
            sel_file = self.selected_square % 8
            sel_row = 7 - sel_rank
            
            scx1 = sel_file * cell_w
            scy1 = 30 + sel_row * cell_h
            scx2 = (sel_file + 1) * cell_w
            scy2 = 30 + (sel_row + 1) * cell_h
            
            self.canvas.create_rectangle(scx1, scy1, scx2, scy2, outline="#FBBF24", width=3)

        # Draw legal moves for selected piece
        if self.selected_square is not None and self.is_human_turn():
            for move in self.game.get_legal_moves():
                if move.from_square == self.selected_square:
                    dest_rank = move.to_square // 8
                    dest_file = move.to_square % 8
                    dest_row = 7 - dest_rank
                    
                    dcx = dest_file * cell_w + cell_w / 2
                    dcy = 30 + dest_row * cell_h + cell_h / 2
                    self.canvas.create_oval(dcx - 6, dcy - 6, dcx + 6, dcy + 6, fill="#10B981", outline="")

        # Draw Chess pieces
        for sq in chess.SQUARES:
            piece = self.game.board.piece_at(sq)
            if piece:
                char = piece_chars[piece.piece_type]
                rank = sq // 8
                file = sq % 8
                row = 7 - rank
                
                cx = file * cell_w + cell_w / 2
                cy = 30 + row * cell_h + cell_h / 2
                
                color = "#FFFFFF" if piece.color == chess.WHITE else "#1C1C1E"
                shadow_color = "#3A3A3C" if piece.color == chess.WHITE else "#E5E5EA"
                
                # Draw drop shadow for 3D outline effect
                self.canvas.create_text(cx + 1, cy + 1, text=char, font=(self.font_family, 32), fill=shadow_color)
                # Draw main piece character
                self.canvas.create_text(cx, cy, text=char, font=(self.font_family, 32), fill=color)

    def handle_chess_click(self, square):
        import chess
        curr_player = self.get_current_player()
        player_color = chess.WHITE if curr_player == "X" else chess.BLACK

        piece = self.game.board.piece_at(square)

        if self.selected_square is None:
            if piece and piece.color == player_color:
                self.selected_square = square
                self.draw_board()
        else:
            # Try to make a move
            move = chess.Move(self.selected_square, square)
            
            # Check for pawn promotion (auto-promote to Queen)
            moving_piece = self.game.board.piece_at(self.selected_square)
            if moving_piece and moving_piece.piece_type == chess.PAWN:
                to_rank = chess.square_rank(square)
                if (moving_piece.color == chess.WHITE and to_rank == 7) or \
                   (moving_piece.color == chess.BLACK and to_rank == 0):
                    move = chess.Move(self.selected_square, square, promotion=chess.QUEEN)

            legal_moves = self.game.get_legal_moves()
            if move in legal_moves:
                self.game.make_move(move, curr_player)
                self.selected_square = None
                self.on_move_made()
            else:
                # If clicking another of their own pieces, update selection
                if piece and piece.color == player_color:
                    self.selected_square = square
                    self.draw_board()
                else:
                    self.selected_square = None
                    self.draw_board()

    def draw_game_over_overlay(self, w, h):
        cx, cy = w / 2, h / 2
        box_w, box_h = 320, 200

        # Semi-transparent feel: draw a dark solid box with rounded corners (rendered via rectangle)
        # Background card
        self.canvas.create_rectangle(cx - box_w/2, cy - box_h/2, cx + box_w/2, cy + box_h/2, 
                                     fill="#1F1F23", outline="#6366F1", width=3)
        
        winner = self.game.get_winner()
        game_choice = self.game_type_var.get()
        
        if winner:
            self.canvas.create_text(cx, cy - 50, text="👑", font=(self.font_family, 36))
            
            # Winner label formatting
            if game_choice == "Reversi (Othello)":
                w_name = "Black (X)" if winner == "X" else "White (O)"
            elif game_choice == "Connect Four":
                w_name = "Red (X)" if winner == "X" else "Yellow (O)"
            else:
                w_name = f"Player {winner}"
                
            self.canvas.create_text(cx, cy + 10, text=f"{w_name} Wins!", 
                                     font=(self.font_family, 18, "bold"), fill="#FFFFFF")
            self.canvas.create_text(cx, cy + 34, text="Well played match.", 
                                     font=(self.font_family, 10), fill="#A1A1AA")
        else:
            self.canvas.create_text(cx, cy - 50, text="🤝", font=(self.font_family, 36))
            self.canvas.create_text(cx, cy + 10, text="It's a Draw!", 
                                     font=(self.font_family, 18, "bold"), fill="#FFFFFF")
            self.canvas.create_text(cx, cy + 34, text="No moves left.", 
                                     font=(self.font_family, 10), fill="#A1A1AA")

        # Play Again Button drawing inside Canvas
        btn_x1, btn_y1 = cx - 75, cy + 55
        btn_x2, btn_y2 = cx + 75, cy + 85
        self.canvas.create_rectangle(btn_x1, btn_y1, btn_x2, btn_y2, 
                                     fill="#6366F1", outline="", tags="overlay_restart")
        self.canvas.create_text(cx, cy + 70, text="Play Again", 
                                 font=(self.font_family, 11, "bold"), fill="#FFFFFF", tags="overlay_restart")

    # ----------------- Interaction Callbacks -----------------
    def on_mouse_move(self, event):
        if self.game.is_terminal() or self.ai_thinking or not self.is_human_turn():
            return

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        game_choice = self.game_type_var.get()

        if game_choice == "Tic-Tac-Toe":
            col = int(event.x // (w / 3))
            row = int(event.y // (h / 3))
            cell = row * 3 + col
            if 0 <= cell < 9:
                if self.hover_cell != cell:
                    self.hover_cell = cell
                    self.draw_board()
        elif game_choice == "Connect Four":
            col = int(event.x // (w / 7))
            if 0 <= col < 7:
                if self.hover_col != col:
                    self.hover_col = col
                    self.draw_board()
        else:  # Chess
            cell_w = w / 8
            cell_h = (h - 60) / 8
            if 30 <= event.y < h - 30:
                col = int(event.x // cell_w)
                row = int((event.y - 30) // cell_h)
                if 0 <= col < 8 and 0 <= row < 8:
                    cell = row * 8 + col
                    if self.hover_cell != cell:
                        self.hover_cell = cell
                        self.draw_board()
            else:
                if self.hover_cell is not None:
                    self.hover_cell = None
                    self.draw_board()

    def on_mouse_leave(self, event):
        self.hover_cell = None
        self.hover_col = None
        self.draw_board()

    def on_canvas_click(self, event):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        # Check overlay "Play Again" click first if game is over
        if self.game.is_terminal():
            items = self.canvas.find_withtag("current")
            if items and any("overlay_restart" in self.canvas.gettags(item) for item in items):
                self.restart_game()
            return

        if self.ai_thinking or not self.is_human_turn():
            return

        game_choice = self.game_type_var.get()
        curr_player = self.get_current_player()

        if game_choice == "Tic-Tac-Toe":
            col = int(event.x // (w / 3))
            row = int(event.y // (h / 3))
            move = row * 3 + col
            legal = self.game.get_legal_moves()
            if move in legal:
                self.game.make_move(move, curr_player)
                self.current_turn = "O" if self.current_turn == "X" else "X"
                self.hover_cell = None
                self.on_move_made()

        elif game_choice == "Connect Four":
            col = int(event.x // (w / 7))
            legal = self.game.get_legal_moves()
            if col in legal:
                self.game.make_move(col, curr_player)
                self.current_turn = "O" if self.current_turn == "X" else "X"
                self.hover_col = None
                self.on_move_made()

        else:  # Chess
            cell_w = w / 8
            cell_h = (h - 60) / 8
            if 30 <= event.y < h - 30:
                col = int(event.x // cell_w)
                row = int((event.y - 30) // cell_h)
                if 0 <= col < 8 and 0 <= row < 8:
                    square = (7 - row) * 8 + col
                    self.handle_chess_click(square)

    def on_move_made(self):
        # Refresh drawing and status text
        self.draw_board()
        self.update_status_label()

        if self.game.is_terminal():
            self.handle_game_terminal()
        else:
            self.check_and_trigger_ai()

    def handle_game_terminal(self):
        winner = self.game.get_winner()
        if winner == "X":
            self.score_x += 1
        elif winner == "O":
            self.score_o += 1
        else:
            self.score_draws += 1
            
        self.update_scoreboard_display()
        self.draw_board()
        self.update_status_label()

    # ----------------- AI Threading & Invocation -----------------
    def check_and_trigger_ai(self):
        if self.game.is_terminal():
            return

        mode = self.mode_var.get()
        curr_player = self.get_current_player()

        if mode == "AI vs AI":
            self.trigger_ai_move()
        elif mode == "Human vs AI":
            play_as_choice = self.play_as_var.get()
            human_symbol = "X" if "X" in play_as_choice else "O"
            if curr_player != human_symbol:
                self.trigger_ai_move()

    def trigger_ai_move(self):
        self.ai_thinking = True
        self.update_status_label()
        self.draw_board()

        # Run minimax selection in background thread to avoid freezing UI
        threading.Thread(target=self.calculate_ai_move_worker, daemon=True).start()

    def calculate_ai_move_worker(self):
        game_choice = self.game_type_var.get()
        difficulty = self.difficulty_var.get().lower()

        # AI Depth Settings based on game type and difficulty
        if game_choice == "Tic-Tac-Toe":
            depths = {"easy": 1, "medium": 3, "hard": 9}
        elif game_choice == "Connect Four":
            depths = {"easy": 2, "medium": 4, "hard": 6}
        else:  # Chess
            depths = {"easy": 1, "medium": 2, "hard": 3}

        depth = depths.get(difficulty, 3)

        curr_player = self.get_current_player()
        opponent = "O" if curr_player == "X" else "X"

        agent = MinimaxAgent(player_symbol=curr_player, opponent_symbol=opponent, max_depth=depth, difficulty=difficulty)
        
        # Clone the game state to ensure thread safety
        cloned_game = self.game.clone()
        move = agent.choose_move(cloned_game)

        # Dispatch back to main thread
        self.root.after(0, self.apply_ai_move_ui, move, curr_player)

    def apply_ai_move_ui(self, move, curr_player):
        # Safety check if game was reset while calculating
        if self.game.is_terminal() or not self.ai_thinking:
            return

        # Double check it is actually that player's turn still
        if self.get_current_player() != curr_player:
            return

        legal = self.game.get_legal_moves()
        if move in legal:
            game_choice = self.game_type_var.get()
            self.game.make_move(move, curr_player)
            if game_choice != "Chess":
                self.current_turn = "O" if self.current_turn == "X" else "X"
            
            self.ai_thinking = False
            self.draw_board()
            self.update_status_label()

            if self.game.is_terminal():
                self.handle_game_terminal()
            else:
                # If AI vs AI, schedule the next move with a short visual delay
                if self.mode_var.get() == "AI vs AI":
                    self.root.after(550, self.check_and_trigger_ai)
                else:
                    self.check_and_trigger_ai()
        else:
            # Fallback if something weird happened
            self.ai_thinking = False
            self.update_status_label()
            self.draw_board()


if __name__ == "__main__":
    root = tk.Tk()
    app = BoardGameApp(root)
    root.mainloop()
