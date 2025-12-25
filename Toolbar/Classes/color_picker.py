import pygame 
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Toolbar.toolbar import Toolbar
    from collections.abc import Callable

class ColorPicker:
    def __init__(self, toolbar: "Toolbar", width: int, height: int, pos_x: int, pos_y: int, event: "Callable[[], None]") -> None:
        self.toolbar = toolbar

        self.color_picker: pygame.Surface | None = None

        self.width = width
        self.height = height
        self.pos_x = pos_x
        self.pos_y = pos_y

        self.event = event

        self.is_moving = False

        self.gradient_width = int(width * 0.9)
        self.gradient_height = int(height * 0.4)

        self.gradient = pygame.Surface((self.gradient_width, self.gradient_height))

        for i in range(self.gradient_width):
            color = pygame.Color(0)
            color.hsla = (int(360 * i / self.gradient_width), 100, 50, 100)
            pygame.draw.rect(self.gradient, color, (i, 0, 1, self.gradient_height))

        self.update()

    def update(self, thumb_value: float = 0):
        assert self.toolbar.toolbar_surface

        self.color_picker = pygame.Surface((self.width, self.height))

        self.gradient_container = pygame.Surface((self.gradient_width, self.height * 0.7))
        gradient_container_center = self.gradient_container.get_rect(center=(self.width / 2, self.height / 2))
        self.gradient_container.fill("red")

        lower_limit = ((self.gradient_container.get_width() * 0.05) / 2) / self.gradient_container.get_width()
        upper_limit = 1 - (((self.gradient_container.get_width() * 0.05) / 2) / self.gradient_container.get_width())
        
        if thumb_value >= upper_limit: thumb_value = upper_limit
        if thumb_value <= lower_limit: thumb_value = lower_limit

        self.thumb = pygame.Surface((self.gradient_container.get_width() * 0.05, self.gradient_container.get_height()))
        self.thumb.fill("green")
        thumb_position = self.thumb.get_rect(center=(self.gradient_container.get_width() * thumb_value, self.gradient_container.get_height() / 2))

        gradient_center = self.gradient.get_rect(center=(self.gradient_container.get_width() / 2, self.gradient_container.get_height() / 2))

        self.gradient_container.blit(self.gradient, gradient_center)
        self.gradient_container.blit(self.thumb, thumb_position)

        self.color_picker.blit(self.gradient_container, gradient_container_center)
        self.toolbar.toolbar_surface.blit(self.color_picker, (self.pos_x, self.pos_y))

    def track_collision(self):
        assert self.gradient_container

        track_rect = self.gradient_container.get_rect(topleft = (self.pos_x, self.pos_y))
        return track_rect.collidepoint(pygame.mouse.get_pos())
    
    def begin_move(self):
        if self.track_collision() and not self.is_moving:
            self.is_moving = True

    def end_move(self):
        self.is_moving = False

    def set_value(self):
        assert self.color_picker
        assert self.gradient_container

        if not self.is_moving: return

        track_left_pos = self.pos_x + ((self.color_picker.get_width() - self.gradient_container.get_width()) / 2)
        track_right_pos = track_left_pos + self.gradient_container.get_width()

        value = (pygame.mouse.get_pos()[0] - track_left_pos) / (track_right_pos - track_left_pos)

        self.update(value)
        self.toolbar.update()