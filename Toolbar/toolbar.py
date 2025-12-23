import pygame
from typing import TYPE_CHECKING
from Toolbar.Classes.button import Button

if TYPE_CHECKING:
    import main

class Toolbar:
    def __init__(self, main: "main.Main") -> None:
        self.main = main
        
        self.toolbar_surface: pygame.Surface | None = None

        self.button = Button(self, 200, 50, 20, 30, "Hello")

        self.init()

    def init(self):
        self.toolbar_surface = pygame.Surface((self.main.window.get_width(), 100))
        self.toolbar_surface.fill("blue")

        self.button.update()

        self.main.window.blit(self.toolbar_surface, (0, 0))

    def event_poll(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.button.click()