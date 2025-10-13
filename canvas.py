from math import floor
from tkinter import * # type: ignore
from typing import TYPE_CHECKING # <--don't like this

if TYPE_CHECKING:
    from main import Main

class MainCanvas(Canvas):
    def __init__(self, root: "Main") -> None:
        self.root = root

        super().__init__(self.root, bg=self.root.bg)
        self.grid(sticky="NESW", row=1, column=0)
        
        self.bind("<Button-1>", self.draw_pixel)
        self.init_grid()

    def init_grid(self):
        STATE = "normal" if self.root.show_grid else "hidden"

        for y in range(self.root.canvas_size[1]):
            for x in range(self.root.canvas_size[0]):
                SIZE = self.root.pixel_size
                TOP_X = SIZE * x
                TOP_Y = SIZE * y
                BOTTOM_X = (SIZE * x) + SIZE
                BOTTOM_Y = (SIZE * y) + SIZE

                self.create_rectangle(TOP_X, 
                                      TOP_Y, 
                                      BOTTOM_X, 
                                      BOTTOM_Y, 
                                      outline="black", tags="grid_el", state=STATE)
                
    def toggle_grid(self):
        if self.root.show_grid:
            self.itemconfig("grid_el", state="normal")
        else:
            self.itemconfig("grid_el", state="hidden")

    def draw_pixel(self, event: Event):
        SIZE = self.root.pixel_size
        GRID_X = floor(event.x / self.root.pixel_size)
        GRID_Y = floor(event.y / self.root.pixel_size)

        self.delete(f"{GRID_X}-{GRID_Y}")

        self.create_rectangle(SIZE * GRID_X, 
                              SIZE * GRID_Y, 
                              (SIZE * GRID_X) + SIZE, 
                              (SIZE * GRID_Y) + SIZE, 
                              fill=self.root.color, tags=f"{GRID_X}-{GRID_Y}")
        
        print(self.gettags(f"{GRID_X}-{GRID_Y}"))