import pygame
from math import floor
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from canvas import Canvas
    from main import Main

class Draw:
    def __init__(self, canvas: "Canvas", main: "Main") -> None:
        self.canvas = canvas
        self.main = main

    def get_pixel_coords(self) -> dict[str, int] | None:
        GRID_X = floor((pygame.mouse.get_pos()[0] - self.canvas.offset_x) / self.canvas.scale)
        GRID_Y = floor((pygame.mouse.get_pos()[1] - self.canvas.offset_y - self.main.toolbar_height) / self.canvas.scale)

        if GRID_X < 0 or GRID_X > self.main.canvas_width: return
        if GRID_Y < 0 or GRID_Y > self.main.canvas_height: return

        start_x: int = floor(GRID_X - floor(self.main.pixel_size / 2))
        start_y: int = floor(GRID_Y - floor(self.main.pixel_size / 2))

        end_x: int = start_x + self.main.pixel_size
        end_y: int = start_y + self.main.pixel_size

        if start_x < 0:
            start_x = 0

        if start_y < 0:
            start_y = 0

        if end_x > self.main.canvas_width:
            end_x = self.main.canvas_width

        if end_y > self.main.canvas_height:
            end_y = self.main.canvas_height

        width: int = end_x - start_x
        height: int = end_y - start_y

        return {
            "start_x": start_x,
            "start_y": start_y,
            "end_x": end_x,
            "end_y": end_y,
            "width": width,
            "height": height
        }
    
    def cursor(self):
        coords = self.get_pixel_coords()

        scaled = pygame.transform.scale(self.canvas.temp_surface, (self.main.canvas_width * self.canvas.scale, self.main.canvas_height * self.canvas.scale))
        rect = scaled.get_rect(topleft = (self.canvas.offset_x, self.canvas.offset_y + self.main.toolbar_height))

        if not rect.collidepoint(pygame.mouse.get_pos()):
            self.canvas.temp_surface.fill((0, 0, 0, 0))
            self.canvas.render_canvas()
            return

        if coords:
            self.canvas.temp_surface.fill((0, 0, 0, 0))
            pygame.draw.rect(self.canvas.temp_surface, self.main.color, (coords["start_x"], coords["start_y"], coords["width"], coords["height"]))
            self.canvas.render_canvas()

    def draw(self):
        coords = self.get_pixel_coords()

        if coords:
            self.canvas.undo_redo.set_snapshot_rect(coords["start_x"], coords["start_y"], coords["end_x"], coords["end_y"])

            pygame.draw.rect(self.canvas.canvas_surface, self.main.color, (coords["start_x"], coords["start_y"], coords["width"], coords["height"]))
            self.canvas.render_canvas()

    def delete(self):
        coords = self.get_pixel_coords()

        if coords:
            self.canvas.undo_redo.set_snapshot_rect(coords["start_x"], coords["start_y"], coords["end_x"], coords["end_y"])

            pygame.draw.rect(self.canvas.canvas_surface, self.main.bg_color, (coords["start_x"], coords["start_y"], coords["width"], coords["height"]))
            self.canvas.render_canvas()