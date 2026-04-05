import numpy as np
import time
import math
import random
import csv

# ── Constants ─────────────────────────────────────────────────────────────────────
ROW_COUNT = 6
COLUMN_COUNT = 7
EMPTY = 0
PLAYER1 = 1
PLAYER2 = 2
WINDOW_LENGTH = 4

# ── Board Engine ─────────────────────────────────────────────────────────────────────
def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT), dtype=int)

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid(board, col):
    if col >= 0 and col < COLUMN_COUNT:
        if board[ROW_COUNT - 1][col] == EMPTY:
            return True
    return False

def next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == EMPTY:
            return r

def get_valid_locations(board):
    valid_locations = []
    for c in range(COLUMN_COUNT):
        if is_valid(board, c):
            valid_locations.append(c)
    return valid_locations

# Check if the last move was a winning move for the given piece.
def winning_move(board, piece):
    # Check horizontal locations
    for r in range(ROW_COUNT):
        for c in range(COLUMN_COUNT - 3):
            if board[r][c] == piece and board[r][c + 1] == piece and board[r][c + 2] == piece and board[r][c + 3] == piece:
                return True
                
    # Check vertical locations
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if board[r + 0][c] == piece and board[r + 1][c] == piece and board[r + 2][c] == piece and board[r + 3][c] == piece:
                return True
                
    # Check positively sloped diagonals
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            if board[r + 0][c + 0] == piece and board[r + 1][c + 1] == piece and board[r + 2][c + 2] == piece and board[r + 3][c + 3] == piece:
                return True
                
    # Check negatively sloped diagonals
    for r in range(3, ROW_COUNT):
        for c in range(COLUMN_COUNT - 3):
            if board[r - 0][c + 0] == piece and board[r - 1][c + 1] == piece and board[r - 2][c + 2] == piece and board[r - 3][c + 3] == piece:
                return True
                
    return False

# Is the game over? Either player has won or there are no valid moves left.
def is_terminal_node(board):
    if winning_move(board, PLAYER1):
        return True
    if winning_move(board, PLAYER2):
        return True
    if len(get_valid_locations(board)) == 0:
        return True
    return False

# ── Heuristics ─────────────────────────────────────────────────────────────────────
# Assign points based on every 4-slot segment. AI is forced to block if the opponent has a 3-in-a-row, causing a subtraction of 4 points
def evaluate_window(window, piece):
    score = 0
    
    if piece == PLAYER2:
        opp = PLAYER1
    else:
        opp = PLAYER2
        
    count = window.count(piece)
    emp = window.count(EMPTY)
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

