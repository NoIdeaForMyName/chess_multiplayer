import sys
import socket
import threading
import logging
from threading import Lock
from time import sleep

from game import *
from serialize import *
from server_network_constants import *

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')


class SingleGameHandler:

    def __init__(self, game_name: str, socket_: tuple[str, int], first_connection_ip: str, first_player_color: Color, game_time: float):

        logging.info('SingleGameHandler created with socket: %s', socket_)
        self._game_name = game_name
        self._socket = socket_
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(socket_)
        self._server_socket.listen()

        self._first_connection_ip: str = first_connection_ip
        self._player1_socket = None
        self._player2_socket = None
        self._player1_ip = None
        self._player2_ip = None
        self._player1_port = None
        self._player2_port = None

        self._first_player_color = first_player_color
        self._game_time = game_time
        self._player_nicknames: list[str] = ['', '']

        self._game_lasts = False

        self.lock = Lock()

    @property
    def game_name(self):
        return self._game_name

    @property
    def socket(self):
        return self._socket

    @property
    def game_lasts(self):
        return self._game_lasts

    def __str__(self):
        return self.game_name

    def send_game_initial_params(self) -> None:
        self.wait_for_players()
        white_nick = self._player_nicknames[0] if self._first_player_color == Color.White else self._player_nicknames[1]
        black_nick = self._player_nicknames[1] if white_nick != self._player_nicknames[1] else self._player_nicknames[0]
        data = {
            'player_color': self._first_player_color,
            'w_nick': white_nick,
            'b_nick': black_nick,
            'time': self._game_time
        }
        logging.info('sending initial game info to both players...')
        self._player1_socket.sendall(send_data(data))
        data['player_color'] = Color.Black if self._first_player_color == Color.White else Color.White
        self._player2_socket.sendall(send_data(data))

    def start(self) -> None:
        self.send_game_initial_params()
        self._game_lasts = True
        self.set_timer(self._game_time)
        thread = threading.Thread(target=self.run_game)
        thread.start()
        self._game_lasts = False

    def set_timer(self, duration):
        timer = threading.Timer(duration, lambda: sys.exit())
        timer.start()

    def run_game(self) -> None:
        white_socket = self._player1_socket if self._first_player_color == Color.White else self._player2_socket
        black_socket = self._player2_socket if white_socket == self._player1_socket else self._player1_socket

        sending_socket: socket.socket = white_socket
        receiving_socket: socket.socket = black_socket

        logging.info('starting the game...')
        logging.info('CURRENT THREAD: %s', threading.current_thread().name)
        winner = None
        while not winner:
            logging.info('waiting for player move...')
            try:
                raw_data = sending_socket.recv(1024)
                message = receive_data(raw_data)
            except ConnectionResetError:
                message = {'disconnected': True}
                raw_data = send_data(message)

            try:
                logging.info('player move received: %s', message)
                if message.get('move', None):
                    receiving_socket.sendall(raw_data)
                    logging.info('performed move sent to another player')
                elif message.get('winner', None):
                    winner = message['winner']
                    receiving_socket.sendall(send_data(message))
            except ConnectionResetError:
                message = {'disconnected': True}
                sending_socket.sendall(send_data(message))
                break

            logging.info('next player turn...')
            temp = sending_socket
            sending_socket = receiving_socket
            receiving_socket = temp

        logging.info('game ended, winner: %s', winner)

    def wait_for_players(self) -> None:
        logging.info('waiting for first player to join...')
        while not self.verify_first_connection():
            logging.info('WHILE LOOP waiting for player...')
            self._player1_socket, (self._player1_ip, self._player1_port) = self._server_socket.accept()
            logging.info('WHILE LOOP player joined!: %s', self._player1_ip, self._first_connection_ip)
        logging.info('first player joined!')
        logging.info('getting first player nickname...')
        t1 = threading.Thread(target=self.get_player_nickname, args=(self._player1_socket, 0,))
        t1.start()
        logging.info('waiting for second player to join...')
        self._player2_socket, (self._player2_ip, self._player2_port) = self._server_socket.accept()
        logging.info('getting second player nickname...')
        t2 = threading.Thread(target=self.get_player_nickname, args=(self._player2_socket, 1,))
        t2.start()
        t1.join()
        logging.info('first player nickname received: %s', self._player_nicknames[0])
        t2.join()
        logging.info('second player nickname received: %s', self._player_nicknames[1])

    def get_player_nickname(self, player_socket, player_nb) -> None:
        data = player_socket.recv(1024)
        self.lock.acquire()
        self._player_nicknames[player_nb] = data.decode()
        self.lock.release()

    def verify_first_connection(self):
        return self._player1_ip == self._first_connection_ip


def main():
    server = SingleGameHandler('test_game', (SERVER_IP, GAME_SERVER_FIRST_PORT), '127.0.0.1', Color.Black, 300)
    t = threading.Thread(target=server.start)
    t.start()
    t.join()


if __name__ == '__main__':
    main()
