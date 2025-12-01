import pygame
from PIL import Image, ImageDraw
from math import ceil, floor
import time

def ex_time(func):
    def wrapper(*args, **kwargs) -> None:
        s = time.time()
        func(*args, **kwargs)
        e = time.time()
        print(e-s)
    return wrapper

class Canvas:
    def __init__(self, window: pygame.Surface) -> None:
        self.window = window
        self.canvas = pygame.Surface(pygame.display.get_surface().get_size())

        self.scale = 1
        self.pixel_size = 1

        self.offset_x = 0
        self.offset_y = 0

        self.start_x = 0
        self.start_y = 0

        self.main_image = Image.new("RGBA", (50, 50), "white")
        ImageDraw.Draw(self.main_image).rectangle((0, 0, 25, 25), "red")

        self.pygame_main_image = pygame.image.fromstring(self.main_image.tobytes(), self.main_image.size, "RGBA")
        self.pygame_scaled_image = self.pygame_main_image

        self.update()

    @ex_time
    def update(self, event=None):
        coord_x = self.offset_x if self.offset_x > 0 else 0
        coord_y = self.offset_y if self.offset_y > 0 else 0

        self.render_canvas()

        self.canvas.fill("green")
        self.canvas.blit(self.pygame_scaled_image, (coord_x, coord_y))
        self.window.blit(self.canvas, (0, 0))

    def set_offset(self, x: float, y: float):
        canvas_width = self.main_image.width * self.scale
        canvas_height = self.main_image.height * self.scale

        screen_width = self.canvas.get_width()
        screen_height = self.canvas.get_height()
        
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

    def render_canvas(self):
        canvas_width = self.main_image.width * self.scale
        canvas_height = self.main_image.height * self.scale

        crop_left = 0
        crop_top = 0
        crop_right = canvas_width
        crop_bottom = canvas_height

        if self.offset_x < 0:
            crop_left = self.offset_x * -1

        if self.offset_y < 0:
            crop_top = self.offset_y * -1

        if canvas_width + self.offset_x > self.canvas.get_width():
            crop_right = canvas_width - ((canvas_width + self.offset_x) - self.canvas.get_width())

        if canvas_height + self.offset_y > self.canvas.get_height():
            crop_bottom = canvas_height - ((canvas_height + self.offset_y) - self.canvas.get_height())

        cropped = pygame.Surface((floor(crop_right - crop_left) / self.scale, 
                                  ceil(crop_bottom - crop_top) / self.scale))
        
        cropped.blit(self.pygame_main_image, (0, 0), (floor(crop_left / self.scale), 
                                                      floor(crop_top / self.scale), 
                                                      ceil(crop_right / self.scale), 
                                                      ceil(crop_bottom / self.scale)))
        
        self.pygame_scaled_image = pygame.transform.scale(cropped, (floor(crop_right - crop_left), 
                                                                    ceil(crop_bottom - crop_top)))

    def event_poll(self, events):
        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                self.zoom(event)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                self.begin_pan(event)
            elif event.type == pygame.MOUSEMOTION and event.buttons == (0, 1, 0):
                self.pan()
            elif event.type == pygame.MOUSEMOTION:
                self.place_pixel(event)

    def place_pixel(self, event):
        GRID_X = floor((event.pos[0] - self.offset_x) / self.scale)
        GRID_Y = floor((event.pos[1] - self.offset_y) / self.scale)

        if GRID_X < 0 or GRID_X > self.main_image.width: return
        if GRID_Y < 0 or GRID_Y > self.main_image.height: return

        start_x = floor((GRID_X - floor(self.pixel_size / 2)) * self.scale)
        start_y = floor((GRID_Y - floor(self.pixel_size / 2)) * self.scale)

        end_x = start_x + floor(self.pixel_size * self.scale)
        end_y = start_y + floor(self.pixel_size * self.scale)

        if start_x < 0:
            start_x = 0

        if start_y < 0:
            start_y = 0

        if end_x > self.pygame_scaled_image.get_width():
            end_x = self.pygame_scaled_image.get_width()

        if end_y > self.pygame_scaled_image.get_height():
            end_y = self.pygame_scaled_image.get_height()

        start = floor(self.pygame_scaled_image.get_width() / self.main_image.width) * GRID_X
        end = floor(self.pygame_scaled_image.get_width() / self.main_image.width) * (GRID_X + 1)

        def draw():
            pygame.draw.rect(self.canvas, "blue", ((start_x + self.offset_x), 
                                                   (start_y + self.offset_y), 
                                                   end_x - start_x, 
                                                   end_y - start_y))

        self.update(draw)

    def zoom(self, event):
        global scale, offset_x, offset_y, scaled

        PREV_SCALE = self.scale

        if event.y == 1 and floor(self.scale) <= 100:
            self.scale = floor(self.scale + 1)
        elif event.y == -1 and floor(self.scale) > 1:
            self.scale = floor(self.scale - 1)
        else:
            return

        SCALE = self.scale

        x = pygame.mouse.get_pos()[0] - (pygame.mouse.get_pos()[0] - self.offset_x) * (SCALE / PREV_SCALE)
        y = pygame.mouse.get_pos()[1] - (pygame.mouse.get_pos()[1] - self.offset_y) * (SCALE / PREV_SCALE)

        self.set_offset(x, y)
        self.update()

    def begin_pan(self, event):
        self.start_x = event.pos[0]
        self.start_y = event.pos[1]

    def pan(self):
        x = self.offset_x + (pygame.mouse.get_pos()[0] - self.start_x)
        y = self.offset_y + (pygame.mouse.get_pos()[1] - self.start_y)

        self.set_offset(x, y)
        self.update()

        self.start_x = pygame.mouse.get_pos()[0]
        self.start_y = pygame.mouse.get_pos()[1]
