import numpy as np
import pygame
import sys
import math
import random
import time
import argparse
import statistics
import csv

# ── Colors ─────────────────────────────────────────────────────────────────────
BG_COLOR      = (13,  17,  38)
BOARD_COLOR   = (28,  58,  148)
CELL_COLOR    = (13,  17,  38)
P1_COLOR      = (220, 60,  60)
P2_COLOR      = (240, 200, 20)
P1_SHADOW     = (120, 20,  20)
P2_SHADOW     = (140, 110, 0)
WHITE         = (255, 255, 255)
LIGHT_GRAY    = (180, 185, 210)
DARK_GRAY     = (40,  44,  65)

# ── Dimensions ─────────────────────────────────────────────────────────────────
ROW_COUNT     = 6
COLUMN_COUNT  = 7
SQUARESIZE    = 100
RADIUS        = SQUARESIZE // 2 - 8
HEADER_H      = SQUARESIZE
SCORE_H       = 52
WIDTH         = COLUMN_COUNT * SQUARESIZE
HEIGHT        = HEADER_H + ROW_COUNT * SQUARESIZE + SCORE_H

# ── Game constants ──────────────────────────────────────────────────────────────
EMPTY         = 0
PLAYER1       = 1
PLAYER2       = 2
WINDOW_LENGTH = 4
AI_DEPTH      = 5

# ── Modes ───────────────────────────────────────────────────────────────────────
MODE_PVP      = "pvp"
MODE_MINIMAX  = "minimax"
MODE_AB       = "alpha-beta"


# ── Board helpers ───────────────────────────────────────────────────────────────

def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT), dtype=int)

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid(board, col):
    return 0 <= col < COLUMN_COUNT and board[ROW_COUNT - 1][col] == EMPTY

def next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == EMPTY:
            return r

def is_board_full(board):
    return all(board[ROW_COUNT - 1][c] != EMPTY for c in range(COLUMN_COUNT))

def get_valid_locations(board):
    return [c for c in range(COLUMN_COUNT) if is_valid(board, c)]

def winning_move(board, piece):
    for r in range(ROW_COUNT):
        for c in range(COLUMN_COUNT - 3):
            if all(board[r][c + i] == piece for i in range(4)):
                return [(r, c + i) for i in range(4)]
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if all(board[r + i][c] == piece for i in range(4)):
                return [(r + i, c) for i in range(4)]
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return [(r + i, c + i) for i in range(4)]
    for r in range(3, ROW_COUNT):
        for c in range(COLUMN_COUNT - 3):
            if all(board[r - i][c + i] == piece for i in range(4)):
                return [(r - i, c + i) for i in range(4)]
    return None

# ── AI scoring ──────────────────────────────────────────────────────────────────

def evaluate_window(window, piece):
    score   = 0
    opp     = PLAYER1 if piece == PLAYER2 else PLAYER2
    count   = window.count(piece)
    emp     = window.count(EMPTY)
    opp_cnt = window.count(opp)

    if count == 4:
        score += 100
    elif count == 3 and emp == 1:
        score += 5
    elif count == 2 and emp == 2:
        score += 2
    if opp_cnt == 3 and emp == 1:
        score -= 4
    return score

def score_position(board, piece):
    score = 0
    center = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    score += center.count(piece) * 3

    for r in range(ROW_COUNT):
        row_arr = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            score += evaluate_window(row_arr[c:c + WINDOW_LENGTH], piece)

    for c in range(COLUMN_COUNT):
        col_arr = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            score += evaluate_window(col_arr[r:r + WINDOW_LENGTH], piece)

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            score += evaluate_window([board[r + i][c + i] for i in range(WINDOW_LENGTH)], piece)

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            score += evaluate_window([board[r + 3 - i][c + i] for i in range(WINDOW_LENGTH)], piece)

    return score

def is_terminal_node(board):
    return (winning_move(board, PLAYER1) or
            winning_move(board, PLAYER2) or
            len(get_valid_locations(board)) == 0)

def board_from_moves(moves, first_player=PLAYER1):
    board = create_board()
    turn = first_player

    for col in moves:
        if not is_valid(board, col):
            raise ValueError(f"Invalid move sequence: column {col} is not playable")
        row = next_open_row(board, col)
        drop_piece(board, row, col, turn)
        turn = PLAYER1 if turn == PLAYER2 else PLAYER2

    return board, turn

