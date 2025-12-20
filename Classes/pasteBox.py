import pygame
from math import ceil, floor
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import canvas

class PasteBox:
    def __init__(self, canvas: "canvas.Canvas") -> None:
        self.canvas = canvas

        assert self.canvas.copied_area is not None
        self.ref = self.canvas.copied_area

        self.copied_area = self.ref
        self.scaled_area = self.ref

        self.grid_x = floor((pygame.mouse.get_pos()[0] - self.canvas.offset_x) / self.canvas.scale) - floor(self.copied_area.get_width() / 2)
        self.grid_y = floor((pygame.mouse.get_pos()[1] - self.canvas.offset_y) / self.canvas.scale) - floor(self.copied_area.get_width() / 2)
        self.right = self.grid_x + self.copied_area.get_width()
        self.bottom = self.grid_y + self.copied_area.get_height()

        self.top_left = None
        self.bottom_left = None
        self.top_right = None
        self.bottom_right = None

        self.is_moving = False
        self.is_scaling = False

        self.selected_node = ""

        self.update()

    def update(self):
        self.canvas.top_layer.fill((0, 0, 0, 0))

        canvas_x = (self.grid_x * self.canvas.scale) + self.canvas.offset_x
        canvas_y = (self.grid_y * self.canvas.scale) + self.canvas.offset_y

        self.scaled_area = pygame.transform.scale(self.copied_area, (self.copied_area.get_width() * self.canvas.scale, self.copied_area.get_height() * self.canvas.scale))

        self.canvas.top_layer.blit(self.scaled_area, (canvas_x, canvas_y))

        pygame.draw.rect(self.canvas.top_layer, "red", (canvas_x, canvas_y, self.scaled_area.get_width(), self.scaled_area.get_height()), 1)
        
        self.top_left = pygame.draw.rect(self.canvas.top_layer, "red", (canvas_x, 
                                                                        canvas_y, 
                                                                        self.canvas.scale / 3, 
                                                                        self.canvas.scale / 3))
        
        self.bottom_left = pygame.draw.rect(self.canvas.top_layer, "red", (canvas_x, 
                                                                           (canvas_y + self.scaled_area.get_height()) - (self.canvas.scale / 3), 
                                                                           self.canvas.scale / 3, 
                                                                           self.canvas.scale / 3))
        
        self.top_right = pygame.draw.rect(self.canvas.top_layer, "red", ((canvas_x + self.scaled_area.get_width()) - (self.canvas.scale / 3), 
                                                                         canvas_y, 
                                                                         self.canvas.scale / 3, 
                                                                         self.canvas.scale / 3))
        
        self.bottom_right = pygame.draw.rect(self.canvas.top_layer, "red", ((canvas_x + self.scaled_area.get_width()) - (self.canvas.scale / 3), 
                                                                            (canvas_y + self.scaled_area.get_height()) - (self.canvas.scale / 3), 
                                                                            self.canvas.scale / 3, 
                                                                            self.canvas.scale / 3))

    def collision(self):
        canvas_x = (self.grid_x * self.canvas.scale) + self.canvas.offset_x
        canvas_y = (self.grid_y * self.canvas.scale) + self.canvas.offset_y
        copied_area_rect = self.scaled_area.get_rect(topleft = (canvas_x, canvas_y))

        if self.top_left and self.top_left.collidepoint(pygame.mouse.get_pos()): # type: ignore
            self.selected_node = "top_left"
            return "node"
        elif self.bottom_left and self.bottom_left.collidepoint(pygame.mouse.get_pos()):
            self.selected_node = "bottom_left"
            return "node"
        elif self.top_right and self.top_right.collidepoint(pygame.mouse.get_pos()):
            self.selected_node = "top_right"
            return "node"
        elif self.bottom_right and self.bottom_right.collidepoint(pygame.mouse.get_pos()):
            self.selected_node = "bottom_right"
            return "node"
        elif copied_area_rect.collidepoint(pygame.mouse.get_pos()):
            return "copied_area"
        
    def begin_scale(self):
        self.is_scaling = True

        self.right = self.grid_x + self.copied_area.get_width()
        self.bottom = self.grid_y + self.copied_area.get_height()
    
    def scale(self):
        gx = (pygame.mouse.get_pos()[0] - self.canvas.offset_x) / self.canvas.scale
        gy = (pygame.mouse.get_pos()[1] - self.canvas.offset_y) / self.canvas.scale

        size_x = 0
        size_y = 0

        if self.selected_node == "top_left":
            size_x = self.right - ceil(gx) if self.right - ceil(gx) > 1 else 1
            size_y = self.bottom - ceil(gy) if self.bottom - ceil(gy) > 1 else 1

            self.grid_x = self.right - size_x
            self.grid_y = self.bottom - size_y
        elif self.selected_node == "bottom_left":
            size_x = self.right - ceil(gx) if self.right - ceil(gx) > 1 else 1
            size_y = gy - self.grid_y if gy - self.grid_y > 1 else 1

            self.grid_x = self.right - size_x
        elif self.selected_node == "top_right":
            size_x = gx - self.grid_x if gx - self.grid_x > 1 else 1
            size_y = self.bottom - ceil(gy) if self.bottom - ceil(gy) > 1 else 1

            self.grid_y = self.bottom - size_y
        elif self.selected_node == "bottom_right":
            size_x = gx - self.grid_x if gx - self.grid_x > 1 else 1
            size_y = gy - self.grid_y if gy - self.grid_y > 1 else 1

        self.copied_area = pygame.transform.scale(self.ref, (size_x, size_y))

        self.update()
        self.canvas.render_canvas()

    def stop_scaling(self):
        self.selected_node = ""
        self.is_scaling = False
    
    def begin_move(self):
        self.is_moving = True
    
    def move(self):
        x = floor((pygame.mouse.get_pos()[0] - self.canvas.offset_x) / self.canvas.scale) - floor(self.copied_area.get_width() / 2)
        y = floor((pygame.mouse.get_pos()[1] - self.canvas.offset_y) / self.canvas.scale) - floor(self.copied_area.get_height() / 2)

        self.grid_x = x
        self.grid_y = y

        self.update()
        self.canvas.render_canvas()

    def stop_moving(self):
        self.is_moving = False

    def commit_paste(self):
        self.canvas.canvas_surface.blit(self.copied_area, (self.grid_x, self.grid_y))
        self.clear_paste_box()

    def clear_paste_box(self):
        self.canvas.paste_box = None
        self.canvas.top_layer.fill((0, 0, 0, 0))
        self.canvas.render_canvas()