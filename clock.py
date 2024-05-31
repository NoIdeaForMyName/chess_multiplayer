from time import time


class ChessClock:
    def __init__(self, max_time: float) -> None:
        self._max_time: float = max_time
        self._time_rest: float = max_time
        self._time_passed: bool = False
        self._current_time: float = time()

    def start_timer(self):
        self._current_time = time()

    def refresh_time(self):
        diff = time()-self._current_time
        self._current_time = time()
        self._time_rest -= diff
        if self._time_rest <= 0:
            self._time_passed = True

    @property
    def time_passed(self):
        return self._time_passed

    @property
    def time_rest(self):
        return self._time_rest

    def time_rest_str(self) -> str:
        total_seconds = int(self.time_rest)
        minutes = total_seconds // 60
        remaining_seconds = total_seconds % 60
        return f"{minutes:02}:{remaining_seconds:02}"