def benchmark_algorithms(depth, repeats, csv_path=None):
    scenarios = [
        ("Opening center", [3]),
        ("Center fight", [3, 3, 2, 4, 2]),
        ("Tactical mid", [3, 2, 3, 2, 4, 1, 4]),
        ("Edge pressure", [0, 1, 0, 1, 6, 5, 6]),
    ]
    csv_rows = []

    print("\n=== Connect Four Search Benchmark ===")
    print(f"depth={depth} repeats={repeats}\n")

    header = (
        f"{'Scenario':<16} {'Algorithm':<10} {'Avg ms':>10} {'Avg nodes':>12} "
        f"{'Avg cutoffs':>12} {'Best col':>8} {'Best score':>10}"
    )
    print(header)
    print("-" * len(header))

    for name, moves in scenarios:
        board, turn = board_from_moves(moves)
        if turn != PLAYER2:
            raise ValueError(f"Scenario '{name}' does not leave the AI to move")
        if is_terminal_node(board):
            raise ValueError(f"Scenario '{name}' is terminal and cannot be benchmarked")

        results = {}
        for algo in (MODE_MINIMAX, MODE_AB):
            times = []
            nodes = []
            cutoffs = []
            chosen_col = None
            chosen_score = None

            for _ in range(repeats):
                stats = {"nodes": 0, "cutoffs": 0}
                started_at = time.perf_counter()

                if algo == MODE_MINIMAX:
                    col, score = minimax(board.copy(), depth, True, stats)
                else:
                    col, score = minimax_ab(board.copy(), depth, -math.inf, math.inf, True, stats)

                elapsed_ms = (time.perf_counter() - started_at) * 1000
                times.append(elapsed_ms)
                nodes.append(stats["nodes"])
                cutoffs.append(stats["cutoffs"])
                chosen_col = col
                chosen_score = score

            results[algo] = {
                "avg_time": statistics.mean(times),
                "avg_nodes": statistics.mean(nodes),
                "avg_cutoffs": statistics.mean(cutoffs),
                "col": chosen_col,
                "score": chosen_score,
            }

        for algo in (MODE_MINIMAX, MODE_AB):
            row = results[algo]
            print(
                f"{name:<16} {algo:<10} {row['avg_time']:>10.2f} {row['avg_nodes']:>12.0f} "
                f"{row['avg_cutoffs']:>12.0f} {str(row['col']):>8} {row['score']:>10}"
            )
            csv_rows.append({
                "scenario": name,
                "algorithm": algo,
                "depth": depth,
                "repeats": repeats,
                "avg_ms": f"{row['avg_time']:.4f}",
                "avg_nodes": f"{row['avg_nodes']:.0f}",
                "avg_cutoffs": f"{row['avg_cutoffs']:.0f}",
                "best_col": row["col"],
                "best_score": row["score"],
                "speedup_vs_minimax": "",
                "node_reduction_pct_vs_minimax": "",
            })

        mm = results[MODE_MINIMAX]
        ab = results[MODE_AB]
        speedup = mm["avg_time"] / ab["avg_time"] if ab["avg_time"] > 0 else float("inf")
        node_reduction = (1 - (ab["avg_nodes"] / mm["avg_nodes"])) * 100 if mm["avg_nodes"] > 0 else 0
        print(f"{'':<16} {'speedup':<10} {speedup:>10.2f}x {'node reduction':>12} {node_reduction:>8.2f}%")
        csv_rows.append({
            "scenario": name,
            "algorithm": "summary",
            "depth": depth,
            "repeats": repeats,
            "avg_ms": "",
            "avg_nodes": "",
            "avg_cutoffs": "",
            "best_col": "",
            "best_score": "",
            "speedup_vs_minimax": f"{speedup:.4f}",
            "node_reduction_pct_vs_minimax": f"{node_reduction:.4f}",
        })
        print()

    if csv_path:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "scenario",
                    "algorithm",
                    "depth",
                    "repeats",
                    "avg_ms",
                    "avg_nodes",
                    "avg_cutoffs",
                    "best_col",
                    "best_score",
                    "speedup_vs_minimax",
                    "node_reduction_pct_vs_minimax",
                ],
            )
            writer.writeheader()
            writer.writerows(csv_rows)
        print(f"CSV written to: {csv_path}")

