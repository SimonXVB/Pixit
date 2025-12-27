import pygame 
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Toolbar.toolbar import Toolbar
    from collections.abc import Callable

class Slider:
    def __init__(self, toolbar: "Toolbar", width: int, height: int, pos_x: int, pos_y: int, label_text: str, event: "Callable[[], None]") -> None:
        self.toolbar = toolbar

        self.width = width
        self.height = height
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.label_text = label_text
        self.event = event

        self.value: float = 0
        self.is_moving: bool = False
        self.is_hovering = True

        self.slider: pygame.Surface = pygame.Surface((self.width, self.height))
        self.track_container: pygame.Surface = pygame.Surface((self.width * 0.7, self.height * 0.7), flags=pygame.SRCALPHA)
        self.label: pygame.Surface = pygame.Surface((self.width * 0.25, self.height), flags=pygame.SRCALPHA)

        self.thumb_width = self.track_container.get_width() * 0.04

        self.update()

    def event_poll(self, event):
        if self.track_collision(): 
            if not self.is_hovering:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.is_hovering = True
        else: 
            if self.is_hovering and not self.is_moving:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                self.is_hovering = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.begin_move()
        elif event.type == pygame.MOUSEMOTION:
            self.set_value()
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.is_hovering and self.is_moving and not self.track_collision():
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                self.is_hovering = False
            self.end_move()

    def update(self):
        self.slider.fill(self.toolbar.main.colors["secondary"])
        self.track_container.fill((0, 0, 0, 0))
        self.label.fill((0, 0, 0, 0))

        position = self.value
        lower_limit = (self.thumb_width / 2) / self.track_container.get_width()
        upper_limit = 1 - ((self.thumb_width / 2) / self.track_container.get_width())

        if position >= upper_limit: position = upper_limit
        if position <= lower_limit: position = lower_limit

        text = pygame.font.SysFont("Arial", int(self.height * 0.6)).render(self.label_text + "px", True, "white")
        label_center = text.get_rect(center=(self.label.get_width() / 2, self.label.get_height() / 2))
        pygame.draw.rect(self.label, "white", (0, 0, self.label.get_width(), self.label.get_height()), 2, 2)
        self.label.blit(text, label_center)

        track = pygame.Surface((self.track_container.get_width() - self.thumb_width, self.track_container.get_height() * 0.4))
        track_center = track.get_rect(center=(self.track_container.get_width() / 2, self.track_container.get_height() / 2))
        track.fill("white")

        thumb = pygame.Surface((self.thumb_width, self.track_container.get_height()))
        thumb_position = thumb.get_rect(center=(self.track_container.get_width() * position, self.track_container.get_height() / 2))
        thumb.fill("white")

        self.track_container.blit(track, track_center)
        self.track_container.blit(thumb, thumb_position)
        
        track_container_center = self.track_container.get_rect(center=(self.width / 2, self.height / 2))
        self.slider.blit(self.track_container, (0, track_container_center[1]))
        self.slider.blit(self.label, (self.width * 0.75, 0))
        
        self.toolbar.toolbar_surface.blit(self.slider, (self.pos_x, self.pos_y))

    def track_collision(self):
        track_rect = self.track_container.get_rect(topleft = (self.pos_x, self.pos_y))
        return track_rect.collidepoint(pygame.mouse.get_pos())

    def set_value(self):
        if not self.is_moving: return

        right_pos = (self.pos_x + self.track_container.get_width()) - (self.thumb_width / 2)
        value = (pygame.mouse.get_pos()[0] - self.pos_x) / (right_pos - self.pos_x)

        if value < 0: value = 0
        if value > 1: value = 1

        self.value = value

        self.event()
        self.update()
        self.toolbar.update()

    def set_label_text(self, label_text: str):
        self.label_text = label_text
        self.update()
        self.toolbar.update()
    
    def begin_move(self):
        if self.track_collision() and not self.is_moving:
            self.is_moving = True

    def end_move(self):
        self.is_moving = False

    def get_value(self) -> float:
        return self.value