# Score the board based on how favorable it is for the given piece. Center column is weighted more heavily since it's more advantageous.
def score_position(board, piece):
    score = 0
    
    # Score center column
    center_array = []
    for i in list(board[:, COLUMN_COUNT // 2]):
        center_array.append(int(i))
    center_count = center_array.count(piece)
    score += center_count * 3
    
    # Score Horizontal
    for r in range(ROW_COUNT):
        row_arr = []
        for i in list(board[r, :]):
            row_arr.append(int(i))
        for c in range(COLUMN_COUNT - 3):
            window = row_arr[c:c + WINDOW_LENGTH]
            score += evaluate_window(window, piece)
            
    # Score Vertical
    for c in range(COLUMN_COUNT):
        col_arr = []
        for i in list(board[:, c]):
            col_arr.append(int(i))
        for r in range(ROW_COUNT - 3):
            window = col_arr[r:r + WINDOW_LENGTH]
            score += evaluate_window(window, piece)
            
    # Score positive sloped diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = []
            for i in range(WINDOW_LENGTH):
                window.append(board[r + i][c + i])
            score += evaluate_window(window, piece)
            
    # Score negative sloped diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = []
            for i in range(WINDOW_LENGTH):
                window.append(board[r + 3 - i][c + i])
            score += evaluate_window(window, piece)
            
    return score

# ── Algorithm to track nodes ─────────────────────────────────────────────────────────────────────
def minimax(board, depth, maximizing):
    valid = get_valid_locations(board)
    terminal = is_terminal_node(board)
    nodes = 1

    if depth == 0 or terminal:
        if terminal:
            if winning_move(board, PLAYER2): 
                return (None, 10000000, nodes)
            elif winning_move(board, PLAYER1): 
                return (None, -10000000, nodes)
            else: 
                return (None, 0, nodes)
        else:
            current_score = score_position(board, PLAYER2)
            return (None, current_score, nodes)

    if maximizing:
        value = -math.inf
        column = random.choice(valid)
        for col in valid:
            b_copy = board.copy()
            row = next_open_row(board, col)
            drop_piece(b_copy, row, col, PLAYER2)
            
            result = minimax(b_copy, depth - 1, False)
            new_score = result[1]
            new_nodes = result[2]
            
            nodes += new_nodes
            if new_score > value:
                value = new_score
                column = col
                
        return column, value, nodes
    else:
        value = math.inf
        column = random.choice(valid)
        for col in valid:
            b_copy = board.copy()
            row = next_open_row(board, col)
            drop_piece(b_copy, row, col, PLAYER1)
            
            result = minimax(b_copy, depth - 1, True)
            new_score = result[1]
            new_nodes = result[2]
            
            nodes += new_nodes
            if new_score < value:
                value = new_score
                column = col
                
        return column, value, nodes

#Includes alpha and beta parameters to track the best scores for both players and prune branches that won't influence the final decision, thus reducing the number of nodes evaluated.
#Pruning line is when alpha >= beta; if there is a better move elsewhere, stop looking at this branch since the opponent will never allow it to happen.
def minimax_ab(board, depth, alpha, beta, maximizing):
    valid = get_valid_locations(board)
    terminal = is_terminal_node(board)
    nodes = 1

    if depth == 0 or terminal:
        if terminal:
            if winning_move(board, PLAYER2):
                return (None, 10000000, nodes)
            elif winning_move(board, PLAYER1):
                return (None, -10000000, nodes)
            else:
                return (None, 0, nodes)
        else:
            current_score = score_position(board, PLAYER2)
            return (None, current_score, nodes)

    if maximizing:
        value = -math.inf
        column = random.choice(valid)
        for col in valid:
            b_copy = board.copy()
            row = next_open_row(board, col)
            drop_piece(b_copy, row, col, PLAYER2)
            
            result = minimax_ab(b_copy, depth - 1, alpha, beta, False)
            new_score = result[1]
            new_nodes = result[2]
            
            nodes += new_nodes
            if new_score > value:
                value = new_score
                column = col
                
            alpha = max(alpha, value)
            if alpha >= beta:
                break
                
        return column, value, nodes
    else:
        value = math.inf
        column = random.choice(valid)
        for col in valid:
            b_copy = board.copy()
            row = next_open_row(board, col)
            drop_piece(b_copy, row, col, PLAYER1)
            
            result = minimax_ab(b_copy, depth - 1, alpha, beta, True)
            new_score = result[1]
            new_nodes = result[2]
            
            nodes += new_nodes
            if new_score < value:
                value = new_score
                column = col
                
            beta = min(beta, value)
            if alpha >= beta:
                break
                
        return column, value, nodes

# ── Benchmarking Suite ─────────────────────────────────────────────────────────────────────
def make_board():
    """Generate a random mid-game board state (approx 10 moves played) to simulate real decisions."""
    board = create_board()
    for current_move in range(10):
        valid_locations = get_valid_locations(board)
        col = random.choice(valid_locations)
        
        if current_move % 2 == 0:
            piece = PLAYER1
        else:
            piece = PLAYER2
            
        row = next_open_row(board, col)
        drop_piece(board, row, col, piece)
        
    return board

def test():
    depths_to_test = [2, 3, 4, 5, 6]
    trials_per_depth = 5 # Number of different board states to test per depth
    
    results = []

    for depth in depths_to_test:
        print(f"\nEvaluating Depth {depth}...")
        for trial in range(trials_per_depth):
            board = make_board()
            
            # Test Minimax 
            start = time.perf_counter()
            mm_result = minimax(board, depth, True)
            mm_col = mm_result[0]
            mm_score = mm_result[1]
            mm_nodes = mm_result[2]
            mm_time = (time.perf_counter() - start) * 1000
            
            # Test Alpha-Beta
            start = time.perf_counter()
            ab_result = minimax_ab(board, depth, -math.inf, math.inf, True)
            ab_col = ab_result[0]
            ab_score = ab_result[1]
            ab_nodes = ab_result[2]
            ab_time = (time.perf_counter() - start) * 1000
            
            # Calculate efficiency
            if mm_nodes > 0:
                pruning_efficiency = ((mm_nodes - ab_nodes) / mm_nodes) * 100
            else:
                pruning_efficiency = 0

            # Check if same move chosen
            if mm_col == ab_col:
                same_move = True
            else:
                same_move = False

            results.append({
                "Depth": depth,
                "Trial": trial + 1,
                "MM_Time_ms": round(mm_time, 4),
                "MM_Nodes": mm_nodes,
                "AB_Time_ms": round(ab_time, 4),
                "AB_Nodes": ab_nodes,
                "Nodes_Reduced_%": round(pruning_efficiency, 2),
                "Same_Move_Chosen": same_move
            })

    # Output to CSV
    csv_filename = "depth_scaling_benchmark.csv"
    keys = results[0].keys()
    with open(csv_filename, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames = keys)
        dict_writer.writeheader()
        dict_writer.writerows(results)

if __name__ == "__main__":
    test()