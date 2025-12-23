import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import toolbar

class Button:
    def __init__(self, toolbar: "toolbar.Toolbar", width: int, height: int, pos_x: int, pos_y: int, text: str) -> None:
        self.toolbar = toolbar

        self.width: int = width
        self.height: int = height
        self.pos_x: int = pos_x
        self.pos_y: int = pos_y

        self.clicked = False

        self.text = text

    def update(self):
        self.button = pygame.Surface((self.width, self.height))
        self.button.fill("red")

        font = pygame.font.SysFont("Arial", int(self.height * 0.80)).render(self.text , True, "White")
        center = font.get_rect(center=(self.width / 2, self.height / 2))

        self.button.blit(font, center)

        assert self.toolbar.toolbar_surface
        self.toolbar.toolbar_surface.blit(self.button, (self.pos_x, self.pos_y))

    def collision(self):
        button_rect = self.button.get_rect(topleft = (self.pos_x, self.pos_y))
        return button_rect.collidepoint(pygame.mouse.get_pos())
    
    def click(self):
        if not self.collision(): return

        print("click")
        print("")
            