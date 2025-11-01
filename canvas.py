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

class DrawingCanvas(Canvas):
    def __init__(self, root: "Main"):
        self.root = root

        self.start_x: int = 0
        self.start_y: int = 0

        self.offset_x: float = 0
        self.offset_y: float = 0

        self.selected_area: dict[str, int] = {"start_x": 0,"start_y": 0,"end_x": 0,"end_y": 0}
        self.copied_area = None #PIL Image
        self.pasted_area = None #Canvas Image

        super().__init__(self.root, bg=self.root.bg_color, highlightthickness=0)
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

        self.bind("<Control-c>", self._copy_selected)
        self.bind("<Control-v>", self._paste_selected)
        self.bind("<Return>", self._commit_selected)

        self.canvas_image = Image.new("RGBA", (self.root.canvas_width, self.root.canvas_height), "white")
        self.loaded_canvas_image = self.canvas_image.load()
        self.scaled_canvas_image = self.canvas_image
        self.canvas_photo_image = ImageTk.PhotoImage(self.scaled_canvas_image)
        self.canvas_image_item = self.create_image((0,0), image=self.canvas_photo_image, anchor="nw") # type: ignore


    def _perform_action_click(self, event: Event):
        self.focus_set()

        if self.root.interaction_state == "draw":
            self._draw_pixel(event)
        elif self.root.interaction_state == "delete":
            self._delete_pixel(event)
        elif self.root.interaction_state == "select":
            self._get_starting_coords(event)


    def _perform_action_motion(self, event: Event):
        if self.root.interaction_state == "draw":
            self._draw_pixel(event)
        elif self.root.interaction_state == "delete":
            self._delete_pixel(event)
        elif self.root.interaction_state == "select":
            self._select(event)


    def _perform_action_up(self, event: Event):
        if self.root.interaction_state == "draw":
            self._update_canvas_image()
            self.delete("pointer")
            self.delete("pixel")


    def update_bg_color(self):
        self.configure(bg=self.root.bg_color)


    def _update_canvas_image(self):
        SCALE = self.root.scale / 100

        self.scaled_canvas_image = self.canvas_image.resize((int(self.root.canvas_width * SCALE), int(self.root.canvas_height * SCALE)), Image.Resampling.NEAREST) # type: ignore
        self.canvas_photo_image = ImageTk.PhotoImage(self.scaled_canvas_image)
        self.itemconfig(self.canvas_image_item, image=self.canvas_photo_image)


    def resize_canvas(self):
        new_image = Image.new("RGBA", (self.root.canvas_width, self.root.canvas_height), "white")
        new_image.paste(self.canvas_image, (0, 0))

        self.canvas_image = new_image
        self.loaded_canvas_image = new_image.load()

        self._update_canvas_image()
        

    def place_pixel(self, event: Event, fill: str, tag: str, delete: bool, commit_pixel:bool):
        SCALE = self.root.scale / 100
        GRID_X = floor((event.x - self.offset_x) / SCALE)
        GRID_Y = floor((event.y - self.offset_y) / SCALE)

        if GRID_X > self.root.canvas_width - 1 or GRID_X < 0: return
        if GRID_Y > self.root.canvas_height - 1 or GRID_Y < 0: return

        START_X = GRID_X - int(self.root.pixel_size / 2) if GRID_X - int(self.root.pixel_size / 2) > 0 else 0
        START_Y = GRID_Y - int(self.root.pixel_size / 2) if GRID_Y - int(self.root.pixel_size / 2) > 0 else 0

        WIDTH = self.root.pixel_size if GRID_X - int(self.root.pixel_size / 2) > 0 else self.root.pixel_size + (GRID_X - int(self.root.pixel_size / 2))
        HEIGHT = self.root.pixel_size if GRID_Y - int(self.root.pixel_size / 2) > 0 else self.root.pixel_size + (GRID_Y - int(self.root.pixel_size / 2))

        END_X = START_X + WIDTH if START_X + WIDTH < self.root.canvas_width else self.root.canvas_width
        END_Y = START_Y + HEIGHT if START_Y + HEIGHT < self.root.canvas_height else self.root.canvas_height

        self.create_rectangle((START_X * SCALE) + self.offset_x,
                              (START_Y * SCALE) + self.offset_y,
                              (END_X * SCALE) + self.offset_x,
                              (END_Y * SCALE) + self.offset_y,
                              fill=fill, outline="", tags=tag)
        
        if commit_pixel:
            rgb = tuple(int(fill.lstrip("#")[i:i+2],16) for i in (0, 2, 4)) if not delete else (0, 0, 0, 0)

            for i in range(HEIGHT):
                for j in range(WIDTH):
                    try:
                        self.loaded_canvas_image[START_X + j, START_Y + i] = rgb # type: ignore
                    except IndexError:
                        pass


    def _display_pointer_location(self, event: Event):
        self.delete("pointer")
        
        if self.root.interaction_state == "draw":
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
                         fill=self.root.bg_color,
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

        self.offset_x = event.x - (event.x - self.offset_x) * (SCALE / PREV_SCALE)
        self.offset_y = event.y - (event.y - self.offset_y) * (SCALE / PREV_SCALE)

        if self.pasted_area:
            SCALED_COPIED_AREA = self.copied_area.resize((int(self.copied_area.width * SCALE), int(self.copied_area.height * SCALE)), Image.Resampling.NEAREST) # type: ignore
            self.scaled_copied_area = ImageTk.PhotoImage(SCALED_COPIED_AREA)
            self.itemconfig(self.pasted_area, image=self.scaled_copied_area)

        self._update_canvas_image()
        self.scale(ALL, event.x, event.y, SCALE / PREV_SCALE, SCALE / PREV_SCALE)
        

    def _get_starting_coords(self, event: Event):
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

        WIDTH = self.root.canvas_width
        HEIGHT = self.root.canvas_height
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
            elif el > WIDTH - 1:
                x_coords[i] = WIDTH - 1

        for i, el in enumerate(y_coords):
            if el < 0:
                y_coords[i] = 0
            elif el > HEIGHT - 1:
                y_coords[i] = HEIGHT - 1

        self.selected_area = {
            "start_x": x_coords[0],
            "start_y" : y_coords[0],
            "end_x": x_coords[1],
            "end_y": y_coords[1]
        }

        self.create_rectangle((x_coords[0] * SCALE) + self.offset_x,
                              (y_coords[0] * SCALE) + self.offset_y, 
                              ((x_coords[1] * SCALE) + self.offset_x) + SCALE, 
                              ((y_coords[1] * SCALE) + self.offset_y) + SCALE,
                              outline="black", tags="select_outline", width=2)


    def _delete_selected(self, event: Event):
        SIZE_X = self.selected_area["end_x"] - self.selected_area["start_x"]
        SIZE_Y = self.selected_area["end_y"] - self.selected_area["start_y"]

        for i in range(SIZE_Y + 1):
            for j in range(SIZE_X + 1):
                try:
                    self.loaded_image[self.selected_area["start_x"] + j, self.selected_area["start_y"] + i] = (0, 0, 0, 0) # type: ignore
                except IndexError:
                    pass
        
        self._update_canvas_image()


    def _copy_selected(self, event: Event):
        self.copied_area = self.canvas_image.crop((self.selected_area["start_x"],
                                                   self.selected_area["start_y"],
                                                   self.selected_area["end_x"],
                                                   self.selected_area["end_y"]))
        
    
    def _paste_selected(self, event: Event):
        SCALE = self.root.scale / 100
        GRID_X = floor((event.x - self.offset_x) / SCALE)
        GRID_Y = floor((event.y - self.offset_y) / SCALE)

        if GRID_X > self.root.canvas_width - 1 or GRID_X < 0: return
        if GRID_Y > self.root.canvas_height - 1 or GRID_Y < 0: return

        self.delete("placement_box")

        SCALED_COPIED_AREA = self.copied_area.resize((int(self.copied_area.width * SCALE), int(self.copied_area.height * SCALE)), Image.Resampling.NEAREST) # type: ignore
        self.copied_area_photo_image = ImageTk.PhotoImage(SCALED_COPIED_AREA)

        self.pasted_area = self.create_image(((GRID_X * SCALE) + self.offset_x, # type: ignore
                                              (GRID_Y * SCALE) + self.offset_y), 
                                              image=self.copied_area_photo_image, tags="placement_box")

        self.create_rectangle(((GRID_X * SCALE) - (SCALED_COPIED_AREA.width / 2) + self.offset_x, 
                               (GRID_Y * SCALE) - (SCALED_COPIED_AREA.height / 2) + self.offset_y, 
                               (GRID_X * SCALE) + (SCALED_COPIED_AREA.width / 2) + self.offset_x, 
                               (GRID_Y * SCALE) + (SCALED_COPIED_AREA.height / 2) + self.offset_y), 
                               outline="blue", width=2, tags="placement_box")
        
        self.tag_bind("placement_box", "<Button-1>", self._get_starting_coords)
        self.tag_bind("placement_box", "<B1-Motion>", self._move_selected)


    def _move_selected(self, event: Event):
        X = event.x - self.start_x
        Y = event.y - self.start_y

        self.start_x = event.x
        self.start_y = event.y

        COORDS = self.coords(self.pasted_area) # type: ignore
        BBOX = self.bbox(self.pasted_area) # type: ignore

        WIDTH = BBOX[2] -  BBOX[0]
        HEIGHT = BBOX[3] -  BBOX[1]

        WORLD_X = (COORDS[0] - (WIDTH / 2)) - self.offset_x
        WORLD_Y = (COORDS[1] - (HEIGHT / 2)) - self.offset_y

        if WORLD_X + X < WIDTH * -1 or WORLD_X + WIDTH + X > self.scaled_canvas_image.width + WIDTH: return
        if WORLD_Y + Y < HEIGHT * -1 or WORLD_Y + HEIGHT + Y > self.scaled_canvas_image.height + HEIGHT: return

        self.move("placement_box", X, Y) # type: ignore


    def _commit_selected(self, event: Event):
        SCALE = self.root.scale / 100

        X = self.coords(self.pasted_area)[0] # type: ignore
        Y = self.coords(self.pasted_area)[1] # type: ignore

        HALF_X = (self.bbox(self.pasted_area)[2] - self.bbox(self.pasted_area)[0]) / 2 # type: ignore
        HALF_Y = (self.bbox(self.pasted_area)[1] - self.bbox(self.pasted_area)[3]) / 2 # type: ignore
        
        self.canvas_image.paste(self.copied_area, (int(((X - HALF_X) - self.offset_x) / SCALE), int(((Y + HALF_Y) - self.offset_y) / SCALE))) # type: ignore

        self.pasted_area = None
        self.delete("placement_box")

        self._update_canvas_image()