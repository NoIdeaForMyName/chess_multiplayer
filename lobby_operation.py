from enum import Enum, auto
from dataclasses import dataclass
from typing import Any


class OperationType(Enum):
    AllGames = auto()
    StartGame = auto()
    JoinGame = auto()
    Disconnect = auto()


@dataclass(frozen=False)
class GameInfo:
    name: str
    server_socket: tuple[str, int]
    players_connected: int


@dataclass(frozen=True)
class LobbyOperation:
    type: OperationType
    data: Any
