import pygame
import time

from typing import TYPE_CHECKING
from math import floor

from Canvas.Classes.select import Select
from Canvas.Classes.zoomPan import ZoomPan
from Canvas.Classes.draw import Draw
from Canvas.Classes.undoRedo import UndoRedo

if TYPE_CHECKING: 
    from Classes.pasteBox import PasteBox
    from main import Main

class Canvas:
    def __init__(self, main: "Main") -> None:
        self.main = main

        self.draw = Draw(self, main)
        self.zoom_pan = ZoomPan(self, main)
        self.select = Select(self, main)
        self.undo_redo = UndoRedo(self)

        self.base_layer = pygame.Surface((self.main.window.get_width(), self.main.window.get_height() - self.main.toolbar_height))
        self.top_layer = pygame.Surface(self.base_layer.get_size(), flags=pygame.SRCALPHA)
        self.top_layer.fill((0, 0, 0, 0))

        self.scale = floor((self.base_layer.get_height() / self.main.canvas_height) * 0.95) if floor((self.base_layer.get_height() / self.main.canvas_height) * 0.95) > 1 else 1
        self.baseline_scale = self.scale

        self.offset_x = (self.base_layer.get_width() / 2) - ((self.main.canvas_width * self.scale) / 2)
        self.offset_y = (self.base_layer.get_height() / 2) - ((self.main.canvas_height * self.scale) / 2)

        self.paste_box: "PasteBox | None" = None

        self.canvas_surface = pygame.Surface((self.main.canvas_width, self.main.canvas_height))
        self.canvas_surface.fill(self.main.bg_color)

        self.temp_surface = pygame.Surface((self.main.canvas_width, self.main.canvas_height), flags=pygame.SRCALPHA)
        self.temp_surface.fill((0, 0, 0, 0))

        self.render_canvas()

    def canvas_collision(self):
        canvas_rect = self.base_layer.get_rect(topleft = (0, self.main.toolbar_height))
        return canvas_rect.collidepoint(pygame.mouse.get_pos())

    def event_poll(self, events):
        if not self.canvas_collision(): return

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
                self.draw.draw()
            elif self.main.interaction_state == "delete":
                self.draw.delete()
            elif self.main.interaction_state == "select":
                if self.paste_box and self.paste_box.collision() == "node":
                    self.paste_box.begin_scale()
                elif self.paste_box and self.paste_box.collision() == "copied_area":
                    self.paste_box.begin_move()
                else:
                    if self.paste_box:
                        self.paste_box.commit_paste()

                    self.select.begin_select()
        elif event.button == 2:
            self.zoom_pan.begin_pan()
        elif event.button == 3:
            self.draw.delete()

    def mouse_motion(self, event):
        if event.buttons == (1, 0, 0):
            if self.main.interaction_state == "draw":
                self.draw.draw()
            elif self.main.interaction_state == "delete":
                self.draw.delete()
            elif self.main.interaction_state == "select":
                if self.paste_box and self.paste_box.is_scaling:
                    self.paste_box.scale()
                elif self.paste_box and self.paste_box.is_moving:
                    self.paste_box.move()
                else:
                    self.select.select()
        elif event.buttons == (0, 1, 0):
            self.zoom_pan.pan()
        elif event.buttons == (0, 0, 1):
            self.draw.cursor()
            self.draw.delete()

        if self.main.interaction_state == "draw" or self.main.interaction_state == "delete":
            self.draw.cursor()
        
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
            self.select.delete()

            if self.paste_box:
                self.paste_box.clear_paste_box()

    def set_canvas_size(self, new_x: int, new_y: int):
        x = new_x if new_x > 1 else self.main.canvas_width
        y = new_y if new_y > 1 else self.main.canvas_height

        self.main.canvas_width = x
        self.main.canvas_height = y

        new_canvas = pygame.Surface((x, y))
        new_canvas.fill("white")
        new_canvas.blit(self.canvas_surface, (0, 0))

        self.canvas_surface = new_canvas

        self.scale = floor((self.base_layer.get_height() / self.main.canvas_height) * 0.95) if floor((self.base_layer.get_height() / self.main.canvas_height) * 0.95) > 1 else 1
        self.baseline_scale = self.scale

        self.offset_x = (self.base_layer.get_width() / 2) - ((self.main.canvas_width * self.scale) / 2)
        self.offset_y = (self.base_layer.get_height() / 2) - ((self.main.canvas_height * self.scale) / 2)

        self.temp_surface = pygame.Surface((self.main.canvas_width, self.main.canvas_height), flags=pygame.SRCALPHA)
        self.temp_surface.fill((0, 0, 0, 0))

        self.render_canvas()

    def resize(self, size):
        self.base_layer = pygame.Surface((size[0], size[1] - self.main.toolbar_height))
        self.top_layer = pygame.Surface(self.base_layer.get_size(), flags=pygame.SRCALPHA)
        self.top_layer.fill((0, 0, 0, 0))

        self.render_canvas()

    def render_canvas(self):
        pixel_offset_x = ((((self.offset_x * -1) / self.scale) - floor((self.offset_x * -1) / self.scale)) * self.scale) * -1
        pixel_offset_y = ((((self.offset_y * -1) / self.scale) - floor((self.offset_y * -1) / self.scale)) * self.scale) * -1

        x = self.offset_x if self.offset_x > 0 else pixel_offset_x
        y = self.offset_y if self.offset_y > 0 else pixel_offset_y

        scaled_canvas_width = floor(self.main.canvas_width * self.scale)
        scaled_canvas_height = floor(self.main.canvas_height * self.scale)

        #calculate cropping region of the original image
        crop_left = 0
        crop_top = 0
        crop_right = self.main.canvas_width
        crop_bottom = self.main.canvas_height

        if self.offset_x < 0:
            crop_left = floor((self.offset_x * -1) / self.scale)

        if self.offset_y < 0:
            crop_top = floor((self.offset_y * -1) / self.scale)

        if scaled_canvas_width + self.offset_x > self.base_layer.get_width():
            crop_right = floor((scaled_canvas_width - ((scaled_canvas_width + self.offset_x) - self.base_layer.get_width())) / self.scale)

        if scaled_canvas_height + self.offset_y > self.base_layer.get_height():
            crop_bottom = floor((scaled_canvas_height - ((scaled_canvas_height + self.offset_y) - self.base_layer.get_height())) / self.scale)

        #calculate width of the cropped image (so the right/bottom side of the canvas doesn't get cut off when panning)
        width = (crop_right - crop_left) + 1
        height = (crop_bottom - crop_top) + 1

        if (crop_right - crop_left == self.main.canvas_width and scaled_canvas_width + self.offset_x < self.base_layer.get_width()) or scaled_canvas_width + self.offset_x < self.base_layer.get_width():
            width = crop_right - crop_left

        if (crop_bottom - crop_top == self.main.canvas_height and scaled_canvas_height + self.offset_y < self.base_layer.get_height()) or scaled_canvas_height + self.offset_y < self.base_layer.get_height():
            height = crop_bottom - crop_top

        #crop, scale and render to screen
        combined_surface = pygame.Surface((self.main.canvas_width, self.main.canvas_height))
        combined_surface.blit(self.canvas_surface, (0, 0))
        combined_surface.blit(self.temp_surface, (0, 0))

        cropped_surface = pygame.Surface((width, height))
        cropped_surface.blit(combined_surface, (0, 0), (crop_left, crop_top, crop_right + 1, crop_bottom + 1))
        scaled_surface = pygame.transform.scale(cropped_surface, (width * self.scale, height * self.scale))

        if self.paste_box:
            self.paste_box.update()

        self.base_layer.fill((89, 89, 89))
        self.base_layer.blit(scaled_surface, (x, y))
        self.base_layer.blit(self.top_layer, (0, 0))
        self.main.window.blit(self.base_layer, (0, self.main.toolbar_height))