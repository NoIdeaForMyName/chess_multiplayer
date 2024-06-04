import threading

import pygame

from game import *
import time


WAITING_TIME = 2
DUMMY_CLICK = (0, 0), (0, 0)


class MoveAnalyzer:

    def __init__(self, moves):
        self.moves = moves
        self.chess_game = Game(Color.White, 'Me', 'Opponent', 3599)
        self.analysis_thread = None

    def start_analysis(self):
        self.analysis_thread = threading.Thread(target=self.analysis)
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
        self.chess_game.start()
        pygame.quit()

    def analysis(self):
        my_turn = True
        cell_size = Game.CELL_SIZE
        for old, new in self.moves:
            time.sleep(WAITING_TIME)
            if my_turn:
                self.simulate_click(old, new)
            else:
                self.chess_game.another_player_move = [old, new]
                time.sleep(0.001)
                self.simulate_click(*DUMMY_CLICK)  # for refreshing purposes
            my_turn = not my_turn

    def simulate_click(self, old, new):
        old_i = old[1] * Game.CELL_SIZE + Game.CELL_SIZE // 2
        old_j = old[0] * Game.CELL_SIZE + Game.CELL_SIZE // 2 + Game.TIMER_HEIGHT
        new_i = new[1] * Game.CELL_SIZE + Game.CELL_SIZE // 2
        new_j = new[0] * Game.CELL_SIZE + Game.CELL_SIZE // 2 + Game.TIMER_HEIGHT
        mouse_down_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (old_i, old_j), 'button': 1})
        mouse_up_event = pygame.event.Event(pygame.MOUSEBUTTONUP, {'pos': (new_i, new_j), 'button': 1})
        pygame.event.post(mouse_down_event)
        pygame.event.post(mouse_up_event)


def main():
    move_list = [[[6, 2], [5, 2]], [[1, 3], [2, 3]], [[6, 1], [4, 1]], [[0, 4], [4, 0]]]
    analyzer = MoveAnalyzer(move_list)
    analyzer.start_analysis()


if __name__ == '__main__':
    main()
