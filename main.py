from tkinter import * # type: ignore
from tkinter import colorchooser, ttk
from toolbar import Toolbar
from canvas import DrawingCanvas

class Main(Tk):
    def __init__(self) -> None:
        super().__init__()

        #window config
        self.title("Pixit")
        self.geometry("700x500")
        self.minsize(700, 500)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        #app data
        self.color: str = "#000000"
        self.bg_color: str = "#0026FF"
        self.interaction_state: str = "draw"
        self.show_grid: bool = True
        self.shape_options: list[str] = ["none", "triangle", "square", "circle", "hexagon"]
        self.current_shape: str = self.shape_options[0]
        self.pixel_size: int = 5
        self.canvas_width: int = 50
        self.canvas_height: int = 50
        self.scale: float = 1
        self.baseline_scale: float = self.scale

        self.toolbar = Toolbar(self)
        self.drawing_canvas = DrawingCanvas(self)

        self.mainloop()
        
    def set_color(self, button: ttk.Button):
        color: str | None = colorchooser.askcolor(initialcolor=self.color)[1]

        if color != None:
            self.color = color
            button.configure(text=color)

    def set_bg_color(self, button: ttk.Button):
        color: str | None = colorchooser.askcolor(initialcolor=self.bg_color)[1]

        if color != None:
            self.bg_color = color
            
            button.configure(text=color)
            self.drawing_canvas.configure(bg=color)

    def toggle_grid(self, button: ttk.Button):
        self.show_grid = not self.show_grid

        button.configure(text=f"grid: {self.show_grid}")
    
    def set_shape(self, shape: StringVar):
        self.shape = str(shape)

    def set_interaction_state(self, interaction: str):
        self.interaction_state = interaction

        self.toolbar.draw_btn.configure(text="DR: True" if interaction == "draw" else "DR: False")
        self.toolbar.move_btn.configure(text="MV: True" if interaction == "move" else "MV: False")
        self.toolbar.delete_btn.configure(text="DL: True" if interaction == "delete" else "DL: False")
        self.toolbar.select_btn.configure(text="SL: True" if interaction == "select" else "SL: False")

    def change_dimensions(self, pixel_size: int, width: int, height: int):
        self.pixel_size = pixel_size
        self.canvas_width = width
        self.canvas_height = height

        self.drawing_canvas.resize_canvas()

if __name__ == "__main__":
    Main()