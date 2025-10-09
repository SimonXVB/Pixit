from tkinter import * # type: ignore
from canvas import MainCanvas
from toolbar import Toolbar
from data import Data

class Main:
    def __init__(self) -> None:
        self.root = Tk()
        self.data = Data()

        self.root.title("Pixit")
        self.root.geometry("450x450")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=2)

        Toolbar(self.root, self.data)
        MainCanvas(self.root, self.data)

        self.root.mainloop()
Main()