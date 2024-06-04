import socket
import threading
import logging
from time import sleep

from game import *
from serialize import *
from server_network_constants import *

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')


class GameClient:
    def __init__(self, server_socket: tuple[str, int], nickname: str) -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket = server_socket
        self._nickname: str = nickname

        self._chess_game: Game | None = None

    @property
    def chess_game(self):
        return self._chess_game

    def connect(self):
        logging.info('Connecting to server...')
        self._socket.connect(self._server_socket)
        logging.info('Connected to server!')

    def send_nickname(self):
        logging.info('Sending nickname to server...')
        self._socket.sendall(self._nickname.encode())
        logging.info('Nickname sent!')

    def start_client(self, my_turn: bool) -> None:
        logging.info('START CLIENT METHOD and wait 0.01 sec')
        sleep(0.01)

        game_lasts = True
        last_move = None
        while game_lasts:
            if not my_turn:
                logging.info('Waiting for opponent to move...')
                operation = receive_data(self._socket.recv(1024))
                if operation.get('winner', None):
                    self._chess_game.forced_game_ending(operation['winner'])
                    break
                elif operation.get('disconnected', None):
                    self._chess_game.forced_game_ending(self._nickname)
                    break
                else:
                    move = operation['move']
                logging.info(f'Opponent moved: {move}')
                moves_length = len(self._chess_game.all_move_list)
                self._chess_game.another_player_move = move
                self.wait_until_move_performed(moves_length, self._chess_game.all_move_list)
                last_move = move
                my_turn = not my_turn
            elif self._chess_game.all_move_list and self._chess_game.all_move_list[-1] != last_move:
                logging.info('Self move detected. Sending to server...')
                logging.info(f'ALL MOVE LIST: {self._chess_game.all_move_list}')
                logging.info(f'LAST MOVE: {last_move}')
                last_move = self._chess_game.all_move_list[-1]
                data = {'move': last_move}
                self._socket.sendall(send_data(data))
                logging.info(f'Self move sent to: {self._server_socket}')
                my_turn = not my_turn
            game_lasts = self._chess_game.game_state == GameState.InProgress
        self._socket.sendall(send_data({'winner': self._chess_game.winner}))
        logging.info(f'Game ended!\nPlayer: {self._chess_game.winner} won!')

    def wait_until_move_performed(self, length, list):
        while length == len(list):
            sleep(0.001) # used because did not want to implement synchronous programming
            # in game.py - I wanted it to stay 'single-threaded', so didn't use semaphore

    def start_game(self):
        logging.info(f'START GAME METHOD; THREAD: {threading.current_thread().name}')

        self.connect()
        self.send_nickname()

        logging.info('Waiting for the game args from server...')
        args = receive_data(self._socket.recv(1024))
        logging.info(f'Received game args from server: {args}')

        self._chess_game = Game(*tuple(args.values()))

        logging.info('Starting the game...')
        my_turn = args['player_color'] == Color.White
        client_thread = threading.Thread(target=self.start_client, args=(my_turn,))
        client_thread.daemon = True

        client_thread.start()
        self._chess_game.start()

        while not self._chess_game.winner:
            sleep(1)


def main():
    game = GameClient((SERVER_IP, GAME_SERVER_FIRST_PORT), 'Mic')
    game.start_game()


if __name__ == '__main__':
    main()
