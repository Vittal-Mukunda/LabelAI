# C:\LabelAI\ui\annotation_panel.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QPushButton,
                             QLineEdit, QLabel, QListWidgetItem, QAbstractItemView)
from PyQt5.QtCore import pyqtSignal

class AnnotationPanel(QWidget):
    classLabelSelected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        # --- Class Label Management ---
        layout.addWidget(QLabel("Class Labels"))
        self.class_input = QLineEdit()
        self.class_input.setPlaceholderText("Enter new class label")
        add_class_btn = QPushButton("Add Class")
        add_class_btn.clicked.connect(self.add_class_label)

        self.class_list_widget = QListWidget()
        self.class_list_widget.itemClicked.connect(self.on_class_label_selected)

        # --- Annotation List ---
        layout.addWidget(QLabel("Annotations"))
        self.annotation_list_widget = QListWidget()
        self.annotation_list_widget.setSelectionMode(QAbstractItemView.NoSelection)

        layout.addWidget(self.class_input)
        layout.addWidget(add_class_btn)
        layout.addWidget(self.class_list_widget)
        layout.addWidget(self.annotation_list_widget)

    def add_class_label(self):
        """Adds a new class label from the input field."""
        label_text = self.class_input.text().strip()
        if label_text:
            # Check if the item already exists
            if not self.class_list_widget.findItems(label_text, 0):
                self.class_list_widget.addItem(label_text)
                self.class_input.clear()

    def on_class_label_selected(self, item):
        """Emits the text of the selected class label."""
        self.classLabelSelected.emit(item.text())

    def get_selected_class_label(self):
        """Returns the text of the currently selected class label."""
        selected_items = self.class_list_widget.selectedItems()
        if selected_items:
            return selected_items[0].text()
        return None

    def select_label_by_index(self, index):
        """Selects a class label by its 1-based index for keyboard shortcuts."""
        if 0 < index <= self.class_list_widget.count():
            item = self.class_list_widget.item(index - 1)
            self.class_list_widget.setCurrentItem(item)
            self.classLabelSelected.emit(item.text())

    def update_annotations(self, annotations):
        """Updates the annotation list for the current image."""
        self.annotation_list_widget.clear()
        for i, ann in enumerate(annotations):
            label = ann.get('label', 'Unlabeled')
            ann_type = ann.get('type', 'N/A')
            item_text = f"Annotation {i+1}: {label} [{ann_type}]"
            self.annotation_list_widget.addItem(item_text)
