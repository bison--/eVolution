import pygame
from pygame.surface import Surface
from local_modules import BaseModule


class BindText(BaseModule.BaseModule):

    def __init__(self, screen: Surface):
        super().__init__(screen)
        #self.timer_interval = 0.1
        self.primary_color = (20, 7, 61)
        self.position = (0, 400)
        self.font_size = 50
        self.color = (245, 101, 44)  # orange
        self.position = (0, 10)
        self.font = None  # type: pygame.font or None

        self._bind_object = None
        self._bind_value_name = None
        self._bind_value_function = False
        self._text = "-"

        self.calculate()

    def bind_object(self, _object, _value_name, _is_function):
        self._bind_object = _object
        self._bind_value_name = _value_name
        self._bind_value_function = _is_function
        self.calculate()
        self.execute_timer()

    def calculate(self):
        self.font = pygame.font.SysFont("MS Comic Sans,Comic Neue", self.font_size)

    def execute_timer(self):
        if self._bind_value_function:
            self._text = str(getattr(self._bind_object, self._bind_value_name)())
        else:
            self._text = str(getattr(self._bind_object, self._bind_value_name))

    def draw(self):
        self._screen.blit(
            self.font.render(self._text, True, self.color),
            self.position
        )