import pygame
from math import ceil, floor
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import canvas

class PasteBox:
    def __init__(self, canvas: "canvas.Canvas") -> None:
        self.canvas = canvas

        assert self.canvas.copied_area is not None
        self.copied_area = self.canvas.copied_area
        self.scaled_copied_area = self.copied_area
        self.canvas_copied_area = pygame.transform.scale(self.scaled_copied_area, (self.scaled_copied_area.get_width() * self.canvas.scale, 
                                                                                   self.scaled_copied_area.get_height() * self.canvas.scale))

        self.grid_x = floor((pygame.mouse.get_pos()[0] - self.canvas.offset_x) / self.canvas.scale) - floor(self.scaled_copied_area.get_width() / 2)
        self.grid_y = floor((pygame.mouse.get_pos()[1] - self.canvas.offset_y) / self.canvas.scale) - floor(self.scaled_copied_area.get_height() / 2)
        self.right = self.grid_x + self.scaled_copied_area.get_width()
        self.bottom = self.grid_y + self.scaled_copied_area.get_height()

        self.is_moving = False
        self.is_scaling = False

        self.top_left_node = None
        self.bottom_left_node = None
        self.top_right_node = None
        self.bottom_right_node = None

        self.selected_node = ""

        self.update()

    def update(self):
        self.canvas.top_layer.fill((0, 0, 0, 0))

        canvas_x = (self.grid_x * self.canvas.scale) + self.canvas.offset_x
        canvas_y = (self.grid_y * self.canvas.scale) + self.canvas.offset_y

        self.canvas_copied_area = pygame.transform.scale(self.scaled_copied_area, (self.scaled_copied_area.get_width() * self.canvas.scale, self.scaled_copied_area.get_height() * self.canvas.scale))
        self.canvas.top_layer.blit(self.canvas_copied_area, (canvas_x, canvas_y))

        pygame.draw.rect(self.canvas.top_layer, "red", (canvas_x, canvas_y, self.canvas_copied_area.get_width(), self.canvas_copied_area.get_height()), 1)

        offset = (self.canvas.scale / 3) / 2
        
        self.top_left_node = pygame.draw.rect(self.canvas.top_layer, "red", (canvas_x - offset, 
                                                                             canvas_y - offset, 
                                                                             self.canvas.scale / 3, 
                                                                             self.canvas.scale / 3))
        
        self.bottom_left_node = pygame.draw.rect(self.canvas.top_layer, "red", (canvas_x - offset, 
                                                                                (canvas_y + self.canvas_copied_area.get_height()) - offset, 
                                                                                self.canvas.scale / 3, 
                                                                                self.canvas.scale / 3))
        
        self.top_right_node = pygame.draw.rect(self.canvas.top_layer, "red", ((canvas_x + self.canvas_copied_area.get_width()) - offset, 
                                                                              canvas_y - offset, 
                                                                              self.canvas.scale / 3, 
                                                                              self.canvas.scale / 3))
        
        self.bottom_right_node = pygame.draw.rect(self.canvas.top_layer, "red", ((canvas_x + self.canvas_copied_area.get_width()) - offset, 
                                                                                 (canvas_y + self.canvas_copied_area.get_height()) - offset, 
                                                                                 self.canvas.scale / 3, 
                                                                                 self.canvas.scale / 3))

    def collision(self):
        assert self.top_left_node
        assert self.bottom_left_node
        assert self.top_right_node
        assert self.bottom_right_node

        canvas_x = (self.grid_x * self.canvas.scale) + self.canvas.offset_x
        canvas_y = (self.grid_y * self.canvas.scale) + (self.canvas.offset_y + self.canvas.toolbar_height)
        canvas_copied_area_rect = self.canvas_copied_area.get_rect(topleft = (canvas_x, canvas_y))

        pos_x = pygame.mouse.get_pos()[0]
        pos_y = pygame.mouse.get_pos()[1] - self.canvas.toolbar_height

        if self.top_left_node.collidepoint((pos_x, pos_y)):
            self.selected_node = "top_left"
            return "node"
        elif self.bottom_left_node.collidepoint((pos_x, pos_y)):
            self.selected_node = "bottom_left"
            return "node"
        elif self.top_right_node.collidepoint((pos_x, pos_y)):
            self.selected_node = "top_right"
            return "node"
        elif self.bottom_right_node.collidepoint((pos_x, pos_y)):
            self.selected_node = "bottom_right"
            return "node"
        elif canvas_copied_area_rect.collidepoint(pygame.mouse.get_pos()):
            return "copied_area"
        
    def begin_scale(self):
        self.is_scaling = True

        self.right = self.grid_x + self.scaled_copied_area.get_width()
        self.bottom = self.grid_y + self.scaled_copied_area.get_height()
    
    def scale(self):
        gx = (pygame.mouse.get_pos()[0] - self.canvas.offset_x) / self.canvas.scale
        gy = (pygame.mouse.get_pos()[1] - self.canvas.offset_y - self.canvas.toolbar_height) / self.canvas.scale

        new_size_x = 0
        new_size_y = 0

        if self.selected_node == "top_left":
            new_size_x = self.right - ceil(gx) if self.right - ceil(gx) > 1 else 1
            new_size_y = self.bottom - ceil(gy) if self.bottom - ceil(gy) > 1 else 1

            self.grid_x = self.right - new_size_x
            self.grid_y = self.bottom - new_size_y
        elif self.selected_node == "bottom_left":
            new_size_x = self.right - ceil(gx) if self.right - ceil(gx) > 1 else 1
            new_size_y = gy - self.grid_y if gy - self.grid_y > 1 else 1

            self.grid_x = self.right - new_size_x
        elif self.selected_node == "top_right":
            new_size_x = gx - self.grid_x if gx - self.grid_x > 1 else 1
            new_size_y = self.bottom - ceil(gy) if self.bottom - ceil(gy) > 1 else 1

            self.grid_y = self.bottom - new_size_y
        elif self.selected_node == "bottom_right":
            new_size_x = gx - self.grid_x if gx - self.grid_x > 1 else 1
            new_size_y = gy - self.grid_y if gy - self.grid_y > 1 else 1

        self.scaled_copied_area = pygame.transform.scale(self.copied_area, (new_size_x, new_size_y))
        self.update()
        self.canvas.render_canvas()

    def stop_scaling(self):
        self.selected_node = ""
        self.is_scaling = False
    
    def begin_move(self):
        self.is_moving = True
    
    def move(self):
        gx = floor((pygame.mouse.get_pos()[0] - self.canvas.offset_x) / self.canvas.scale) - floor(self.scaled_copied_area.get_width() / 2)
        gy = floor((pygame.mouse.get_pos()[1] - self.canvas.offset_y - self.canvas.toolbar_height) / self.canvas.scale) - floor(self.scaled_copied_area.get_height() / 2)

        self.grid_x = gx
        self.grid_y = gy

        self.update()
        self.canvas.render_canvas()

    def stop_moving(self):
        self.is_moving = False

    def commit_paste(self):
        assert self.canvas.canvas_surface

        self.canvas.canvas_surface.blit(self.scaled_copied_area, (self.grid_x, self.grid_y))

        self.canvas.undo_redo.create_snapshot({"left": self.grid_x,
                                               "top": self.grid_y,
                                               "right": self.grid_x + self.scaled_copied_area.get_width(),
                                               "bottom": self.grid_y + self.scaled_copied_area.get_height()})

        self.clear_paste_box()

    def clear_paste_box(self):
        self.canvas.paste_box = None
        self.canvas.top_layer.fill((0, 0, 0, 0))
        self.canvas.render_canvas()