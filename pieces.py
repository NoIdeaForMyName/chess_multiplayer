import abc
from enum import Enum, auto


# class PieceType(Enum):
#     WhitePawn = auto()
#     BlackPawn = auto()
#     Knight = auto()
#     Bishop = auto()
#     Rook = auto()
#     Queen = auto()
#     King = auto()

class Color(Enum):
    White = auto()
    Black = auto()
    Empty = auto()


class Piece(abc.ABC):
    BOARD_SIZE = 8

    def __init__(self, color: Color, points: int, moves: list[tuple[int, int]]) -> None:
        self._color: Color = color
        self.points: int = points
        self._moves: list[tuple[int, int]] = moves

    @property
    def color(self):
        return self._color

    @property
    def moves(self) -> list[tuple[int, int]]:
        return self._moves

    def possible_moves(self, i, j) -> list[tuple[int, int]]:
        possible = []
        for move_i, move_j in self.moves:
            possible.append((move_i+i, move_j+j))
        return self.filter_outside_board(possible)

    def filter_outside_board(self, moves: list[tuple[int, int]]) -> list[tuple[int, int]]:
        return list(filter(lambda m: 0 <= m[0] < self.BOARD_SIZE and 0 <= m[1] < self.BOARD_SIZE, moves))

    def __str__(self):
        return self.__class__.__name__ + self.color.name


class EmptyPiece(Piece):
    def __init__(self):
        super().__init__(Color.Empty, 0, [])


class Pawn(Piece):
    def __init__(self, color: Color) -> None:
        points = 1
        moves = [(-1, 0)]
        if color == Color.Black:
            moves = [(1, 0)]
        super().__init__(color, points, moves)
        self._was_moved: bool = False

    def first_move(self, i, j) -> tuple[int, int]:
        move_i = self.moves[0][0] * 2
        return move_i+i, j

    def possible_takes(self, i, j) -> list[tuple[int, int]]:
        move_i, move_j = self.possible_moves(i, j)[0]
        return self.filter_outside_board([(move_i, move_j+1), (move_i, move_j-1)])

    def en_passant(self, i, j) -> list[tuple[int, int]]:
        pass  # TODO

    @property
    def was_moved(self):
        return self._was_moved

    @was_moved.setter
    def was_moved(self, value: bool):
        self._was_moved = value


class Knight(Piece):
    def __init__(self, color: Color) -> None:
        points = 3
        moves = [
            (2, 1),
            (2, -1),
            (1, 2),
            (-1, 2),
            (-2, 1),
            (-2, -1),
            (-1, -2),
            (1, -2)
        ]
        super().__init__(color, points, moves)


class Bishop(Piece):
    def __init__(self, color: Color) -> None:
        points = 3

        moves = [(i, i) for i in range(1, 9)]
        moves.extend([(i, -i) for i in range(1, 9)])
        moves.extend([(-i, i) for i in range(1, 9)])
        moves.extend([(-i, -i) for i in range(1, 9)])

        super().__init__(color, points, moves)


class Rook(Piece):
    def __init__(self, color: Color) -> None:
        points = 5

        moves = [(i, 0) for i in range(1, 9)]
        moves.extend([(0, i) for i in range(1, 9)])
        moves.extend([(-i, 0) for i in range(1, 9)])
        moves.extend([(0, -i) for i in range(1, 9)])

        super().__init__(color, points, moves)
        self._can_castle = True

    @property
    def can_castle(self):
        return self._can_castle

    @can_castle.setter
    def can_castle(self, value: bool):
        self._can_castle = value


class Queen(Piece):
    def __init__(self, color: Color) -> None:
        points = 9

        moves = [(i, i) for i in range(1, 9)]
        moves.extend([(i, -i) for i in range(1, 9)])
        moves.extend([(-i, i) for i in range(1, 9)])
        moves.extend([(-i, -i) for i in range(1, 9)])
        moves.extend([(i, 0) for i in range(1, 9)])
        moves.extend([(0, i) for i in range(1, 9)])
        moves.extend([(-i, 0) for i in range(1, 9)])
        moves.extend([(0, -i) for i in range(1, 9)])

        super().__init__(color, points, moves)


class King(Piece):
    def __init__(self, color: Color) -> None:
        points = -1

        moves = [
            (1, 0),
            (1, 1),
            (0, 1),
            (-1, 1),
            (-1, 0),
            (-1, -1),
            (0, -1),
            (1, -1)
        ]

        super().__init__(color, points, moves)
        self._can_castle = True

    def castling_moves(self) -> dict[tuple[int, int], list[tuple[int, int]]]:
        match self.color:
            case Color.White:
                return {
                    (7, 1): [(7, 0), (7, 2)],
                    (7, 5): [(7, 7), (7, 4)]

                }
            case Color.Black:
                return {
                    (0, 1): [(0, 0), (0, 2)],
                    (0, 5): [(0, 7), (0, 4)]
                }

    @property
    def can_castle(self):
        return self._can_castle

    @can_castle.setter
    def can_castle(self, value: bool):
        self._can_castle = value
