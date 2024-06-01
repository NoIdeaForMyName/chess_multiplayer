from enum import Enum, auto
from dataclasses import dataclass
from typing import Any


class OperationType(Enum):
    StartGame = auto()
    # JoinGame = auto()  # it is not made by server - only client
    Disconnect = auto()


@dataclass(frozen=True)
class LobbyOperation:
    type: OperationType
    data: Any
