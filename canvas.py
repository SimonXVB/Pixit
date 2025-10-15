from math import floor
from tkinter import * # type: ignore
from typing import TYPE_CHECKING, Union # <--don't like this

if TYPE_CHECKING:
    from main import Main

class MainCanvas(Canvas):
    def __init__(self, root: "Main") -> None:
        self.root = root
        self.items: list[dict[str, Union[str, int]]] = []

        super().__init__(self.root, bg=self.root.bg)
        self.grid(sticky="NESW", row=1, column=0)
        
        self.bind("<Button-1>", self._current_drawing_state)
        self.bind("<B1-Motion>", self._current_drawing_state)

        self.bind("<Button-3>", self._delete_pixel)
        self.bind("<B3-Motion>", self._delete_pixel)

        self.bind("<MouseWheel>", self.zoom)

        self._init_grid()


    def _init_grid(self):
        STATE = "normal" if self.root.show_grid else "hidden"

        self.delete("grid_el")

        for y in range(self.root.canvas_size[1]):
            for x in range(self.root.canvas_size[0]):
                SIZE = self.root.pixel_size
                TOP_X = SIZE * x
                TOP_Y = SIZE * y
                BOTTOM_X = (SIZE * x) + SIZE
                BOTTOM_Y = (SIZE * y) + SIZE

                self.create_rectangle(TOP_X, 
                                      TOP_Y, 
                                      BOTTOM_X, 
                                      BOTTOM_Y, 
                                      outline="black", tags="grid_el", state=STATE)


    def toggle_grid(self):
        if self.root.show_grid:
            self.itemconfig("grid_el", state="normal")
        else:
            self.itemconfig("grid_el", state="hidden")


    def _draw_pixel(self, event: Event):
        SIZE = self.root.pixel_size
        GRID_X = floor(event.x / SIZE)
        GRID_Y = floor(event.y / SIZE)
        TAG = f"{GRID_X}-{GRID_Y}"

        if GRID_X > self.root.canvas_size[0] - 1 or GRID_X < 0: return
        if GRID_Y > self.root.canvas_size[1] - 1 or GRID_Y < 0: return

        self.items = [item for item in self.items if item["tag"] != f"{GRID_X}-{GRID_Y}"]
        self.delete(f"{GRID_X}-{GRID_Y}")

        self.create_rectangle(SIZE * GRID_X, 
                              SIZE * GRID_Y, 
                              (SIZE * GRID_X) + SIZE, 
                              (SIZE * GRID_Y) + SIZE,
                              fill=self.root.color, tags=[TAG, "pixel"])
        
        self.items.append({
            "tag": TAG,
            "color": self.root.color,
            "x": GRID_X,
            "y": GRID_Y
        })


    def _delete_pixel(self, event: Event):
        GRID_X = floor(event.x / self.root.pixel_size)
        GRID_Y = floor(event.y / self.root.pixel_size)
        TAG = f"{GRID_X}-{GRID_Y}"

        if GRID_X > self.root.canvas_size[0] - 1 or GRID_X < 0: return
        if GRID_Y > self.root.canvas_size[1] - 1 or GRID_Y < 0: return

        self.items = [item for item in self.items if item["tag"] != TAG]
        self.delete(TAG)


    def _current_drawing_state(self, event: Event):
        if self.root.is_selecting:
            pass
        elif self.root.is_deleting:
            self._delete_pixel(event)
        else:
            self._draw_pixel(event)


    def update_canvas(self):
        self._init_grid()

        for item in self.items:
            SIZE = self.root.pixel_size
            GRID_X = int(item["x"])
            GRID_Y = int(item["y"])

            self.delete(item["tag"])

            self.create_rectangle(SIZE * int(item["x"]), 
                        SIZE * GRID_Y, 
                        (SIZE * GRID_X) + SIZE, 
                        (SIZE * GRID_Y) + SIZE,
                        fill=self.root.color, tags=[f"{GRID_X}-{GRID_Y}", "pixel"])


    def zoom(self, event: Event):
        new_scale: float = 1

        if self.root.scale < 200 and event.delta > 0:
            self.root.scale += 5
            new_scale = 1.05
        elif self.root.scale > -200 and event.delta < 0:
            self.root.scale -= 5
            new_scale = 0.95

        self.scale(ALL, event.x, event.y, new_scale, new_scale)