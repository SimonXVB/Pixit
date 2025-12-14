import pygame
from math import floor
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import main
    import canvas

class Draw:
    def __init__(self, canvas: "canvas.Canvas", main: "main.Main") -> None:
        self.main = main
        self.canvas = canvas

    def get_pixel_coords(self, event) -> dict[str, int] | None:
        GRID_X = floor((event.pos[0] - self.canvas.offset_x) / self.main.scale)
        GRID_Y = floor((event.pos[1] - self.canvas.offset_y) / self.main.scale)

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
    
    def cursor(self, event):
        coords = self.get_pixel_coords(event)

        if coords:
            self.canvas.temp_surface.fill((0, 0, 0, 0))
            pygame.draw.rect(self.canvas.temp_surface, "blue", (coords["start_x"], coords["start_y"], coords["width"], coords["height"]))
            self.canvas.render_canvas()

    def draw(self, event):
        coords = self.get_pixel_coords(event)

        if coords:
            pygame.draw.rect(self.canvas.canvas_surface, "red", (coords["start_x"], coords["start_y"], coords["width"], coords["height"]))
            self.canvas.render_canvas()

    def delete(self, event):
        coords = self.get_pixel_coords(event)

        if coords:
            pygame.draw.rect(self.canvas.canvas_surface, "white", (coords["start_x"], coords["start_y"], coords["width"], coords["height"]))
            self.canvas.render_canvas()