# C:\LabelAI\ui\image_sidebar.py

import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QListWidgetItem, QHBoxLayout, QMessageBox
from PyQt5.QtCore import pyqtSignal, QSize, Qt
from PyQt5.QtGui import QIcon

class ImageSidebar(QWidget):
    imageSelected = pyqtSignal(str)
    addImagesClicked = pyqtSignal()
    imagesDeleted = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(150)
        self.setMaximumWidth(250)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add...")
        self.delete_button = QPushButton("Delete...")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)

        self.image_list_widget = QListWidget()
        self.image_list_widget.setIconSize(QSize(128, 128))
        self.image_list_widget.setSelectionMode(QListWidget.ExtendedSelection)
        self.image_list_widget.setViewMode(QListWidget.IconMode)
        self.image_list_widget.setResizeMode(QListWidget.Adjust)
        self.image_list_widget.setMovement(QListWidget.Static)
        
        self.image_list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.add_button.clicked.connect(self.addImagesClicked)
        self.delete_button.clicked.connect(self.handle_delete_request)

        layout.addLayout(button_layout)
        layout.addWidget(self.image_list_widget)

    def handle_delete_request(self):
        selected_items = self.image_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Delete Images", "No images selected.")
            return

        reply = QMessageBox.question(self, "Confirm Deletion", 
                                     f"Are you sure you want to delete {len(selected_items)} image(s)?\n"
                                     "This will also delete their annotation files and cannot be undone.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            paths_to_delete = [item.data(Qt.UserRole) for item in selected_items]
            self.imagesDeleted.emit(paths_to_delete)

    def on_item_double_clicked(self, item):
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

    def clear_all(self):
        """Clears all images from the sidebar."""
        self.image_list_widget.clear()

