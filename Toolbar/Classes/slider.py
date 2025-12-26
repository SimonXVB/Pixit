import pygame 
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Toolbar.toolbar import Toolbar
    from collections.abc import Callable

class Slider:
    def __init__(self, toolbar: "Toolbar", width: int, height: int, pos_x: int, pos_y: int, event: "Callable[[], None]") -> None:
        self.toolbar = toolbar

        self.width = width
        self.height = height
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.event = event

        self.value: float = 0
        self.is_moving: bool = False

        self.slider: pygame.Surface = pygame.Surface((self.width, self.height))
        self.slider.fill("green")

        self.track_container: pygame.Surface = pygame.Surface((self.width * 0.95, self.height * 0.7))
        self.thumb_width = self.track_container.get_width() * 0.05

        self.update()

    def update(self):
        assert self.toolbar.toolbar_surface

        track_container_center = self.track_container.get_rect(center=(self.width / 2, self.height / 2))
        self.track_container.fill("green")

        position = self.value
        lower_limit = (self.thumb_width / 2) / self.track_container.get_width()
        upper_limit = 1 - ((self.thumb_width / 2) / self.track_container.get_width())

        if position >= upper_limit: position = upper_limit
        if position <= lower_limit: position = lower_limit

        track = pygame.Surface((self.track_container.get_width() - self.thumb_width, self.track_container.get_height() * 0.4))
        track_center = track.get_rect(center=(self.track_container.get_width() / 2, self.track_container.get_height() / 2))
        track.fill("white")

        thumb = pygame.Surface((self.thumb_width, self.track_container.get_height()))
        thumb_position = thumb.get_rect(center=(self.track_container.get_width() * position, self.track_container.get_height() / 2))
        thumb.fill("red")

        self.track_container.blit(track, track_center)
        self.track_container.blit(thumb, thumb_position)
        
        self.slider.blit(self.track_container, track_container_center)
        self.toolbar.toolbar_surface.blit(self.slider, (self.pos_x, self.pos_y))

    def set_value(self):
        assert self.slider
        assert self.track_container

        if not self.is_moving: return

        left_pos = (self.pos_x + ((self.slider.get_width() - self.track_container.get_width()) / 2)) + (self.thumb_width / 2)
        right_pos = (left_pos + self.track_container.get_width()) - (self.thumb_width / 2)

        value = (pygame.mouse.get_pos()[0] - left_pos) / (right_pos - left_pos)

        if value < 0: value = 0
        if value > 1: value = 1

        self.value = value

        self.event()
        self.update()
        self.toolbar.update()

    def track_collision(self):
        assert self.track_container

        track_rect = self.track_container.get_rect(topleft = (self.pos_x, self.pos_y))
        return track_rect.collidepoint(pygame.mouse.get_pos())
    
    def begin_move(self):
        if self.track_collision() and not self.is_moving:
            self.is_moving = True

    def end_move(self):
        self.is_moving = False

    def get_value(self) -> float:
        return self.value