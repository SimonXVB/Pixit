from tkinter import * # type: ignore
import data

class MainCanvas:
    def __init__(self, root: Tk, data: "data.Data") -> None:
        self.root = root
        self.data = data

        self.canvas = Canvas(self.root, bg=self.data.bg)
        self.canvas.grid(sticky="NESW", row=1, column=0)