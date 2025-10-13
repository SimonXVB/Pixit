from tkinter import * # type: ignore
from tkinter import colorchooser, ttk
from toolbar import Toolbar
from canvas import MainCanvas

class Main(Tk):
    def __init__(self) -> None:
        super().__init__()

        #window config
        self.title("Pixit")
        self.geometry("700x500")
        self.minsize(450, 450)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        #app data
        self.color: str = "#000000"
        self.bg: str = "#0026FF"
        self.is_deleting: bool = False
        self.is_selecting: bool = False
        self.show_grid: bool = True
        self.shape_options: list[str] = ["none", "triangle", "square", "circle", "hexagon"]
        self.shape: str = self.shape_options[0]
        self.canvas_size: list[int] = [20, 15]

        self.toolbar = Toolbar(self)
        self.main_canvas = MainCanvas(self)

        self.mainloop()
        

    def set_color(self, button: ttk.Button):
        color: str | None = colorchooser.askcolor(initialcolor=self.color)[1]

        if color != None:
            self.color = color
            button.configure(text=color)


    def set_bg_color(self, button: ttk.Button):
        color: str | None = colorchooser.askcolor(initialcolor=self.bg)[1]

        if color != None and self.main_canvas:
            self.bg = color
            button.configure(text=color)
            self.main_canvas.configure(background=color)


    def toggle_grid(self, button: ttk.Button):
        self.show_grid = not self.show_grid

        button.configure(text=f"grid: {self.show_grid}")
        self.main_canvas.draw_grid()
    

    def set_shape(self, x: StringVar):
        self.shape = str(x)


    def set_interaction_state(self, interaction: str):
        if interaction == "delete":
            self.is_deleting = not self.is_deleting
            self.is_selecting = False
        elif interaction == "select": 
            self.is_selecting = not self.is_selecting
            self.is_deleting = False

        self.toolbar.delete_btn.configure(text=str(self.is_deleting))
        self.toolbar.select_btn.configure(text=str(self.is_selecting))
Main()