# ── Minimax (no pruning) ────────────────────────────────────────────────────────

def minimax(board, depth, maximizing, stats=None):
    if stats is not None:
        stats["nodes"] += 1

    valid    = get_valid_locations(board)
    terminal = is_terminal_node(board)

    if depth == 0 or terminal:
        if terminal:
            if winning_move(board, PLAYER2):
                return (None,  100_000_000_000_000)
            elif winning_move(board, PLAYER1):
                return (None, -100_000_000_000_000)
            else:
                return (None, 0)
        return (None, score_position(board, PLAYER2))

    if maximizing:
        value  = -math.inf
        column = random.choice(valid)
        for col in valid:
            row    = next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER2)
            new_score = minimax(b_copy, depth - 1, False, stats)[1]
            if new_score > value:
                value  = new_score
                column = col
        return column, value
    else:
        value  = math.inf
        column = random.choice(valid)
        for col in valid:
            row    = next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER1)
            new_score = minimax(b_copy, depth - 1, True, stats)[1]
            if new_score < value:
                value  = new_score
                column = col
        return column, value

# ── Minimax with alpha-beta pruning ─────────────────────────────────────────────

def minimax_ab(board, depth, alpha, beta, maximizing, stats=None):
    if stats is not None:
        stats["nodes"] += 1

    valid    = get_valid_locations(board)
    terminal = is_terminal_node(board)

    if depth == 0 or terminal:
        if terminal:
            if winning_move(board, PLAYER2):
                return (None,  100_000_000_000_000)
            elif winning_move(board, PLAYER1):
                return (None, -100_000_000_000_000)
            else:
                return (None, 0)
        return (None, score_position(board, PLAYER2))

    if maximizing:
        value  = -math.inf
        column = random.choice(valid)
        for col in valid:
            row    = next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER2)
            new_score = minimax_ab(b_copy, depth - 1, alpha, beta, False, stats)[1]
            if new_score > value:
                value  = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                if stats is not None:
                    stats["cutoffs"] += 1
                break
        return column, value
    else:
        value  = math.inf
        column = random.choice(valid)
        for col in valid:
            row    = next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER1)
            new_score = minimax_ab(b_copy, depth - 1, alpha, beta, True, stats)[1]
            if new_score < value:
                value  = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                if stats is not None:
                    stats["cutoffs"] += 1
                break
        return column, value

# ── Color helpers ───────────────────────────────────────────────────────────────

def lighten(color, amount):
    return tuple(min(255, c + amount) for c in color)

def darken(color, amount):
    return tuple(max(0, c - amount) for c in color)

# ── Drawing ─────────────────────────────────────────────────────────────────────

def board_cell_center(r, c):
    x = c * SQUARESIZE + SQUARESIZE // 2
    y = SCORE_H + HEADER_H + (ROW_COUNT - 1 - r) * SQUARESIZE + SQUARESIZE // 2
    return (x, y)

