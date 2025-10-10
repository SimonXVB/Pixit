from tkinter import * # type: ignore
import data

class Toolbar:
    def __init__(self, root: Tk, data: "data.Data") -> None:
        self.root = root
        self.data = data

        toolbar_frame = Frame(self.root, bg="red", height=50)
        toolbar_frame.rowconfigure(0, weight=1)
        toolbar_frame.grid_propagate(False)
        toolbar_frame.grid(sticky="NEWS", column=0, row=0)

        self.color_button(toolbar_frame, 0)
        self.bg_color_button(toolbar_frame, 1)
        self.delete_button(toolbar_frame, 2)
        self.select_button(toolbar_frame, 3)
        self.grid_button(toolbar_frame, 4)
        self.shape_dropdown(toolbar_frame, 5)


    def color_button(self, parent: Frame, col: int):
        def set_color():
            self.data.set_color(button)

        button = Button(parent, text="col", fg="white", background=self.data.color, width=10, command=set_color)
        button.grid(sticky="NSW", column=col, row=0)


    def bg_color_button(self, parent: Frame, col: int):
        def set_bg_color():
            self.data.set_bg_color(button)

        button = Button(parent, text="bg col", fg="white", background=self.data.bg, width=10, command=set_bg_color)
        button.grid(sticky="NSW", column=col, row=0)

        
    def delete_button(self, parent: Frame, col: int):
        def set_interaction_state():
            self.data.set_interaction_state("delete")

        button = Button(parent, background="green", width=10, textvariable=self.data.delete_var, command=set_interaction_state)
        button.grid(sticky="NSW", column=col, row=0)


    def select_button(self, parent: Frame, col: int):
        def set_interaction_state():
            self.data.set_interaction_state("select")

        button = Button(parent, background="purple", fg="white", width=10, textvariable=self.data.select_var, command=set_interaction_state)
        button.grid(sticky="NSW", column=col, row=0)


    def grid_button(self, parent: Frame, col: int):
        def toggle_grid():
            self.data.toggle_grid(button)

        button = Button(parent, text=f"grid: {self.data.show_grid}", background="yellow", width=10, command=toggle_grid)
        button.grid(sticky="NSW", column=col, row=0)


    def shape_dropdown(self, parent: Frame, col: int):
        selected = StringVar(parent, self.data.shape)

        def set_shape(x: StringVar):
            self.data.set_shape(x)

        dropdown = OptionMenu(parent, selected, *self.data.shape_options, command=set_shape)
        dropdown.grid(sticky="NSW", column=col, row=0)