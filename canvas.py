from re import S
import pygame
import time
from typing import TYPE_CHECKING
from math import ceil, floor
from Classes.select import Select
from Classes.zoomPan import ZoomPan
from Classes.draw import Draw

if TYPE_CHECKING: 
    from main import Main

def ex_time(func):
    def wrapper(*args, **kwargs) -> None:
        s = time.time()
        func(*args, **kwargs)
        e = time.time()
        print(e-s)
    return wrapper

def normal_round(n):
    if n - floor(n) < 0.5:
        return floor(n)
    return ceil(n)

class Canvas:
    def __init__(self, main: "Main", window: pygame.Surface) -> None:
        self.main = main
        self.window = window

        self.base_layer = pygame.Surface(pygame.display.get_surface().get_size())
        self.top_layer = pygame.Surface(pygame.display.get_surface().get_size(), flags=pygame.SRCALPHA)
        self.top_layer.fill((0, 0, 0, 0))

        self.draw = Draw(self, main)
        self.zoom_pan = ZoomPan(self, main)
        self.select = Select(self, main)

        self.main.scale = (self.base_layer.get_height() / self.main.canvas_height) * 0.95
        self.main.baseline_scale = self.main.scale

        self.offset_x = 0
        self.offset_y = 0

        self.canvas_surface = pygame.Surface((self.main.canvas_width, self.main.canvas_height))
        self.canvas_surface.fill("white")
        pygame.draw.rect(self.canvas_surface, "red", (10, 10, 10, 10))

        self.temp_surface = pygame.Surface((self.main.canvas_width, self.main.canvas_height), flags=pygame.SRCALPHA)
        self.temp_surface.fill((0, 0, 0, 0))

        self.render_canvas()

    def event_poll(self, events):
        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                self.top_layer.fill((0, 0, 0, 0))
                self.temp_surface.fill((0, 0, 0, 0))
                self.zoom_pan.zoom(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_down(event)
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_motion(event)
            elif event.type == pygame.KEYDOWN:
                self.key_down(event)

    def mouse_down(self, event):
        if event.button == 1:
            self.temp_surface.fill((0, 0, 0, 0))
            self.render_canvas()
            self.select.begin_select(event)
            #self.draw.draw(event)
        elif event.button == 2:
            self.temp_surface.fill((0, 0, 0, 0))
            self.zoom_pan.begin_pan(event)
        elif event.button == 3:
            self.temp_surface.fill((0, 0, 0, 0))
            self.draw.delete(event)

    def mouse_motion(self, event):
        if event.buttons == (1, 0, 0):
            self.select.select(event)
            # self.draw.cursor(event)
            # self.draw.draw(event)
        elif event.buttons == (0, 1, 0):
            self.zoom_pan.pan()
        elif event.buttons == (0, 0, 1):
            self.draw.cursor(event)
            self.draw.delete(event)
        else:
            pass
            #self.cursor(event)

    def key_down(self, event):
        if event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
            self.select.copy()
        elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:
            self.select.paste()

    def render_canvas(self):
        pixel_offset_x = ((((self.offset_x * -1) / self.main.scale) - floor((self.offset_x * -1) / self.main.scale)) * self.main.scale) * -1
        pixel_offset_y = ((((self.offset_y * -1) / self.main.scale) - floor((self.offset_y * -1) / self.main.scale)) * self.main.scale) * -1

        x = self.offset_x if self.offset_x > 0 else pixel_offset_x
        y = self.offset_y if self.offset_y > 0 else pixel_offset_y

        canvas_width = floor(self.main.canvas_width * self.main.scale)
        canvas_height = floor(self.main.canvas_height * self.main.scale)

        #calculate cropping region of the original image
        crop_left = 0
        crop_top = 0
        crop_right = self.main.canvas_width
        crop_bottom = self.main.canvas_height

        if self.offset_x < 0:
            crop_left = floor((self.offset_x * -1) / self.main.scale)

        if self.offset_y < 0:
            crop_top = floor((self.offset_y * -1) / self.main.scale)

        if canvas_width + self.offset_x > self.base_layer.get_width():
            crop_right = floor((canvas_width - ((canvas_width + self.offset_x) - self.base_layer.get_width())) / self.main.scale)

        if canvas_height + self.offset_y > self.base_layer.get_height():
            crop_bottom = floor((canvas_height - ((canvas_height + self.offset_y) - self.base_layer.get_height())) / self.main.scale)

        #calculate width of the cropped image (so the right/bottom side of the canvas doesn't get cut off when panning)
        width = (crop_right - crop_left) + 1
        height = (crop_bottom - crop_top) + 1

        if (crop_right - crop_left == self.main.canvas_width and canvas_width + self.offset_x < self.base_layer.get_width()) or canvas_width + self.offset_x < self.base_layer.get_width():
            width = crop_right - crop_left

        if (crop_bottom - crop_top == self.main.canvas_height and canvas_height + self.offset_y < self.base_layer.get_height()) or canvas_height + self.offset_y < self.base_layer.get_height():
            height = crop_bottom - crop_top

        #crop, scale and render to screen
        combined_surface = pygame.Surface((self.main.canvas_width, self.main.canvas_height))
        combined_surface.blit(self.canvas_surface, (0, 0))
        combined_surface.blit(self.temp_surface, (0, 0))

        cropped_surface = pygame.Surface((width, height))
        cropped_surface.blit(combined_surface, (0, 0), (crop_left, crop_top, crop_right + 1, crop_bottom + 1))
        scaled_surface = pygame.transform.scale(cropped_surface, (width * self.main.scale, height * self.main.scale))

        self.base_layer.fill("green")
        self.base_layer.blit(scaled_surface, (x, y))
        self.base_layer.blit(self.top_layer, (0, 0))
        self.window.blit(self.base_layer, (0, 0))