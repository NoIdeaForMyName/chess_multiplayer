import sys

from PyQt5.QtWidgets import *
from PyQt5 import uic
import os


class LobbyWindow(QMainWindow):
    def __init__(self):
        super(LobbyWindow, self).__init__()

        uic.loadUi("lobby.ui", self)
        self.setWindowTitle('Chess Multiplayer Lobby')
        self.show()


def main():
    app = QApplication(sys.argv)
    window = LobbyWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
