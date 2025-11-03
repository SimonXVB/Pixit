from tkinter import * # type: ignore
from tkinter import ttk
from components.int_input import IntInput
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import Main

class Toolbar(ttk.Frame):
    def __init__(self, root: "Main") -> None:
        super().__init__(root, height=50)

        self.root = root

        self.rowconfigure(0, weight=1)
        self.grid_propagate(False)
        self.grid(sticky="NEWS", column=0, row=0)

        self.color_btn = self._color_button(self, 0)
        self.bg_color_btn = self._bg_color_button(self, 1)

        self.draw_btn = self._toggle_draw_button(self, 2)
        self.move_btn = self._toggle_move_button(self,3)
        self.delete_btn = self._toggle_delete_button(self, 4)
        self.select_btn = self._toggle_select_button(self, 5)

        self.grid_btn = self._toggle_grid_button(self, 6)
        self.dimensions_btn = self._change_dimensions_button(self, 7)
        self.shape_dd = self._shape_dropdown(self, 8)


    def _color_button(self, parent: "Toolbar", col: int) -> ttk.Button:
        def set_color():
            self.root.set_color(button)

        button = ttk.Button(parent, text="col", width=10, command=set_color)
        button.grid(sticky="NSW", column=col, row=0)

        return button


    def _bg_color_button(self, parent: "Toolbar", col: int) -> ttk.Button:
        def set_bg_color():
            self.root.set_bg_color(button)

        button = ttk.Button(parent, text="bg col", width=10, command=set_bg_color)
        button.grid(sticky="NSW", column=col, row=0)

        return button
    

    def _toggle_draw_button(self, parent: "Toolbar", col: int) -> ttk.Button:
        def set_state():
            self.root.set_interaction_state("draw")

        TEXT = "DR: True" if self.root.interaction_state == "draw" else "DR: False"

        button = ttk.Button(parent, text=TEXT, width=10, command=set_state)
        button.grid(sticky="NSW", column=col, row=0)

        return button


    def _toggle_move_button(self, parent: "Toolbar", col: int) -> ttk.Button:
        def set_state():
            self.root.set_interaction_state("move")

        TEXT = "MV: True" if self.root.interaction_state == "move" else "MV: False"

        button = ttk.Button(parent, text=TEXT, width=10, command=set_state)
        button.grid(sticky="NSW", column=col, row=0)

        return button

        
    def _toggle_delete_button(self, parent: "Toolbar", col: int) -> ttk.Button:
        def set_state():
            self.root.set_interaction_state("delete")

        TEXT = "DL: True" if self.root.interaction_state == "delete" else "DL: False"

        button = ttk.Button(parent, text=TEXT, width=10, command=set_state)
        button.grid(sticky="NSW", column=col, row=0)

        return button


    def _toggle_select_button(self, parent: "Toolbar", col: int) -> ttk.Button:
        def set_state():
            self.root.set_interaction_state("select")

        TEXT = "SL: True" if self.root.interaction_state == "select" else "SL: False"

        button = ttk.Button(parent, text=TEXT, width=10, command=set_state)
        button.grid(sticky="NSW", column=col, row=0)

        return button


    def _toggle_grid_button(self, parent: "Toolbar", col: int) -> ttk.Button:
        def toggle_grid():
            self.root.toggle_grid(button)

        button = ttk.Button(parent, text=f"grid: {self.root.show_grid}", width=10, command=toggle_grid)
        button.grid(sticky="NSW", column=col, row=0)

        return button
    

    def _change_dimensions_button(self, parent: "Toolbar", col: int):
        button = ttk.Button(parent, text="dimen", width=10, command=self._open_change_dimensions_toplevel)
        button.grid(sticky="NSW", column=col, row=0)

        return button
    

    def _open_change_dimensions_toplevel(self):
        def close_toplevel():
            self.root.change_dimensions(int(size_input.get()), int(coord_x_input.get()), int(coord_y_input.get()))
            toplevel.destroy()

        toplevel = Toplevel(self.root, padx=10, pady=10)
        toplevel.title("Set Dimensions")
        toplevel.resizable(False, False)
        toplevel.grab_set()

        #place canvas size widgets
        dim_frame = ttk.Frame(toplevel)
        dim_frame.grid(row=0, column=0)

        dim_label = ttk.Label(dim_frame, text="Dimensions")
        dim_label.grid(row=0, column=0)

        coord_x_label = ttk.Label(dim_frame, text="X:")
        coord_x_label.grid(row=1, column=0)

        coord_x_input = IntInput(dim_frame, str(self.root.canvas_width))
        coord_x_input.grid(row=1, column=1)

        cells_x_label = ttk.Label(dim_frame, text="Cells")
        cells_x_label.grid(row=1, column=2)

        coord_y_label = ttk.Label(dim_frame, text="Y:")
        coord_y_label.grid(row=2, column=0)

        coord_y_input = IntInput(dim_frame, str(self.root.canvas_height))
        coord_y_input.grid(row=2, column=1)

        cells_y_label = ttk.Label(dim_frame, text="Cells")
        cells_y_label.grid(row=2, column=2)

        #place pixel size widgets
        size_frame = ttk.Frame(toplevel)
        size_frame.grid(row=1, column=0)

        size_label = ttk.Label(size_frame, text="Pixel Size")
        size_label.grid(row=0, column=0)

        size_input = IntInput(size_frame, str(self.root.pixel_size))
        size_input.grid(row=1, column=0)

        pixel_label = ttk.Label(size_frame, text="px")
        pixel_label.grid(row=1, column=1)

        #place save button
        save_button = ttk.Button(toplevel, text="Save Changes", command=close_toplevel)
        save_button.grid(row=2, column=1)

        toplevel.mainloop()

    def _shape_dropdown(self, parent: "Toolbar", col: int) -> ttk.OptionMenu:
        selected = StringVar(parent, self.root.current_shape)

        def set_shape(shape: StringVar):
            self.root.set_shape(shape)

        dropdown = ttk.OptionMenu(parent, selected, *self.root.shape_options, command=set_shape)
        dropdown.grid(sticky="NSW", column=col, row=0)

        return dropdown