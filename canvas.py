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
        pass