import pygame 
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Toolbar.toolbar import Toolbar
    from collections.abc import Callable

class Input:
    def __init__(self, toolbar: "Toolbar", width: int, height: int, pos_x: int, pos_y: int, event: "Callable[[], None]") -> None:
        self.toolbar = toolbar

        self.input: pygame.Surface | None = None

        self.value = "0"
        self.is_focused = False

        self.width = width
        self.height = height
        self.pos_x = pos_x
        self.pos_y = pos_y

        self.event = event

        self.update()

    def collision(self):
        assert self.input

        input_rect = self.input.get_rect(topleft = (self.pos_x, self.pos_y))
        return input_rect.collidepoint(pygame.mouse.get_pos())
    
    def set_focus(self):
        if self.collision():
            self.is_focused = True
        else:
            self.is_focused = False

    def update(self):
        assert self.toolbar.toolbar_surface

        self.input = pygame.Surface((self.width, self.height))
        self.input.fill("yellow")

        font = pygame.font.SysFont("Arial", int(self.height * 0.80)).render(self.value + "px", True, "Black")
        center = font.get_rect(center=(self.width / 2, self.height / 2))

        self.input.blit(font, (self.width * 0.02, center[1]))
        self.toolbar.toolbar_surface.blit(self.input, (self.pos_x, self.pos_y))
        self.toolbar.update()

    def add_input(self, event):
        if not self.is_focused: return

        if event.unicode.isnumeric() and len(self.value) < 4:
            self.value += event.unicode

        self.update()

    def remove_input(self):
        if not self.is_focused or len(self.value) < 0: return

        self.value = self.value[:-1]
        self.update()

    def get_value(self) -> int:
        return int(self.value)
    
    def set_value(self, value: str):
        if self.value.isnumeric():
            self.value = value
            self.update()