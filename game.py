import pygame
import sys

from board import *

# Initialize Pygame
pygame.init()
pygame.font.init()

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
RED = (255, 0, 0)

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

piece_images = {name: pygame.transform.scale(pygame.image.load(f'resources\\{name}.png'), (CELL_SIZE, CELL_SIZE)) for
                name in piece_names}


def draw_board(checked_king_pos: tuple[int, int]):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if (row, col) != checked_king_pos:
                color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
            else:
                color = RED
            pygame.draw.rect(screen, color, pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))


def draw_pieces(board: list[tuple[int, int]], drag_piece: Piece):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            if not isinstance(piece, EmptyPiece) and piece is not drag_piece:
                piece_img = piece_images[str(piece)]
                screen.blit(piece_img, (CELL_SIZE * col, CELL_SIZE * row))


def get_cell_under_mouse():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    row = mouse_y // CELL_SIZE
    col = mouse_x // CELL_SIZE
    return row, col


def main():
    dragging_piece = None
    dragging_piece_rect = None
    dragging_piece_pos = None

    checked_king_pos = None

    clock = pygame.time.Clock()
    chess_game = ChessBoard()
    board = chess_game.board

    game_lasts = True

    while game_lasts:
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
                        # board[row][col] = None
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and dragging_piece:
                    row, col = get_cell_under_mouse()
                    # board[row][col] = dragging_piece
                    move_type, check_state = chess_game.move(dragging_piece_pos, (row, col))
                    match move_type:
                        case MoveType.InvalidMove:
                            ...  # invalid move sound
                        case MoveType.Move:
                            ...  # regular move sound
                        case MoveType.Take:
                            ...  # take sound
                    match check_state:
                        case CheckState.NoCheck:
                            checked_king_pos = None
                        case CheckState.Check:
                            checked_king_pos = chess_game.find_king(chess_game.white_king if board[row][
                                                                                                 col].color == Color.Black else chess_game.black_king)
                        case CheckState.Checkmate:
                            game_lasts = False  # end game
                    dragging_piece = None
                    dragging_piece_rect = None
                    dragging_piece_pos = None
                    print('CHECK STATE', check_state)
            elif event.type == pygame.MOUSEMOTION:
                if dragging_piece:
                    dragging_piece_rect.center = pygame.mouse.get_pos()

        draw_board(checked_king_pos)
        draw_pieces(board, dragging_piece)

        if dragging_piece:
            screen.blit(piece_images[str(dragging_piece)], dragging_piece_rect)

        pygame.display.flip()
        clock.tick(60)

    while not (pygame.QUIT in [e.type for e in pygame.event.get()]):
        display_winner(chess_game.winner)
        pygame.display.flip()
        clock.tick(60)

def display_winner(winner: Color):
    font = pygame.font.SysFont('Comic Sans MS', 72)
    text = font.render(f'{winner.name} wins!', False, (255, 255, 255) if winner == Color.White else (0, 0, 0))
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text, text_rect)


if __name__ == "__main__":
    main()
