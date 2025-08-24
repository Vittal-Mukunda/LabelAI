# Placeholder for ui/image_viewer.py

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, Qt

class ImageViewer(QWidget):
    # Signal emitted when annotations are changed by the user.
    annotationsChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.image_label = QLabel("No Image Loaded")
        self.image_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label)

        self.image_path = None
        self.pixmap = None
        self.annotations = []
        self.active_tool = "bbox" # Default tool
        self.active_class_label = None # Will be set from the main window

    def load_image(self, path):
        """Loads an image from the given file path."""
        self.image_path = path
        self.pixmap = QPixmap(path)
        self.image_label.setPixmap(self.pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.annotations = [] # Reset annotations when a new image is loaded
        self.annotationsChanged.emit()

    def set_tool(self, tool_name):
        """Sets the active drawing tool (e.g., 'bbox', 'polygon')."""
        self.active_tool = tool_name
        print(f"ImageViewer tool set to: {self.active_tool}")

    def set_active_class_label(self, label):
        """
        Receives the currently selected class label from the main window.
        This is the other half of the fix for Bug 2.
        """
        self.active_class_label = label
        print(f"ImageViewer active class set to: {self.active_class_label}")

    def load_annotations(self, annotations_data):
        """Loads annotation data for the current image."""
        self.annotations = annotations_data
        self.annotationsChanged.emit()
        # In a real implementation, you would also draw these annotations on the image.

    def mousePressEvent(self, event):
        """
        Handles mouse presses to start drawing an annotation.
        This is where Bug 2 manifests.
        """
        # Check if a class label is selected before allowing annotation.
        if not self.active_class_label:
            QMessageBox.warning(self, "No Class Label", "Please select a class label from the panel before annotating.")
            return

        # Placeholder for creating an annotation.
        # In a real app, you would start tracking mouse movement here.
        print(f"Starting to draw a '{self.active_tool}' with label '{self.active_class_label}' at {event.pos()}.")

        # Create a dummy annotation for demonstration
        new_annotation = {
            "label": self.active_class_label,
            "type": self.active_tool,
            "coordinates": [event.x(), event.y()] # Simplified
        }
        self.annotations.append(new_annotation)
        self.annotationsChanged.emit()

    def resizeEvent(self, event):
        """Handle resizing of the widget to scale the image."""
        if self.pixmap:
            self.image_label.setPixmap(self.pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
