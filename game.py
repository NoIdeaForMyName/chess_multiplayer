import pygame
import sys
from enum import Enum, auto

from board import *
from clock import *


class GameState(Enum):
    NotStarted = auto()
    InProgress = auto()
    Ended = auto()


class Game:

    SCREEN_WIDTH = 600
    SCREEN_HEIGHT = 700
    BOARD_SIZE = 8
    CELL_SIZE = SCREEN_WIDTH // BOARD_SIZE
    TIMER_HEIGHT = (SCREEN_HEIGHT-SCREEN_WIDTH)//2

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    DARK_BROWN = (139, 69, 19)
    LIGHT_BROWN = (222, 184, 135)
    RED = (255, 0, 0)

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

    def __init__(self, white_player: str, black_player: str, time: float) -> None:

        self.piece_images = {
            name: pygame.transform.scale(pygame.image.load(f'resources\\{name}.png'), (self.CELL_SIZE, self.CELL_SIZE)) for
            name in self.piece_names}

        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Chess Game")
        self.clock = pygame.time.Clock()
        self._game_state: GameState = GameState.NotStarted
        self.players = {
            Color.White: white_player,
            Color.Black: black_player,
            Color.Empty: 'Draw'
        }
        self._winner: str | None = None
        self.clocks = {
            Color.White: ChessClock(time),
            Color.Black: ChessClock(time)
        }
        self.active_clock = self.clocks[Color.White]

    @property
    def game_state(self):
        return self._game_state

    @property
    def winner(self):
        return self._winner

    def draw_board(self, checked_king_pos: tuple[int, int]):
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                if (row, col) != checked_king_pos:
                    color = self.LIGHT_BROWN if (row + col) % 2 == 0 else self.DARK_BROWN
                else:
                    color = self.RED
                pygame.draw.rect(self.screen, color, pygame.Rect(col * self.CELL_SIZE, row * self.CELL_SIZE + self.TIMER_HEIGHT, self.CELL_SIZE, self.CELL_SIZE))

    def draw_pieces(self, board: list[tuple[int, int]], drag_piece: Piece):
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                piece = board[row][col]
                if not isinstance(piece, EmptyPiece) and piece is not drag_piece:
                    piece_img = self.piece_images[str(piece)]
                    self.screen.blit(piece_img, (self.CELL_SIZE * col, self.CELL_SIZE * row + self.TIMER_HEIGHT))

    def get_cell_under_mouse(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_y -= self.TIMER_HEIGHT
        row = mouse_y // self.CELL_SIZE
        col = mouse_x // self.CELL_SIZE
        return row, col

    def start(self):
        dragging_piece = None
        dragging_piece_rect = None
        dragging_piece_pos = None

        checked_king_pos = None

        chess_game = ChessBoard()
        board = chess_game.board

        game_lasts = True
        self._game_state = GameState.InProgress

        while game_lasts:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        row, col = self.get_cell_under_mouse()
                        if not isinstance(board[row][col], EmptyPiece) and board[row][col].color == chess_game.turn:
                            dragging_piece = board[row][col]
                            dragging_piece_pos = (row, col)
                            dragging_piece_rect = self.piece_images[str(dragging_piece)].get_rect(center=pygame.mouse.get_pos())
                            # board[row][col] = None
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and dragging_piece:
                        row, col = self.get_cell_under_mouse()
                        # board[row][col] = dragging_piece
                        move_type, check_state = chess_game.move(dragging_piece_pos, (row, col))

                        if move_type == MoveType.InvalidMove:
                            ...  # invalid move sound
                        else:
                            self.active_clock = self.switch_clocks()
                            if move_type == MoveType.Move:
                                ...  # regular move sound
                            elif move_type == MoveType.Take:
                                ...  # take sound
                        match check_state:
                            case CheckState.NoCheck:
                                checked_king_pos = None
                            case CheckState.Check:
                                checked_king_pos = chess_game.find_king(chess_game.white_king if board[row][col].color == Color.Black else chess_game.black_king)
                            case CheckState.Checkmate:
                                game_lasts = False  # end game
                        dragging_piece = None
                        dragging_piece_rect = None
                        dragging_piece_pos = None
                        # print('CHECK STATE', check_state)
                elif event.type == pygame.MOUSEMOTION:
                    if dragging_piece:
                        dragging_piece_rect.center = pygame.mouse.get_pos()

            self.draw_board(checked_king_pos)
            self.draw_pieces(board, dragging_piece)

            if dragging_piece:
                self.screen.blit(self.piece_images[str(dragging_piece)], dragging_piece_rect)

            if self.update_elapsed_time():
                game_lasts = False
                self._game_state = GameState.Ended
                self._winner = self.players[Color.White if self.clocks[Color.Black] == self.active_clock else Color.Black]

            self.display_elapsed_time()

            pygame.display.flip()
            self.clock.tick(60)

        self._game_state = GameState.Ended
        self._winner = self.players[chess_game.winner]

        while not (pygame.QUIT in [e.type for e in pygame.event.get()]):
            self.display_winner(chess_game.winner)
            pygame.display.flip()
            self.clock.tick(60)

    def switch_clocks(self) -> ChessClock:
        self.active_clock.refresh_time()
        clocks = list(self.clocks.values())
        new_active = clocks[0] if clocks[1] == self.active_clock else clocks[1]
        new_active.start_timer()
        return new_active

    def update_elapsed_time(self) -> bool:
        self.active_clock.refresh_time()
        if self.active_clock.time_passed:
            return True
        return False

    def display_elapsed_time(self) -> None:
        pygame.draw.rect(self.screen, self.LIGHT_BROWN, pygame.Rect(0, 0, self.SCREEN_WIDTH, self.TIMER_HEIGHT))
        pygame.draw.rect(self.screen, self.LIGHT_BROWN, pygame.Rect(0, self.SCREEN_HEIGHT-self.TIMER_HEIGHT, self.SCREEN_WIDTH, self.TIMER_HEIGHT))

        font = pygame.font.SysFont('Comic Sans MS', 30)
        text_white = font.render(self.clocks[Color.White].time_rest_str(), False, self.BLACK)
        text_black = font.render(self.clocks[Color.Black].time_rest_str(), False, self.BLACK)
        text_white_rect = text_white.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT - self.TIMER_HEIGHT // 2))
        text_black_rect = text_black.get_rect(center=(self.SCREEN_WIDTH // 2, self.TIMER_HEIGHT // 2))
        self.screen.blit(text_white, text_white_rect)
        self.screen.blit(text_black, text_black_rect)

    def display_winner(self, winner: Color):
        font = pygame.font.SysFont('Comic Sans MS', 72)
        text = font.render(f'{winner.name} wins!', False, (255, 255, 255) if winner == Color.White else (0, 0, 0))
        text_rect = text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)


def main():
    game = Game('Mic', 'Mac', 600)
    game.start()
    print(game.winner)


if __name__ == "__main__":
    main()
