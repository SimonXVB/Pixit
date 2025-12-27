from math import ceil
import pygame
from sys import exit
from Canvas.canvas import Canvas
from Toolbar.toolbar import Toolbar

class Main:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Pixit")

        #init
        self.window = pygame.display.set_mode((1820, 980), vsync=1, flags=pygame.RESIZABLE)

        self.color: pygame.Color = pygame.Color((255, 0, 0, 255))
        self.bg_color = pygame.Color((255, 255, 255))
        self.pixel_size: int = 5
        self.canvas_width: int = 50
        self.canvas_height: int = 50
        self.toolbar_height = 100
        self.interaction_state = "draw"

        self.colors = {
            "primary": pygame.Color((115, 115, 115, 255)),
            "secondary": pygame.Color((66, 66, 66, 255)),
            "auxiliary": pygame.Color((145, 145, 145, 255)),
            "border": pygame.Color((33, 33, 33, 255))
        }

        self.canvas = Canvas(main=self)
        self.toolbar = Toolbar(main=self, canvas=self.canvas)

        self.clock = pygame.time.Clock()

        #start the event loop
        self.event_loop()

    def resize(self, event):
        width, height = event.size

        if width < 750:
            width = 750

        if height < 650:
            height = 650

        self.window = pygame.display.set_mode((width, height), vsync=1, flags=pygame.RESIZABLE)
        self.toolbar.resize((width, height))
        self.canvas.resize((width, height))

    def set_interaction_state(self, state: str):
        if self.interaction_state == state: return

        if self.canvas.paste_box:
            self.canvas.paste_box.commit_paste()

        self.interaction_state = state

    def set_brush_size(self, value: float):
        min = 1
        max = 150

        new_size = int(max * value)

        if new_size > max: new_size = max
        if new_size < min: new_size = min

        self.toolbar.size_slider.set_label_text(str(new_size))

        self.pixel_size = new_size

    def set_color(self, color: pygame.Color):
        self.color = color

    def event_loop(self):
        while True:
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.VIDEORESIZE:
                    self.resize(event)

            self.toolbar.event_poll(events)
            self.canvas.event_poll(events)

            pygame.display.update()
            self.clock.tick(120)

if __name__ == "__main__":
    Main()