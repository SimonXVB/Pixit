import pygame
from math import floor, ceil
from typing import TYPE_CHECKING
from Canvas.Classes.pasteBox import PasteBox

if TYPE_CHECKING:
    from canvas import Canvas
    from main import Main

class Select:
    def __init__(self, canvas: "Canvas", main: "Main") -> None:
        self.canvas = canvas
        self.main = main

        self.select_coords = {}
        self.copied_area: "pygame.Surface | None" = None

        self.start_x = 0
        self.start_y = 0

    def select(self):
        left = floor((self.start_x - self.canvas.offset_x) / self.canvas.scale)
        top = floor((self.start_y - self.canvas.offset_y - self.main.toolbar_height) / self.canvas.scale)
        right = ceil((pygame.mouse.get_pos()[0] - self.canvas.offset_x) / self.canvas.scale)
        bottom = ceil((pygame.mouse.get_pos()[1] - self.canvas.offset_y - self.main.toolbar_height) / self.canvas.scale)

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

        self.select_coords = {
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
        self.select_coords = {}
        self.canvas.temp_surface.fill((0, 0, 0, 0))
        self.canvas.render_canvas()

    def begin_select(self):
        self.clear_select()

        self.start_x = pygame.mouse.get_pos()[0]
        self.start_y = pygame.mouse.get_pos()[1]

    def copy(self):
        if not self.select_coords: return

        self.copied_area = pygame.Surface((self.select_coords["width"], self.select_coords["height"]))
        self.copied_area.blit(self.canvas.canvas_surface, (0, 0), (self.select_coords["left"], 
                                                                   self.select_coords["top"], 
                                                                   self.select_coords["right"], 
                                                                   self.select_coords["bottom"]))
    
    def paste(self):
        if not self.copied_area: return

        self.main.set_interaction_state("select")
        self.canvas.paste_box = PasteBox(self.canvas, self.copied_area)

        self.clear_select()

    def delete(self):
        if not self.select_coords: return

        delete_area = pygame.Surface((self.select_coords["width"], self.select_coords["height"]))
        delete_area.fill(self.main.bg_color)

        self.canvas.canvas_surface.blit(delete_area, (self.select_coords["left"], self.select_coords["top"]))

        self.canvas.undo_redo.create_snapshot({"left": self.select_coords["left"],
                                               "top": self.select_coords["top"],
                                               "right": self.select_coords["right"],
                                               "bottom": self.select_coords["bottom"]})

        self.clear_select()