import pygame
import time

from typing import TYPE_CHECKING
from math import floor

from Canvas.Classes.select import Select
from Canvas.Classes.zoomPan import ZoomPan
from Canvas.Classes.draw import Draw
from Canvas.Classes.undoRedo import UndoRedo

def ex_time(func):
    def wrapper(*args, **kwargs) -> None:
        s = time.time()
        func(*args, **kwargs)
        e = time.time()
        print(e-s)
    return wrapper

if TYPE_CHECKING: 
    from Classes.pasteBox import PasteBox
    from main import Main

class Canvas:
    def __init__(self, main: "Main") -> None:
        self.main = main

        self.color: pygame.Color = pygame.Color(255, 255, 255, 255)
        self.bg_color = "#ffffff"
        self.pixel_size: int = 5
        self.canvas_width: int = 50
        self.canvas_height: int = 50
        self.toolbar_height = self.main.toolbar_height

        self.draw = Draw(self)
        self.zoom_pan = ZoomPan(self)
        self.select = Select(self)
        self.undo_redo = UndoRedo(self)

        self.base_layer = pygame.Surface((self.main.window.get_width(), self.main.window.get_height() - self.toolbar_height))
        self.top_layer = pygame.Surface(self.base_layer.get_size(), flags=pygame.SRCALPHA)
        self.top_layer.fill((0, 0, 0, 0))

        self.scale = (self.base_layer.get_height() / self.canvas_height) * 0.95
        self.baseline_scale = self.scale

        self.offset_x = (self.base_layer.get_width() / 2) - ((self.canvas_width * self.scale) / 2)
        self.offset_y = (self.base_layer.get_height() / 2) - ((self.canvas_height * self.scale) / 2)

        self.select_coords = {}
        self.copied_area: "pygame.Surface | None" = None
        self.paste_box: "PasteBox | None" = None

        self.canvas_surface = pygame.Surface((self.canvas_width, self.canvas_height))
        self.canvas_surface.fill("white")

        self.temp_surface = pygame.Surface((self.canvas_width, self.canvas_height), flags=pygame.SRCALPHA)
        self.temp_surface.fill((0, 0, 0, 0))

        self.render_canvas()

    def event_poll(self, events):
        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                self.zoom_pan.zoom(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_down(event)
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_motion(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_up()
            elif event.type == pygame.KEYDOWN:
                self.key_down(event)

    def mouse_down(self, event):
        if event.button == 1:
                if self.main.interaction_state == "draw":
                    self.draw.draw(event)
                elif self.main.interaction_state == "delete":
                    self.draw.delete(event)
                elif self.main.interaction_state == "select":
                    self.select.select()

                if self.paste_box and self.paste_box.collision() == "node":
                    self.paste_box.begin_scale()
                elif self.paste_box and self.paste_box.collision() == "copied_area":
                    self.paste_box.begin_move()

                if self.paste_box:
                    self.paste_box.commit_paste()
        elif event.button == 2:
            self.zoom_pan.begin_pan()
        elif event.button == 3:
            self.draw.delete(event)

    def mouse_motion(self, event):
        if event.buttons == (1, 0, 0):
            if self.main.interaction_state == "draw":
                self.draw.cursor(event)
                self.draw.draw(event)
            elif self.main.interaction_state == "delete":
                self.draw.cursor(event)
                self.draw.delete(event)
            elif self.main.interaction_state == "select":
                self.select.select()

            if self.paste_box and self.paste_box.is_scaling:
                self.paste_box.scale()
            elif self.paste_box and self.paste_box.is_moving:
                self.paste_box.move()
        elif event.buttons == (0, 1, 0):
            self.zoom_pan.pan()
        elif event.buttons == (0, 0, 1):
            self.draw.cursor(event)
            self.draw.delete(event)
        
    def mouse_up(self):
        self.undo_redo.create_snapshot()

        if self.paste_box:
            self.paste_box.stop_moving()
            self.paste_box.stop_scaling()

    def key_down(self, event):
        if event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
            self.select.copy()
        elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:
            self.select.paste()
        elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
            self.undo_redo.undo()
        elif event.key == pygame.K_y and pygame.key.get_mods() & pygame.KMOD_CTRL:
            self.undo_redo.redo()
        elif event.key == pygame.K_RETURN:
            if self.paste_box:
                self.paste_box.commit_paste()
        elif event.key == pygame.K_BACKSPACE:
            if self.paste_box:
                self.paste_box.clear_paste_box()

            if self.select_coords:
                self.select.delete()

    def set_canvas_size(self, x: int, y: int):
        self.canvas_width = x
        self.canvas_height = y

        new_canvas = pygame.Surface((x, y))
        new_canvas.fill("white")
        new_canvas.blit(self.canvas_surface, (0, 0))

        self.canvas_surface = new_canvas

        self.scale = (self.base_layer.get_height() / self.canvas_height) * 0.95
        self.baseline_scale = self.scale

        self.offset_x = (self.base_layer.get_width() / 2) - ((self.canvas_width * self.scale) / 2)
        self.offset_y = (self.base_layer.get_height() / 2) - ((self.canvas_height * self.scale) / 2)

        self.temp_surface = pygame.Surface((self.canvas_width, self.canvas_height), flags=pygame.SRCALPHA)
        self.temp_surface.fill((0, 0, 0, 0))

        self.render_canvas()

    def render_canvas(self):
        pixel_offset_x = ((((self.offset_x * -1) / self.scale) - floor((self.offset_x * -1) / self.scale)) * self.scale) * -1
        pixel_offset_y = ((((self.offset_y * -1) / self.scale) - floor((self.offset_y * -1) / self.scale)) * self.scale) * -1

        x = self.offset_x if self.offset_x > 0 else pixel_offset_x
        y = self.offset_y if self.offset_y > 0 else pixel_offset_y

        canvas_width = floor(self.canvas_width * self.scale)
        canvas_height = floor(self.canvas_height * self.scale)

        #calculate cropping region of the original image
        crop_left = 0
        crop_top = 0
        crop_right = self.canvas_width
        crop_bottom = self.canvas_height

        if self.offset_x < 0:
            crop_left = floor((self.offset_x * -1) / self.scale)

        if self.offset_y < 0:
            crop_top = floor((self.offset_y * -1) / self.scale)

        if canvas_width + self.offset_x > self.base_layer.get_width():
            crop_right = floor((canvas_width - ((canvas_width + self.offset_x) - self.base_layer.get_width())) / self.scale)

        if canvas_height + self.offset_y > self.base_layer.get_height():
            crop_bottom = floor((canvas_height - ((canvas_height + self.offset_y) - self.base_layer.get_height())) / self.scale)

        #calculate width of the cropped image (so the right/bottom side of the canvas doesn't get cut off when panning)
        width = (crop_right - crop_left) + 1
        height = (crop_bottom - crop_top) + 1

        if (crop_right - crop_left == self.canvas_width and canvas_width + self.offset_x < self.base_layer.get_width()) or canvas_width + self.offset_x < self.base_layer.get_width():
            width = crop_right - crop_left

        if (crop_bottom - crop_top == self.canvas_height and canvas_height + self.offset_y < self.base_layer.get_height()) or canvas_height + self.offset_y < self.base_layer.get_height():
            height = crop_bottom - crop_top

        #crop, scale and render to screen
        combined_surface = pygame.Surface((self.canvas_width, self.canvas_height))
        combined_surface.blit(self.canvas_surface, (0, 0))
        combined_surface.blit(self.temp_surface, (0, 0))

        cropped_surface = pygame.Surface((width, height))
        cropped_surface.blit(combined_surface, (0, 0), (crop_left, crop_top, crop_right + 1, crop_bottom + 1))
        scaled_surface = pygame.transform.scale(cropped_surface, (width * self.scale, height * self.scale))

        if self.paste_box:
            self.paste_box.update()

        self.base_layer.fill("green")
        self.base_layer.blit(scaled_surface, (x, y))
        self.base_layer.blit(self.top_layer, (0, 0))
        self.main.window.blit(self.base_layer, (0, self.toolbar_height))