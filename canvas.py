import time
from tkinter import * # type: ignore
from typing import TYPE_CHECKING
from math import ceil, floor
from PIL import Image, ImageTk, ImageDraw, ImageColor

if TYPE_CHECKING:
    from main import Main

def ex_time(func):
    def wrapper(*args, **kwargs) -> None:
        s = time.time()
        func(*args, **kwargs)
        e = time.time()
        print(e-s)
    return wrapper

def normal_round(n):
    if n - floor(n) < 0.5:
        return floor(n)
    return ceil(n)

class DrawingCanvas(Canvas):
    def __init__(self, root: "Main"):
        super().__init__(root, bg=root.bg_color, highlightthickness=0)
        self.grid(sticky="NESW", row=1, column=0)
        self.update()

        self.root = root

        self.root.scale = (self.winfo_height() / self.root.canvas_height) * 0.95
        self.root.baseline_scale = self.root.scale

        self.main_image = Image.new("RGBA", (self.root.canvas_width, self.root.canvas_height), "white")
        self.scaled_main_image = self.main_image.resize((int(self.root.canvas_width * self.root.scale), 
                                                         int(self.root.canvas_height * self.root.scale)), 
                                                         Image.Resampling.NEAREST)
        
        self.canvas_photo_image = ImageTk.PhotoImage(self.scaled_main_image)
        self.canvas_image_item = self.create_image((0, 0), image=self.canvas_photo_image, anchor="nw")

        self.offset_x: float = 0
        self.offset_y: float = 0

        self.start_x: int = 0
        self.start_y: int = 0

        self.selected_area: dict[str, int] = {"start_x": 0,"start_y": 0,"end_x": 0,"end_y": 0}
        self.copied_area = None #PIL Image
        self.pasted_area = None #Canvas Image
        
        self.bind("<Button-1>", self._m1_down)
        self.bind("<B1-Motion>", self._m1_motion)
        self.bind("<B1-ButtonRelease>", self._mouse_up)

        self.bind("<Button-3>", self._delete_pixel)
        self.bind("<B3-Motion>", self._delete_pixel)
        self.bind("<B3-ButtonRelease>", self._mouse_up)

        self.bind("<Button-2>", self._start_pan)
        self.bind("<B2-Motion>", self._pan)

        self.bind("<Control-c>", self._copy_selected)
        self.bind("<Control-v>", self._paste_selected)
        self.bind("<Return>", self._commit_pasted)

        self.bind("<MouseWheel>", self._zoom)
        self.bind("<BackSpace>", self._delete_selected)
        self.bind("<Motion>", self._mouse_motion)
        self.bind("<Configure>", lambda e: self._update_scale())

    def _m1_down(self, event: Event):
        self.focus_set()

        if self.root.interaction_state == "draw":
            self._draw_pixel(event)
        elif self.root.interaction_state == "delete":
            self._delete_pixel(event)
        elif self.root.interaction_state == "select":
            self._start_select(event)
        elif self.root.interaction_state == "move":
            self._start_pan(event)

        if self.pasted_area:
            CURRENT = self.find_withtag("current")
            PLACEMENT_ID = self.find_withtag("placement_box")

            if CURRENT[0] != PLACEMENT_ID[0] and CURRENT[0] != PLACEMENT_ID[1]:
                self._commit_pasted(event)

    def _m1_motion(self, event: Event):
        if self.root.interaction_state == "draw":
            self._draw_pixel(event)
        elif self.root.interaction_state == "delete":
            self._delete_pixel(event)
        elif self.root.interaction_state == "select":
            self._select(event)
        elif self.root.interaction_state == "move":
            self._pan(event)

    def _mouse_up(self, event: Event):
        self.delete("pointer")
        self.delete("pixel")

        self.canvas_photo_image = ImageTk.PhotoImage(self.scaled_main_image)
        self.itemconfig(self.canvas_image_item, image=self.canvas_photo_image)

    def _mouse_motion(self, event: Event):
        self._display_pointer_location(event)

    def _update_canvas_image(self):
        width = int(self.root.pixel_size * self.root.scale) * self.root.canvas_width

        print(width)

        self.scaled_main_image = self.main_image.resize((width , 
                                                         width), 
                                                         Image.Resampling.NEAREST)

        self.canvas_photo_image = ImageTk.PhotoImage(self.scaled_main_image)
        self.itemconfig(self.canvas_image_item, image=self.canvas_photo_image)

    def _update_scale(self):
        self.root.scale = (self.winfo_height() / self.root.canvas_height) * 0.95
        self.root.baseline_scale = self.root.scale

        self._update_canvas_image()

        self.offset_x = (self.winfo_width() - self.canvas_photo_image.width()) / 2
        self.offset_y = (self.winfo_height() - self.canvas_photo_image.height()) / 2
        self.moveto(ALL, self.offset_x, self.offset_y)

    def resize_canvas(self):
        self._update_scale()

        new_image = Image.new("RGBA", (self.root.canvas_width, self.root.canvas_height), "white")
        new_image.paste(self.main_image, (0, 0))

        self.main_image = new_image
        self._update_canvas_image()
        
    def place_pixel(self, event: Event, fill: str, tag: str, delete: bool, commit_pixel:bool):
        self._clear_select()
        self._clear_pasted()

        GRID_X = floor((event.x - self.offset_x) / (self.scaled_main_image.width / self.root.canvas_width))
        GRID_Y = floor((event.y - self.offset_y) / (self.scaled_main_image.height / self.root.canvas_height))

        if GRID_X >= self.root.canvas_width or GRID_X < 0: return
        if GRID_Y >= self.root.canvas_height or GRID_Y < 0: return

        START_X = GRID_X - floor(self.root.pixel_size / 2) if GRID_X - floor(self.root.pixel_size / 2) > 0 else 0
        START_Y = GRID_Y - floor(self.root.pixel_size / 2) if GRID_Y - floor(self.root.pixel_size / 2) > 0 else 0

        WIDTH = self.root.pixel_size if GRID_X - floor(self.root.pixel_size / 2) > 0 else self.root.pixel_size + (GRID_X - floor(self.root.pixel_size / 2))
        HEIGHT = self.root.pixel_size if GRID_Y - floor(self.root.pixel_size / 2) > 0 else self.root.pixel_size + (GRID_Y - floor(self.root.pixel_size / 2))

        END_X = START_X + WIDTH if START_X + WIDTH < self.root.canvas_width else self.root.canvas_width
        END_Y = START_Y + HEIGHT if START_Y + HEIGHT < self.root.canvas_height else self.root.canvas_height

        size = self.scaled_main_image.width / self.root.canvas_width

        scaled_sx = GRID_X * size
        scaled_sy = GRID_Y * size

        scaled_ex = (GRID_X * size) + size - 1
        scaled_ey = (GRID_Y * size) + size - 1

        print(scaled_sx, scaled_ex)
        
        self.create_rectangle(scaled_sx + self.offset_x,
                              scaled_sy + self.offset_y,
                              scaled_ex + self.offset_x,
                              scaled_ey + self.offset_y,
                              fill=fill, outline=fill, tags=tag)
        
        if commit_pixel:
            ImageDraw.Draw(self.main_image).rectangle([START_X, START_Y, END_X - 1, END_Y - 1], fill, outline=None)
            ImageDraw.Draw(self.scaled_main_image).rectangle([scaled_sx, scaled_sy, 
                                                              scaled_ex, scaled_ey],
                                                              fill, outline=None)
        
        print(int((START_X * self.root.scale)), (START_X * self.root.scale), self.scaled_main_image.width)
        print(int((END_X * self.root.scale)), (END_X * self.root.scale), self.root.pixel_size * self.root.scale)
        print((int((END_X * self.root.scale))) - int((START_X * self.root.scale)), (event.x - self.offset_x) / self.root.scale)
        print(floor((event.x - self.offset_x) / (self.scaled_main_image.width / self.root.canvas_width)), GRID_X, (event.x - self.offset_x))
        print("")
        print("")

    def _display_pointer_location(self, event: Event):
        self.delete("pointer")
        
        if self.root.interaction_state == "draw":
            self.place_pixel(event=event,
                            fill="red",
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

        ZOOM_INTERVAL = self.root.baseline_scale * 0.05
        PREV_SCALE = self.root.scale

        if self.root.scale + ZOOM_INTERVAL <= self.root.baseline_scale * 3 and event.delta > 0:
            self.root.scale += ZOOM_INTERVAL
        elif self.root.scale - ZOOM_INTERVAL >= self.root.baseline_scale * 0.05 and event.delta < 0:
            self.root.scale -= ZOOM_INTERVAL
        else:
            return

        SCALE = self.root.scale

        self.offset_x = event.x - (event.x - self.offset_x) * (SCALE / PREV_SCALE)
        self.offset_y = event.y - (event.y - self.offset_y) * (SCALE / PREV_SCALE)

        if self.pasted_area:
            SCALED_COPIED_AREA = self.copied_area.resize((int(self.copied_area.width * SCALE), int(self.copied_area.height * SCALE)), Image.Resampling.NEAREST) # type: ignore

            self.scaled_copied_area = ImageTk.PhotoImage(SCALED_COPIED_AREA)
            self.itemconfig(self.pasted_area, image=self.scaled_copied_area)

        self._update_canvas_image()
        self.scale(ALL, event.x, event.y, SCALE / PREV_SCALE, SCALE / PREV_SCALE)


    def _start_pan(self, event: Event):
        self.start_x = event.x
        self.start_y = event.y

        self._clear_select()

    def _pan(self, event: Event):     
        x = event.x - self.start_x
        y = event.y - self.start_y

        self.offset_x += x
        self.offset_y += y

        self.start_x = event.x
        self.start_y = event.y

        self.move(ALL, x, y)

    def _start_select(self, event: Event):
        self.start_x = event.x
        self.start_y = event.y

        self._clear_select()

    def _select(self, event: Event):
        self._clear_select()
        self._clear_pasted()

        WIDTH = self.root.canvas_width
        HEIGHT = self.root.canvas_height

        x_coords = [floor((self.start_x - self.offset_x) / self.root.scale), floor((event.x - self.offset_x) / self.root.scale)] # [top x, bottom x]
        y_coords = [floor((self.start_y - self.offset_y) / self.root.scale), floor((event.y - self.offset_y) / self.root.scale)] # [top y, bottom y]

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

        self.create_rectangle((x_coords[0] * self.root.scale) + self.offset_x,
                              (y_coords[0] * self.root.scale) + self.offset_y, 
                              (x_coords[1] * self.root.scale) + self.offset_x, 
                              (y_coords[1] * self.root.scale) + self.offset_y,
                              outline="black", tags="select_outline", width=2)
        
    def _clear_select(self):
        self.delete("select_outline")
        self.selected_area = {}

    def _delete_selected(self, event: Event):
        SIZE_X = self.selected_area["end_x"] - self.selected_area["start_x"]
        SIZE_Y = self.selected_area["end_y"] - self.selected_area["start_y"]

        for i in range(SIZE_Y + 1):
            for j in range(SIZE_X + 1):
                try:
                    self.main_image.load()[self.selected_area["start_x"] + j, self.selected_area["start_y"] + i] = (0, 0, 0, 0) # type: ignore
                except IndexError:
                    pass
        
        self._clear_select()
        self._update_canvas_image()

    def _copy_selected(self, event: Event):
        self.copied_area = self.main_image.crop((self.selected_area["start_x"],
                                                   self.selected_area["start_y"],
                                                   self.selected_area["end_x"],
                                                   self.selected_area["end_y"]))
    
        self._clear_pasted()
        self._clear_select()
        
    def _paste_selected(self, event: Event):
        GRID_X = floor((event.x - self.offset_x) / self.root.scale)
        GRID_Y = floor((event.y - self.offset_y) / self.root.scale)

        if GRID_X > self.root.canvas_width or GRID_X < 0: return
        if GRID_Y > self.root.canvas_height or GRID_Y < 0: return

        self.root.set_interaction_state("move")
        self._clear_pasted()

        SCALED_COPIED_AREA = self.copied_area.resize((int(self.copied_area.width * self.root.scale), int(self.copied_area.height * self.root.scale)), Image.Resampling.NEAREST) # type: ignore
        self.copied_area_photo_image = ImageTk.PhotoImage(SCALED_COPIED_AREA)

        self.pasted_area = self.create_image(((GRID_X * self.root.scale) + self.offset_x,
                                              (GRID_Y * self.root.scale) + self.offset_y), 
                                              image=self.copied_area_photo_image, tags="placement_box")

        self.create_rectangle(((GRID_X * self.root.scale) - (SCALED_COPIED_AREA.width / 2) + self.offset_x, 
                               (GRID_Y * self.root.scale) - (SCALED_COPIED_AREA.height / 2) + self.offset_y, 
                               (GRID_X * self.root.scale) + (SCALED_COPIED_AREA.width / 2) + self.offset_x, 
                               (GRID_Y * self.root.scale) + (SCALED_COPIED_AREA.height / 2) + self.offset_y), 
                               outline="blue", width=2, tags=["placement_box", "placement_outline"])
        
        self.tag_bind("placement_box", "<Button-1>", self._start_move_pasted)
        self.tag_bind("placement_box", "<B1-Motion>", self._move_pasted)

    def _start_move_pasted(self, event: Event):
        self.start_x = event.x
        self.start_y = event.y

        self._clear_select()

    def _move_pasted(self, event: Event):
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

        if WORLD_X + X < WIDTH * -1 or WORLD_X + WIDTH + X > self.canvas_photo_image.width() + WIDTH: return
        if WORLD_Y + Y < HEIGHT * -1 or WORLD_Y + HEIGHT + Y > self.canvas_photo_image.height() + HEIGHT: return

        self.move("placement_box", X, Y)

    def _commit_pasted(self, event: Event):
        X = self.coords(self.pasted_area)[0] # type: ignore
        Y = self.coords(self.pasted_area)[1] # type: ignore

        HALF_X = (self.bbox(self.pasted_area)[2] - self.bbox(self.pasted_area)[0]) / 2 # type: ignore
        HALF_Y = (self.bbox(self.pasted_area)[1] - self.bbox(self.pasted_area)[3]) / 2 # type: ignore
        
        self.main_image.paste(self.copied_area, (int(((X - HALF_X) - self.offset_x) / self.root.scale), int(((Y + HALF_Y) - self.offset_y) / self.root.scale))) # type: ignore

        self._clear_pasted()
        self._update_canvas_image()

    def _clear_pasted(self):
        self.pasted_area = None
        self.delete("placement_box")