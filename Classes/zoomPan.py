import pygame
from math import floor
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import canvas

class ZoomPan:
    def __init__(self, canvas: "canvas.Canvas") -> None:
        self.canvas = canvas

        self.start_x = 0
        self.start_y = 0

    def set_offset(self, x: int, y: int):
        canvas_width = self.canvas.canvas_width * self.canvas.scale
        canvas_height = self.canvas.canvas_height * self.canvas.scale

        screen_width = self.canvas.base_layer.get_width()
        screen_height = self.canvas.base_layer.get_height()
        
        if canvas_width < screen_width:
            if (canvas_width / 2) * -1 < x < screen_width - (canvas_width / 2):
                self.canvas.offset_x = x
            elif x < (canvas_width / 2) * -1:
                self.canvas.offset_x = int((canvas_width / 2) * -1)
            elif x > screen_width - (canvas_width / 2):
                self.canvas.offset_x = int(screen_width - (canvas_width / 2))
        else:
            if (screen_width / 2) - canvas_width < x < screen_width / 2:
                self.canvas.offset_x = x
            elif x <  (screen_width / 2) - canvas_width:
                self.canvas.offset_x = int((screen_width / 2) - canvas_width)
            elif x > screen_width / 2:
                self.canvas.offset_x = int(screen_width / 2)

        if canvas_height < screen_height:
            if (canvas_height / 2) * -1 < y < screen_height - (canvas_height / 2):
                self.canvas.offset_y = y
            elif y < (canvas_height / 2) * -1:
                self.canvas.offset_y = int((canvas_height / 2) * -1)
            elif y > screen_height - (canvas_height / 2):
                self.canvas.offset_y = int(screen_height - (canvas_height / 2))
        else:
            if (screen_height / 2) - canvas_height < y < screen_height / 2:
                self.canvas.offset_y = y
            elif y < (screen_height / 2) - canvas_height:
                self.canvas.offset_y = int((screen_height / 2) - canvas_height)
            elif y > screen_height / 2:
                self.canvas.offset_y = int(screen_height / 2)

    def zoom(self, event):
        PREV_SCALE = self.canvas.scale
        SCALE_INTERVAL = self.canvas.baseline_scale * 0.05

        if event.y == 1 and self.canvas.scale <= self.canvas.baseline_scale * 10:
            self.canvas.scale = self.canvas.scale + SCALE_INTERVAL
        elif event.y == -1 and self.canvas.scale > self.canvas.baseline_scale * 0.1:
            self.canvas.scale = self.canvas.scale - SCALE_INTERVAL
        else:
            return

        x = floor(pygame.mouse.get_pos()[0] - (pygame.mouse.get_pos()[0] - self.canvas.offset_x) * (self.canvas.scale / PREV_SCALE))
        y = floor(pygame.mouse.get_pos()[1] - (pygame.mouse.get_pos()[1] - self.canvas.offset_y) * (self.canvas.scale / PREV_SCALE))

        self.set_offset(x, y)
        self.canvas.render_canvas()

    def begin_pan(self, event):
        self.start_x = event.pos[0]
        self.start_y = event.pos[1]

    def pan(self):
        x = self.canvas.offset_x + (pygame.mouse.get_pos()[0] - self.start_x)
        y = self.canvas.offset_y + (pygame.mouse.get_pos()[1] - self.start_y)

        self.start_x = pygame.mouse.get_pos()[0]
        self.start_y = pygame.mouse.get_pos()[1]

        self.set_offset(x, y)
        self.canvas.render_canvas()