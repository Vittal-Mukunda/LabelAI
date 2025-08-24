# C:\LabelAI\ui\image_viewer.py

from PyQt5.QtWidgets import QLabel, QInputDialog
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QPolygonF
# --- FIX 1: Import pyqtSignal ---
from PyQt5.QtCore import Qt, QPoint, QRect, QPointF, pyqtSignal

class ImageViewer(QLabel):
    # --- FIX 2: Define the signal as a class attribute ---
    # This signal will be emitted whenever the annotation list is modified.
    annotationsChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.pixmap = None
        self.annotations = []
        self.setMinimumSize(1, 1)

        self.active_tool = "bbox"
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.current_polygon_points = []
        self.setMouseTracking(True)

    def set_tool(self, tool_name):
        self.active_tool = tool_name
        self.current_polygon_points = []
        self.start_point, self.end_point = QPoint(), QPoint()
        self.update()
        print(f"Tool set to: {self.active_tool}")

    def load_image(self, path):
        self.pixmap = QPixmap(path)
        self.update()

    def load_annotations(self, annotations):
        self.annotations = annotations
        self.update()

    def mousePressEvent(self, event):
        if self.active_tool == "bbox" and event.button() == Qt.LeftButton:
            self.start_point = event.pos()
            self.end_point = event.pos()
        elif self.active_tool == "polygon":
            if event.button() == Qt.LeftButton:
                self.current_polygon_points.append(event.pos())
            elif event.button() == Qt.RightButton and len(self.current_polygon_points) > 2:
                self.finalize_polygon()
        self.update()

    def mouseMoveEvent(self, event):
        if self.active_tool == "bbox" and event.buttons() & Qt.LeftButton:
            self.end_point = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        if self.active_tool == "bbox" and event.button() == Qt.LeftButton:
            self.finalize_bbox()

    def finalize_bbox(self):
        rect = QRect(self.start_point, self.end_point).normalized()
        label, ok = QInputDialog.getText(self, 'Input Label', 'Enter object label:')
        if ok and label:
            annotation = {
                "label": label, 
                "type": "bbox", 
                "bbox": [rect.x(), rect.y(), rect.width(), rect.height()]
            }
            self.annotations.append(annotation)
            # --- FIX 3: Emit the signal after adding an annotation ---
            self.annotationsChanged.emit()
        self.start_point, self.end_point = QPoint(), QPoint()
        self.update()

    def finalize_polygon(self):
        label, ok = QInputDialog.getText(self, 'Input Label', 'Enter object label:')
        if ok and label:
            points = [[p.x(), p.y()] for p in self.current_polygon_points]
            annotation = {"label": label, "type": "polygon", "points": points}
            self.annotations.append(annotation)
            # --- FIX 3: Emit the signal here as well ---
            self.annotationsChanged.emit()
        self.current_polygon_points = []
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.pixmap:
            painter.drawText(self.rect(), Qt.AlignCenter, "No image loaded")
            return

        scaled_pixmap = self.pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        x = (self.width() - scaled_pixmap.width()) / 2
        y = (self.height() - scaled_pixmap.height()) / 2
        painter.drawPixmap(QPoint(int(x), int(y)), scaled_pixmap)
        
        pen = QPen(QColor(0, 255, 0), 2)
        painter.setPen(pen)
        for ann in self.annotations:
            if ann["type"] == "bbox":
                painter.drawRect(QRect(*ann["bbox"]))
                painter.drawText(ann["bbox"][0], ann["bbox"][1] - 5, ann["label"])
            elif ann["type"] == "polygon":
                points = [QPointF(p[0], p[1]) for p in ann["points"]]
                painter.drawPolygon(QPolygonF(points))
                painter.drawText(points[0].x(), points[0].y() - 5, ann["label"])

        pen.setColor(QColor(255, 255, 0))
        painter.setPen(pen)
        if self.active_tool == "bbox" and not self.start_point.isNull():
            painter.drawRect(QRect(self.start_point, self.end_point))
        elif self.active_tool == "polygon" and self.current_polygon_points:
            points = self.current_polygon_points + [self.mapFromGlobal(self.cursor().pos())]
            painter.drawPolyline(QPolygonF(points))
