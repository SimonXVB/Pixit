import pygame 
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Toolbar.toolbar import Toolbar
    from collections.abc import Callable

class Input:
    def __init__(self, toolbar: "Toolbar", width: int, height: int, pos_x: int, pos_y: int, label_text: str) -> None:
        self.toolbar = toolbar

        self.input = pygame.Surface((width, height))
        self.field = pygame.Surface((width * 0.8, height))

        self.label = pygame.Surface((width * 0.2, height))
        self.label.fill(self.toolbar.main.colors["secondary"])
        self.input.blit(self.label, (width * 0.8, 0))

        text = pygame.font.SysFont("Arial", int(height * 0.7)).render(label_text, True, "white")
        label_center = text.get_rect(center=(self.label.get_width() / 2, self.label.get_height() / 2))
        self.label.blit(text, label_center)
        self.input.blit(self.label, (width * 0.8, 0))

        self.width = width
        self.height = height
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.label_text = label_text

        self.value: str = "0"
        self.prev_value: str = "0"

        self.is_focused: bool = False
        self.is_hovering: bool = False

        self.update()

    def event_poll(self, event):
        if self.collision(): 
            if not self.is_hovering:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
                self.is_hovering = True
        else: 
            if self.is_hovering:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                self.is_hovering = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.set_focus()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.remove_input()
            else:
                self.add_input(event)

    def update(self):
        self.field.fill(self.toolbar.main.colors["secondary"])

        value = pygame.font.SysFont("Arial", int(self.height * 0.7)).render(self.value, True, "white")
        self.field.blit(value, (self.field.get_width() * 0.04, self.height * 0.1))

        px = pygame.font.SysFont("Arial", int(self.height * 0.7)).render("px", True, "white")
        self.field.blit(px, (self.field.get_width() - 30, self.height * 0.1))

        if self.is_focused:
            cursor = pygame.Surface((2, int(self.height * 0.80)))
            cursor.fill("white")
            self.field.blit(cursor, (value.get_width() + 5, 3))

        pygame.draw.line(self.field, "white", (self.field.get_width() - 2, 0), (self.field.get_width() - 2, self.height), 2)
        self.input.blit(self.field, (0, 0))
        pygame.draw.rect(self.input, "white", (0, 0, self.input.get_width(), self.height), 2, 2)

        self.toolbar.toolbar_surface.blit(self.input, (self.pos_x, self.pos_y))

    def collision(self):
        input_rect = self.input.get_rect(topleft = (self.pos_x, self.pos_y))
        return input_rect.collidepoint(pygame.mouse.get_pos())
    
    def set_focus(self):
        if self.collision():
            self.is_focused = True
            self.update()
            self.toolbar.update()
        else:
            self.is_focused = False

            if self.value == "":
                self.value = self.prev_value
            
            self.update()
            self.toolbar.update()

    def add_input(self, event):
        if not self.is_focused: return

        if event.unicode.isnumeric() and len(self.value) < 3:
            self.value += event.unicode
            self.update()
            self.toolbar.update()

    def remove_input(self):
        if not self.is_focused or len(self.value) < 0: return

        self.prev_value = self.value
        self.value = self.value[:-1]

        self.update()
        self.toolbar.update()

    def set_value(self, value: int):
        if self.value.isnumeric():
            self.value = str(value)
            
            self.update()
            self.toolbar.update()

    def get_value(self) -> int:
        if self.value == "":
            self.value = self.prev_value

        return int(self.value)