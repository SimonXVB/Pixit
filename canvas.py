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

class DrawingCanvas(Canvas):
    def __init__(self, root: "Main"):
        super().__init__(root, bg=root.bg_color, highlightthickness=0)
        self.grid(sticky="NESW", row=1, column=0)
        self.update()

        self.root = root

        self.root.scale = floor(self.winfo_height() / self.root.canvas_height) - 1
        self.root.baseline_scale = self.root.scale

        self.start_x: int = 0
        self.start_y: int = 0

        self.selected_area: dict[str, int] = {"start_x": 0,"start_y": 0,"end_x": 0,"end_y": 0}
        self.copied_area = None #PIL Image
        self.pasted_area = None #Canvas Image

        self.main_image = Image.new("RGBA", (self.root.canvas_width, self.root.canvas_height), "white")
        self.scaled_main_image = self.main_image.resize((self.root.canvas_width * self.root.scale, 
                                                         self.root.canvas_height * self.root.scale), 
                                                         Image.Resampling.NEAREST)
        
        self.offset_x: float = (self.winfo_width() - self.scaled_main_image.width) / 2
        self.offset_y: float = (self.winfo_height() - self.scaled_main_image.height) / 2
        
        self.canvas_photo_image = ImageTk.PhotoImage(self.scaled_main_image)
        self.canvas_image_item = self.create_image((self.offset_x, self.offset_y), image=self.canvas_photo_image, anchor="nw")
        
        self.bind("<Button-1>", self._m1_down)
        self.bind("<B1-Motion>", self._m1_motion)
        self.bind("<B1-ButtonRelease>", self._mouse_up)

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
            self._display_pointer_location(event)
        elif self.root.interaction_state == "select":
            self._select(event)
        elif self.root.interaction_state == "move":
            self._pan(event)

    def _mouse_up(self, event: Event):
        self.delete("pixel")
        self.canvas_photo_image = ImageTk.PhotoImage(self.scaled_main_image)
        self.itemconfig(self.canvas_image_item, image=self.canvas_photo_image)

    def _mouse_motion(self, event: Event):
        self._display_pointer_location(event)

    def _update_canvas_image(self):
        self.scaled_main_image = self.main_image.resize((self.root.canvas_width * self.root.scale, 
                                                         self.root.canvas_height * self.root.scale), 
                                                         Image.Resampling.NEAREST)

        self.canvas_photo_image = ImageTk.PhotoImage(self.scaled_main_image)
        self.itemconfig(self.canvas_image_item, image=self.canvas_photo_image)

    def _update_scale(self):
        self.root.scale = floor(self.winfo_height() / self.root.canvas_height) - 1
        self.root.baseline_scale = self.root.scale

        self._update_canvas_image()

    def resize_canvas(self):
        self._update_scale()

        new_image = Image.new("RGBA", (self.root.canvas_width, self.root.canvas_height), "white")
        new_image.paste(self.main_image, (0, 0))

        self.main_image = new_image
        self._update_canvas_image()
        
    def place_pixel(self, event: Event, tag: str, commit_pixel:bool):
        self._clear_select()
        self._clear_pasted()

        GRID_X = floor((event.x - self.offset_x) / (self.scaled_main_image.width / self.root.canvas_width))
        GRID_Y = floor((event.y - self.offset_y) / (self.scaled_main_image.height / self.root.canvas_height))

        if GRID_X >= self.root.canvas_width or GRID_X < 0: return
        if GRID_Y >= self.root.canvas_height or GRID_Y < 0: return

        start_x = floor((GRID_X - floor(self.root.pixel_size / 2)) * self.root.scale)
        start_y = floor((GRID_Y - floor(self.root.pixel_size / 2)) * self.root.scale)

        end_x = start_x + floor(self.root.pixel_size * self.root.scale)
        end_y = start_y + floor(self.root.pixel_size * self.root.scale)

        if start_x < 0:
            start_x = 0

        if start_y < 0:
            start_y = 0

        if end_x > self.scaled_main_image.width:
            end_x = self.scaled_main_image.width

        if end_y > self.scaled_main_image.width:
            end_y = self.scaled_main_image.width

        if tag == "pointer" and self.root.interaction_state == "delete":
            self.create_rectangle(start_x + self.offset_x,
                                start_y + self.offset_y,
                                end_x + self.offset_x - 1,
                                end_y + self.offset_y - 1,
                                fill="", outline=self.root.color, tags=tag)
        else:
            rect_fill = self.root.color if self.root.interaction_state != "delete" else self.root.bg_color

            self.create_rectangle(start_x + self.offset_x,
                    start_y + self.offset_y,
                    end_x + self.offset_x - 1,
                    end_y + self.offset_y - 1,
                    fill=rect_fill, outline=rect_fill, tags=tag)
        
        if commit_pixel:
            img_fill = self.root.color if self.root.interaction_state != "delete" else "#ffffff00"

            ImageDraw.Draw(self.scaled_main_image).rectangle([start_x, start_y, end_x - 1, end_y - 1], fill=img_fill)
            ImageDraw.Draw(self.main_image).rectangle([floor(start_x / self.root.scale), 
                                                       floor(start_y / self.root.scale), 
                                                       floor(end_x / self.root.scale) - 1, 
                                                       floor(end_y / self.root.scale) - 1], 
                                                       fill=img_fill)
            
    def _display_pointer_location(self, event: Event):
        self.delete("pointer")
        
        if self.root.interaction_state == "draw" or self.root.interaction_state == "delete":
            self.place_pixel(event=event, tag="pointer", commit_pixel=False)

    def _draw_pixel(self, event: Event):
        self.place_pixel(event=event, tag="pixel", commit_pixel=True)

    def _delete_pixel(self, event: Event):
        self.place_pixel(event=event, tag="pixel", commit_pixel=True)
        
    def _check_set_bounds(self, x: float, y: float):
        if self.scaled_main_image.width < self.winfo_width():
            if (self.scaled_main_image.width / 2) * -1 < x < self.winfo_width() - (self.scaled_main_image.width / 2):
                self.offset_x = x
            elif x < (self.scaled_main_image.width / 2) * -1:
                self.offset_x = (self.scaled_main_image.width / 2) * -1
            elif x > self.winfo_width() - (self.scaled_main_image.width / 2):
                self.offset_x = self.winfo_width() - (self.scaled_main_image.width / 2)
        else:
            if (self.winfo_width() / 2) - self.scaled_main_image.width < x < self.winfo_width() / 2:
                self.offset_x = x
            elif x < (self.winfo_width() / 2) - self.scaled_main_image.width:
                self.offset_x = (self.winfo_width() / 2) - self.scaled_main_image.width
            elif x > self.winfo_width() / 2:
                self.offset_x = self.winfo_width() / 2

        if self.scaled_main_image.height < self.winfo_height():
            if (self.scaled_main_image.height / 2) * -1 < y < self.winfo_height() - (self.scaled_main_image.height / 2):
                self.offset_y = y
            elif y < (self.scaled_main_image.height / 2) * -1:
                self.offset_y = (self.scaled_main_image.height / 2) * -1
            elif y > self.winfo_height() - (self.scaled_main_image.height / 2):
                self.offset_y = self.winfo_height() - (self.scaled_main_image.height / 2)
        else:
            if (self.winfo_height() / 2) - self.scaled_main_image.height < y < self.winfo_height() / 2:
                self.offset_y = y
            elif y < (self.winfo_height() / 2) - self.scaled_main_image.height:
                self.offset_y = (self.winfo_height() / 2) - self.scaled_main_image.height
            elif y > self.winfo_height() / 2:
                self.offset_y = self.winfo_height() / 2

    def _zoom(self, event: Event):
        self._clear_select()

        ZOOM_INTERVAL = self.root.baseline_scale * 0.1
        PREV_SCALE = self.root.scale

        if self.root.scale + ZOOM_INTERVAL <= self.root.baseline_scale * 3 and event.delta > 0:
            self.root.scale = floor(self.root.scale) + 1
        elif self.root.scale - ZOOM_INTERVAL >= self.root.baseline_scale * 0.05 and event.delta < 0:
            self.root.scale = floor(self.root.scale) - 1
        else:
            return

        SCALE = self.root.scale

        x = floor(event.x - (event.x - self.offset_x) * (SCALE / PREV_SCALE))
        y = floor(event.y - (event.y - self.offset_y) * (SCALE / PREV_SCALE))

        if self.pasted_area:
            SCALED_COPIED_AREA = self.copied_area.resize((int(self.copied_area.width * SCALE), int(self.copied_area.height * SCALE)), Image.Resampling.NEAREST) # type: ignore

            self.scaled_copied_area = ImageTk.PhotoImage(SCALED_COPIED_AREA)
            self.itemconfig(self.pasted_area, image=self.scaled_copied_area)


        self._check_set_bounds(x, y)
        self.moveto(ALL, self.offset_x, self.offset_y)

        self._update_canvas_image()
        self._display_pointer_location(event)


    def _start_pan(self, event: Event):
        self.start_x = event.x
        self.start_y = event.y

        self._clear_select()

    def _pan(self, event: Event):     
        x = floor(self.offset_x + (event.x - self.start_x))
        y = floor(self.offset_y + (event.y - self.start_y))

        self._check_set_bounds(x, y)
        self.moveto(ALL, self.offset_x, self.offset_y)

        self.start_x = event.x
        self.start_y = event.y




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