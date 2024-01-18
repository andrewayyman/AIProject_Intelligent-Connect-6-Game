import numpy as np
import random
import pygame
import sys
import math
import tkinter as tk
from tkinter import simpledialog


"""
Define colors 

"""

LIGHT_ORANGE = (255, 183, 77)  # background color
BLACK = (0, 0, 0)              # lines color 
WHITE_C = (250, 250, 250)      # player1 color
BLACK_C = (0, 0, 0)            # player2 color

PLAYER = 0
AI = 1


EMPTY = 0           #empty slots
PLAYER_PIECE = 1    #player pieces
AI_PIECE = 2        #AI pieces




# Number of pieces needed to win
WINDOW_LENGTH = 6


# Intialize create_board function
def create_board():
    board = np.zeros((19,19))
    return board


# Places a game piece on the game board 
def drop_piece(board, row, col, piece):
    board[row][col] = piece



# Checks if the specified column is a valid location
def is_valid_location(board, col):
    return board[board.shape[0] - 1][col] == 0


# Finds the next empty row in the column.
def get_next_open_row(board, col):
    for r in range(board.shape[0]):
        if board[r][col] == 0:
            return r


# Print the board and flip it vertically
def print_board(board):
    print(np.flip(board, 0))



# This function checks if a player  has a winning move
# It iterates through all possible positions and checks for a winning move
    
def winning_move(board, piece):
    # Check horizontal locations for win
    for c in range(board.shape[1] - WINDOW_LENGTH + 1):
        for r in range(board.shape[0]):
            if all(board[r][c + i] == piece for i in range(WINDOW_LENGTH)):
                return True
    
    # Check vertical locations for win
    for c in range(board.shape[1]):
        for r in range(board.shape[0] - WINDOW_LENGTH + 1):
            if all(board[r + i][c] == piece for i in range(WINDOW_LENGTH)):
                return True
    
    # Check positively sloped diagonals
    for c in range(board.shape[1] - WINDOW_LENGTH + 1):
        for r in range(board.shape[0] - WINDOW_LENGTH + 1):
            if all(board[r + i][c + i] == piece for i in range(WINDOW_LENGTH)):
                return True
    
    # Check negatively sloped diagonals
    for c in range(board.shape[1] - WINDOW_LENGTH + 1):
        for r in range(WINDOW_LENGTH - 1, board.shape[0]):
            if all(board[r - i][c + i] == piece for i in range(WINDOW_LENGTH)):
                return True




# heuristic function

# calculates a score for a window of game pieces for player (piece)
def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE

    if window.count(piece) == 6:
        score += 1000
    elif window.count(piece) == 5 and window.count(EMPTY) == 1:
        score += 50
    elif window.count(piece) == 4 and window.count(EMPTY) == 2:
        score += 10

    if window.count(opp_piece) == 5 and window.count(EMPTY) == 1:
        score -= 40
    if window.count(opp_piece) == 4 and window.count(EMPTY) == 2:
        score -= 20
    if window.count(opp_piece) == 3 and window.count(EMPTY) == 3:
        score -= 10
    if window.count(opp_piece) == 2 and window.count(EMPTY) == 4:
        score -= 5
    if window.count(opp_piece) == 1 and window.count(EMPTY) == 5:
        score -= 2

    return score



# heuristic function

