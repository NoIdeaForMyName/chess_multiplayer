import sys

import socket
import threading

from game_server import *
from dataclasses import dataclass
from serialize import *
from lobby_operation import *
from networking import *


class ServerLobby:

    def __init__(self, socket_: tuple[str, int]) -> None:
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(socket_)
        self._server_socket.listen()

        self._player_list: list[Socket] = []
        self._game_list: list[GameInfo] = []
        self._players_thread: list[threading.Thread] = []
        self._games_thread: list[threading.Thread] = []
        self._running = True
        self._lock = threading.Lock()

    def start(self):
        print('listening for new players...')
        self.listen_for_new_players()

    def listen_for_new_players(self):
        while self._running:
            player_socket = Socket(*self._server_socket.accept())
            print('new player found!')
            self.inform_new_player(player_socket.connection)
            with self._lock:
                # in order not to append players while the list is iterated through
                print('adding new player to the list of players...')
                self._player_list.append(player_socket)
                thread = threading.Thread(target=self.listen_for_player_operations, args=(player_socket,))
                self._players_thread.append(thread)
                print('player added and started constant checking for his operations')
                thread.start()

    def inform_new_player(self, player: socket.socket):
        print('informing player about all available games')
        player.sendall(send_data(LobbyOperation(OperationType.AllGames, self._game_list)))
        print('player informed')

    def listen_for_player_operations(self, player: Socket):  # including players that disconnects, starting games, joining games etc.
        print('constant checking for player operations...')
        while self._running:
            try:
                operation = receive_data(player.connection.recv(1024))
            except EOFError:
                operation = None
                print('Disconnect message')
            print('operation found!')
            if not operation:  # if message is None, it is disconnect message
                operation = LobbyOperation(OperationType.Disconnect, None)
            match operation.type:
                case OperationType.StartGame:
                    print('player wants to start a game')
                    game_info = self.start_game(player, *operation.data)
                    print('broadcasting new game to all players')
                    self.broadcast(LobbyOperation(OperationType.StartGame, game_info), player)
                case OperationType.JoinGame:
                    print('player joined game')
                    if operation.data.players_connected == 2:
                        print('Both players are ready; removing game from list...')
                        print('LIST:', self._game_list)
                        print('OPERATION DATA TO REMOVE:', operation.data)
                        self.remove_from_game_list(operation.data)
                        print('informing other players about started game...')
                        self.broadcast(operation, player)
                        print('other players informed')
                case OperationType.Disconnect:
                    print('player wants to disconnect')
                    self.disconnect_player(player)
                    break

    def remove_from_game_list(self, value: GameInfo) -> None:
        for i in range(len(self._game_list)):
            game_info = self._game_list[i]
            if (game_info.name, game_info.server_socket) == (value.name, value.server_socket):
                del self._game_list[i]
                break


    def broadcast(self, data, sender: Socket):
        print('broadcast started...')
        with self._lock:
            for player in self._player_list:
                if player != sender:
                    player.connection.sendall(send_data(data))
        print('broadcast ended')

    def disconnect_server(self):
        self._running = False
        with self._lock:
            for player in self._player_list:
                player.connection.close()

    def start_game(self, player: Socket, server_port, game_name: str, nickname: str, color: Color, game_time: float) -> GameInfo:
        # needed: (ip, port), nickname, serwer_ip, port (127.0.0.1, 12345), color, time
        print('starting game for player; creating SingleGameHandler...')
        game_handler = SingleGameHandler(game_name, (SERVER_IP, server_port), player.info[0], color, game_time)
        game_info = GameInfo(game_name, (SERVER_IP, server_port), 1)
        self._game_list.append(game_info)
        thread = threading.Thread(target=game_handler.start)
        self._games_thread.append(thread)
        print('SingleGameHandler added; starting game handler in separate thread...')
        thread.start()
        print('informing player that his game handler is running')
        # TODO tu powinna byc jakas przerwa zeby gracz nie probowal od razu sie laczyc bo serwer
        # moze jeszcze nie dzialac (no chyba ze moze tak byc ze bedzie sie laczyl zanim serwer sie uruchomi
        # i jak sie uruchomi to go polaczy, wtedy to git
        player.connection.sendall(send_data(LobbyOperation(OperationType.StartGame, None)))
        print('player informed about his game handler')
        return game_info

    def disconnect_player(self, player):
        with self._lock:
            self._player_list.remove(player)
        player.connection.close()
        print('player disconnected')


def main():
    server_lobby = ServerLobby((SERVER_IP, LOBBY_SERVER_PORT))
    server_lobby.start()


if __name__ == '__main__':
    main()


'''
1. nasłuchiwacz utworzenia nowej gry
2. broadcast do wszystkich klientów gdy zajdzie jakas zmiana
3. cała lista dla nowo połączonego klienta
4. nasłuchiwacz dołączenia do gry
'''
