import pygame
from sys import exit
from canvas import Canvas

pygame.init()
window = pygame.display.set_mode((1280, 720), vsync=1)
clock = pygame.time.Clock()

events = []
canvas = Canvas(window)

while True:
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    canvas.event_poll(events)
    canvas.update()

    pygame.display.update()
    clock.tick(120)