import numpy as np
import pygame
import sys
import math

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

PLAYER1       = 1
PLAYER2       = 2


# ── Board helpers ───────────────────────────────────────────────────────────────

def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT), dtype=int)

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid(board, col):
    return 0 <= col < COLUMN_COUNT and board[ROW_COUNT - 1][col] == 0

def next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def is_board_full(board):
    return all(board[ROW_COUNT - 1][c] != 0 for c in range(COLUMN_COUNT))

def winning_move(board, piece):
    # Horizontal
    for r in range(ROW_COUNT):
        for c in range(COLUMN_COUNT - 3):
            if all(board[r][c + i] == piece for i in range(4)):
                return [(r, c + i) for i in range(4)]
    # Vertical
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if all(board[r + i][c] == piece for i in range(4)):
                return [(r + i, c) for i in range(4)]
    # Positive diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return [(r + i, c + i) for i in range(4)]
    # Negative diagonal
    for r in range(3, ROW_COUNT):
        for c in range(COLUMN_COUNT - 3):
            if all(board[r - i][c + i] == piece for i in range(4)):
                return [(r - i, c + i) for i in range(4)]
    return None


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
    pygame.draw.circle(surface, piece_color, (cx, cy), RADIUS)
    pygame.draw.circle(surface, lighten(piece_color, 80),
                       (cx - RADIUS // 3, cy - RADIUS // 3), RADIUS // 4)

def draw_score_bar(surface, scores, turn, font_sm):
    pygame.draw.rect(surface, DARK_GRAY, (0, 0, WIDTH, SCORE_H))

    p1_lbl = font_sm.render("Player 1", True, P1_COLOR)
    p1_sc  = font_sm.render(str(scores[PLAYER1]), True, WHITE)
    surface.blit(p1_lbl, (16, 6))
    surface.blit(p1_sc,  (16, 28))

    p2_lbl = font_sm.render("Player 2", True, P2_COLOR)
    p2_sc  = font_sm.render(str(scores[PLAYER2]), True, WHITE)
    surface.blit(p2_lbl, (WIDTH - p2_lbl.get_width() - 16, 6))
    surface.blit(p2_sc,  (WIDTH - p2_sc.get_width()  - 16, 28))

    if turn in (PLAYER1, PLAYER2):
        color = P1_COLOR if turn == PLAYER1 else P2_COLOR
        name  = "Player 1's Turn" if turn == PLAYER1 else "Player 2's Turn"
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

            if piece == 0:
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

def draw_victory(surface, winner, font_big, font_sm):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))
    surface.blit(overlay, (0, 0))

    if winner == PLAYER1:
        color, text = P1_COLOR, "Player 1 Wins!"
    elif winner == PLAYER2:
        color, text = P2_COLOR, "Player 2 Wins!"
    else:
        color, text = LIGHT_GRAY, "It's a Draw!"

    # Glow layers
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


# ── Main ────────────────────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Connect Four")

    font_big = pygame.font.SysFont("monospace", 60, bold=True)
    font_sm  = pygame.font.SysFont("monospace", 21)

    scores   = {PLAYER1: 0, PLAYER2: 0}
    clock    = pygame.time.Clock()

    def reset():
        return create_board(), False, PLAYER1, None, None

    board, game_over, turn, hover_col, win_cells = reset()

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    board, game_over, turn, hover_col, win_cells = reset()

            if not game_over:
                if event.type == pygame.MOUSEMOTION:
                    hover_col = int(event.pos[0] // SQUARESIZE)

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
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
                            turn = 0   # draw sentinel
                        else:
                            turn = PLAYER2 if turn == PLAYER1 else PLAYER1

        # ── Render ──────────────────────────────────────────────────────────────
        screen.fill(BG_COLOR)
        draw_score_bar(screen, scores, turn, font_sm)

        if not game_over:
            draw_hover(screen, hover_col, turn)
        else:
            pygame.draw.rect(screen, BG_COLOR, (0, SCORE_H, WIDTH, HEADER_H))

        draw_board(screen, board, win_cells)

        if game_over:
            if win_cells:
                winner = board[win_cells[0][0]][win_cells[0][1]]
            else:
                winner = None
            draw_victory(screen, winner, font_big, font_sm)

        pygame.display.flip()


if __name__ == "__main__":
    main()