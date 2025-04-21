import pygame
import sys
import time # Used for pausing at game end

# --- Constants ---
WIDTH = 300
HEIGHT = 300
LINE_WIDTH = 5
BOARD_ROWS = 3
BOARD_COLS = 3
SQUARE_SIZE = WIDTH // BOARD_COLS
CIRCLE_RADIUS = SQUARE_SIZE // 3
CIRCLE_WIDTH = 8 # Slightly thicker for visibility
CROSS_WIDTH = 8 # Slightly thicker for visibility
SPACE = SQUARE_SIZE // 4 # Padding for X

# Colors (RGB)
BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
CIRCLE_COLOR = (239, 231, 200) # White-ish
CROSS_COLOR = (66, 66, 66)    # Dark Grey
TEXT_COLOR = (10, 80, 75) # Darker color for text

# Player representation
PLAYER_X = 'X'
PLAYER_O = 'O' # AI is 'O'

# --- Pygame Setup ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic Tac Toe - Minimax")
font = pygame.font.SysFont(None, 40) # Font for messages

# --- Game Variables ---
board = None # Initialize in reset_game
player_turn = None # 1 for Player X, 2 for Player O (AI)
game_over = None
winner = None

# --- Functions ---

def draw_lines():
    """Draws the grid lines on the screen."""
    screen.fill(BG_COLOR) # Clear screen first
    # Horizontal lines
    for i in range(1, BOARD_ROWS):
        pygame.draw.line(screen, LINE_COLOR, (0, i * SQUARE_SIZE), (WIDTH, i * SQUARE_SIZE), LINE_WIDTH)
    # Vertical lines
    for i in range(1, BOARD_COLS):
        pygame.draw.line(screen, LINE_COLOR, (i * SQUARE_SIZE, 0), (i * SQUARE_SIZE, HEIGHT), LINE_WIDTH)

