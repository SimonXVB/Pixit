import pygame 
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Toolbar.toolbar import Toolbar
    from collections.abc import Callable

class Slider:
    def __init__(self, toolbar: "Toolbar", width: int, height: int, pos_x: int, pos_y: int, event: "Callable[[], None]") -> None:
        self.toolbar = toolbar

        self.slider: pygame.Surface | None = None
        self.track_container: pygame.Surface | None = None
        self.thumb: pygame.Surface | None = None

        self.width: int = width
        self.height: int = height
        self.pos_x: int = pos_x
        self.pos_y: int = pos_y

        self.is_moving = False

        self.event = event

        self.update()

    def update(self, thumb_value: float = 0):
        assert self.toolbar.toolbar_surface

        self.slider = pygame.Surface((self.width, self.height))
        self.slider.fill("green")

        track_container = pygame.Surface((self.width * 0.95, self.height * 0.7))
        track_container_center = track_container.get_rect(center=(self.width / 2, self.height / 2))
        track_container.fill("green")

        track = pygame.Surface((track_container.get_width() * 0.97, track_container.get_height() * 0.4))
        track_center = track.get_rect(center=(track_container.get_width() / 2, track_container.get_height() / 2))
        track.fill("white")

        lower_limit = ((track_container.get_width() * 0.05) / 2) / track_container.get_width()
        upper_limit = 1 - (((track_container.get_width() * 0.05) / 2) / track_container.get_width())
        
        if thumb_value >= upper_limit: thumb_value = upper_limit
        if thumb_value <= lower_limit: thumb_value = lower_limit

        thumb = pygame.Surface((track_container.get_width() * 0.05, track_container.get_height()))
        thumb_position = thumb.get_rect(center=(track_container.get_width() * thumb_value, track_container.get_height() / 2))
        thumb.fill("red")

        track_container.blit(track, track_center)
        track_container.blit(thumb, thumb_position)
        
        self.slider.blit(track_container, track_container_center)
        self.toolbar.toolbar_surface.blit(self.slider, (self.pos_x, self.pos_y))

        self.track_container = track_container
        self.thumb = thumb

    def track_collision(self):
        assert self.track_container

        track_rect = self.track_container.get_rect(topleft = (self.pos_x, self.pos_y))
        return track_rect.collidepoint(pygame.mouse.get_pos())
    
    def begin_move(self):
        if self.track_collision() and not self.is_moving:
            self.is_moving = True

    def end_move(self):
        self.is_moving = False

    def set_value(self):
        if not self.is_moving: return

        assert self.slider
        assert self.track_container

        track_left_pos = self.pos_x + ((self.slider.get_width() - self.track_container.get_width()) / 2)
        track_right_pos = track_left_pos + self.track_container.get_width()

        value = (pygame.mouse.get_pos()[0] - track_left_pos) / (track_right_pos - track_left_pos)

        self.update(value)
        self.toolbar.update()