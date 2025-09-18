import random
import os
import tkinter


has_first_move = False

offsets = [
    (-1, 0),
    (1, 0),
    (0, -1),
    (0, 1),
    (1, -1),
    (-1, 1),
    (-1, -1),
    (1, 1)
]

# Two different boards are used. The Guess Board has what players see in the terminal while the Bomb Board is the layer "underneath" that has the bombs that have not yet been revealed. 
def make_bomb_board(length, width, difficulty, coordy, coordx): # Takes coords as input to generate bomb board without bombs at the players first move location. 
    board = [[0 for _ in range(width)] for _ in range(length)]
    safe_spots = []
    safe_spots.append([coordy, coordx])
    
    
    for offsety, offsetx in offsets:
        if 0 <= coordy + offsety < length and 0 <= coordx + offsetx < width:
            safe_spots.append([coordy + offsety, coordx + offsetx])
    
    bombs_placed = 0
    while bombs_placed < difficulty:
        y = random.randint(0, length - 1)
        x = random.randint(0, width - 1)
        if [y, x] not in safe_spots and board[y][x] != 'x': #generate bombs in a random location and only places them if they are not in the designated safe spots. 
            board[y][x] = 'x'
            bombs_placed += 1

    # Calculate adjacent bomb counts
    for i in range(length): 
        for j in range(width):
            if board[i][j] == 'x':
                for offsety, offsetx in offsets:
                    ni, nj = i + offsety, j + offsetx # uses the offset tuple list to look at every square around a bomb
                    if 0 <= ni < length and 0 <= nj < width and board[ni][nj] != 'x': # if the offset squares are within bounds of the board, add one
                        board[ni][nj] += 1 # this creates the numbered tiles where the number on the tile represents the number of adjacent bombs
            
    return board

def make_guess_board(length, width): # makes the guess board which is the one displayed for players to see. 
    return [['   ' for _ in range(width)] for _ in range(length)] 

def adjacent_zeroes(g_board, b_board, coordy, coordx): # recursive function for revealing adjacent 'zero' squares. This makes it so players don't have to manually reveal every free tile which is extremely tedious. 
    if not (0 <= coordy < len(g_board) and 0 <= coordx < len(g_board[0])):
        return
    
    if b_board[coordy][coordx] == 0 and "0" not in g_board[coordy][coordx]:
        g_board[coordy][coordx] = " 0 "
        for offsety, offsetx in offsets:
            ny, nx = coordy + offsety, coordx + offsetx
            if 0 <= ny < len(g_board) and 0 <= nx < len(g_board[0]):
                if b_board[ny][nx] == 0:
                    adjacent_zeroes(g_board, b_board, ny, nx)
                elif b_board[ny][nx] > 0:
                    g_board[ny][nx] = f" {b_board[ny][nx]} "

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def num_to_alpha(num):
    return chr((num % 26) + 97)

def alpha_to_num(alpha):
    return ord(alpha) - 97

def display_board(board):
    print('  ', end='')
    for i in range(len(board[0])):
        print(f" {num_to_alpha(i)}  ", end="")
    print('')
    print(' ', end='')
    print("-" * (4 * len(board[0])))
    
    for num, row in enumerate(board):
        print(num_to_alpha(num).upper() + "|" + "|".join(str(cell) for cell in row) + "|")
        if num != len(board) - 1:
            print(" " + "-" * (4 * len(board[0])))
    
    print(' ', end='')
    print("-" * (4 * len(board[0])))
    print('')

def lose(g_board, b_board):
    for i in range(len(g_board)):
        for j in range(len(g_board[0])):
            g_board[i][j] = f" {b_board[i][j]} " if b_board[i][j] == 'x' else f" {b_board[i][j]} "

def player_move(board):
    while True:
        coords = input("Please enter the coordinates of the tile you would like to reveal (like- De): ").lower().replace(' ', '')
        if len(coords) == 2 and coords[0].isalpha() and coords[1].isalpha():
            try:
                coord_num_y = alpha_to_num(coords[0])
                coord_num_x = alpha_to_num(coords[1])
                if 0 <= coord_num_y < len(board) and 0 <= coord_num_x < len(board[0]):
                    return coord_num_y, coord_num_x
                else:
                    print("Coordinates out of bounds. Try again.")
            except:
                pass
        print("Invalid input. Please enter coordinates like 'De'.")

def move_handler(g_board, b_board, coord_num_y, coord_num_x):
    global has_first_move
    
    if b_board[coord_num_y][coord_num_x] == 'x':
        if not has_first_move:
            # If first move is a bomb, move the bomb
            for i in range(len(b_board)):
                for j in range(len(b_board[0])):
                    if b_board[i][j] != 'x' and [i, j] != [coord_num_y, coord_num_x]:
                        b_board[i][j] = 'x'
                        b_board[coord_num_y][coord_num_x] = 0
                        # Recalculate numbers
                        for y in range(len(b_board)):
                            for x in range(len(b_board[0])):
                                if b_board[y][x] != 'x':
                                    b_board[y][x] = 0
                                    for offsety, offsetx in offsets:
                                        ny, nx = y + offsety, x + offsetx
                                        if 0 <= ny < len(b_board) and 0 <= nx < len(b_board[0]) and b_board[ny][nx] == 'x':
                                            b_board[y][x] += 1
                        move_handler(g_board, b_board, coord_num_y, coord_num_x)
                        return
        else:
            lose(g_board, b_board)
            return True
    
    if not has_first_move:
        has_first_move = True
    
    if b_board[coord_num_y][coord_num_x] > 0:
        g_board[coord_num_y][coord_num_x] = f" {b_board[coord_num_y][coord_num_x]} "
    elif b_board[coord_num_y][coord_num_x] == 0:
        adjacent_zeroes(g_board, b_board, coord_num_y, coord_num_x)
    
    return False

def check_win(g_board, b_board):
    for i in range(len(g_board)):
        for j in range(len(g_board[0])):
            if g_board[i][j] == '   ' and b_board[i][j] != 'x':
                return False
    return True

def game():
    clear_console()
    length, width = 10, 10
    difficulty = 20  # Number of bombs
    
    guess_board = make_guess_board(length, width)
    display_board(guess_board)
    
    # Get first move and generate board
    firstmovey, firstmovex = player_move(guess_board)
    bomb_board = make_bomb_board(length, width, difficulty, firstmovey, firstmovex)
    
    # Handle first move
    game_over = move_handler(guess_board, bomb_board, firstmovey, firstmovex)
    
    while not game_over:
        clear_console()
        display_board(guess_board)
        
        if check_win(guess_board, bomb_board):
            print("Congratulations! You won!")
            lose(guess_board, bomb_board)  # Reveal the board
            clear_console()
            display_board(guess_board)
            break
        
        movey, movex = player_move(guess_board)
        game_over = move_handler(guess_board, bomb_board, movey, movex)
    
    # Show final board
    clear_console()
    display_board(guess_board)
    print("Game over!")

if __name__ == "__main__":

    game()
