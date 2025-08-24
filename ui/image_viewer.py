# C:\LabelAI\ui\image_viewer.py

from PyQt5.QtWidgets import QLabel, QMessageBox
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QPolygonF
from PyQt5.QtCore import Qt, QPoint, QRect, QPointF, QRectF, pyqtSignal

class ImageViewer(QLabel):
    annotationsChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.pixmap = None
        self.annotations = []
        self.setMinimumSize(1, 1)

        self.active_tool = "bbox"
        self.active_label = None # To store the label from MainWindow
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.current_polygon_points = []
        self.setMouseTracking(True)

    # --- Helper methods for coordinate conversion (unchanged) ---
    def get_display_rect(self):
        """Calculates the rectangle where the image is actually displayed (accounts for letterboxing)."""
        if not self.pixmap:
            return QRect()

        scaled_pixmap = self.pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        x = (self.width() - scaled_pixmap.width()) / 2
        y = (self.height() - scaled_pixmap.height()) / 2
        return QRect(int(x), int(y), scaled_pixmap.width(), scaled_pixmap.height())

    def to_relative_coords(self, point):
        """Converts a point from widget coordinates to relative image coordinates (0.0-1.0)."""
        if not self.pixmap:
            return None
        
        display_rect = self.get_display_rect()
        if not display_rect.contains(point):
            return None # Click was outside the image

        clamped_x = max(display_rect.x(), min(point.x(), display_rect.right()))
        clamped_y = max(display_rect.y(), min(point.y(), display_rect.bottom()))

        relative_x = (clamped_x - display_rect.x()) / display_rect.width()
        relative_y = (clamped_y - display_rect.y()) / display_rect.height()
        return QPointF(relative_x, relative_y)

    def to_widget_coords(self, point):
        """Converts a point from relative image coordinates back to widget coordinates."""
        display_rect = self.get_display_rect()
        abs_x = point.x() * display_rect.width() + display_rect.x()
        abs_y = point.y() * display_rect.height() + display_rect.y()
        return QPoint(int(abs_x), int(abs_y))

    def set_tool(self, tool_name):
        self.active_tool = tool_name
        self.current_polygon_points = []
        self.start_point, self.end_point = QPoint(), QPoint()
        self.update()
        print(f"Tool set to: {self.active_tool}")

    # --- FIX: Add the missing set_active_label method ---
    def set_active_label(self, label):
        """Receives the active label from MainWindow."""
        self.active_label = label

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

    # --- FIX: Finalize methods now use self.active_label instead of a dialog ---
    def finalize_bbox(self):
        if not self.active_label:
            QMessageBox.warning(self, "No Label Selected", "Please select a class label from the panel before annotating.")
            self.start_point, self.end_point = QPoint(), QPoint()
            self.update()
            return

        start_rel = self.to_relative_coords(self.start_point)
        end_rel = self.to_relative_coords(self.end_point)
        
        self.start_point, self.end_point = QPoint(), QPoint()
        
        if start_rel and end_rel:
            rect = QRectF(start_rel, end_rel).normalized()
            annotation = {
                "label": self.active_label, 
                "type": "bbox", 
                "bbox": [rect.x(), rect.y(), rect.width(), rect.height()]
            }
            self.annotations.append(annotation)
            self.annotationsChanged.emit()
        self.update()

    def finalize_polygon(self):
        if not self.active_label:
            QMessageBox.warning(self, "No Label Selected", "Please select a class label from the panel before annotating.")
            self.current_polygon_points = []
            self.update()
            return
            
        relative_points = [self.to_relative_coords(p) for p in self.current_polygon_points]
        self.current_polygon_points = []
        relative_points = [p for p in relative_points if p is not None]

        if len(relative_points) > 2:
            points = [[p.x(), p.y()] for p in relative_points]
            annotation = {"label": self.active_label, "type": "polygon", "points": points}
            self.annotations.append(annotation)
            self.annotationsChanged.emit()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.pixmap:
            painter.drawText(self.rect(), Qt.AlignCenter, "No image loaded")
            return

        display_rect = self.get_display_rect()
        painter.drawPixmap(display_rect, self.pixmap)
        
        pen = QPen(QColor(0, 255, 0), 2)
        painter.setPen(pen)
        
        for ann in self.annotations:
            if ann["type"] == "bbox":
                p1 = self.to_widget_coords(QPointF(ann["bbox"][0], ann["bbox"][1]))
                p2 = self.to_widget_coords(QPointF(ann["bbox"][0] + ann["bbox"][2], ann["bbox"][1] + ann["bbox"][3]))
                painter.drawRect(QRect(p1, p2))
                painter.drawText(p1.x(), p1.y() - 5, ann["label"])
            elif ann["type"] == "polygon":
                points = [self.to_widget_coords(QPointF(p[0], p[1])) for p in ann["points"]]
                painter.drawPolygon(QPolygonF(points))
                if points:
                    painter.drawText(points[0].x(), points[0].y() - 5, ann["label"])

        pen.setColor(QColor(255, 255, 0))
        painter.setPen(pen)
        if self.active_tool == "bbox" and not self.start_point.isNull():
            painter.drawRect(QRect(self.start_point, self.end_point))
        elif self.active_tool == "polygon" and self.current_polygon_points:
            points = self.current_polygon_points + [self.mapFromGlobal(self.cursor().pos())]
            painter.drawPolyline(QPolygonF(points))
