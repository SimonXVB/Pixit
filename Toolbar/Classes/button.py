import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Toolbar.toolbar import Toolbar
    from collections.abc import Callable

class Button:
    def __init__(self, toolbar: "Toolbar", width: int, height: int, pos_x: int, pos_y: int, text: str, event: "Callable[[], None]") -> None:
        self.toolbar = toolbar

        self.button: pygame.Surface = pygame.Surface((width, height), flags=pygame.SRCALPHA)
        self.button.fill((0, 0, 0, 0))

        self.width: int = width
        self.height: int = height
        self.pos_x: int = pos_x
        self.pos_y: int = pos_y
        self.text = text
        self.event = event

        self.is_hovering: bool = False

        self.update()

    def event_poll(self, event):
        if self.collision(): 
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.click()

            if not self.is_hovering:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.is_hovering = True
                self.update()
                self.toolbar.update()
        else: 
            if self.is_hovering:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                self.is_hovering = False
                self.update()
                self.toolbar.update()

    def update(self):
        self.button.fill(self.toolbar.main.colors["secondary"])
        font = pygame.font.SysFont("Arial", int(self.height * 0.80)).render(self.text , True, "white" if not self.is_hovering else "black")
        center = font.get_rect(center=(self.width / 2, self.height / 2))

        if self.is_hovering:
            pygame.draw.rect(self.button, "white", (0, 0, self.button.get_width(), self.button.get_height()), 0, 2)

        self.button.blit(font, center)
        self.toolbar.toolbar_surface.blit(self.button, (self.pos_x, self.pos_y))

    def collision(self):
        button_rect = self.button.get_rect(topleft = (self.pos_x, self.pos_y))
        return button_rect.collidepoint(pygame.mouse.get_pos())
    
    def click(self):
        self.event()