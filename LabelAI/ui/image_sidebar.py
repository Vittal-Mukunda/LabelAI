# C:\LabelAI\ui\image_sidebar.py

from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtCore import pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QPixmap

class ImageSidebar(QListWidget):
    # Signal emitted when an image thumbnail is clicked.
    # The string argument will be the full path to the image.
    imageSelected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIconSize(QSize(100, 100))
        self.setFlow(QListWidget.LeftToRight)
        self.setWrapping(True)
        self.setResizeMode(QListWidget.Adjust)
        self.setViewMode(QListWidget.IconMode)
        self.itemClicked.connect(self.on_item_clicked)

    def add_images(self, image_paths):
        """Adds multiple images to the sidebar as thumbnails."""
        for path in image_paths:
            # Store the full path in the item's data
            item = QListWidgetItem()
            item.setData(1, path) # Using a custom role to store the path

            # Create a thumbnail icon
            pixmap = QPixmap(path)
            item.setIcon(QIcon(pixmap))
            item.setText(path.split('/')[-1]) # Show filename

            self.addItem(item)

    def on_item_clicked(self, item):
        """Emits a signal with the full image path when an item is clicked."""
        path = item.data(1)
        if path:
            self.imageSelected.emit(path)

    def clear_images(self):
        """Clears all images from the sidebar."""
        self.clear()
