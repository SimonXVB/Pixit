class Data:
    def __init__(self) -> None:
        self.color: str = "#000000"
        self.bg: str = "#FFFB00"
        self.is_deleting: bool = False
        self.is_selecting: bool = False
        self.show_grid: bool = True
        self.shape_options: list[str] = ["none", "triangle", "square", "circle", "hexagon"]
        self.shape: str = "none"