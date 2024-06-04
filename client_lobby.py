import traceback

import socket
import sys
import logging
import threading

from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import QCoreApplication, QMetaObject, Qt, Q_ARG, pyqtSlot
import os
import datetime as dt

from server_lobby import *
from game_client import *
from networking import *
from move_analyzer import *

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')
ARCHIVE_PATH = '.\\archive'


class LobbyWindow(QMainWindow):
    def __init__(self, server_socket: tuple[str, int]):
        super(LobbyWindow, self).__init__()

        uic.loadUi("lobby.ui", self)
        self.setWindowTitle('Chess Multiplayer Lobby')
        self.show()
        self.setFixedSize(self.size())

        self.join_button.clicked.connect(self.join_button_clicked)
        self.create_button.clicked.connect(self.create_game)
        self.game_list.model().rowsInserted.connect(self.check_game_list_and_nickname)
        self.game_list.model().rowsRemoved.connect(self.check_game_list_and_nickname)
        # self.game_list.itemClicked.connect(self.game_list_clicked)
        self.game_name.textChanged.connect(self.game_name_or_nickname_changed)
        self.nickname.textChanged.connect(self.check_game_list_and_nickname)
        self.nickname.textChanged.connect(self.game_name_or_nickname_changed)
        self.browse_button.clicked.connect(self.choose_file)
        self.accept_button.clicked.connect(self.game_analysis)

        socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.info('Connecting to a lobby server...')
        socket_.connect(server_socket)
        self._server_socket = Socket(socket_, server_socket)
        self._client_connected = True
        logging.info('Connected to lobby server')

        self._my_game_info = None
        self._my_game_client = None
        self._available_port_number = GAME_SERVER_FIRST_PORT

        self._listen_server_thread = threading.Thread(target=self.listen_server_operations)
        self._listen_server_thread.daemon = True
        self._listen_server_thread.start()

    def choose_file(self):
        filename = QFileDialog().getOpenFileName(self, 'Open file')[0]
        self.filepath.setText(filename)

    def game_analysis(self):
        moves = read_data_from_file(self.filepath.text())
        threading.Thread(target=MoveAnalyzer(moves).start_analysis())

    def join_button_clicked(self):
        game_info: GameInfo = self.game_list.currentItem().game_info
        game_info.players_connected += 1
        self.join_game(game_info)

    @pyqtSlot(GameInfo)
    def join_game_in_main_thread(self, game_info: GameInfo):
        self.join_game(game_info)

    def join_game(self, game_info: GameInfo):
        logging.info('Joining new game...')
        self._client_connected = False
        logging.info('Stopped listening to server')

        self.hide()
        logging.info('Hiding window...\nStarting the game client...')

        logging.info('Sending info to server about joining to the game')
        self._server_socket.connection.sendall(send_data(LobbyOperation(OperationType.JoinGame, game_info)))
        logging.info('Info sent; Starting game client...')
        self._my_game_client = GameClient(game_info.server_socket, self.nickname.text())
        self._my_game_client.start_game()
        logging.info('Game has ended')

        logging.info('Saving game to archive...')
        filename = game_info.display_info.replace(';', '_').replace(' ', '')
        filename += self.get_current_timestamp()
        write_data_to_file(self._my_game_client.chess_game.all_move_list, os.path.join(ARCHIVE_PATH, filename))
        logging.info('Moves from game saved')

        self.close()

    def get_current_timestamp(self):
        now = dt.datetime.now()
        timestamp = now.strftime('%Y-%m-%d_%H;%M;%S')
        return timestamp

    def create_game(self):
        logging.info('Creating new game...')
        game_server_port = self._available_port_number
        game_name = self.game_name.text()
        color = Color.White if self.white_radio.isChecked() else Color.Black
        game_time = self.game_time.time().minute() * 60
        args = game_server_port, game_name, self.nickname.text(), color, game_time
        logging.info(f'New game created with args: {args}')
        logging.info('Sending info about new game to server...')
        self._server_socket.connection.sendall(send_data(LobbyOperation(OperationType.StartGame, args)))
        logging.info('Info about new game sent')
        display_info = f'{game_name}; {opposite_color(color).name}; {game_time}'
        self._my_game_info = GameInfo(game_name, (SERVER_IP, game_server_port), 1, display_info)

    def check_game_list_and_nickname(self):
        if self.game_list.count() == 0 or not self.game_list.currentItem() or self.nickname.text() == '':
            self.join_button.setEnabled(False)
        else:
            self.join_button.setEnabled(True)

    def game_name_or_nickname_changed(self):
        if self.game_name.text() == '' or self.nickname.text() == '':
            self.create_button.setEnabled(False)
        else:
            self.create_button.setEnabled(True)

    def listen_server_operations(self):
        while self._client_connected:
            logging.info('Waiting for any server operation...')
            operation = receive_data(self._server_socket.connection.recv(1024))
            logging.info(f'Server operation received: {operation}')
            if not operation:
                operation = LobbyOperation(OperationType.Disconnect, None)
            match operation.type:
                case OperationType.AllGames:
                    logging.info('operation: AllGames; got list of all games available')
                    game_info_list = operation.data
                    for game_info in game_info_list:
                        item = GameInfoItem(game_info=game_info)
                        self.game_list.addItem(item)
                    self._available_port_number = game_info_list[-1].server_socket[1] + 1 if game_info_list else self._available_port_number
                case OperationType.StartGame:
                    logging.info('operation: StartGame')
                    if not operation.data and self._my_game_info:
                        logging.info('My game was created on server; I can join it now...')
                        QMetaObject.invokeMethod(self, "join_game_in_main_thread", Qt.QueuedConnection,
                                                 Q_ARG(GameInfo, self._my_game_info))
                    else:
                        logging.info('New game available on the list; adding...')
                        item = GameInfoItem(game_info=operation.data)
                        self.game_list.addItem(item)
                        self._available_port_number = operation.data.server_socket[1] + 1
                case OperationType.JoinGame:
                    logging.info('operation: JoinGame - if game is full - it is deleted from list')
                    if operation.data.players_connected == 2:
                        self.remove_from_QListWidget(operation.data)
                case OperationType.Disconnect:
                    logging.info('operation: Disconnect; disconnecting from server...')
                    self._server_socket.connection.close()
                    self.close()
                    sys.exit(0)
        self._server_socket.connection.close()

    def remove_from_QListWidget(self, value: GameInfo) -> None:
        for i in range(self.game_list.count()):
            item_: GameInfoItem = self.game_list.item(i)
            if (item_.game_info.name, item_.game_info.server_socket) == (value.name, value.server_socket):
                self.game_list.removeItemWidget(item_)
                break

    def closeEvent(self, event):
        logging.info('Closing lobby client...')
        sys.exit()


class GameInfoItem(QListWidgetItem):
    def __init__(self, game_info: GameInfo, parent=None):
        super().__init__(game_info.display_info, parent)
        self.game_info = game_info


def main():
    app = QApplication(sys.argv)
    window = LobbyWindow(('127.0.0.1', 54321))
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
