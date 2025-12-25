import pygame
from typing import TYPE_CHECKING
from Toolbar.Classes.button import Button
from Toolbar.Classes.slider import Slider
from Toolbar.Classes.input import Input

if TYPE_CHECKING:
    import main

class Toolbar:
    def __init__(self, main: "main.Main") -> None:
        self.main = main
        
        self.toolbar_surface: pygame.Surface | None = pygame.Surface((self.main.window.get_width(), 100))
        self.toolbar_surface.fill("blue")

        self.buttons = {
            "button": Button(self, 200, 50, 20, 30, "Hello", lambda: print("button test")),
            "button1": Button(self, 200, 50, 300, 30, "Bye", lambda: print("button test1"))
        }

        self.slider = Slider(self, 400, 30, 600, 25, lambda: print("slider test"))
        self.input = Input(self, 300, 70, 1050, 10, lambda: print("input1 test"))

        self.update()

    def update(self):
        assert self.toolbar_surface
        self.main.window.blit(self.toolbar_surface, (0, 0))

    def event_poll(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for element in self.buttons.values():
                    element.click()

                self.slider.begin_move()
                self.input.set_focus()
            elif event.type == pygame.MOUSEMOTION:
                self.slider.set_value()
            elif event.type == pygame.MOUSEBUTTONUP:
                self.slider.end_move()
            elif event.type == pygame.KEYDOWN:
                self.input.add_input(event)

                if event.key == pygame.K_BACKSPACE:
                    self.input.remove_input()