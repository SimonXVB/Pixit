from tkinter import * # type: ignore
from canvas import MainCanvas
from toolbar import Toolbar
from data import Data

class Main:
    def __init__(self) -> None:
        self.root = Tk()
        self.data = Data()

        self.root.title("Pixit")
        self.root.geometry("700x500")
        self.root.minsize(450, 450)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        self.toolbar: Toolbar = Toolbar(self.root, self.data)
        self.main_canvas: MainCanvas = MainCanvas(self.root, self.data)

        self.data.toolbar = self.toolbar
        self.data.main_canvas = self.main_canvas

        self.root.mainloop()
Main()