# C:\LabelAI\ui\image_sidebar.py

import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QListWidgetItem
from PyQt5.QtCore import pyqtSignal, QSize, Qt
from PyQt5.QtGui import QIcon, QPixmap

class ImageSidebar(QWidget):
    # Emits the full path of the image to be opened
    imageSelected = pyqtSignal(str)
    # Signals that the "Add Images" button was clicked
    addImagesClicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(150)
        self.setMaximumWidth(250)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        self.add_button = QPushButton("Add Images...")
        self.add_button.clicked.connect(self.addImagesClicked)

        self.image_list_widget = QListWidget()
        self.image_list_widget.setIconSize(QSize(128, 128))
        self.image_list_widget.setViewMode(QListWidget.IconMode)
        self.image_list_widget.setResizeMode(QListWidget.Adjust)
        self.image_list_widget.setMovement(QListWidget.Static)
        self.image_list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)

        layout.addWidget(self.add_button)
        layout.addWidget(self.image_list_widget)

    def on_item_double_clicked(self, item):
        """When a thumbnail is double-clicked, emit the signal to open it."""
        path = item.data(Qt.UserRole)
        if path:
            self.imageSelected.emit(path)

    def populate_from_directory(self, image_dir):
        """Scans a directory and populates the list with image thumbnails."""
        self.image_list_widget.clear()
        image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']
        
        if not os.path.isdir(image_dir):
            return

        for filename in sorted(os.listdir(image_dir)):
            if any(filename.lower().endswith(ext) for ext in image_extensions):
                full_path = os.path.join(image_dir, filename)
                
                # Create an item with a thumbnail and store the full path
                item = QListWidgetItem(QIcon(full_path), filename)
                item.setData(Qt.UserRole, full_path)
                item.setToolTip(full_path)
                
                self.image_list_widget.addItem(item)