#  calculates the overall score of the game board for a specified player.
def score_position(board, piece):
    score = 0

    # Score center column
    center_array = [int(i) for i in list(board[:, board.shape[1] // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    # Score Horizontal
    for r in range(board.shape[0]):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(board.shape[1] - 5):
            window = row_array[c:c + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score Vertical
    for c in range(board.shape[1]):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(board.shape[0] - 5):
            window = col_array[r:r + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score positively sloped diagonal
    for r in range(board.shape[0] - 5):
        for c in range(board.shape[1] - 5):
            window = [board[r + i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    for r in range(board.shape[0] - 5):
        for c in range(board.shape[1] - 5):
            window = [board[r + 5 - i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score                       #The scores are used in the Minimax algorithm



#  Checks if the game has reached a terminal state.

def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0




'''
The Minimax algorithm is used to find the best move for the AI player in the game.
It explores possible future game states up to a certain depth, considering both maximizing (AI)
and minimizing (player) scenarios. The function returns the best move (column) and its corresponding score.

'''

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 100000000000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -10000000000000)
            else:    # Game is over, no more valid moves
                return (None, 0)
        else:        # Depth is zero
            return (None, score_position(board, AI_PIECE))
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else:  # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value



#  Checks for columns that are not yet full.

def get_valid_locations(board):
    valid_locations = []
    for col in range(board.shape[1]):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations


#  This function selects the best move and choosing the one with the highest score.
def pick_best_move(board, piece):
    valid_locations = get_valid_locations(board)
    best_score = -10000
    best_col = random.choice(valid_locations)
    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, piece)
        score = score_position(temp_board, piece)
        if score > best_score:
            best_score = score
            best_col = col

    return best_col



# For drawing the game board on the Pygame 

def draw_board(board):
    # Dynamically adjust circle size based on the board size
    circle_radius = int(min(SQUARESIZE / 2 - 5, height / (2 * board.shape[0])))

    for c in range(board.shape[1]):
        for r in range(board.shape[0]):
           pygame.draw.rect(screen, LIGHT_ORANGE, (c * SQUARESIZE, r * SQUARESIZE  , SQUARESIZE, SQUARESIZE))
           pygame.draw.rect(screen, BLACK, (c * SQUARESIZE, r * SQUARESIZE , SQUARESIZE, SQUARESIZE),1) 

    for c in range(board.shape[1]):
        for r in range(board.shape[0]):
            if board[r][c] == PLAYER_PIECE:
               pygame.draw.circle(screen, WHITE_C, (int(c * SQUARESIZE + SQUARESIZE / 1), height - int(r * SQUARESIZE + SQUARESIZE / 1)), circle_radius)   
            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(screen, BLACK_C, (int(c * SQUARESIZE + SQUARESIZE / 1), height - int(r * SQUARESIZE + SQUARESIZE / 1)), circle_radius)

    pygame.display.update()





# Create the game board
board = create_board()

# To track whether the game has ended.
game_over = False

# Print the initial board
print_board(board)

# Initialize pygame
pygame.init()

# Set the size of each square on the board
SQUARESIZE = 40

# Set the width and height of the board based on the size of the board
width = board.shape[1] * SQUARESIZE
height = (board.shape[0] ) * SQUARESIZE



size = (width, height)

# Set the radius of each game piece
RADIUS = int(SQUARESIZE / 2 - 5)

# Create the game window
screen = pygame.display.set_mode(size)

# Draw the initial board
draw_board(board)

# Update the display
pygame.display.update()

# Set the font for displaying messages
myfont = pygame.font.SysFont("monospace", 75)



# Determine the starting player
turn = PLAYER            # Start with the human player
player_moves = 0         # Counter for the number of moves the player has made
max_moves_per_turn = 2   # Number of moves each player can make before switching

# Main game loop
while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True  # Set the game_over flag to exit the loop
        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
            posx = event.pos[0]
            col = int((posx / SQUARESIZE))
       
            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, PLAYER_PIECE)
                player_moves += 1

                if player_moves == 1:
                    # If it's the first move, switch to the AI's turn
                    turn = AI
                elif player_moves == max_moves_per_turn:
                    # After the player makes max_moves_per_turn moves, switch back to the player's turn
                    turn = PLAYER
                    player_moves = 0  # Reset player's move counter

                if winning_move(board, PLAYER_PIECE):
                    label = myfont.render("Player 1 wins!!", 1, WHITE_C)
                    screen.blit(label, (40, 10))
                    game_over = True
                elif len(get_valid_locations(board)) == 0:
                    label = myfont.render("It's a draw!", 1, (255, 255, 255))
                    screen.blit(label, (40, 10))
                    game_over = True

                print_board(board)
                draw_board(board)

    if turn == AI and not game_over:
        # AI makes max_moves_per_turn moves
        for _ in range(max_moves_per_turn):
            col, minimax_score = minimax(board, 2, -math.inf, math.inf, True)

            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, AI_PIECE)

            if winning_move(board, AI_PIECE):
                label = myfont.render("AI wins!!", 1, BLACK_C)
                screen.blit(label, (40, 10))
                game_over = True
            elif len(get_valid_locations(board)) == 0:
                label = myfont.render("It's a draw!", 1, (255, 255, 255))
                screen.blit(label, (40, 10))
                game_over = True

            print_board(board)
            draw_board(board)

        # Switch back to the human player's turn
        turn = PLAYER

    if game_over:
        pygame.time.delay(2000)  # Increased delay to 2 seconds

    # Limit frames per second (FPS)
    pygame.time.Clock().tick(30)

# Quit pygame and exit the program
pygame.quit()
sys.exit()