from tkinter import * # type: ignore
from tkinter import colorchooser
import canvas
import toolbar

class Data:
    """
    Data class to store data needed for app and to perform data related actions.
    """
    def __init__(self) -> None:
        self.color: str = "#000000"
        self.bg: str = "#0026FF"
        self.is_deleting: bool = False
        self.is_selecting: bool = False
        self.show_grid: bool = True
        self.shape_options: list[str] = ["none", "triangle", "square", "circle", "hexagon"]
        self.shape: str = "none" 

        self.main_canvas: "canvas.MainCanvas | None" = None
        self.toolbar: "toolbar.Toolbar | None" = None

        self.delete_var = StringVar(value=f"del: {self.is_deleting}")
        self.select_var = StringVar(value=f"sel: {self.is_selecting}")


    def set_color(self, button: Button):
        color: str | None = colorchooser.askcolor()[1]

        if color != None:
            self.color = color
            button.configure(background=self.color)


    def set_bg_color(self, button: Button):
        color: str | None = colorchooser.askcolor(initialcolor=self.bg)[1]

        if color != None and self.main_canvas:
            self.bg = color
            button.configure(background=color)
            self.main_canvas.canvas.configure(background=color)


    def toggle_grid(self, button: Button):
        self.show_grid = not self.show_grid
        button.configure(text=f"grid: {self.show_grid}")
    

    def set_shape(self, x: StringVar):
        self.shape = str(x)


    def set_interaction_state(self, interaction: str):
        if interaction == "delete":
            self.is_deleting = not self.is_deleting
            self.is_selecting = False
        elif interaction == "select": 
            self.is_selecting = not self.is_selecting
            self.is_deleting = False

        self.delete_var.set(f"del: {self.is_deleting}")
        self.select_var.set(f"sel: {self.is_selecting}")