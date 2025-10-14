from tkinter import *  # type: ignore
from tkinter import ttk

class IntInput(ttk.Entry):
    def __init__(self, parent: ttk.Frame, value: str, row: int, col: int) -> None:
        self.var = StringVar(parent, value)
        self.var.trace_add("write", self.check_int)

        super().__init__(parent, textvariable=self.var)
        self.grid(row=row, column=col)

    def check_int(self, a: str, b: str, c: str):
        pass