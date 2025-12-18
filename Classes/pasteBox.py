import pygame
from math import floor
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import canvas

class PasteBox:
    def __init__(self, canvas: "canvas.Canvas") -> None:
        self.canvas = canvas

        assert self.canvas.copied_area is not None
        self.copied_area = self.canvas.copied_area
        self.scaled_area = pygame.transform.scale(self.copied_area, (self.copied_area.get_width() * self.canvas.scale, self.copied_area.get_height() * self.canvas.scale))

        self.grid_x = floor((pygame.mouse.get_pos()[0] - self.canvas.offset_x) / self.canvas.scale) - floor(self.copied_area.get_width() / 2)
        self.grid_y = floor((pygame.mouse.get_pos()[1] - self.canvas.offset_y) / self.canvas.scale) - floor(self.copied_area.get_width() / 2)

        self.is_moving = False
        self.is_scaling = False

        self.update()

    def update(self):
        self.canvas.top_layer.fill((0, 0, 0, 0))

        canvas_x = (self.grid_x * self.canvas.scale) + self.canvas.offset_x
        canvas_y = (self.grid_y * self.canvas.scale) + self.canvas.offset_y

        self.scaled_area = pygame.transform.scale(self.copied_area, (self.copied_area.get_width() * self.canvas.scale, self.copied_area.get_height() * self.canvas.scale))

        self.canvas.top_layer.blit(self.scaled_area, (canvas_x, canvas_y))
        pygame.draw.rect(self.canvas.top_layer, "blue", (canvas_x, canvas_y, self.scaled_area.get_width(), self.scaled_area.get_height()), 1)

    def collision(self):
        canvas_x = (self.grid_x * self.canvas.scale) + self.canvas.offset_x
        canvas_y = (self.grid_y * self.canvas.scale) + self.canvas.offset_y
        rect = self.scaled_area.get_rect(topleft = (canvas_x, canvas_y))

        return rect.collidepoint(pygame.mouse.get_pos())
    
    def begin_move(self):
        self.is_moving = True
    
    def move(self):
        x = floor((pygame.mouse.get_pos()[0] - self.canvas.offset_x) / self.canvas.scale) - floor(self.copied_area.get_width() / 2)
        y = floor((pygame.mouse.get_pos()[1] - self.canvas.offset_y) / self.canvas.scale) - floor(self.copied_area.get_height() / 2)

        self.grid_x = x
        self.grid_y = y

        self.update()
        self.canvas.render_canvas()

    def stop_moving(self):
        self.is_moving = False

    def commit_paste(self):
        self.canvas.canvas_surface.blit(self.copied_area, (self.grid_x, self.grid_y))

        self.canvas.top_layer.fill((0, 0, 0, 0))
        self.canvas.paste_box = None
        
        self.canvas.render_canvas()