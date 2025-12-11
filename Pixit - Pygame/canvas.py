import pygame
from typing import TYPE_CHECKING
from math import ceil, floor
import time

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

        self.main.scale = (self.base_layer.get_height() / self.main.canvas_height) * 0.95
        self.main.baseline_scale = self.main.scale

        self.offset_x = 0
        self.offset_y = 0

        self.start_x = 0
        self.start_y = 0

        self.copied_area_coords = {"left": 0, "top": 0, "right": 0, "bottom": 0, "height": 0, "width": 0}
        self.copied_area = None

        self.canvas_surface = pygame.Surface((self.main.canvas_width, self.main.canvas_height))
        self.canvas_surface.fill("white")
        pygame.draw.rect(self.canvas_surface, "red", (10, 10, 10, 10))

        self.temp_surface = pygame.Surface((self.main.canvas_width, self.main.canvas_height), flags=pygame.SRCALPHA)
        self.temp_surface.fill((0, 0, 0, 0))

        self.render_canvas()

    def event_poll(self, events):
        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                self.zoom(event)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                self.begin_pan(event)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # self.draw(event)
                self.begin_select(event)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                self.delete(event)
            elif event.type == pygame.MOUSEMOTION and event.buttons == (1, 0, 0):
                # self.cursor(event)
                # self.draw(event)
                self.select(event)
            elif event.type == pygame.MOUSEMOTION and event.buttons == (0, 1, 0):
                self.pan()
            elif event.type == pygame.MOUSEMOTION and event.buttons == (0, 0, 1):
                self.cursor(event)
                self.delete(event)
            elif event.type == pygame.MOUSEMOTION:
                pass
                #self.cursor(event)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.copy()
                elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.paste()

    def render_canvas(self):
        pixel_offset_x = ((((self.offset_x * -1) / self.main.scale) - floor((self.offset_x * -1) / self.main.scale)) * self.main.scale) * -1
        pixel_offset_y = ((((self.offset_y * -1) / self.main.scale) - floor((self.offset_y * -1) / self.main.scale)) * self.main.scale) * -1

        x = self.offset_x if self.offset_x > 0 else pixel_offset_x
        y = self.offset_y if self.offset_y > 0 else pixel_offset_y

        canvas_width = floor(self.canvas_surface.get_width() * self.main.scale)
        canvas_height = floor(self.canvas_surface.get_height() * self.main.scale)

        #calculate cropping region of the original image
        crop_left = 0
        crop_top = 0
        crop_right = self.canvas_surface.get_width()
        crop_bottom = self.canvas_surface.get_height()

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

        if (crop_right - crop_left == self.canvas_surface.get_width() and canvas_width + self.offset_x < self.base_layer.get_width()) or canvas_width + self.offset_x < self.base_layer.get_width():
            width = crop_right - crop_left

        if (crop_bottom - crop_top == self.canvas_surface.get_height() and canvas_height + self.offset_y < self.base_layer.get_height()) or canvas_height + self.offset_y < self.base_layer.get_height():
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
        self.window.blit(self.base_layer, (0, 0))
        self.window.blit(self.top_layer, (0, 0))

    def set_offset(self, x: float, y: float):
        canvas_width = self.canvas_surface.get_width() * self.main.scale
        canvas_height = self.canvas_surface.get_height() * self.main.scale

        screen_width = self.base_layer.get_width()
        screen_height = self.base_layer.get_height()
        
        if canvas_width < screen_width:
            if (canvas_width / 2) * -1 < x < screen_width - (canvas_width / 2):
                self.offset_x = x
            elif x < (canvas_width / 2) * -1:
                self.offset_x = (canvas_width / 2) * -1
            elif x > screen_width - (canvas_width / 2):
                self.offset_x = screen_width - (canvas_width / 2)
        else:
            if (screen_width / 2) - canvas_width < x < screen_width / 2:
                self.offset_x = x
            elif x <  (screen_width / 2) - canvas_width:
                self.offset_x = (screen_width / 2) - canvas_width
            elif x > screen_width / 2:
                self.offset_x = screen_width / 2

        if canvas_height < screen_height:
            if (canvas_height / 2) * -1 < y < screen_height - (canvas_height / 2):
                self.offset_y = y
            elif y < (canvas_height / 2) * -1:
                self.offset_y = (canvas_height / 2) * -1
            elif y > screen_height - (canvas_height / 2):
                self.offset_y = screen_height - (canvas_height / 2)
        else:
            if (screen_height / 2) - canvas_height < y < screen_height / 2:
                self.offset_y = y
            elif y < (screen_height / 2) - canvas_height:
                self.offset_y = (screen_height / 2) - canvas_height
            elif y > screen_height / 2:
                self.offset_y = screen_height / 2

    def get_pixel_coords(self, event) -> dict[str, int] | None:
        GRID_X = floor((event.pos[0] - self.offset_x) / self.main.scale)
        GRID_Y = floor((event.pos[1] - self.offset_y) / self.main.scale)

        if GRID_X < 0 or GRID_X > self.canvas_surface.get_height(): return
        if GRID_Y < 0 or GRID_Y > self.canvas_surface.get_width(): return

        start_x: int = floor(GRID_X - floor(self.main.pixel_size / 2))
        start_y: int = floor(GRID_Y - floor(self.main.pixel_size / 2))

        end_x: int = start_x + self.main.pixel_size
        end_y: int = start_y + self.main.pixel_size

        if start_x < 0:
            start_x = 0

        if start_y < 0:
            start_y = 0

        if end_x > self.canvas_surface.get_width():
            end_x = self.canvas_surface.get_width()

        if end_y > self.canvas_surface.get_height():
            end_y = self.canvas_surface.get_height()

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
            self.temp_surface.fill((0, 0, 0, 0))
            pygame.draw.rect(self.temp_surface, "blue", (coords["start_x"], coords["start_y"], coords["width"], coords["height"]))
            self.render_canvas()

    def draw(self, event):
        coords = self.get_pixel_coords(event)

        if coords:
            pygame.draw.rect(self.canvas_surface, "red", (coords["start_x"], coords["start_y"], coords["width"], coords["height"]))
            self.render_canvas()

    def delete(self, event):
        coords = self.get_pixel_coords(event)

        if coords:
            pygame.draw.rect(self.canvas_surface, "white", (coords["start_x"], coords["start_y"], coords["width"], coords["height"]))
            self.render_canvas()

    def zoom(self, event):
        PREV_SCALE = self.main.scale
        SCALE_INTERVAL = self.main.baseline_scale * 0.05

        if event.y == 1 and self.main.scale <= self.main.baseline_scale * 10:
            self.main.scale = self.main.scale + SCALE_INTERVAL
        elif event.y == -1 and self.main.scale > self.main.baseline_scale * 0.1:
            self.main.scale = self.main.scale - SCALE_INTERVAL
        else:
            return

        SCALE = self.main.scale

        x = floor(pygame.mouse.get_pos()[0] - (pygame.mouse.get_pos()[0] - self.offset_x) * (SCALE / PREV_SCALE))
        y = floor(pygame.mouse.get_pos()[1] - (pygame.mouse.get_pos()[1] - self.offset_y) * (SCALE / PREV_SCALE))

        self.set_offset(x, y)
        self.render_canvas()

    def begin_pan(self, event):
        self.start_x = event.pos[0]
        self.start_y = event.pos[1]

    def pan(self):
        x = self.offset_x + (pygame.mouse.get_pos()[0] - self.start_x)
        y = self.offset_y + (pygame.mouse.get_pos()[1] - self.start_y)

        self.set_offset(x, y)
        self.render_canvas()

        self.start_x = pygame.mouse.get_pos()[0]
        self.start_y = pygame.mouse.get_pos()[1]

    def begin_select(self, event):
        self.start_x = event.pos[0]
        self.start_y = event.pos[1]

    def select(self, event):
        left = floor((self.start_x - self.offset_x) / self.main.scale)
        top = floor((self.start_y - self.offset_y) / self.main.scale)
        right = ceil((event.pos[0] - self.offset_x) / self.main.scale)
        bottom = ceil((event.pos[1] - self.offset_y) / self.main.scale)

        if left < 0:
            left = 0
        
        if top < 0:
            top = 0
        
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

        self.top_layer.fill((0, 0, 0, 0))
        pygame.draw.rect(self.top_layer, (0, 98, 255, 85), (ceil(left * self.main.scale) + self.offset_x, 
                                                            ceil(top * self.main.scale) + self.offset_y, 
                                                            ceil(width * self.main.scale), 
                                                            ceil(height * self.main.scale)))
        self.render_canvas()

    def copy(self):
        self.copied_area = pygame.Surface((self.copied_area_coords["width"], self.copied_area_coords["height"]))
        self.copied_area.blit(self.canvas_surface, (0, 0), (self.copied_area_coords["left"], 
                                                            self.copied_area_coords["top"], 
                                                            self.copied_area_coords["right"], 
                                                            self.copied_area_coords["bottom"]))
    
    def paste(self):
        if self.copied_area == None: return

        x = floor((pygame.mouse.get_pos()[0] - self.offset_x) / self.main.scale) - floor(self.copied_area_coords["width"] / 2)
        y = floor((pygame.mouse.get_pos()[1] - self.offset_y) / self.main.scale) - floor(self.copied_area_coords["height"] / 2)

        self.temp_surface.blit(self.copied_area, (x, y))
        self.render_canvas()