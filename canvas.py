import time
from tkinter import * # type: ignore
from typing import TYPE_CHECKING
from math import floor
from PIL import Image, ImageTk

if TYPE_CHECKING:
    from main import Main

def ex_time(func): # type: ignore
    def wrapper(*args, **kwargs) -> None: # type: ignore
        s = time.time()
        func(*args, **kwargs)
        e = time.time()
        print(e-s)
    return wrapper # type: ignore

class MainCanvas(Canvas):
    def __init__(self, root: "Main"):
        self.root = root

        self.start_x: int = 0
        self.start_y: int = 0

        self.offset_x: float = 0
        self.offset_y: float = 0

        self.selected_area: dict[str, int] = {}

        super().__init__(self.root, bg=self.root.bg, highlightthickness=0)
        self.grid(sticky="NESW", row=1, column=0)
        
        self.bind("<Button-1>", self._perform_action_click)
        self.bind("<B1-Motion>", self._perform_action_motion)
        self.bind("<B1-ButtonRelease>", self._perform_action_up)

        self.bind("<Button-3>", self._delete_pixel)
        self.bind("<B3-Motion>", self._delete_pixel)
        self.bind("<B3-ButtonRelease>", self._perform_action_up)

        self.bind("<Button-2>", self._get_starting_coords)
        self.bind("<B2-Motion>", self._pan)

        self.bind("<MouseWheel>", self._zoom)
        self.bind("<BackSpace>", self._delete_selected)
        self.bind("<Motion>", self._display_pointer_location)

        self.image = Image.new("RGBA", (self.root.canvas_size[0], self.root.canvas_size[1]), "white")
        self.loaded_image = self.image.load()
        self.scaled_image = self.image
        
        self.photo_image = ImageTk.PhotoImage(self.scaled_image)
        self.image_item = self.create_image((0,0), image=self.photo_image, anchor="nw") # type: ignore


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
            pass
        else:
            self.scale_image()
            self.delete("pointer")
            self.delete("pixel")

    def scale_image(self):
        SCALE = self.root.scale / 100

        self.scaled_image = self.image.resize((int(self.root.canvas_size[0] * SCALE), int(self.root.canvas_size[0] * SCALE)), Image.Resampling.NEAREST) # type: ignore
        self.photo_image = ImageTk.PhotoImage(self.scaled_image)
        self.itemconfig(self.image_item, image=self.photo_image)


    def resize_canvas(self):
        new_image = Image.new("RGBA", (self.root.canvas_size[0], self.root.canvas_size[1]), "white")
        new_image.paste(self.image, (0, 0))

        self.image = new_image
        self.loaded_image = self.image.load()
        self.scale_image()

    def place_pixel(self, event: Event, fill: str, tag: str, delete: bool, commit_pixel:bool):
        SCALE = self.root.scale / 100
        GRID_X = floor((event.x - self.offset_x) / SCALE)
        GRID_Y = floor((event.y - self.offset_y) / SCALE)

        if GRID_X > self.root.canvas_size[0] - 1 or GRID_X < 0: return
        if GRID_Y > self.root.canvas_size[1] - 1 or GRID_Y < 0: return

        START_X = GRID_X - int(self.root.pixel_size / 2) if GRID_X - int(self.root.pixel_size / 2) > 0 else 0
        START_Y = GRID_Y - int(self.root.pixel_size / 2) if GRID_Y - int(self.root.pixel_size / 2) > 0 else 0

        SIZE_X = self.root.pixel_size if GRID_X - int(self.root.pixel_size / 2) > 0 else self.root.pixel_size + (GRID_X - int(self.root.pixel_size / 2))
        SIZE_Y = self.root.pixel_size if GRID_Y - int(self.root.pixel_size / 2) > 0 else self.root.pixel_size + (GRID_Y - int(self.root.pixel_size / 2))

        END_X = START_X + SIZE_X if START_X + SIZE_X < self.root.canvas_size[0] else self.root.canvas_size[0]
        END_Y = START_Y + SIZE_Y if START_Y + SIZE_Y < self.root.canvas_size[1] else self.root.canvas_size[1]

        self.create_rectangle((SCALE * START_X) + self.offset_x,
                            (SCALE * START_Y) + self.offset_y,
                            (SCALE * END_X) + self.offset_x,
                            (SCALE * END_Y) + self.offset_y,
                            fill=fill, outline="", tags=tag)
        
        if commit_pixel:
            rgb = tuple(int(fill.lstrip("#")[i:i+2],16) for i in (0, 2, 4)) if not delete else (255, 255, 255, 0)

            for i in range(self.root.pixel_size):
                for j in range(self.root.pixel_size):
                    try:
                        self.loaded_image[START_X + j, START_Y + i] = rgb # type: ignore
                    except IndexError:
                        pass
        

    def toggle_grid(self):
        if self.root.show_grid:
            self.itemconfig("grid_el", state="normal")
        else:
            self.itemconfig("grid_el", state="hidden")
        

    # def init_grid(self):
    #     STATE = "normal" if self.root.show_grid else "hidden"
    #     SCALE = self.root.scale / 100

    #     self.delete("grid_el")

    #     for x in range(self.root.canvas_size[0] + 1):
    #         self.create_line(((self.root.pixel_size * x) * SCALE) + self.offset_x, 
    #                          self.offset_y,
    #                          ((self.root.pixel_size * x) * SCALE) + self.offset_x, 
    #                          ((self.root.pixel_size * self.root.canvas_size[1]) * SCALE) + self.offset_y, 
    #                          tags="grid_el", state=STATE)

    #     for y in range(self.root.canvas_size[1] + 1):
    #         self.create_line(self.offset_x, 
    #                          ((self.root.pixel_size * y) * SCALE) + self.offset_y,
    #                          ((self.root.pixel_size * self.root.canvas_size[0]) * SCALE) + self.offset_x, 
    #                          ((self.root.pixel_size * y) * SCALE) + self.offset_y,
    #                          tags="grid_el", state=STATE)


    def _display_pointer_location(self, event: Event):
        self.delete("pointer")
        if not self.root.is_selecting:
            self.place_pixel(event=event,
                            fill=self.root.color,
                            delete=False,
                            tag="pointer",
                            commit_pixel=False)


    def _draw_pixel(self, event: Event):
        self.place_pixel(event=event,
                         fill=self.root.color,
                         delete=False,
                         tag="pixel",
                         commit_pixel=True)


    def _delete_pixel(self, event: Event):
        self.place_pixel(event=event,
                         fill=self.root.bg,
                         delete=True,
                         tag="pixel",
                         commit_pixel=True)


    def _zoom(self, event: Event):
        self._clear_select()

        PREV_SCALE = self.root.scale / 100

        if self.root.scale < 300 and event.delta > 0:
            self.root.scale += 5
        elif self.root.scale > 5 and event.delta < 0:
            self.root.scale -= 5
        else:
            return

        SCALE = self.root.scale / 100
        POS_X = event.x
        POS_Y = event.y

        self.offset_x = POS_X - (POS_X - self.offset_x) * (SCALE / PREV_SCALE)
        self.offset_y = POS_Y - (POS_Y - self.offset_y) * (SCALE / PREV_SCALE)

        self.scale_image()
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


    def _clear_select(self):
        self.delete("select_outline")
        self.selected_area = {}


    def _select(self, event: Event):
        self._clear_select()

        C_SIZE = self.root.canvas_size
        SCALE = self.root.scale / 100

        x_coords = [floor((self.start_x - self.offset_x) / SCALE), floor((event.x - self.offset_x) / SCALE)] # [top x, bottom x]
        y_coords = [floor((self.start_y - self.offset_y) / SCALE), floor((event.y - self.offset_y) / SCALE)] # [top y, bottom y]

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

        self.create_rectangle((x_coords[0] * SCALE) + self.offset_x,
                              (y_coords[0] * SCALE) + self.offset_y, 
                              ((x_coords[1] * SCALE) + self.offset_x) + SCALE, 
                              ((y_coords[1] * SCALE) + self.offset_y) + SCALE,
                              outline="black", tags="select_outline", width=2)


    def _delete_selected(self, event: Event):
        SIZE_X = self.selected_area["bottom_x"] - self.selected_area["top_x"]
        SIZE_Y = self.selected_area["bottom_y"] - self.selected_area["top_y"]

        for i in range(SIZE_Y + 1):
            for j in range(SIZE_X + 1):
                try:
                    self.loaded_image[self.selected_area["top_x"] + j, self.selected_area["top_y"] + i] = (255, 255, 255, 0) # type: ignore
                except IndexError:
                    pass
        
        self.scale_image()