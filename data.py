class Data:
    def __init__(self) -> None:
        self.color: str = "#000000"
        self.shape: str | None = None
        self.is_deleting: bool = False
        self.is_selecting: bool = False
        self.show_grid: bool = True