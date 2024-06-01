import socket
import threading
from time import sleep

from game import *
from serialize import *


class GameClient:

    def __init__(self, server_socket: tuple[str, int], nickname: str) -> None:
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket = server_socket
        self._nickname: str = nickname
        #self._chess_game = None

    def connect(self):
        print('Connecting to server...')
        self._socket.connect(self._server_socket)
        print('Connected to server!')

    def send_nickname(self):
        print('Sending nickname to server...')
        self._socket.sendall(self._nickname.encode())
        print('Nickname sent!')

    def start_client(self, chess_game: Game, my_turn: bool) -> None:
        print('START CLIENT METHOD and wait 0.01 sec')
        sleep(0.01)

        game_lasts = True
        last_move = None
        while game_lasts:
            #print('client_loop')
            if not my_turn:
                print('Waiting for opponent to move...')
                move = receive_data(self._socket.recv(1024))['move']
                print('Opponent moved:', move)
                moves_length = len(chess_game.all_move_list)
                chess_game.another_player_move = move
                # TODO somethin like java's wait (notify would be appending move to list in game's all_move_list)
                self.wait_until_move_performed(moves_length, chess_game.all_move_list)
                last_move = move
                my_turn = not my_turn
            elif chess_game.all_move_list != [] and chess_game.all_move_list[len(chess_game.all_move_list)-1] != last_move:
                # new move made
                print('Self move detected. Sending to server...')
                print('ALL MOVE LIST:', chess_game.all_move_list)
                print('LAST MOVE:', last_move)
                last_move = chess_game.all_move_list[len(chess_game.all_move_list)-1]
                data = {'move': last_move}
                self._socket.sendall(send_data(data))
                print('Self move sent!')
                my_turn = not my_turn
            game_lasts = chess_game.game_state == GameState.InProgress
        print('Game ended!\nPlayer:', chess_game.winner, 'won!')

    def wait_until_move_performed(self, length, list):  # TODO i know it looks bad...
        while length == len(list):
            pass

    def start_game(self):
        print('START GAME METHOD; THREAD:', threading.current_thread().name)

        self.connect()
        self.send_nickname()

        print('Waiting for the game args from server...')
        args = receive_data(self._socket.recv(1024))
        print('Received game args from server:', args)

        # chess_game = Game(**args) For some reason it didn't work
        chess_game = Game(*tuple(args.values()))

        print('Starting the game...')
        my_turn = args['player_color'] == Color.White
        client_thread = threading.Thread(target=self.start_client, args=(chess_game, my_turn,))

        client_thread.start()
        chess_game.start()

        client_thread.join()


def main():
    game = GameClient(('127.0.0.1', 12345), 'Mic')
    game.start_game()


if __name__ == '__main__':
    main()

'''
plan:
1. wyslij nickname (to jako jedyne nie w formacie json - potem wszystko jaki json)
2. odbierz parametry gry i rozpocznij gre
3. gracz po wykonaniu ruchu wysyla ten ruch do serwera (wlacznie z nickiem zwyciezcy na koniec)
'''