import pygame
import sys
import random

# Game constants
WIDTH, HEIGHT = 300, 350  # Extra space for leaderboard
LINE_WIDTH = 5
BOARD_ROWS = 3
BOARD_COLS = 3
SQUARE_SIZE = WIDTH // BOARD_COLS

# Colors
BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
X_COLOR = (66, 66, 66)
O_COLOR = (239, 231, 200)
LEADER_COLOR = (0, 0, 0)
WIN_COLOR = (200, 0, 0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Random vs Minimax AI (Leaderboard)")
FONT = pygame.font.SysFont("Arial", 24)

def draw_leaderboard(ai_wins, rando_wins, draws):
    text = f"AI: {ai_wins}   Rand: {rando_wins}   Draw: {draws}"
    label = FONT.render(text, True, LEADER_COLOR)
    pygame.draw.rect(screen, (230,230,230), (0, 0, WIDTH, 50)) 
    screen.blit(label, (10, 10))

def draw_lines():
    y_offset = 50
    for i in range(1, BOARD_ROWS):
        pygame.draw.line(screen, LINE_COLOR, (0, y_offset+SQUARE_SIZE*i), (WIDTH, y_offset+SQUARE_SIZE*i), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (SQUARE_SIZE*i, y_offset), (SQUARE_SIZE*i, y_offset+WIDTH), LINE_WIDTH)

def draw_figures(board):
    y_offset = 50
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            x = col*SQUARE_SIZE
            y = row*SQUARE_SIZE+y_offset
            if board[row][col] == 1:
                # Draw X
                pygame.draw.line(screen, X_COLOR, (x+20, y+20),
                                 (x+SQUARE_SIZE-20, y+SQUARE_SIZE-20), LINE_WIDTH)
                pygame.draw.line(screen, X_COLOR, (x+20, y+SQUARE_SIZE-20),
                                 (x+SQUARE_SIZE-20, y+20), LINE_WIDTH)
            elif board[row][col] == 2:
                # Draw O
                pygame.draw.circle(screen, O_COLOR,
                                   (x+SQUARE_SIZE//2, y+SQUARE_SIZE//2),
                                   SQUARE_SIZE//2-20, LINE_WIDTH)

def is_winner(board, player):
    # Returns (True, [(row,col), ...]) if player wins, else (False, [])
    for i in range(3):
        # Rows
        if all([board[i][j]==player for j in range(3)]):
            return True, [(i,0),(i,1),(i,2)]
        # Columns
        if all([board[j][i]==player for j in range(3)]):
            return True, [(0,i),(1,i),(2,i)]
    # Diagonals
    if all([board[i][i]==player for i in range(3)]):
        return True, [(0,0),(1,1),(2,2)]
    if all([board[i][2-i]==player for i in range(3)]):
        return True, [(0,2),(1,1),(2,0)]
    return False, []

def is_board_full(board):
    return all([board[row][col] != 0 for row in range(3) for col in range(3)])

def minimax(b, depth, is_maximizing):
    ai_win, _ = is_winner(b, 2)
    rando_win, _ = is_winner(b, 1)
    if ai_win:
        return 1
    if rando_win:
        return -1
    if is_board_full(b):
        return 0

    if is_maximizing:
        best_score = -float('inf')
        for row in range(3):
            for col in range(3):
                if b[row][col] == 0:
                    b[row][col] = 2
                    score = minimax(b, depth+1, False)
                    b[row][col] = 0
                    best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for row in range(3):
            for col in range(3):
                if b[row][col] == 0:
                    b[row][col] = 1
                    score = minimax(b, depth+1, True)
                    b[row][col] = 0
                    best_score = min(score, best_score)
        return best_score

def ai_move(board):
    best_score = -float('inf')
    move = None
    for row in range(3):
        for col in range(3):
            if board[row][col] == 0:
                board[row][col] = 2
                score = minimax(board, 0, False)
                board[row][col] = 0
                if score > best_score:
                    best_score = score
                    move = (row, col)
    if move:
        board[move[0]][move[1]] = 2

def random_move(board):
    empty = [(r,c) for r in range(3) for c in range(3) if board[r][c]==0]
    if empty:
        move = random.choice(empty)
        board[move[0]][move[1]] = 1

def reset_board():
    return [[0 for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]

def draw_win_line(winning_cells):
    y_offset = 50
    x0 = winning_cells[0][1]*SQUARE_SIZE + SQUARE_SIZE//2
    y0 = winning_cells[0][0]*SQUARE_SIZE + SQUARE_SIZE//2 + y_offset
    x1 = winning_cells[2][1]*SQUARE_SIZE + SQUARE_SIZE//2
    y1 = winning_cells[2][0]*SQUARE_SIZE + SQUARE_SIZE//2 + y_offset
    pygame.draw.line(screen, WIN_COLOR, (x0, y0), (x1, y1), LINE_WIDTH*2)

# Leaderboard counts
ai_wins = 0
rando_wins = 0
draws = 0

# Main loop
running = True
player_turn = True  # Rando starts for fairness!

board = reset_board()

screen.fill(BG_COLOR)
draw_leaderboard(ai_wins, rando_wins, draws)
draw_lines()
draw_figures(board)
pygame.display.update()
CLOCK = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if player_turn and not is_winner(board, 1)[0] and not is_winner(board, 2)[0] and not is_board_full(board):
        random_move(board)
        player_turn = False

    elif not player_turn and not is_winner(board, 1)[0] and not is_winner(board, 2)[0] and not is_board_full(board):
        ai_move(board)
        player_turn = True

    # Draw everything (after move)
    screen.fill(BG_COLOR)
    draw_leaderboard(ai_wins, rando_wins, draws)
    draw_lines()
    draw_figures(board)
    pygame.display.update()

    # Check for game end
    rando_won, winning_cells_rando = is_winner(board, 1)
    ai_won, winning_cells_ai = is_winner(board, 2)
    if rando_won:
        screen.fill(BG_COLOR)
        draw_leaderboard(ai_wins, rando_wins, draws)
        draw_lines()
        draw_figures(board)
        draw_win_line(winning_cells_rando)
        pygame.display.update()
        pygame.time.wait(1000)
        rando_wins += 1
        board = reset_board()
        player_turn = True  # rando starts
    elif ai_won:
        screen.fill(BG_COLOR)
        draw_leaderboard(ai_wins, rando_wins, draws)
        draw_lines()
        draw_figures(board)
        draw_win_line(winning_cells_ai)
        pygame.display.update()
        pygame.time.wait(1000)
        ai_wins += 1
        board = reset_board()
        player_turn = True
    elif is_board_full(board):
        pygame.display.update()
        pygame.time.wait(800)
        draws += 1
        board = reset_board()
        player_turn = True

    CLOCK.tick(120)  # Fast but see the effect!