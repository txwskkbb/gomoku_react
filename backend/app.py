from flask import Flask, request, jsonify
from flask_cors import CORS
import math

# --- Game Constants ---
BOARD_SIZE = 15  # 15x15 is more standard for Gomoku and performs better
WIN_COUNT = 5
EMPTY = 0
PLAYER = 1
AI = 2
MAX_DEPTH = 3 # Keep depth low (1 or 2) for reasonable performance

# --- Flask App Setup ---
app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# --- Game State ---
# In a real multi-user app, you'd use sessions or a database.
# For this example, a global variable is fine.
board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

# --- Game Logic (Ported from your JS) ---

def check_win(r, c, player):
    if r < 0 or r >= BOARD_SIZE or c < 0 or c >= BOARD_SIZE:
        return False
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    for dr, dc in directions:
        count = 1
        # Check in one direction
        for i in range(1, WIN_COUNT):
            rr, cc = r + dr * i, c + dc * i
            if 0 <= rr < BOARD_SIZE and 0 <= cc < BOARD_SIZE and board[rr][cc] == player:
                count += 1
            else:
                break
        # Check in the opposite direction
        for i in range(1, WIN_COUNT):
            rr, cc = r - dr * i, c - dc * i
            if 0 <= rr < BOARD_SIZE and 0 <= cc < BOARD_SIZE and board[rr][cc] == player:
                count += 1
            else:
                break
        if count >= WIN_COUNT:
            return True
    return False

def evaluate_board(player_to_eval):
    # Simplified evaluation for performance. A full pattern-based one is great but slow.
    # This checks for potential wins.
    score = 0
    # Check all lines for patterns
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == EMPTY:
                continue
            
            # Simple score: player's pieces are good, opponent's are bad
            current_player = board[r][c]
            multiplier = 1 if current_player == player_to_eval else -1
            
            # Check potential lines from this piece
            if check_win(r, c, current_player):
                score += 10000 * multiplier
                
    return score

def generate_candidates():
    candidates = set()
    # If board is empty, suggest the center
    is_empty = all(cell == EMPTY for row in board for cell in row)
    if is_empty:
        return [[BOARD_SIZE // 2, BOARD_SIZE // 2]]

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] != EMPTY:
                for dr in range(-1, 2):
                    for dc in range(-1, 2):
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] == EMPTY:
                            candidates.add((nr, nc))
    return [list(c) for c in candidates]

def minimax(depth, is_max, alpha, beta):
    # Check for terminal state (win/loss) or max depth
    player_win = any(check_win(r, c, PLAYER) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if board[r][c] == PLAYER)
    ai_win = any(check_win(r, c, AI) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if board[r][c] == AI)

    if player_win: return -10000
    if ai_win: return 10000
    if depth == 0: return 0 # Simplified evaluation for speed

    candidates = generate_candidates()
    if not candidates: return 0 # Draw

    if is_max:
        best = -math.inf
        for r, c in candidates:
            board[r][c] = AI
            val = minimax(depth - 1, False, alpha, beta)
            board[r][c] = EMPTY
            best = max(best, val)
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best
    else: # is_min
        best = math.inf
        for r, c in candidates:
            board[r][c] = PLAYER
            val = minimax(depth - 1, True, alpha, beta)
            board[r][c] = EMPTY
            best = min(best, val)
            beta = min(beta, best)
            if beta <= alpha:
                break
        return best

def ai_move():
    best_score = -math.inf
    move = None
    candidates = generate_candidates()
    
    if not candidates: return None

    # Pre-check: If AI can win in one move, take it.
    for r, c in candidates:
        board[r][c] = AI
        if check_win(r, c, AI):
            return [r, c]
        board[r][c] = EMPTY

    # Pre-check: If Player can win in one move, block it.
    for r, c in candidates:
        board[r][c] = PLAYER
        if check_win(r, c, PLAYER):
            move = [r, c]
            board[r][c] = EMPTY
            break
        board[r][c] = EMPTY
    
    if move is None:
        for r, c in candidates:
            board[r][c] = AI
            score = minimax(MAX_DEPTH, False, -math.inf, math.inf)
            board[r][c] = EMPTY
            if score > best_score:
                best_score = score
                move = [r, c]

    return move

# --- API Endpoints ---
@app.route('/api/move', methods=['POST'])
def handle_move():
    global board
    data = request.json
    row, col = data['row'], data['col']
    
    # Player's move
    if board[row][col] == EMPTY:
        board[row][col] = PLAYER
        if check_win(row, col, PLAYER):
            return jsonify({'board': board, 'gameOver': True, 'message': '你赢了！'})
    else:
        return jsonify({'error': 'Invalid move'}), 400

    # AI's move
    ai_pos = ai_move()
    if ai_pos:
        r, c = ai_pos
        board[r][c] = AI
        if check_win(r, c, AI):
            return jsonify({'board': board, 'gameOver': True, 'message': 'AI 赢了！'})
    
    # Check for draw
    if not generate_candidates():
        return jsonify({'board': board, 'gameOver': True, 'message': '平局！'})

    return jsonify({'board': board, 'gameOver': False, 'message': '轮到你了'})

@app.route('/api/restart', methods=['POST'])
def restart_game():
    global board
    board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    return jsonify({'board': board, 'gameOver': False, 'message': '游戏开始，请落子'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
