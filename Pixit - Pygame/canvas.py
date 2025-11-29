import pygame
from PIL import Image, ImageDraw

class Canvas:
    def __init__(self, window: pygame.Surface) -> None:
        self.window = window
        self.canvas = pygame.Surface(pygame.display.get_surface().get_size())

        self.scale = 1

        self.offset_x = 0
        self.offset_y = 0

        self.start_x = 0
        self.start_y = 0

        self.main_image = Image.new("RGBA", (50, 50), "white")
        ImageDraw.Draw(self.main_image).rectangle((0, 0, 25, 25), "red")

        self.pygame_main_image = pygame.image.fromstring(self.main_image.tobytes(), self.main_image.size, "RGBA")
        self.pygame_scaled_image = self.pygame_main_image

        self.update()

    def update(self):
        self.canvas.fill("green")
        self.canvas.blit(self.pygame_scaled_image, (self.offset_x, self.offset_y))
        self.window.blit(self.canvas, (0, 0))

    def event_poll(self, events):
        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                self.zoom(event)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
                self.begin_pan(event)
            elif event.type == pygame.MOUSEMOTION and event.buttons == (0, 1, 0):
                self.pan()

    def zoom(self, event):
        global scale, offset_x, offset_y, scaled

        PREV_SCALE = self.scale

        if event.y == 1:
            self.scale = self.scale * 1.05
            print(self.scale)
        elif event.y == -1:
            self.scale = self.scale * 0.95

        SCALE = self.scale

        x = pygame.mouse.get_pos()[0]
        y = pygame.mouse.get_pos()[1]

        self.offset_x = x - (x - self.offset_x) * (SCALE / PREV_SCALE)
        self.offset_y = y - (y - self.offset_y) * (SCALE / PREV_SCALE)

        self.pygame_scaled_image = pygame.transform.scale(self.pygame_main_image, (50 * self.scale, 50 * self.scale))
        self.update()

    def begin_pan(self, event):
        self.start_x = event.pos[0]
        self.start_y = event.pos[1]

    def pan(self):
        self.offset_x += pygame.mouse.get_pos()[0] - self.start_x
        self.offset_y += pygame.mouse.get_pos()[1] - self.start_y

        self.start_x = pygame.mouse.get_pos()[0]
        self.start_y = pygame.mouse.get_pos()[1]