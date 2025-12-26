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
        self.window = pygame.display.set_mode((1820, 980), vsync=1)

        self.toolbar_height = 100
        self.interaction_state = "draw"

        self.canvas = Canvas(main=self)
        self.toolbar = Toolbar(main=self, canvas=self.canvas)

        self.clock = pygame.time.Clock()

        #start the event loop
        self.event_loop()

    def set_interaction_state(self, state: str):
        self.interaction_state = state

    def set_brush_size(self, value: float):
        min = 1
        max = 150

        new_size = int(max * value)

        if new_size > max: new_size = max
        if new_size < min: new_size = min

        self.canvas.pixel_size = new_size

    def set_color(self, color: pygame.Color):
        print(color)

        self.canvas.color = color

    def event_loop(self):
        while True:
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            self.toolbar.event_poll(events)
            self.canvas.event_poll(events)

            #print(self.clock.get_fps())

            pygame.display.update()
            self.clock.tick(120)

if __name__ == "__main__":
    Main()