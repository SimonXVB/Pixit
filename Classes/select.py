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

        self.copied_area_coords = {}
        self.copied_area = None

        self.paste_box = None

    def begin_select(self, event):
        self.start_x = event.pos[0]
        self.start_y = event.pos[1]

    def select(self, event):
        left = floor((self.start_x - self.canvas.offset_x) / self.main.scale)
        top = floor((self.start_y - self.canvas.offset_y) / self.main.scale)
        right = ceil((event.pos[0] - self.canvas.offset_x) / self.main.scale)
        bottom = ceil((event.pos[1] - self.canvas.offset_y) / self.main.scale)

        if right < left: 
            left, right = right, left

        if bottom < top: 
            top, bottom = bottom, top

        if left < 0: left = 0
        if top < 0: top = 0
        
        if right > self.main.canvas_width: 
            right = self.main.canvas_width

        if bottom > self.main.canvas_height: 
            bottom = self.main.canvas_height

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
        pygame.draw.rect(self.canvas.temp_surface, (0, 98, 255, 85), (left, top, width, height))
        self.canvas.render_canvas()

    def copy(self):
        self.copied_area = pygame.Surface((self.copied_area_coords["width"], 
                                           self.copied_area_coords["height"]))
        
        self.copied_area.blit(self.canvas.canvas_surface, (0, 0), (self.copied_area_coords["left"], 
                                                                   self.copied_area_coords["top"], 
                                                                   self.copied_area_coords["right"], 
                                                                   self.copied_area_coords["bottom"]))
    
    def paste(self):
        self.paste_box = PasteBox(self, self.canvas, self.main)
        self.canvas.render_canvas()

class PasteBox:
    def __init__(self, select: "Select", canvas: "canvas.Canvas", main: "main.Main") -> None:
        self.select = select
        self.canvas = canvas
        self.main = main

        self.pos_x = self.canvas.offset_x + (self.canvas.offset_x - pygame.mouse.get_pos()[0])
        self.pos_y = self.canvas.offset_y + (self.canvas.offset_y - pygame.mouse.get_pos()[1])
        
        self.prev_scale = self.main.scale

        self.update()

    def update(self):
        if not self.select.copied_area: return

        self.canvas.top_layer.fill((0, 0, 0, 0))

        x = self.canvas.offset_x - (self.pos_x * (self.main.scale / self.prev_scale))
        y = self.canvas.offset_y - (self.pos_y * (self.main.scale / self.prev_scale))
        scaled = pygame.transform.scale(self.select.copied_area, (self.select.copied_area.get_width() * self.main.scale, self.select.copied_area.get_height() * self.main.scale))
        
        self.canvas.top_layer.blit(scaled, (x, y))

    def collision(self):
        pass