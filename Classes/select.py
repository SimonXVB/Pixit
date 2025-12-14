import pygame
from math import floor, ceil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import main
    import canvas

class Select:
    def __init__(self, canvas: "canvas.Canvas", main: "main.Main") -> None:
        self.main = main
        self.canvas = canvas

        self.start_x = 0
        self.start_y = 0

        self.copied_area_coords = {"left": 0, "top": 0, "right": 0, "bottom": 0, "height": 0, "width": 0}
        self.copied_area = None

    def begin_select(self, event):
        self.start_x = event.pos[0]
        self.start_y = event.pos[1]

    def select(self, event):
        left = floor((self.start_x - self.canvas.offset_x) / self.main.scale)
        top = floor((self.start_y - self.canvas.offset_y) / self.main.scale)
        right = ceil((event.pos[0] - self.canvas.offset_x) / self.main.scale)
        bottom = ceil((event.pos[1] - self.canvas.offset_y) / self.main.scale)

        if left < 0: left = 0
        if top < 0: top = 0
        
        if right > self.main.canvas_width: 
            right = self.main.canvas_width

        if bottom > self.main.canvas_height: 
            bottom = self.main.canvas_height

        if right < left: 
            left, right = right, left

        if bottom < top: 
            top, bottom = bottom, top

        width = right - left
        height = bottom - top

        self.copied_area_coords = {
            "left": left,
            "top": top,
            "right": right,
            "bottom": bottom,
            "width": width,
            "height": height
        }

        self.canvas.temp_surface.fill((0, 0, 0, 0))
        self.canvas.top_layer.fill((0, 0, 0, 0))

        pygame.draw.rect(self.canvas.temp_surface, (0, 98, 255, 85), (left, top, width, height))

        pygame.draw.circle(self.canvas.top_layer, "red", ((left * self.main.scale) + self.canvas.offset_x, (top * self.main.scale) + self.canvas.offset_y), self.main.scale)
        pygame.draw.circle(self.canvas.top_layer, "red", ((right * self.main.scale) + self.canvas.offset_x, (top * self.main.scale) + self.canvas.offset_y), self.main.scale)
        pygame.draw.circle(self.canvas.top_layer, "red", ((left * self.main.scale) + self.canvas.offset_x, (bottom * self.main.scale) + self.canvas.offset_y), self.main.scale)
        pygame.draw.circle(self.canvas.top_layer, "red", ((right * self.main.scale) + self.canvas.offset_x, (bottom * self.main.scale) + self.canvas.offset_y), self.main.scale)

        self.canvas.render_canvas()

    def copy(self):
        self.copied_area = pygame.Surface((self.copied_area_coords["width"], self.copied_area_coords["height"]))
        self.copied_area.blit(self.canvas.canvas_surface, (0, 0), (self.copied_area_coords["left"], 
                                                            self.copied_area_coords["top"], 
                                                            self.copied_area_coords["right"], 
                                                            self.copied_area_coords["bottom"]))
    
    def paste(self):
        if self.copied_area == None: return

        x = floor((pygame.mouse.get_pos()[0] - self.canvas.offset_x) / self.main.scale) - floor(self.copied_area_coords["width"] / 2)
        y = floor((pygame.mouse.get_pos()[1] - self.canvas.offset_y) / self.main.scale) - floor(self.copied_area_coords["height"] / 2)

        self.canvas.temp_surface.blit(self.copied_area, (x, y))
        self.canvas.render_canvas()