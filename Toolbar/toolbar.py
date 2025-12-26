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
        
        self.toolbar_surface: pygame.Surface | None = pygame.Surface((self.main.window.get_width(), 100))
        self.toolbar_surface.fill("blue")

        self.buttons = {
            "Save": Button(self, 35, 35, 10, 10, "SV", lambda: print("Save")),
            "Load": Button(self, 35, 35, 10, 55, "LD", lambda: print("Load")),
            "Draw": Button(self, 35, 80, 75, 10, "D", lambda: self.main.set_interaction_state("draw")),
            "Delete": Button(self, 35, 35, 120, 10, "DL", lambda: self.main.set_interaction_state("delete")),
            "Select": Button(self, 35, 35, 120, 55, "SL", lambda: self.main.set_interaction_state("select")),
            "Undo": Button(self, 35, 35, 195, 10, "UD", lambda: self.canvas.undo_redo.undo()),
            "Redo": Button(self, 35, 35, 195, 55, "RD", lambda: self.canvas.undo_redo.redo()),
            "Copy": Button(self, 35, 35, 240, 10, "C", lambda: self.canvas.select.copy()),
            "Paste": Button(self, 35, 35, 240, 55, "P", lambda: self.canvas.select.paste()),
            "Apply": Button(self, 35, 80, 695, 10, "A", lambda: self.canvas.set_canvas_size(self.x_input.get_value(), self.y_input.get_value())),
        }

        self.size_slider = Slider(self, 250, 35, 305, 10, lambda: self.main.set_brush_size(self.size_slider.get_value()))
        self.color_picker = ColorPicker(self, 250, 35, 305, 55, lambda: self.main.set_color(self.color_picker.get_color()))

        self.x_input = Input(self, 100, 35, 585, 10, lambda: print("X Input"))
        self.y_input = Input(self, 100, 35, 585, 55, lambda: print("Y Input"))

        self.update()

    def update(self):
        assert self.toolbar_surface
        self.main.window.blit(self.toolbar_surface, (0, 0))

    def toolbar_collision(self):
        assert self.toolbar_surface

        toolbar_rect = self.toolbar_surface.get_rect(topleft = (0, 0))
        return toolbar_rect.collidepoint(pygame.mouse.get_pos())

    def event_poll(self, events):
        if not self.toolbar_collision(): return

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for element in self.buttons.values():
                    element.click()

                self.size_slider.begin_move()
                self.color_picker.begin_move()
                self.x_input.set_focus()
                self.y_input.set_focus()
            elif event.type == pygame.MOUSEMOTION:
                self.size_slider.set_value()
                self.color_picker.set_value()
            elif event.type == pygame.MOUSEBUTTONUP:
                self.size_slider.end_move()
                self.color_picker.end_move()
            elif event.type == pygame.KEYDOWN:
                self.x_input.add_input(event)
                self.y_input.add_input(event)

                if event.key == pygame.K_BACKSPACE:
                    self.x_input.remove_input()
                    self.y_input.remove_input()