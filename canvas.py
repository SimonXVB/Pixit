from tkinter import * # type: ignore
from data import Data

class MainCanvas:
    def __init__(self, root: Tk, data: Data) -> None:
        self.root = root
        self.data = data

        canvas = Canvas(self.root, bg="blue")
        canvas.grid(sticky="NESW", row=1, column=0)

