import pygame
import sys

from board import *

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
BOARD_SIZE = 8
CELL_SIZE = SCREEN_WIDTH // BOARD_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BROWN = (139, 69, 19)
LIGHT_BROWN = (222, 184, 135)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chess Game")

piece_names = [
    'BishopBlack',
    'BishopWhite',
    'KingBlack',
    'KingWhite',
    'KnightBlack',
    'KnightWhite',
    'PawnBlack',
    'PawnWhite',
    'QueenBlack',
    'QueenWhite',
    'RookBlack',
    'RookWhite'
]

piece_images = {name: pygame.transform.scale(pygame.image.load(f'resources\\{name}.png'), (CELL_SIZE, CELL_SIZE)) for name in piece_names}

def draw_board():
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
            pygame.draw.rect(screen, color, pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_pieces(board):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            if not isinstance(piece, EmptyPiece):
                piece_img = piece_images[str(piece)]
                screen.blit(piece_img, (CELL_SIZE*col, CELL_SIZE*row))

def get_cell_under_mouse():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    row = mouse_y // CELL_SIZE
    col = mouse_x // CELL_SIZE
    return row, col

def main():
    dragging_piece = None
    dragging_piece_rect = None
    dragging_piece_pos = None

    clock = pygame.time.Clock()
    chess_game = ChessBoard()
    board = chess_game.board

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    row, col = get_cell_under_mouse()
                    if not isinstance(board[row][col], EmptyPiece):
                        dragging_piece = board[row][col]
                        dragging_piece_pos = (row, col)
                        dragging_piece_rect = piece_images[str(dragging_piece)].get_rect(center=pygame.mouse.get_pos())
                        #board[row][col] = None
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and dragging_piece:
                    row, col = get_cell_under_mouse()
                    #board[row][col] = dragging_piece
                    chess_game.move(dragging_piece_pos, (row, col))
                    dragging_piece = None
                    dragging_piece_rect = None
                    dragging_piece_pos = None
            elif event.type == pygame.MOUSEMOTION:
                if dragging_piece:
                    dragging_piece_rect.center = pygame.mouse.get_pos()

        draw_board()
        draw_pieces(board)

        if dragging_piece:
            screen.blit(piece_images[str(dragging_piece)], dragging_piece_rect)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
