import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Toolbar.toolbar import Toolbar
    from collections.abc import Callable

class Button:
    def __init__(self, toolbar: "Toolbar", width: int, height: int, pos_x: int, pos_y: int, text: str, event: "Callable[[], None]") -> None:
        self.toolbar = toolbar

        self.button: pygame.Surface | None = None

        self.width: int = width
        self.height: int = height
        self.pos_x: int = pos_x
        self.pos_y: int = pos_y

        self.text = text
        self.event = event

        self.update()

    def update(self):
        assert self.toolbar.toolbar_surface

        self.button = pygame.Surface((self.width, self.height))
        self.button.fill("red")

        font = pygame.font.SysFont("Arial", int(self.height * 0.80)).render(self.text , True, "White")
        center = font.get_rect(center=(self.width / 2, self.height / 2))

        self.button.blit(font, center)
        self.toolbar.toolbar_surface.blit(self.button, (self.pos_x, self.pos_y))

    def collision(self):
        assert self.button

        button_rect = self.button.get_rect(topleft = (self.pos_x, self.pos_y))
        return button_rect.collidepoint(pygame.mouse.get_pos())
    
    def click(self):
        if not self.collision(): return
        self.event()