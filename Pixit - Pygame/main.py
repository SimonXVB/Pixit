import pygame
from sys import exit
from canvas import Canvas

class Main:
    def __init__(self) -> None:
        pygame.init()

        self.window = pygame.display.set_mode((1280, 720), vsync=1)
        self.clock = pygame.time.Clock()
        self.canvas = Canvas(self.window)

        #starts the event loop
        self.event_loop()

    def event_loop(self):
        while True:
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            self.canvas.event_poll(events)
            self.canvas.update()

            pygame.display.update()
            self.clock.tick(120)

if __name__ == "__main__":
    Main()