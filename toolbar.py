from tkinter import * # type: ignore
from tkinter import colorchooser
from data import Data

class Toolbar:
    HEIGHT: int = 3

    def __init__(self, root: Tk, data: Data) -> None:
        self.root = root
        self.data = data

        self.delete_var = StringVar(self.root, f"del: {self.data.is_deleting}")
        self.select_var = StringVar(self.root, f"sel: {self.data.is_selecting}")

        toolbar_frame = Frame(self.root, background="red", height=75)

        self.color_button(toolbar_frame, 0)
        self.delete_button(toolbar_frame, 1)
        self.select_button(toolbar_frame, 2)

        toolbar_frame.grid(sticky="NEW", column=0, row=0)

    def color_button(self, parent: Frame, col: int):
        def set_color():
            color: str | None = colorchooser.askcolor()[1]

            if color != None:
                self.data.color = color
                button.configure(background=color)

        button = Button(parent, background=self.data.color, width=10, height=self.HEIGHT, command=set_color)
        button.grid(sticky="W", column=col, row=0)
        
    def delete_button(self, parent: Frame, col: int):
        button = Button(parent, background="green", width=10, height=self.HEIGHT, textvariable=self.delete_var, command=lambda: self.toggle_button_state("delete"))
        button.grid(sticky="W", column=col, row=0)

    def select_button(self, parent: Frame, col: int):
        button = Button(parent, background="purple", fg="white", width=10, height=self.HEIGHT, textvariable=self.select_var, command=lambda: self.toggle_button_state("select"))
        button.grid(sticky="W", column=col, row=0)

    def toggle_button_state(self, interaction: str):
        if interaction == "delete":
            self.data.is_deleting = not self.data.is_deleting
            self.data.is_selecting = False
        elif interaction == "select": 
            self.data.is_selecting = not self.data.is_selecting
            self.data.is_deleting = False

        self.delete_var.set(f"del: {self.data.is_deleting}")
        self.select_var.set(f"sel: {self.data.is_selecting}")