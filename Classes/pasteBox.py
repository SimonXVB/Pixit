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

        self.grid_x = floor((pygame.mouse.get_pos()[0] - self.canvas.offset_x) / self.canvas.scale) - floor(self.copied_area.get_width() / 2)
        self.grid_y = floor((pygame.mouse.get_pos()[1] - self.canvas.offset_y) / self.canvas.scale) - floor(self.copied_area.get_width() / 2)

        self.right = 0
        self.bottom = 0

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
        
        self.top_left = pygame.draw.rect(self.canvas.top_layer, "red", (canvas_x - (self.canvas.scale / 4), 
                                                                        canvas_y - (self.canvas.scale / 4), 
                                                                        self.canvas.scale / 2, 
                                                                        self.canvas.scale / 2))
        
        self.bottom_left = pygame.draw.rect(self.canvas.top_layer, "red", (canvas_x - (self.canvas.scale / 4), 
                                                                           (canvas_y + self.scaled_area.get_height()) - (self.canvas.scale / 4), 
                                                                           self.canvas.scale / 2, 
                                                                           self.canvas.scale / 2))
        
        self.top_right = pygame.draw.rect(self.canvas.top_layer, "red", ((canvas_x + self.scaled_area.get_width()) - (self.canvas.scale / 4), 
                                                                         canvas_y - (self.canvas.scale / 4), 
                                                                         self.canvas.scale / 2, 
                                                                         self.canvas.scale / 2))
        
        self.bottom_right = pygame.draw.rect(self.canvas.top_layer, "red", ((canvas_x + self.scaled_area.get_width()) - (self.canvas.scale / 4), 
                                                                            (canvas_y + self.scaled_area.get_height()) - (self.canvas.scale / 4), 
                                                                            self.canvas.scale / 2, 
                                                                            self.canvas.scale / 2))

    def collision(self):
        canvas_x = (self.grid_x * self.canvas.scale) + self.canvas.offset_x
        canvas_y = (self.grid_y * self.canvas.scale) + self.canvas.offset_y
        copied_area_rect = self.scaled_area.get_rect(topleft = (canvas_x, canvas_y))

        if self.top_left.collidepoint(pygame.mouse.get_pos()):
            self.selected_node = "top_left"
            return "node"
        elif self.bottom_left.collidepoint(pygame.mouse.get_pos()):
            self.selected_node = "bottom_left"
            return "node"
        elif self.top_right.collidepoint(pygame.mouse.get_pos()):
            self.selected_node = "top_right"
            return "node"
        elif self.bottom_right.collidepoint(pygame.mouse.get_pos()):
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

        if self.selected_node == "top_left":
            self.top_left_scale(gx, gy)
        elif self.selected_node == "bottom_left":
            self.bottom_left_scale(gx, gy)
        elif self.selected_node == "top_right":
            self.top_right_scale(gx, gy)
        elif self.selected_node == "bottom_right":
            self.bottom_right_scale(gx, gy)

        self.update()
        self.canvas.render_canvas()

    def top_left_scale(self, gx, gy):
            diff_x = self.right - ceil(gx)
            diff_y = self.bottom - ceil(gy)
            
            if diff_x < 1: diff_x = 1
            if diff_y < 1: diff_y = 1

            self.copied_area = pygame.transform.scale(self.ref, (diff_x, diff_y))

            self.grid_x = self.right - self.copied_area.get_width()
            self.grid_y = self.bottom - self.copied_area.get_height()
    
    def bottom_left_scale(self, gx, gy):
        diff_x = self.right - ceil(gx)
        diff_y = gy - self.grid_y

        if diff_x < 1: diff_x = 1
        if diff_y < 1: diff_y = 1

        self.copied_area = pygame.transform.scale(self.ref, (diff_x, diff_y))
        self.grid_x = self.right - self.copied_area.get_width()

    def top_right_scale(self, gx, gy):
        diff_x = gx - self.grid_x
        diff_y = self.bottom - ceil(gy)

        if diff_x < 1: diff_x = 1
        if diff_y < 1: diff_y = 1

        self.copied_area = pygame.transform.scale(self.ref, (diff_x, diff_y))
        self.grid_y = self.bottom - self.copied_area.get_height()

    def bottom_right_scale(self, gx, gy):
        diff_x = gx - self.grid_x
        diff_y = gy - self.grid_y

        if diff_x < 1: diff_x = 1
        if diff_y < 1: diff_y = 1

        self.copied_area = pygame.transform.scale(self.ref, (diff_x, diff_y))

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

        self.canvas.top_layer.fill((0, 0, 0, 0))
        self.canvas.paste_box = None
        
        self.canvas.render_canvas()