import pygame
from math import floor
from typing import TYPE_CHECKING
import time

def ex_time(func):
    def wrapper(*args, **kwargs) -> None:
        s = time.time()
        func(*args, **kwargs)
        e = time.time()
        print(e-s)
    return wrapper

if TYPE_CHECKING:
    import canvas

class UndoRedo:
    def __init__(self, canvas: "canvas.Canvas") -> None:
        self.canvas = canvas

        self.current_snapshot_coords = {}

        self.undo_list: list = []

    def compare_coords(self, left, top, right, bottom):
        if not self.current_snapshot_coords:
            self.current_snapshot_coords = {"left": left,
                                            "top": top,
                                            "right": right,
                                            "bottom": bottom}

        new_left = left if self.current_snapshot_coords["left"] > left else self.current_snapshot_coords["left"]
        new_top = top if self.current_snapshot_coords["top"] > top else self.current_snapshot_coords["top"]
        new_right = right if self.current_snapshot_coords["right"] < right else self.current_snapshot_coords["right"]
        new_bottom = bottom if self.current_snapshot_coords["bottom"] < bottom else self.current_snapshot_coords["bottom"]

        self.current_snapshot_coords = {"left": new_left,
                                        "top": new_top,
                                        "right": new_right,
                                        "bottom": new_bottom}

    def end_snapshot(self):
        if not self.current_snapshot_coords: return

        snap = self.current_snapshot_coords

        width = snap["right"] - snap["left"]
        height = snap["bottom"] - snap["top"]

        snapshot = pygame.Surface((width, height))
        snapshot.blit(self.canvas.canvas_surface, (0, 0), (snap["left"], snap["top"], snap["right"], snap["bottom"]))

        self.undo_list.append({
            "x": snap["left"],
            "y": snap["top"],
            "snapshot": snapshot
        })

        self.current_snapshot_coords = {}

    def undo(self):
        if len(self.undo_list) <= 0: return

        self.undo_list.pop()
        self.canvas.canvas_surface.fill("white")

        for i in range(len(self.undo_list)):
            el = self.undo_list[i]

            self.canvas.canvas_surface.blit(el["snapshot"], (el["x"], el["y"]))

        self.canvas.render_canvas()

    def redo(self):
        pass