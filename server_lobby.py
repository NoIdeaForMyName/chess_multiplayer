import sys

import socket
import threading

from game_server import *
from dataclasses import dataclass
from serialize import *
from lobby_operation import *


@dataclass(frozen=True)
class Socket:
    connection: socket.socket
    info: tuple[str, int]


class ServerLobby:

    def __init__(self, socket_: tuple[str, int]) -> None:
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(socket_)
        self._server_socket.listen()

        self._player_list: list[Socket] = []
        self._game_list: list[SingleGameHandler] = []
        self._players_thread: list[threading.Thread] = []
        self._games_thread: list[threading.Thread] = []
        self._running = True
        self._lock = threading.Lock()

    def listen_for_new_players(self):
        while self._running:
            player_socket = Socket(*self._server_socket.accept())
            self.inform_new_player(player_socket.connection)
            with self._lock:
                # in order not to append players while the list is iterated through
                self._player_list.append(player_socket)
                thread = threading.Thread(target=self.listen_for_player_operations, args=(player_socket,))
                self._players_thread.append(thread)
                thread.start()

    def inform_new_player(self, player: socket.socket):
        player.sendall(send_data(self._game_list))

    def listen_for_player_operations(self, player: Socket):  # including players that disconnects, starting games, joining games etc.
        while self._running:
            msg = receive_data(player.connection.recv(1024))
            if msg:
                operation = LobbyOperation(*msg)
            else:  # if message is None, it is disconnect message
                operation = LobbyOperation(OperationType.Disconnect, None)
            match operation.type:
                case OperationType.StartGame:
                    game_handler = self.start_game(player, *msg)
                    self.broadcast(LobbyOperation(OperationType.StartGame, game_handler), player)
                case OperationType.Disconnect:
                    self.disconnect_player(player)

    def broadcast(self, data, sender: Socket):
        with self._lock:
            for player in self._player_list:
                if player != sender:
                    player.connection.sendall(send_data(data))

    def disconnect_server(self):
        self._running = False
        with self._lock:
            for player in self._player_list:
                player.connection.close()

    def start_game(self, player: Socket, game_name: str, nickname: str, color: Color, game_time: float) -> SingleGameHandler:
        # needed: (ip, port), nickname, serwer_ip, port (127.0.0.1, 12345), color, time
        game_handler = SingleGameHandler(game_name, ('127.0.0.1', 12345), player.info[0], color, game_time)
        self._game_list.append(game_handler)
        thread = threading.Thread(target=game_handler.start)
        self._games_thread.append(thread)
        thread.start()
        player.connection.sendall(send_data(LobbyOperation(OperationType.StartGame, None)))
        return game_handler

    def disconnect_player(self, player):
        with self._lock:
            self._player_list.remove(player)

'''
1. nasłuchiwacz utworzenia nowej gry
2. broadcast do wszystkich klientów gdy zajdzie jakas zmiana
3. cała lista dla nowo połączonego klienta
4. nasłuchiwacz dołączenia do gry
'''
