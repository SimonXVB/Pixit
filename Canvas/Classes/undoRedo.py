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

        self.snapshots: list = []
        self.redo_snapshots: list = []

    def set_snapshot_rect(self, left, top, right, bottom):
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

    def create_snapshot(self, custom_coords = None):
        coords = self.current_snapshot_coords if not custom_coords else custom_coords
        if not coords: return

        snapshot = pygame.Surface((coords["right"] - coords["left"], coords["bottom"] - coords["top"]))
        snapshot.blit(self.canvas.canvas_surface, (0, 0), (coords["left"], coords["top"], coords["right"], coords["bottom"]))

        self.snapshots.append({
            "x": coords["left"],
            "y": coords["top"],
            "snapshot": snapshot
        })
        self.current_snapshot_coords = {}
        self.redo_snapshots = []

    def undo(self):
        if len(self.snapshots) <= 0: return

        self.redo_snapshots.append(self.snapshots.pop())

        self.canvas.canvas_surface.fill("white")

        for i in range(len(self.snapshots)):
            el = self.snapshots[i]
            self.canvas.canvas_surface.blit(el["snapshot"], (el["x"], el["y"]))

        self.canvas.render_canvas()

    def redo(self):
        if len(self.redo_snapshots) <= 0: return

        redo_el = self.redo_snapshots.pop()
        self.snapshots.append(redo_el)

        self.canvas.canvas_surface.blit(redo_el["snapshot"], (redo_el["x"], redo_el["y"]))
        self.canvas.render_canvas()