import pygame
from sys import exit
from canvas import Canvas

class Main:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Pixit")

        self.window = pygame.display.set_mode((1820, 980), vsync=1)
        self.clock = pygame.time.Clock()
        self.canvas = Canvas(main=self, window=self.window)

        #app data
        self.pixel_size = 5

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

            #print(self.clock.get_fps())

            pygame.display.update()
            self.clock.tick(120)

if __name__ == "__main__":
    Main()