def draw_piece(surface, cx, cy, piece_color, shadow_color):
    pygame.draw.circle(surface, shadow_color, (cx + 3, cy + 4), RADIUS)
    pygame.draw.circle(surface, piece_color,  (cx, cy), RADIUS)
    pygame.draw.circle(surface, lighten(piece_color, 80),
                       (cx - RADIUS // 3, cy - RADIUS // 3), RADIUS // 4)

def draw_score_bar(surface, scores, turn, mode, font_sm):
    pygame.draw.rect(surface, DARK_GRAY, (0, 0, WIDTH, SCORE_H))

    p1_lbl = font_sm.render("Player 1", True, P1_COLOR)
    p1_sc  = font_sm.render(str(scores[PLAYER1]), True, WHITE)
    surface.blit(p1_lbl, (16, 6))
    surface.blit(p1_sc,  (16, 28))

    p2_name = "Player 2" if mode == MODE_PVP else "AI"
    p2_lbl  = font_sm.render(p2_name, True, P2_COLOR)
    p2_sc   = font_sm.render(str(scores[PLAYER2]), True, WHITE)
    surface.blit(p2_lbl, (WIDTH - p2_lbl.get_width() - 16, 6))
    surface.blit(p2_sc,  (WIDTH - p2_sc.get_width()  - 16, 28))

    if turn in (PLAYER1, PLAYER2):
        if turn == PLAYER1:
            color, name = P1_COLOR, "Player 1's Turn"
        elif mode == MODE_PVP:
            color, name = P2_COLOR, "Player 2's Turn"
        else:
            color, name = P2_COLOR, "AI Thinking..."
        t_surf = font_sm.render(name, True, color)
        surface.blit(t_surf, (WIDTH // 2 - t_surf.get_width() // 2, 16))

def draw_board(surface, board, win_cells=None):
    pygame.draw.rect(surface, BOARD_COLOR,
                     (0, SCORE_H + HEADER_H, WIDTH, ROW_COUNT * SQUARESIZE),
                     border_radius=12)

    for r in range(ROW_COUNT):
        for c in range(COLUMN_COUNT):
            cx, cy = board_cell_center(r, c)
            piece  = board[r][c]
            pygame.draw.circle(surface, (8, 10, 22), (cx, cy), RADIUS + 4)
            if piece == EMPTY:
                pygame.draw.circle(surface, CELL_COLOR, (cx, cy), RADIUS)
            elif piece == PLAYER1:
                draw_piece(surface, cx, cy, P1_COLOR, P1_SHADOW)
            else:
                draw_piece(surface, cx, cy, P2_COLOR, P2_SHADOW)

    if win_cells:
        for (r, c) in win_cells:
            cx, cy = board_cell_center(r, c)
            pygame.draw.circle(surface, WHITE, (cx, cy), RADIUS + 5, 4)

def draw_hover(surface, col, turn):
    pygame.draw.rect(surface, BG_COLOR, (0, SCORE_H, WIDTH, HEADER_H))
    if col is not None and 0 <= col < COLUMN_COUNT:
        color  = P1_COLOR  if turn == PLAYER1 else P2_COLOR
        shadow = P1_SHADOW if turn == PLAYER1 else P2_SHADOW
        cx = col * SQUARESIZE + SQUARESIZE // 2
        cy = SCORE_H + HEADER_H // 2
        draw_piece(surface, cx, cy, color, shadow)

def draw_victory(surface, winner, mode, font_big, font_sm):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))
    surface.blit(overlay, (0, 0))

    if winner == PLAYER1:
        color, text = P1_COLOR, "Player 1 Wins!"
    elif winner == PLAYER2:
        color = P2_COLOR
        text  = "AI Wins!" if mode != MODE_PVP else "Player 2 Wins!"
    else:
        color, text = LIGHT_GRAY, "It's a Draw!"

    for offset in range(5, 0, -1):
        glow = font_big.render(text, True, darken(color, 160 - offset * 25))
        surface.blit(glow, (WIDTH // 2 - glow.get_width() // 2 + offset,
                            HEIGHT // 2 - glow.get_height() // 2 + offset))

    label = font_big.render(text, True, color)
    surface.blit(label, (WIDTH // 2 - label.get_width() // 2,
                         HEIGHT // 2 - label.get_height() // 2))

    sub = font_sm.render("R  to play again     ESC  to quit", True, LIGHT_GRAY)
    surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2,
                       HEIGHT // 2 + label.get_height() // 2 + 20))

def draw_menu(surface, font_big, font_sm):
    surface.fill(BG_COLOR)

    title = font_big.render("Connect Four", True, WHITE)
    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

    btn_w, btn_h = 360, 60
    btn_x = WIDTH // 2 - btn_w // 2

    pvp_rect = pygame.Rect(btn_x, 250, btn_w, btn_h)
    mm_rect  = pygame.Rect(btn_x, 330, btn_w, btn_h)
    ab_rect  = pygame.Rect(btn_x, 410, btn_w, btn_h)

    for rect, label in [
        (pvp_rect, "2 Players"),
        (mm_rect,  "AI —  Minimax"),
        (ab_rect,  "AI - Minimax + Alpha-Beta"),
    ]:
        pygame.draw.rect(surface, BOARD_COLOR, rect, border_radius=10)
        lbl = font_sm.render(label, True, WHITE)
        surface.blit(lbl, (rect.centerx - lbl.get_width() // 2,
                           rect.centery - lbl.get_height() // 2))

    hint = font_sm.render("Choose a mode to start", True, LIGHT_GRAY)
    surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 500))

    pygame.display.flip()
    return pvp_rect, mm_rect, ab_rect


# ── Main ────────────────────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen   = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Connect Four")

    font_big = pygame.font.SysFont("monospace", 60, bold=True)
    font_sm  = pygame.font.SysFont("monospace", 21)
    clock    = pygame.time.Clock()

    # ── Mode selection ──────────────────────────────────────────────────────────
    mode = None
    pvp_rect, mm_rect, ab_rect = draw_menu(screen, font_big, font_sm)

    while mode is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pvp_rect.collidepoint(event.pos):
                    mode = MODE_PVP
                elif mm_rect.collidepoint(event.pos):
                    mode = MODE_MINIMAX
                elif ab_rect.collidepoint(event.pos):
                    mode = MODE_AB

    scores = {PLAYER1: 0, PLAYER2: 0}

    def reset():
        return create_board(), False, PLAYER1, None, None

    board, game_over, turn, hover_col, win_cells = reset()

    while True:
        clock.tick(60)

        # ── AI move ─────────────────────────────────────────────────────────────
        if mode != MODE_PVP and turn == PLAYER2 and not game_over:
            metrics = {"nodes": 0, "cutoffs": 0}
            started_at = time.perf_counter()

            if mode == MODE_MINIMAX:
                col, score = minimax(board, AI_DEPTH, True, metrics)
            else:
                col, score = minimax_ab(board, AI_DEPTH, -math.inf, math.inf, True, metrics)

            elapsed_ms = (time.perf_counter() - started_at) * 1000
            print(
                f"[AI:{mode}] depth={AI_DEPTH} col={col} score={score} "
                f"nodes={metrics['nodes']} cutoffs={metrics['cutoffs']} "
                f"time_ms={elapsed_ms:.2f}"
            )

            if col is not None and is_valid(board, col):
                row = next_open_row(board, col)
                drop_piece(board, row, col, PLAYER2)
                result = winning_move(board, PLAYER2)
                if result:
                    win_cells = result
                    scores[PLAYER2] += 1
                    game_over = True
                elif is_board_full(board):
                    game_over = True
                    turn = 0
                else:
                    turn = PLAYER1

        # ── Events ──────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if event.key == pygame.K_r:
                    board, game_over, turn, hover_col, win_cells = reset()

            if not game_over:
                if event.type == pygame.MOUSEMOTION:
                    hover_col = int(event.pos[0] // SQUARESIZE)

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if turn == PLAYER1 or (mode == MODE_PVP and turn == PLAYER2):
                        col = int(event.pos[0] // SQUARESIZE)
                        if is_valid(board, col):
                            row = next_open_row(board, col)
                            drop_piece(board, row, col, turn)
                            result = winning_move(board, turn)
                            if result:
                                win_cells = result
                                scores[turn] += 1
                                game_over = True
                            elif is_board_full(board):
                                game_over = True
                                turn = 0
                            else:
                                turn = PLAYER2 if turn == PLAYER1 else PLAYER1

        # ── Render ──────────────────────────────────────────────────────────────
        screen.fill(BG_COLOR)
        draw_score_bar(screen, scores, turn, mode, font_sm)

        human_turn = turn == PLAYER1 or (mode == MODE_PVP and turn == PLAYER2)
        if not game_over and human_turn:
            draw_hover(screen, hover_col, turn)
        else:
            pygame.draw.rect(screen, BG_COLOR, (0, SCORE_H, WIDTH, HEADER_H))

        draw_board(screen, board, win_cells)

        if game_over:
            winner = board[win_cells[0][0]][win_cells[0][1]] if win_cells else None
            draw_victory(screen, winner, mode, font_big, font_sm)

        pygame.display.flip()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Connect Four")
    parser.add_argument("--benchmark", action="store_true",
                        help="Run minimax vs alpha-beta benchmark and exit")
    parser.add_argument("--depth", type=int, default=AI_DEPTH,
                        help="Search depth for game and benchmark")
    parser.add_argument("--repeats", type=int, default=5,
                        help="Benchmark repetitions per scenario and algorithm")
    parser.add_argument("--csv", type=str, default="fixed_scenarios_benchmark.csv",
                        help="Output path for benchmark CSV")
    args = parser.parse_args()

    AI_DEPTH = args.depth

    if args.benchmark:
        benchmark_algorithms(depth=args.depth, repeats=args.repeats, csv_path=args.csv)
    else:
        main()