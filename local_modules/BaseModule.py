import time
from pygame.surface import Surface


class BaseModule:

    def __init__(self, screen: Surface):
        self._screen = screen
        self.timer_interval = 1.1
        self.__next_calculation_time = time.time()
        self.time_last_execution = 0
        self.time_last_execution_diff = 0
        self.execution_counter = 0

    def timer(self):
        now = time.time()
        if self.__next_calculation_time <= now:
            self.__next_calculation_time = now + self.timer_interval
            self.time_last_execution_diff = now - self.time_last_execution
            self.time_last_execution = time.time()
            self.execute_timer()

    def frame(self):
        pass

    def calculate(self):
        pass

    def execute_timer(self):
        pass

    def draw(self):
        pass

    def handle_input(self, event):
        pass
