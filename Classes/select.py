import pygame
from math import floor, ceil
from typing import TYPE_CHECKING
from Classes.pasteBox import PasteBox

if TYPE_CHECKING:
    import canvas

class Select:
    def __init__(self, canvas: "canvas.Canvas") -> None:
        self.canvas = canvas

        self.is_selected = False

        self.start_x = 0
        self.start_y = 0

    def begin_select(self, event):
        self.clear_select()

        self.start_x = event.pos[0]
        self.start_y = event.pos[1]

    def select(self, event):
        left = floor((self.start_x - self.canvas.offset_x) / self.canvas.scale)
        top = floor((self.start_y - self.canvas.offset_y) / self.canvas.scale)
        right = ceil((event.pos[0] - self.canvas.offset_x) / self.canvas.scale)
        bottom = ceil((event.pos[1] - self.canvas.offset_y) / self.canvas.scale)

        if right < left: 
            left, right = right, left

        if bottom < top: 
            top, bottom = bottom, top

        if left < 0: left = 0
        if top < 0: top = 0
        
        if right > self.canvas.canvas_width: 
            right = self.canvas.canvas_width

        if bottom > self.canvas.canvas_height: 
            bottom = self.canvas.canvas_height

        width = right - left
        height = bottom - top

        self.canvas.select_coords = {
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

    def clear_select(self):
        self.canvas.select_coords = {}
        self.canvas.temp_surface.fill((0, 0, 0, 0))
        self.canvas.render_canvas()

    def copy(self):
        self.canvas.copied_area = pygame.Surface((self.canvas.select_coords["width"], self.canvas.select_coords["height"]))
        self.canvas.copied_area.blit(self.canvas.canvas_surface, (0, 0), (self.canvas.select_coords["left"], 
                                                                          self.canvas.select_coords["top"], 
                                                                          self.canvas.select_coords["right"], 
                                                                          self.canvas.select_coords["bottom"]))
    
    def paste(self):
        self.canvas.paste_box = PasteBox(self.canvas)
        self.clear_select()

    def delete(self):
        delete_area = pygame.Surface((self.canvas.select_coords["width"], self.canvas.select_coords["height"]))
        delete_area.fill("white")

        self.canvas.canvas_surface.blit(delete_area, (self.canvas.select_coords["left"], self.canvas.select_coords["top"]))
        self.clear_select()