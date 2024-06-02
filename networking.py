from dataclasses import dataclass
import socket


@dataclass(frozen=True)
class Socket:
    connection: socket.socket
    info: tuple[str, int]
