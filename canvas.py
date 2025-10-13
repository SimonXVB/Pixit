from tkinter import * # type: ignore
from typing import TYPE_CHECKING # <--don't like this

if TYPE_CHECKING:
    from main import Main

class MainCanvas(Canvas):
    def __init__(self, root: "Main") -> None:
        self.root = root

        self.canvas = super().__init__(self.root, bg=self.root.bg)
        self.grid(sticky="NESW", row=1, column=0)

        self.draw_grid()

    def draw_grid(self):
        if self.root.show_grid: 
            for y in range(self.root.canvas_size[1]):
                for x in range(self.root.canvas_size[0]):
                    SIZE = 50
                    TOP_X = SIZE * x
                    TOP_Y = SIZE * y
                    BOTTOM_X = (SIZE * x) + SIZE
                    BOTTOM_Y = (SIZE * y) + SIZE

                    self.create_rectangle(TOP_X, 
                                          TOP_Y, 
                                          BOTTOM_X, 
                                          BOTTOM_Y, 
                                          fill="blue", outline="green", tags="grid_el")
        else:
            self.delete("grid_el")