from pieces import *
from enum import Enum, auto

class MoveType(Enum):
    InvalidMove = auto()
    Move = auto()
    Take = auto()

class Board:
    SIZE = 8

    def __init__(self) -> None:
        self.white_king = King(Color.White)
        self.black_king = King(Color.Black)
        self._board: list[list[Piece]] = [
            [Rook(Color.White), Knight(Color.White), Bishop(Color.White), self.white_king, Queen(Color.White), Bishop(Color.White), Knight(Color.White), Rook(Color.White)],
            [Pawn(Color.White) for _ in range(self.SIZE)],
            [EmptyPiece() for _ in range(self.SIZE)],
            [EmptyPiece() for _ in range(self.SIZE)],
            [EmptyPiece() for _ in range(self.SIZE)],
            [EmptyPiece() for _ in range(self.SIZE)],
            [Pawn(Color.Black) for _ in range(self.SIZE)],
            [Rook(Color.Black), Knight(Color.Black), Bishop(Color.Black), self.black_king, Queen(Color.Black), Bishop(Color.Black), Knight(Color.Black), Rook(Color.Black)]
        ]
        self.winner: str | None = None
        self.moves: list[str] = []

    def move(self, old_pos: tuple[int, int], new_pos: tuple[int, int]) -> MoveType:
        old_pos_piece = self._board[old_pos[0]][old_pos[1]]
        new_pos_piece = self._board[new_pos[0]][new_pos[1]]
        if self.validate_move(old_pos_piece, old_pos, new_pos):
            self._board[new_pos[0]][new_pos[1]] = old_pos_piece
            self._board[old_pos[0]][old_pos[1]] = EmptyPiece()
            if isinstance(new_pos_piece, EmptyPiece):
                return MoveType.Move
            else:
                return MoveType.Take
        else:
            return MoveType.InvalidMove

    def validate_move(self, piece: Piece, old: tuple[int, int], new: tuple[int, int]):
        if new in piece.possible_moves(*old):
            if self._board[new[0]][new[1]].color != piece.color:
                return True
            else:
                return False
        if isinstance(piece, Pawn):
            if not piece.was_moved and new == piece.first_move(*old):
                return True
            # TODO add en_passant
            else:
                return False

    def is_check(self, king: King) -> bool:
        king_pos =
