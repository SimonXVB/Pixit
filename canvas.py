from math import floor
from tkinter import * # type: ignore
from typing import TYPE_CHECKING, Union # <--don't like this

if TYPE_CHECKING:
    from main import Main

class MainCanvas(Canvas):
    def __init__(self, root: "Main") -> None:
        self.root = root

        self.start_x: int = 0
        self.start_y: int = 0

        self.offset_x: int = 0
        self.offset_y: int = 0

        self.items: list[dict[str, Union[str, int]]] = []
        self.selected_items: dict[str, int] = {}

        super().__init__(self.root, bg=self.root.bg)
        self.grid(sticky="NESW", row=1, column=0)
        
        self.bind("<Button-1>", self._perform_action_click)
        self.bind("<B1-Motion>", self._perform_action_motion)
        self.bind("<B1-ButtonRelease>", self._perform_action_up)

        self.bind("<Button-3>", self._delete_pixel)
        self.bind("<B3-Motion>", self._delete_pixel)

        self.bind("<Button-2>", self._get_starting_coords)
        self.bind("<B2-Motion>", self._pan)

        self.bind("<MouseWheel>", self.zoom)

        self._init_grid()

    def _perform_action_click(self, event: Event):
        if self.root.is_selecting:
            self._get_starting_coords(event)
        elif self.root.is_deleting:
            self._delete_pixel(event)
        else:
            self._draw_pixel(event)

    def _perform_action_motion(self, event: Event):
        if self.root.is_selecting:
            self._select(event)
        elif self.root.is_deleting:
            self._delete_pixel(event)
        else:
            self._draw_pixel(event)

    def _perform_action_up(self, event: Event):
        if self.root.is_selecting:
            self._stop_select(event)

    def _init_grid(self):
        STATE = "normal" if self.root.show_grid else "hidden"
        SCALE = self.root.scale / 100

        self.delete("grid_el")

        for y in range(self.root.canvas_size[1] + 1):
            self.create_line(self.offset_x, 
                             ((self.root.pixel_size * y) * SCALE) + self.offset_y,
                             ((self.root.pixel_size * self.root.canvas_size[0]) * SCALE) + self.offset_x, 
                             ((self.root.pixel_size * y) * SCALE) + self.offset_y,
                             tags="grid_el", state=STATE)
            
        for x in range(self.root.canvas_size[0] + 1):
            self.create_line(((self.root.pixel_size * x) * SCALE) + self.offset_x, 
                             self.offset_y,
                             ((self.root.pixel_size * x) * SCALE) + self.offset_x, 
                             ((self.root.pixel_size * self.root.canvas_size[1]) * SCALE) + self.offset_y, 
                             tags="grid_el", state=STATE)
    

    def _update_pixels(self):
        for item in self.items:
            SIZE = self.root.pixel_size * (self.root.scale / 100)

            GRID_X = int(item["x"])
            GRID_Y = int(item["y"])

            self.delete(item["tag"])

            self.create_rectangle((SIZE * GRID_X) + self.offset_x, 
                                  (SIZE * GRID_Y) + self.offset_y, 
                                  ((SIZE * GRID_X) + SIZE) + self.offset_x, 
                                  ((SIZE * GRID_Y) + SIZE) + self.offset_y,
                                  fill=str(item["color"]), tags=f"{GRID_X}-{GRID_Y}")
            
            
    def update_canvas(self):
        self._init_grid()
        self._update_pixels()


    def toggle_grid(self):
        if self.root.show_grid:
            self.itemconfig("grid_el", state="normal")
        else:
            self.itemconfig("grid_el", state="hidden")


    def _draw_pixel(self, event: Event):
        SIZE = self.root.pixel_size * (self.root.scale / 100)

        X = event.x - self.offset_x
        Y = event.y - self.offset_y

        GRID_X = floor(X / SIZE)
        GRID_Y = floor(Y / SIZE)
        TAG = f"{GRID_X}-{GRID_Y}"

        if GRID_X > self.root.canvas_size[0] - 1 or GRID_X < 0: return
        if GRID_Y > self.root.canvas_size[1] - 1 or GRID_Y < 0: return

        self.items = [item for item in self.items if item["tag"] != f"{GRID_X}-{GRID_Y}"]
        self.delete(f"{GRID_X}-{GRID_Y}")

        self.create_rectangle((SIZE * GRID_X) + self.offset_x, 
                              (SIZE * GRID_Y) + self.offset_y, 
                              ((SIZE * GRID_X) + SIZE) + self.offset_x, 
                              ((SIZE * GRID_Y) + SIZE) + self.offset_y,
                              fill=self.root.color, tags=TAG)
        
        self.items.append({
            "tag": TAG,
            "color": self.root.color,
            "x": GRID_X,
            "y": GRID_Y
        })


    def _delete_pixel(self, event: Event):
        SIZE = self.root.pixel_size * (self.root.scale / 100)

        X = event.x - self.offset_x
        Y = event.y - self.offset_y

        GRID_X = floor(X / SIZE)
        GRID_Y = floor(Y / SIZE)
        TAG = f"{GRID_X}-{GRID_Y}"

        self.items = [item for item in self.items if item["tag"] != TAG]
        self.delete(TAG)


    def zoom(self, event: Event):
        self.delete("select_outline")

        PREV_SCALE = self.root.scale / 100

        if self.root.scale < 200 and event.delta > 0:
            self.root.scale += 5
        elif self.root.scale > 5 and event.delta < 0:
            self.root.scale -= 5

        SCALE = self.root.scale / 100
        POS_X = event.x
        POS_Y = event.y

        self.offset_x = int(POS_X - (POS_X - self.offset_x) * (SCALE / PREV_SCALE))
        self.offset_y = int(POS_Y - (POS_Y - self.offset_y) * (SCALE / PREV_SCALE))

        self.update_canvas()


    def _get_starting_coords(self, event: Event):
        self.delete("select_outline")

        self.start_x = event.x
        self.start_y = event.y


    def _pan(self, event: Event):
        x = event.x - self.start_x
        y = event.y - self.start_y

        self.offset_x += x
        self.offset_y += y

        self.start_x = event.x
        self.start_y = event.y

        self.update_canvas()

    def _select(self, event: Event):
        self.delete("select_outline")

        START_X = self.start_x
        START_Y = self.start_y
        X = event.x
        Y = event.y

        C_SIZE = self.root.canvas_size
        SIZE = self.root.pixel_size * (self.root.scale / 100)

        x_coords = [floor((START_X - self.offset_x) / SIZE), floor((X - self.offset_x) / SIZE)]
        y_coords = [floor((START_Y - self.offset_y) / SIZE), floor((Y - self.offset_y) / SIZE)]

        if x_coords[1] < x_coords[0]:
            x_coords[0], x_coords[1] = x_coords[1], x_coords[0]

        if y_coords[1] < y_coords[0]:
            y_coords[0], y_coords[1] = y_coords[1], y_coords[0]
        
        for i, el in enumerate(x_coords):
            if el < 0:
                x_coords[i] = 0
            elif el > C_SIZE[0] - 1:
                x_coords[i] = C_SIZE[0] - 1

        for i, el in enumerate(y_coords):
            if el < 0:
                y_coords[i] = 0
            elif el > C_SIZE[1] - 1:
                y_coords[i] = C_SIZE[1] - 1

        self.selected_items = {
            "start_x": x_coords[0],
            "start_y" : y_coords[0],
            "x": x_coords[1],
            "y": y_coords[1]
        }

        self.create_rectangle((x_coords[0] * SIZE) + self.offset_x,
                          (y_coords[0] * SIZE) + self.offset_y, 
                          ((x_coords[1] * SIZE) + self.offset_x) + SIZE, 
                          ((y_coords[1] * SIZE) + self.offset_y) + SIZE,
                          outline="red", tags="select_outline", width=3)

        
    def _stop_select(self, event: Event):
        print(self.selected_items)

        self.delete("select_rect")