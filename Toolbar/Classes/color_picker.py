import pygame 
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Toolbar.toolbar import Toolbar
    from collections.abc import Callable

class ColorPicker:
    def __init__(self, toolbar: "Toolbar", width: int, height: int, pos_x: int, pos_y: int, event: "Callable[[], None]") -> None:
        self.toolbar = toolbar


        self.width = width
        self.height = height
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.event = event

        self.value: float = 0
        self.color: "pygame.Color" = pygame.Color(255, 255, 255, 255)
        self.is_moving: bool = False

        self.color_picker: pygame.Surface = pygame.Surface((self.width, self.height))

        self.gradient_container = pygame.Surface((self.width * 0.95, self.height * 0.7))
        self.thumb_width = self.gradient_container.get_width() * 0.05

        self.gradient_width = int(self.gradient_container.get_width() - self.thumb_width)
        self.gradient_height = int(self.height * 0.4)

        self.gradient = pygame.Surface((self.gradient_width, self.gradient_height))

        for i in range(self.gradient_width):
            color = pygame.Color(0)
            color.hsla = (int(360 * i / self.gradient_width), 100, 50, 100)
            pygame.draw.rect(self.gradient, color, (i, 0, 1, self.gradient_height))

        self.update()

    def update(self):
        assert self.toolbar.toolbar_surface

        gradient_container_center = self.gradient_container.get_rect(center=(self.width / 2, self.height / 2))
        self.gradient_container.fill("black")

        lower_limit = ((self.gradient_container.get_width() * 0.05) / 2) / self.gradient_container.get_width()
        upper_limit = 1 - (((self.gradient_container.get_width() * 0.05) / 2) / self.gradient_container.get_width())

        position = self.value
        
        if position >= upper_limit: position = upper_limit
        if position <= lower_limit: position = lower_limit

        thumb = pygame.Surface((self.gradient_container.get_width() * 0.05, self.gradient_container.get_height()))
        thumb_position = thumb.get_rect(center=(self.gradient_container.get_width() * position, self.gradient_container.get_height() / 2))
        thumb.fill(self.color)

        gradient_center = self.gradient.get_rect(center=(self.gradient_container.get_width() / 2, self.gradient_container.get_height() / 2))

        self.gradient_container.blit(self.gradient, gradient_center)
        self.gradient_container.blit(thumb, thumb_position)

        self.color_picker.blit(self.gradient_container, gradient_container_center)
        self.toolbar.toolbar_surface.blit(self.color_picker, (self.pos_x, self.pos_y))

    def set_value(self):
        assert self.color_picker
        assert self.gradient_container

        if not self.is_moving: return

        left_pos = (self.pos_x + ((self.color_picker.get_width() - self.gradient_container.get_width()) / 2)) + (self.thumb_width / 2)
        right_pos = (left_pos + self.gradient_container.get_width()) - (self.thumb_width / 2)

        value = (pygame.mouse.get_pos()[0] - left_pos) / (right_pos - left_pos)

        if value < 0: value = 0
        if value > 1: value = 1

        self.value = value
        
        range = int((right_pos - left_pos) * value)
        if range >= self.gradient.get_width(): range = self.gradient.get_width() - 1
        if range < 0: range = 0

        self.color = self.gradient.get_at((range, int(self.gradient.get_height() / 2)))
        
        self.event()
        self.update()
        self.toolbar.update()

    def track_collision(self):
        assert self.gradient_container

        track_rect = self.gradient_container.get_rect(topleft = (self.pos_x, self.pos_y))
        return track_rect.collidepoint(pygame.mouse.get_pos())
    
    def begin_move(self):
        if self.track_collision() and not self.is_moving:
            self.is_moving = True

    def end_move(self):
        self.is_moving = False

    def get_color(self) -> "pygame.Color":
        return self.color