from pieces import *
from enum import Enum, auto


class MoveType(Enum):
    InvalidMove = auto()
    Move = auto()
    Take = auto()
    Castle = auto()


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
        self._turn: Color = Color.White

    @property
    def board(self):
        return self._board

    @property
    def turn(self):
        return self._turn

    def move(self, old_pos: tuple[int, int], new_pos: tuple[int, int]) -> tuple[MoveType, CheckState]:
        old_pos_piece = self._board[old_pos[0]][old_pos[1]]
        new_pos_piece = self._board[new_pos[0]][new_pos[1]]
        if old_pos_piece.color == self._turn and self.validate_move_legality(old_pos, new_pos):
            move_type = self.perform_move(old_pos, new_pos)
            enemy_king = self.white_king if old_pos_piece.color == Color.Black else self.black_king
            check_state = self.get_check_state(enemy_king)  # self.find_king(enemy_king)
            if check_state == CheckState.Checkmate:
                self.winner = Color.White if enemy_king.color == Color.Black else Color.Black
            self._turn = Color.Black if self._turn == Color.White else Color.White  # another person's turn
            return move_type, check_state
        else:
            return MoveType.InvalidMove, CheckState.NoCheck

    def perform_move(self, old, new) -> MoveType:
        """
        Special moves (something else happens, apart from making move, flag change etc.):
        king - castling
        pawn - first (double) move
        """
        old_pos_piece = self._board[old[0]][old[1]]

        if isinstance(old_pos_piece, Pawn):
            # pawn made its first move
            old_pos_piece.was_moved = True
        elif isinstance(old_pos_piece, King) and new in old_pos_piece.castling_moves().keys():
            # king makes castling - rook has to move
            rook_positions = old_pos_piece.castling_moves()[new]
            rook_old_pos, rook_new_pos = rook_positions[0], rook_positions[1]
            rook = self._board[rook_old_pos[0]][rook_old_pos[1]]
            self._board[rook_old_pos[0]][rook_old_pos[1]] = EmptyPiece()
            self._board[rook_new_pos[0]][rook_new_pos[1]] = rook
            old_pos_piece.can_castle = False
            rook.can_castle = False
            move_type = MoveType.Castle

        move_type = MoveType.Move if isinstance(self._board[new[0]][new[1]], EmptyPiece) else MoveType.Take
        self._board[new[0]][new[1]] = old_pos_piece
        self._board[old[0]][old[1]] = EmptyPiece()

        return move_type

    def validate_move_legality(self, old: tuple[int, int], new: tuple[int, int]) -> bool:
        piece = self._board[old[0]][old[1]]
        new_pos_piece = self._board[new[0]][new[1]]
        if isinstance(self._board[new[0]][new[1]], King):
            # cannot take King!
            return False
        if isinstance(piece, Pawn):
            # here whole pawn logic is handled, because its moves are different tha the rest of the pieces
            if ((not piece.was_moved and new == piece.first_move(*old) and isinstance(new_pos_piece, EmptyPiece) and isinstance(self._board[old[0]+(1 if piece.color == Color.Black else -1)][old[1]], EmptyPiece)) or # TODO +1 albo -1 dla self._board[old[0]+1][old[1]]
            (new in piece.possible_takes(*old) and not isinstance(new_pos_piece, EmptyPiece) and new_pos_piece != piece.color) or
            (new in piece.possible_moves(*old) and isinstance(new_pos_piece, EmptyPiece))):
                return not self.move_causes_selfcheck(old, new)
            # TODO add en_passant
            else:
                return False
        elif new in piece.possible_moves(*old):
            if isinstance(piece, Knight) or self.free_path_between(old, new):
                if new_pos_piece.color != piece.color:
                    return not self.move_causes_selfcheck(old, new)
            return False
        elif isinstance(piece, King):
            # need to handle castling
            rook_pos = piece.castling_moves().get(new, None)
            rook = self._board[rook_pos[0][0]][rook_pos[0][1]] if rook_pos else None
            rook = rook if isinstance(rook, Rook) else None
            if rook and rook.can_castle and piece.can_castle and self.free_path_between(old, rook_pos[0]) and self.get_check_state(piece, verify_checkmate=False) == CheckState.NoCheck:
                return not self.move_causes_selfcheck(old, new)
            return False

    def free_path_between(self, old: tuple[int, int], new: tuple[int, int]):
        path_i, path_j = new[0]-old[0], new[1]-old[1]
        shift_i = path_i//abs(path_i) if path_i != 0 else 0
        shift_j = path_j//abs(path_j) if path_j != 0 else 0
        ptc = old  # ptc - position to check
        for _ in range(max(abs(path_i), abs(path_j))-1):
            ptc = (ptc[0]+shift_i, ptc[1]+shift_j)
            try:
                if not isinstance(self._board[ptc[0]][ptc[1]], EmptyPiece):  # piece on the way of the move!
                    return False
            except:
                print('Loolz', ptc)
                print('old', old, 'new', new)
        return True

    def move_causes_selfcheck(self, old: tuple[int, int], new: tuple[int, int]) -> bool:
        piece = self._board[old[0]][old[1]]
        new_pos_piece = self._board[new[0]][new[1]]
        self._board[new[0]][new[1]] = piece
        self._board[old[0]][old[1]] = EmptyPiece()
        king = self.white_king if piece.color == Color.White else self.black_king
        selfcheck = False
        if self.get_check_state(king, verify_checkmate=False) != CheckState.NoCheck:  # self.find_king(king)
            selfcheck = True
        self._board[new[0]][new[1]] = new_pos_piece
        self._board[old[0]][old[1]] = piece
        return selfcheck

    def get_check_state(self, king: King, verify_checkmate=True) -> CheckState:
        king_pos = self.find_king(king)
        #king = self._board[king_pos[0]][king_pos[1]]
        for i, line in enumerate(self._board):
            for j, piece in enumerate(line):
                if piece.color != king.color:
                    if ((isinstance(piece, Knight) and king_pos in piece.possible_moves(i, j)) or
                    (not isinstance(piece, Pawn) and king_pos in filter(lambda new: self.free_path_between((i, j), new), piece.possible_moves(i, j))) or
                    (isinstance(piece, Pawn) and king_pos in piece.possible_takes(i, j))):
                        if verify_checkmate and self.is_checkmate(king):
                            return CheckState.Checkmate
                        return CheckState.Check
        return CheckState.NoCheck

    def is_checkmate(self, king: King) -> bool:
        #king = self._board[king_pos[0]][king_pos[1]]
        #possible_moves = king.possible_moves(king_pos[0], king_pos[1])
        for i, line in enumerate(self._board):
            for j, piece in enumerate(line):
                if piece.color != king.color:
                    # we check only if other pieces including king can defend king from checkmate
                    continue
                possible_moves = piece.possible_moves(i, j)
                if isinstance(piece, Pawn):
                    possible_moves.extend(piece.possible_takes(i, j))
                for move_i, move_j in possible_moves:
                    if self.validate_move_legality((i, j), (move_i, move_j)):  # isinstance(self._board[move_i][move_j], EmptyPiece):
                        new_pos_piece = self._board[move_i][move_j]
                        self._board[i][j] = EmptyPiece()
                        self._board[move_i][move_j] = piece
                        if self.get_check_state(king, verify_checkmate=False) == CheckState.NoCheck:
                            self._board[i][j] = piece
                            self._board[move_i][move_j] = new_pos_piece
                            return False
                        self._board[i][j] = piece
                        self._board[move_i][move_j] = new_pos_piece
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