import sys
import socket
import threading
import logging

from game_server import *
from dataclasses import dataclass
from serialize import *
from lobby_operation import *
from networking import *

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')


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
        logging.info('listening for new players...')
        self.listen_for_new_players()

    def listen_for_new_players(self):
        while self._running:
            player_socket = Socket(*self._server_socket.accept())
            logging.info('new player found!')
            self.inform_new_player(player_socket.connection)
            with self._lock:
                logging.info('adding new player to the list of players...')
                self._player_list.append(player_socket)
                thread = threading.Thread(target=self.listen_for_player_operations, args=(player_socket,))
                self._players_thread.append(thread)
                logging.info('player added and started constant checking for his operations')
                thread.start()

    def inform_new_player(self, player: socket.socket):
        logging.info('informing player about all available games')
        player.sendall(send_data(LobbyOperation(OperationType.AllGames, self._game_list)))
        logging.info('player informed')

    def listen_for_player_operations(self, player: Socket):
        logging.info('constant checking for player operations...')
        while self._running:
            try:
                operation = receive_data(player.connection.recv(1024))
            except (EOFError, ConnectionResetError):
                operation = None
                logging.info('Disconnect message')
            logging.info('operation found!')
            if not operation:
                operation = LobbyOperation(OperationType.Disconnect, None)
            match operation.type:
                case OperationType.StartGame:
                    logging.info('player wants to start a game')
                    game_info = self.start_game(player, *operation.data)
                    logging.info('broadcasting new game to all players')
                    self.broadcast(LobbyOperation(OperationType.StartGame, game_info), player)
                case OperationType.JoinGame:
                    logging.info('player joined game')
                    if operation.data.players_connected == 2:
                        logging.info('Both players are ready; removing game from list...')
                        self.remove_from_game_list(operation.data)
                        logging.info('informing other players about started game...')
                        self.broadcast(operation, player)
                        logging.info('other players informed')
                case OperationType.Disconnect:
                    logging.info('player wants to disconnect')
                    self.disconnect_player(player)
                    break

    def remove_from_game_list(self, value: GameInfo) -> None:
        for i in range(len(self._game_list)):
            game_info = self._game_list[i]
            if (game_info.name, game_info.server_socket) == (value.name, value.server_socket):
                del self._game_list[i]
                break

    def broadcast(self, data, sender: Socket):
        logging.info('broadcast started...')
        with self._lock:
            for player in self._player_list:
                if player != sender:
                    player.connection.sendall(send_data(data))
        logging.info('broadcast ended')

    def disconnect_server(self):
        self._running = False
        with self._lock:
            for player in self._player_list:
                player.connection.close()

    def start_game(self, player: Socket, server_port, game_name: str, nickname: str, color: Color, game_time: float) -> GameInfo:
        logging.info('starting game for player; creating SingleGameHandler...')
        game_handler = SingleGameHandler(game_name, (SERVER_IP, server_port), player.info[0], color, game_time)
        game_info = GameInfo(game_name, (SERVER_IP, server_port), 1, f'{game_name};{color.name}; {game_time}')
        self._game_list.append(game_info)
        thread = threading.Thread(target=game_handler.start)
        self._games_thread.append(thread)
        logging.info('SingleGameHandler added; starting game handler in separate thread...')
        thread.start()
        logging.info('informing player that his game handler is running')
        player.connection.sendall(send_data(LobbyOperation(OperationType.StartGame, None)))
        logging.info('player informed about his game handler')
        return game_info

    def disconnect_player(self, player):
        with self._lock:
            self._player_list.remove(player)
        player.connection.close()
        logging.info('player disconnected')


def main():
    server_lobby = ServerLobby((SERVER_IP, LOBBY_SERVER_PORT))
    server_lobby.start()


if __name__ == '__main__':
    main()
