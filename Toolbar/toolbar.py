import pygame
from typing import TYPE_CHECKING
from Toolbar.Classes.button import Button
from Toolbar.Classes.slider import Slider
from Toolbar.Classes.input import Input
from Toolbar.Classes.color_picker import ColorPicker

if TYPE_CHECKING:
    from main import Main
    from Canvas.canvas import Canvas

class Toolbar:
    def __init__(self, main: "Main", canvas: "Canvas") -> None:
        self.main = main
        self.canvas = canvas
        
        self.toolbar_surface: pygame.Surface = pygame.Surface((self.main.window.get_width(), 100))
        self.toolbar_surface.fill(self.main.colors["secondary"])
        pygame.draw.line(self.toolbar_surface, self.main.colors["border"], (0, self.toolbar_surface.get_height()), (self.toolbar_surface.get_width(), self.toolbar_surface.get_height()), 5)

        self.buttons = {
            "Save": Button(self, 35, 35, 10, 10, "SV", lambda: self.main.save_img()),
            "Load": Button(self, 35, 35, 10, 55, "LD", lambda: self.main.load_img()),
            "Draw": Button(self, 35, 80, 75, 10, "D", lambda: self.main.set_interaction_state("draw")),
            "Delete": Button(self, 35, 35, 120, 10, "DL", lambda: self.main.set_interaction_state("delete")),
            "Select": Button(self, 35, 35, 120, 55, "SL", lambda: self.main.set_interaction_state("select")),
            "Undo": Button(self, 35, 35, 195, 10, "UD", lambda: self.canvas.undo_redo.undo()),
            "Redo": Button(self, 35, 35, 195, 55, "RD", lambda: self.canvas.undo_redo.redo()),
            "Copy": Button(self, 35, 35, 240, 10, "C", lambda: self.canvas.select.copy()),
            "Paste": Button(self, 35, 35, 240, 55, "P", lambda: self.canvas.select.paste()),
            "Apply": Button(self, 35, 80, 745, 10, "A", lambda: self.canvas.set_canvas_size(self.x_input.get_value(), self.y_input.get_value())),
        }

        self.size_slider = Slider(self, 250, 35, 305, 10, str(self.main.pixel_size), lambda: self.main.set_brush_size(self.size_slider.get_value()))
        self.color_picker = ColorPicker(self, 250, 35, 305, 55, lambda: self.main.set_color(self.color_picker.get_color()))

        self.x_input = Input(self, 150, 35, 585, 10, "X")
        self.y_input = Input(self, 150, 35, 585, 55, "Y")

        self.x_input.set_value(self.main.canvas_width)
        self.y_input.set_value(self.main.canvas_height)

        self.update()

    def update(self):
        self.main.window.blit(self.toolbar_surface, (0, 0))

    def resize(self, size):
        self.toolbar_surface: pygame.Surface = pygame.Surface((self.main.window.get_width(), 100))
        self.toolbar_surface.fill(self.main.colors["secondary"])
        pygame.draw.line(self.toolbar_surface, self.main.colors["border"], (0, self.toolbar_surface.get_height()), (self.toolbar_surface.get_width(), self.toolbar_surface.get_height()), 5)

        for element in self.buttons.values():
            element.update()

        self.size_slider.update()
        self.color_picker.update()

        self.x_input.update()
        self.y_input.update()

        self.update()

    def toolbar_collision(self):
        toolbar_rect = self.toolbar_surface.get_rect(topleft = (0, 0))
        return toolbar_rect.collidepoint(pygame.mouse.get_pos())

    def event_poll(self, events):
        for event in events:
            for element in self.buttons.values():
                element.event_poll(event)
            
            self.size_slider.event_poll(event)
            self.color_picker.event_poll(event)

            self.x_input.event_poll(event)
            self.y_input.event_poll(event)