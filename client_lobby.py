import socket
import sys

from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import QCoreApplication, QMetaObject, Qt, Q_ARG, pyqtSlot
import os

from server_lobby import *
from game_client import *
from networking import *


class LobbyWindow(QMainWindow):
    def __init__(self, server_socket: tuple[str, int]):
        super(LobbyWindow, self).__init__()

        uic.loadUi("lobby.ui", self)
        self.setWindowTitle('Chess Multiplayer Lobby')
        self.show()

        self.join_button.clicked.connect(self.join_button_clicked)
        self.create_button.clicked.connect(self.create_game)
        self.game_list.model().rowsInserted.connect(self.check_game_list)
        self.game_list.model().rowsRemoved.connect(self.check_game_list)
        # self.game_list.itemClicked.connect(self.game_list_clicked)
        self.game_name.textChanged.connect(self.game_name_changed)

        socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Connecting to a lobby server...')
        socket_.connect(server_socket)
        self._server_socket = Socket(socket_, server_socket)
        self._client_connected = True
        print('Connected to lobby server')

        self._my_game_info = None
        self._nickname = 'NICKNAME_TODO'  # TODO add field to choose nickname
        self._my_game_client = None  # TODO na probe

        self._listen_server_thread = threading.Thread(target=self.listen_server_operations)
        self._listen_server_thread.start()

    def join_button_clicked(self):
        game_info: GameInfo = self.game_list.currentItem().game_info
        game_info.players_connected += 1
        self.join_game(game_info)

    @pyqtSlot(GameInfo)
    def join_game_in_main_thread(self, game_info: GameInfo):
        self.join_game(game_info)

    def join_game(self, game_info: GameInfo):

        print('Joining new game...')
        self._client_connected = False
        # if threading.current_thread().ident != self._listen_server_thread.ident:
        #     self._listen_server_thread.join()
        # not joining because program will freeze on socket.recv() part
        print('Stopped listening to server')

        #QCoreApplication.quit()
        self.close()
        print('Quit application\nStarting the game client...')

        print('Sending info to server about joining to the game')
        self._server_socket.connection.sendall(send_data(LobbyOperation(OperationType.JoinGame, game_info)))
        print('Info sent; Starting game client...')
        self._my_game_client = GameClient(game_info.server_socket, self._nickname)
        self._my_game_client.start_game()
        sys.exit()

    def create_game(self):
        print('Creating new game...')
        game_server_port = self.game_list.item(self.game_list.count()-1).server_socket[1] + 1 if self.game_list.count() > 0 else GAME_SERVER_FIRST_PORT
        game_name = self.game_name.text()
        color = Color.White if self.white_radio.isChecked() else Color.Black
        game_time = self.game_time.time().minute() * 60
        args = game_server_port, game_name, self._nickname, color, game_time
        print('New game created with args:', args)
        print('Sending info about new game to server...')
        self._server_socket.connection.sendall(send_data(LobbyOperation(OperationType.StartGame, args)))
        print('Info about new game sent')
        self._my_game_info = GameInfo(game_name, (SERVER_IP, game_server_port), 1)

    def check_game_list(self):
        if self.game_list.count() == 0 or not self.game_list.currentItem():
            self.join_button.setEnabled(False)
        self.join_button.setEnabled(True)

    def game_name_changed(self):
        if self.game_name.text() == '':
            self.create_button.setEnabled(False)
        else:
            self.create_button.setEnabled(True)

    def listen_server_operations(self):
        while self._client_connected:
            print('Waiting for any server operation...')
            operation = receive_data(self._server_socket.connection.recv(1024))
            print('Server operation received:', operation)
            if not operation:  # if message is None, it is disconnect message
                operation = LobbyOperation(OperationType.Disconnect, None)
            match operation.type:
                case OperationType.AllGames:
                    print('operation: AllGames; got list of all games available')
                    game_info_list = operation.data
                    for game_info in game_info_list:
                        item = GameInfoItem(game_info=game_info)
                        self.game_list.addItem(item)
                case OperationType.StartGame:
                    print('operation: StartGame')
                    if not operation.data and self._my_game_info:  # my game was created, now I can join
                        print('My game was created on server; I can join it now...')
                        #self.join_game(self._my_game_info)
                        QMetaObject.invokeMethod(self, "join_game_in_main_thread", Qt.QueuedConnection,
                                                 Q_ARG(GameInfo, self._my_game_info))
                    else:
                        print('New game available on the list; adding...')
                        item = GameInfoItem(game_info=operation.data)
                        self.game_list.addItem(item)
                case OperationType.JoinGame:
                    print('operation: JoinGame - if game is full - it is deleted from list')
                    if operation.data.players_connected == 2:
                        self.remove_from_QListWidget(operation.data)
                case OperationType.Disconnect:
                    print('operation: Disconnect; disconnecting from server...')
                    self._server_socket.connection.close()
                    #QCoreApplication.quit()
                    self.close()
                    sys.exit(0)
        self._server_socket.connection.close()

    def remove_from_QListWidget(self, value: GameInfo) -> None:
        for i in range(self.game_list.count()):
            item_: GameInfoItem = self.game_list.item(i)
            if (item_.game_info.name, item_.game_info.server_socket) == (value.name, value.server_socket):
                self.game_list.removeItemWidget(item_)
                break


class GameInfoItem(QListWidgetItem):
    def __init__(self, game_info: GameInfo, parent=None):
        super().__init__(game_info.name, parent)
        self.game_info = game_info


def main():

    app = QApplication(sys.argv)
    window = LobbyWindow(('127.0.0.1', 54321))
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
