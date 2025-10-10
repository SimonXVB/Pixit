from tkinter import * # type: ignore
from tkinter import colorchooser
from data import Data

class Toolbar:
    def __init__(self, root: Tk, data: Data) -> None:
        self.root = root
        self.data = data

        self.delete_var = StringVar(self.root, f"del: {self.data.is_deleting}")
        self.select_var = StringVar(self.root, f"sel: {self.data.is_selecting}")

        toolbar_frame = Frame(self.root, bg="red", height=50)
        toolbar_frame.rowconfigure(0, weight=1)
        toolbar_frame.grid_propagate(False)

        self.color_button(toolbar_frame, 0)
        self.bg_color_button(toolbar_frame, 1)
        self.delete_button(toolbar_frame, 2)
        self.select_button(toolbar_frame, 3)
        self.grid_button(toolbar_frame, 4)
        self.shape_dropdown(toolbar_frame, 5)

        toolbar_frame.grid(sticky="NEWS", column=0, row=0)


    def color_button(self, parent: Frame, col: int):
        def set_color():
            color: str | None = colorchooser.askcolor()[1]

            if color != None:
                self.data.color = color
                button.configure(background=self.data.color)

        button = Button(parent, text="col", fg="white", background=self.data.color, width=10, command=set_color)
        button.grid(sticky="NSW", column=col, row=0)


    def bg_color_button(self, parent: Frame, col: int):
        def set_bg_color():
            color: str | None = colorchooser.askcolor()[1]

            if color != None:
                self.data.bg = color
                button.configure(background=self.data.bg)

        button = Button(parent, text="bg col", fg="white", background=self.data.color, width=10, command=set_bg_color)
        button.grid(sticky="NSW", column=col, row=0)

        
    def delete_button(self, parent: Frame, col: int):
        button = Button(parent, background="green", width=10, textvariable=self.delete_var, command=lambda: self.set_interaction_state("delete"))
        button.grid(sticky="NSW", column=col, row=0)


    def select_button(self, parent: Frame, col: int):
        button = Button(parent, background="purple", fg="white", width=10, textvariable=self.select_var, command=lambda: self.set_interaction_state("select"))
        button.grid(sticky="NSW", column=col, row=0)


    def grid_button(self, parent: Frame, col: int):
        def toggle_grid():
            self.data.show_grid = not self.data.show_grid
            button.configure(text=f"grid: {self.data.show_grid}")

        button = Button(parent, text=f"grid: {self.data.show_grid}", background="yellow", width=10, command=toggle_grid)
        button.grid(sticky="NSW", column=col, row=0)


    def shape_dropdown(self, parent: Frame, col: int):
        selected = StringVar(parent, self.data.shape)

        def set_shape(x: StringVar):
            self.data.shape = str(x)
            print(self.data.shape)

        dropdown = OptionMenu(parent, selected, *self.data.shape_options, command=set_shape)
        dropdown.grid(sticky="NSW", column=col, row=0)


    def set_interaction_state(self, interaction: str):
        if interaction == "delete":
            self.data.is_deleting = not self.data.is_deleting
            self.data.is_selecting = False
        elif interaction == "select": 
            self.data.is_selecting = not self.data.is_selecting
            self.data.is_deleting = False

        self.delete_var.set(f"del: {self.data.is_deleting}")
        self.select_var.set(f"sel: {self.data.is_selecting}")