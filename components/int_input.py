from tkinter import *  # type: ignore
from tkinter import ttk

class IntInput(ttk.Entry):
    def __init__(self, parent: ttk.Frame, value: str) -> None:
        self.var = StringVar(parent, value)
        self.var.trace_add("write", self.check_int)

        self.digits = self.var.get()

        super().__init__(parent, textvariable=self.var)

    def check_int(self, a: str, b: str, c: str):
        if self.var.get().isdigit() or self.var.get() == "":
            self.digits = self.var.get()
        else:
            self.var.set(self.digits)