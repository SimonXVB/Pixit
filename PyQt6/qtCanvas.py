import sys
import time
from PySide6.QtGui import QMouseEvent, QPen, QBrush, QPixmap, QPainter
from PySide6.QtWidgets import QGraphicsSceneMouseEvent, QMainWindow, QGraphicsView, QGraphicsScene, QApplication, QGraphicsItem, QGraphicsPixmapItem
from PySide6.QtCore import Qt, QSize

def ex_time(func): # type: ignore
    def wrapper(*args, **kwargs) -> None: # type: ignore
        s = time.time()
        func(*args, **kwargs)
        e = time.time()
        print(e-s)
    return wrapper # type: ignore


class PixmapItem(QGraphicsPixmapItem):
    def __init__(self, pixmap: QPixmap, scene: QGraphicsScene, parent=None):
        super().__init__(pixmap, parent)

        self.pixma = pixmap
        self.scen = scene

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

    @ex_time
    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        painter = QPainter(self.pixma)
        painter.drawRect(int(event.pos().x()), int(event.pos().y()), 100, 75)
        painter.end()

        self.setPixmap(self.pixma)

        return super().mousePressEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Test")

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)

        pixmap = QPixmap(1000, 1000)
        pixmap.fill(Qt.GlobalColor.red)

        idk = PixmapItem(pixmap, self.scene)

        self.scene.addItem(idk)
        self.setCentralWidget(self.view)
        

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()