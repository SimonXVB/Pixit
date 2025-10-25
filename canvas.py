from math import floor
from tkinter import * # type: ignore
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import Main

class MainCanvas(Canvas):
    def __init__(self, root: "Main") -> None:
        self.root = root

        self.start_x: int = 0
        self.start_y: int = 0

        self.offset_x: float = 0
        self.offset_y: float = 0

        self.selected_area: dict[str, int] = {}

        super().__init__(self.root, bg=self.root.bg)
        self.grid(sticky="NESW", row=1, column=0)
        
        self.bind("<Button-1>", self._perform_action_click)
        self.bind("<B1-Motion>", self._perform_action_motion)
        self.bind("<B1-ButtonRelease>", self._perform_action_up)

        self.bind("<Button-3>", self._delete_pixel)
        self.bind("<B3-Motion>", self._delete_pixel)

        self.bind("<Button-2>", self._get_starting_coords)
        self.bind("<B2-Motion>", self._pan)

        self.bind("<MouseWheel>", self._zoom)
        
        self.bind("<BackSpace>", self._delete_selected)

        self.init_grid()


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
        pass

    def init_grid(self):
        STATE = "normal" if self.root.show_grid else "hidden"
        SCALE = self.root.scale / 100

        self.delete("grid_el")

        for x in range(self.root.canvas_size[0] + 1):
            self.create_line(((self.root.pixel_size * x) * SCALE) + self.offset_x, 
                             self.offset_y,
                             ((self.root.pixel_size * x) * SCALE) + self.offset_x, 
                             ((self.root.pixel_size * self.root.canvas_size[1]) * SCALE) + self.offset_y, 
                             tags="grid_el", state=STATE)

        for y in range(self.root.canvas_size[1] + 1):
            self.create_line(self.offset_x, 
                             ((self.root.pixel_size * y) * SCALE) + self.offset_y,
                             ((self.root.pixel_size * self.root.canvas_size[0]) * SCALE) + self.offset_x, 
                             ((self.root.pixel_size * y) * SCALE) + self.offset_y,
                             tags="grid_el", state=STATE)


    def toggle_grid(self):
        if self.root.show_grid:
            self.itemconfig("grid_el", state="normal")
        else:
            self.itemconfig("grid_el", state="hidden")


    def _draw_pixel(self, event: Event):
        SIZE = self.root.pixel_size * (self.root.scale / 100)
        GRID_X = floor((event.x - self.offset_x) / SIZE)
        GRID_Y = floor((event.y - self.offset_y) / SIZE)

        TAG = f"{GRID_X}-{GRID_Y}"
        ITEM = self.find_withtag(TAG)

        if GRID_X > self.root.canvas_size[0] - 1 or GRID_X < 0: return
        if GRID_Y > self.root.canvas_size[1] - 1 or GRID_Y < 0: return

        try:
            self.itemconfig(ITEM[0], fill=self.root.color)
        except IndexError:
            self.create_rectangle((SIZE * GRID_X) + self.offset_x, 
                                (SIZE * GRID_Y) + self.offset_y, 
                                ((SIZE * GRID_X) + SIZE) + self.offset_x, 
                                ((SIZE * GRID_Y) + SIZE) + self.offset_y,
                                fill=self.root.color, tags=[TAG, "pixel"])
            

    def _delete_pixel(self, event: Event):
        SIZE = self.root.pixel_size * (self.root.scale / 100)
        GRID_X = floor((event.x - self.offset_x) / SIZE)
        GRID_Y = floor((event.y - self.offset_y) / SIZE)

        try:
            item = self.find_withtag(f"{GRID_X}-{GRID_Y}")[0]
            self.delete(item)
        except IndexError:
            pass


    def _zoom(self, event: Event):
        self._clear_select()

        PREV_SCALE = self.root.scale / 100

        if self.root.scale < 200 and event.delta > 0:
            self.root.scale += 5
        elif self.root.scale > 5 and event.delta < 0:
            self.root.scale -= 5

        SCALE = self.root.scale / 100
        POS_X = event.x
        POS_Y = event.y

        self.offset_x = POS_X - (POS_X - self.offset_x) * (SCALE / PREV_SCALE)
        self.offset_y = POS_Y - (POS_Y - self.offset_y) * (SCALE / PREV_SCALE)

        self.scale(ALL, POS_X, POS_Y, SCALE / PREV_SCALE, SCALE / PREV_SCALE)


    def _get_starting_coords(self, event: Event):
        self.focus_set()
        self._clear_select()

        self.start_x = event.x
        self.start_y = event.y


    def _pan(self, event: Event):
        x = event.x - self.start_x
        y = event.y - self.start_y

        self.offset_x += x
        self.offset_y += y

        self.start_x = event.x
        self.start_y = event.y

        self.move(ALL, x, y) # type: ignore

    def _select(self, event: Event):
        self._clear_select()

        START_X = self.start_x
        START_Y = self.start_y
        X = event.x
        Y = event.y

        C_SIZE = self.root.canvas_size
        SIZE = self.root.pixel_size * (self.root.scale / 100)

        x_coords = [floor((START_X - self.offset_x) / SIZE), floor((X - self.offset_x) / SIZE)] # [top x, bottom x]
        y_coords = [floor((START_Y - self.offset_y) / SIZE), floor((Y - self.offset_y) / SIZE)] # [top y, bottom y]

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

        self.selected_area = {
            "top_x": x_coords[0],
            "top_y" : y_coords[0],
            "bottom_x": x_coords[1],
            "bottom_y": y_coords[1]
        }

        self.create_rectangle((x_coords[0] * SIZE) + self.offset_x,
                        (y_coords[0] * SIZE) + self.offset_y, 
                        ((x_coords[1] * SIZE) + self.offset_x) + SIZE, 
                        ((y_coords[1] * SIZE) + self.offset_y) + SIZE,
                        outline="red", tags="select_outline", width=3)

        
    def _clear_select(self):
        self.delete("select_outline")
        self.selected_area = {}

        self.itemconfigure("pixel", state="normal")


    def _delete_selected(self, event: Event):
        try:
            for i in range(self.selected_area["top_y"], self.selected_area["bottom_y"] + 1):
                for j in range(self.selected_area["top_x"], self.selected_area["bottom_x"] + 1):
                    self.delete(f"{j}-{i}")
        except KeyError:
            pass