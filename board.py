from pieces import *
from enum import Enum, auto


class MoveType(Enum):
    InvalidMove = auto()
    Move = auto()
    Take = auto()


class CheckState(Enum):
    NoCheck = auto()
    Check = auto()
    Checkmate = auto()

class ChessBoard:
    SIZE = 8

    def __init__(self) -> None:
        self.white_king = King(Color.White)
        self.black_king = King(Color.Black)
        self._board: list[list[Piece]] = [
            [Rook(Color.Black), Knight(Color.Black), Bishop(Color.Black), self.black_king, Queen(Color.Black), Bishop(Color.Black), Knight(Color.Black), Rook(Color.Black)],
            [Pawn(Color.Black) for _ in range(self.SIZE)],
            [EmptyPiece() for _ in range(self.SIZE)],
            [EmptyPiece() for _ in range(self.SIZE)],
            [EmptyPiece() for _ in range(self.SIZE)],
            [EmptyPiece() for _ in range(self.SIZE)],
            [Pawn(Color.White) for _ in range(self.SIZE)],
            [Rook(Color.White), Knight(Color.White), Bishop(Color.White), self.white_king, Queen(Color.White), Bishop(Color.White), Knight(Color.White), Rook(Color.White)]
        ]
        self.winner: Color | None = None
        self.moves: list[str] = []

    @property
    def board(self):
        return self._board

    def move(self, old_pos: tuple[int, int], new_pos: tuple[int, int]) -> tuple[MoveType, CheckState]:
        old_pos_piece = self._board[old_pos[0]][old_pos[1]]
        new_pos_piece = self._board[new_pos[0]][new_pos[1]]
        if self.validate_move_legality(old_pos, new_pos):
            self._board[new_pos[0]][new_pos[1]] = old_pos_piece
            self._board[old_pos[0]][old_pos[1]] = EmptyPiece()
            if isinstance(new_pos_piece, EmptyPiece):
                move_type = MoveType.Move
            else:
                move_type = MoveType.Take
            enemy_king = self.white_king if old_pos_piece.color == Color.Black else self.black_king
            check_state = self.get_check_state(self.find_king(enemy_king))
            if check_state == CheckState.Checkmate:
                self.winner = Color.White if enemy_king.color == Color.Black else Color.Black
            return move_type, check_state
        else:
            return MoveType.InvalidMove, CheckState.NoCheck

    def validate_move_legality(self, old: tuple[int, int], new: tuple[int, int]) -> bool:
        piece = self._board[old[0]][old[1]]
        if new in piece.possible_moves(*old):
            if self._board[new[0]][new[1]].color != piece.color:
                return not self.move_causes_selfcheck(old, new)
            else:
                return False
        if isinstance(piece, Pawn):
            if not piece.was_moved and new == piece.first_move(*old):
                return not self.move_causes_selfcheck(old, new)
            # TODO add en_passant
            else:
                return False

    def move_causes_selfcheck(self, old: tuple[int, int], new: tuple[int, int]) -> bool:
        piece = self._board[old[0]][old[1]]
        new_pos_piece = self._board[new[0]][new[1]]
        self._board[new[0]][new[1]] = piece
        self._board[old[0]][old[1]] = EmptyPiece()
        king = self.white_king if piece.color == Color.White else self.black_king
        selfcheck = False
        if self.get_check_state(self.find_king(king)) != CheckState.NoCheck:
            selfcheck = True
        self._board[new[0]][new[1]] = new_pos_piece
        self._board[old[0]][old[1]] = piece
        return selfcheck

    def get_check_state(self, king_pos: tuple[int, int]) -> CheckState:
        #king_pos = self.find_king(king)
        king = self._board[king_pos[0]][king_pos[1]]
        for i, line in enumerate(self._board):
            for j, piece in enumerate(line):
                if piece.color != king.color and king_pos in piece.possible_moves(i, j):
                    if self.is_checkmate(king_pos):
                        return CheckState.Checkmate
                    return CheckState.Check
        return CheckState.NoCheck

    def is_checkmate(self, king_pos: tuple[int, int]) -> bool:
        king = self._board[king_pos[0]][king_pos[1]]
        possible_moves = king.possible_moves(king_pos[0], king_pos[1])
        for move_i, move_j in possible_moves:
            if isinstance(self._board[move_i][move_j], EmptyPiece):
                self._board[king_pos[0]][king_pos[1]] = EmptyPiece()
                self._board[move_i][move_j] = king
                if not self.get_check_state(king_pos):
                    self._board[king_pos[0]][king_pos[1]] = king
                    self._board[move_i][move_j] = EmptyPiece()
                    return False
                self._board[king_pos[0]][king_pos[1]] = king
                self._board[move_i][move_j] = EmptyPiece()
        return True

    def find_king(self, king: King) -> tuple[int, int]:
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                if self._board[i][j] == king:
                    return i, j
        raise ValueError('There is no king on the board')


# class Board(list):
#     def __getitem__(self, key):
#         if isinstance(key, int) or isinstance(key, slice):
#             super().__getitem__(key)
#         elif isinstance(key, tuple):
#             if not isinstance(key[0], int) or not isinstance(key[1], int):
#                 raise ValueError('Wrong tuple type! Should be: tuple[int, int]')
#             return self[key[0]][key[1]]