def draw_figures():
    """Draws the X's and O's on the board based on the board state."""
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == PLAYER_X:
                # Draw descending line \
                start_desc = (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SPACE)
                end_desc = (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE)
                pygame.draw.line(screen, CROSS_COLOR, start_desc, end_desc, CROSS_WIDTH)
                # Draw ascending line /
                start_asc = (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE)
                end_asc = (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SPACE)
                pygame.draw.line(screen, CROSS_COLOR, start_asc, end_asc, CROSS_WIDTH)
            elif board[row][col] == PLAYER_O:
                center = (int(col * SQUARE_SIZE + SQUARE_SIZE // 2), int(row * SQUARE_SIZE + SQUARE_SIZE // 2))
                pygame.draw.circle(screen, CIRCLE_COLOR, center, CIRCLE_RADIUS, CIRCLE_WIDTH)

def mark_square(row, col, player_symbol):
    """Marks a square on the board if it's available."""
    if board[row][col] == '':
        board[row][col] = player_symbol
        return True
    return False

def available_squares():
    """Returns a list of tuples (row, col) for all empty squares."""
    return [(r, c) for r in range(BOARD_ROWS) for c in range(BOARD_COLS) if board[r][c] == '']

def is_board_full():
    """Checks if the board has any empty squares left."""
    return len(available_squares()) == 0

def check_winner(current_board=None):
    """
    Checks if there is a winner on the given board (or the global board if None).
    Returns the winning player's symbol ('X' or 'O') or None.
    """
    b = current_board if current_board else board # Use provided board or global one

    # Check rows
    for row in range(BOARD_ROWS):
        if b[row][0] == b[row][1] == b[row][2] != '':
            return b[row][0]
    # Check columns
    for col in range(BOARD_COLS):
        if b[0][col] == b[1][col] == b[2][col] != '':
            return b[0][col]
    # Check diagonals
    if b[0][0] == b[1][1] == b[2][2] != '':
        return b[0][0]
    if b[0][2] == b[1][1] == b[2][0] != '':
        return b[0][2]

    return None # No winner

# --- AI Logic (Minimax) ---

def evaluate_board():
    """Evaluates the current board state for the minimax algorithm."""
    winner = check_winner(board)
    if winner == PLAYER_O:
        return 1  # AI wins
    elif winner == PLAYER_X:
        return -1 # Player wins
    elif is_board_full():
        return 0  # Draw
    else:
        return None # Game not finished

def minimax(current_board, depth, is_maximizing):
    """
    Minimax algorithm implementation.
    - is_maximizing: True if it's AI's turn (O), False if Player's turn (X).
    - Returns the best score achievable from the current state.
    """
    score = evaluate_board()
    if score is not None: # Base case: Game over or draw
        return score

    moves = available_squares() # Use the global board's available squares here

    if is_maximizing: # AI's turn (O) - maximize the score
        best_score = -float('inf')
        for r, c in moves:
            current_board[r][c] = PLAYER_O
            current_score = minimax(current_board, depth + 1, False) # Switch to minimizing
            current_board[r][c] = '' # Undo the move
            best_score = max(best_score, current_score)
        return best_score
    else: # Player's turn (X) - minimize the score
        best_score = float('inf')
        for r, c in moves:
            current_board[r][c] = PLAYER_X
            current_score = minimax(current_board, depth + 1, True) # Switch to maximizing
            current_board[r][c] = '' # Undo the move
            best_score = min(best_score, current_score)
        return best_score

def find_best_move():
    """
    Finds the best move for the AI (Player O) using the minimax algorithm.
    Returns the best (row, col) tuple for the AI to move to.
    """
    best_score = -float('inf')
    best_move = None
    moves = available_squares()

    if not moves: # Should not happen if called correctly, but safety check
        return None

    for r, c in moves:
        board[r][c] = PLAYER_O # Try the move
        score = minimax(board, 0, False) # Evaluate starting from opponent's perspective
        board[r][c] = '' # Undo the move

        if score > best_score:
            best_score = score
            best_move = (r, c)

    return best_move

# --- Game Flow ---

def display_message(message):
    """Displays a message centered on the screen."""
    msg_surface = font.render(message, True, TEXT_COLOR)
    msg_rect = msg_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    # Add a semi-transparent background for better readability
    bg_rect = pygame.Surface((msg_rect.width + 20, msg_rect.height + 20), pygame.SRCALPHA)
    bg_rect.fill((200, 200, 200, 180)) # White-ish, semi-transparent
    screen.blit(bg_rect, (msg_rect.left - 10, msg_rect.top - 10))
    screen.blit(msg_surface, msg_rect)
    pygame.display.update() # Update only the message area
    time.sleep(0.5) # Small pause before allowing restart


def show_end_message():
    """Determines and displays the end game message."""
    if winner == PLAYER_X:
        display_message("You Win!")
    elif winner == PLAYER_O:
        display_message("AI Wins!")
    else: # Draw
        display_message("It's a Draw!")
    # Add instruction to restart
    time.sleep(1) # Wait a bit longer
    instruction_font = pygame.font.SysFont(None, 30)
    instruction_surf = instruction_font.render("Click to Play Again", True, TEXT_COLOR)
    instruction_rect = instruction_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
    screen.blit(instruction_surf, instruction_rect)
    pygame.display.update()

def reset_game():
    """Resets the game state for a new round."""
    global board, player_turn, game_over, winner
    board = [['' for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
    player_turn = 1 # Player X starts
    game_over = False
    winner = None
    draw_lines() # Redraw the initial empty board

# --- Main Game Loop ---
reset_game() # Initialize the first game
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            # If game is over, a click restarts the game
            if game_over:
                reset_game()
                continue # Skip the rest of the event handling for this click

            # Player's turn logic
            if player_turn == 1 and not game_over:
                mouseX = event.pos[0]
                mouseY = event.pos[1]

                clicked_col = mouseX // SQUARE_SIZE
                clicked_row = mouseY // SQUARE_SIZE

                # Check bounds and if square is valid
                if 0 <= clicked_row < BOARD_ROWS and 0 <= clicked_col < BOARD_COLS:
                    if mark_square(clicked_row, clicked_col, PLAYER_X):
                        # Check if player's move ended the game
                        winner = check_winner()
                        if winner or is_board_full():
                            game_over = True
                        else:
                            player_turn = 2 # Switch to AI's turn

    # AI's turn logic (outside the event loop to run after player's move)
    if player_turn == 2 and not game_over:
        best_move = find_best_move()
        if best_move:
            mark_square(best_move[0], best_move[1], PLAYER_O)
            # Check if AI's move ended the game
            winner = check_winner()
            if winner or is_board_full():
                game_over = True
            else:
                player_turn = 1 # Switch back to Player's turn

    # --- Drawing ---
    # Always redraw the board state unless game just reset (handled in reset_game)
    if not game_over or (game_over and winner is None and not is_board_full()): # Redraw during play or right before msg
        draw_lines() # Redraw grid in case messages overlayed it
        draw_figures()

    # --- Game Over Handling ---
    if game_over:
        show_end_message()
        # The game waits here until the user clicks (handled in MOUSEBUTTONDOWN event)

    # Update the full display
    pygame.display.update()

# --- Cleanup ---
pygame.quit()
sys.exit()