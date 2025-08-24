fix-file-dialog
# C:\LabelAI\ui\annotation_panel.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QPushButton,
                             QLineEdit, QLabel, QListWidgetItem, QAbstractItemView)
from PyQt5.QtCore import pyqtSignal

class AnnotationPanel(QWidget):
  
 # Placeholder for ui/annotation_panel.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QPushButton, QLineEdit, QTreeWidgetItem
from PyQt5.QtCore import pyqtSignal

class AnnotationPanel(QWidget):
    # Signal to indicate the active class label has changed.
    # The string argument will be the name of the class label.
 main
    classLabelSelected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

 fix-file-dialog
        layout = QVBoxLayout(self)

        # --- Class Label Management ---
        layout.addWidget(QLabel("Class Labels"))

        # Main layout
        layout = QVBoxLayout(self)

        # Class label management
main
        self.class_input = QLineEdit()
        self.class_input.setPlaceholderText("Enter new class label")
        add_class_btn = QPushButton("Add Class")
        add_class_btn.clicked.connect(self.add_class_label)

fix-file-dialog
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

        # Use a QTreeWidget to support grouped annotations (Feature 3)
        self.annotation_tree = QTreeWidget()
        self.annotation_tree.setColumnCount(1)
        self.annotation_tree.setHeaderLabels(["Annotations"])
        self.annotation_tree.itemClicked.connect(self.on_item_clicked)

        layout.addWidget(self.class_input)
        layout.addWidget(add_class_btn)
        layout.addWidget(self.annotation_tree)

        self.class_labels = {} # To store class labels as top-level items
main

    def add_class_label(self):
        """Adds a new class label from the input field."""
        label_text = self.class_input.text().strip()
fix-file-dialog
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
=======
        if label_text and label_text not in self.class_labels:
            class_item = QTreeWidgetItem(self.annotation_tree)
            class_item.setText(0, label_text)
            self.class_labels[label_text] = class_item
            self.class_input.clear()

    def on_item_clicked(self, item, column):
        """When an item is clicked, check if it's a top-level class label."""
        # This helps fix the "Active Label Not Recognized" bug (Bug 2).
        # We emit the signal only if a class label (a top-level item) is selected.
        if item.parent() is None: # It's a class label
            self.classLabelSelected.emit(item.text(0))

    def get_selected_class_label(self):
        """
        This method is the key to fixing Bug 2.
        It should return the text of the currently selected top-level item (class label).
        """
        selected_items = self.annotation_tree.selectedItems()
        if not selected_items:
            return None

        selected_item = selected_items[0]
        # A class label is a top-level item (it has no parent)
        if selected_item.parent() is None:
            return selected_item.text(0)
        # If a child (annotation) is selected, return its parent's (class) label
        else:
            return selected_item.parent().text(0)

    def select_label_by_index(self, index):
        """
        Selects a class label by its numerical index (for Feature 2: Keyboard Shortcuts).
        The index is 1-based.
        """
        if 0 < index <= self.annotation_tree.topLevelItemCount():
            item = self.annotation_tree.topLevelItem(index - 1)
            self.annotation_tree.setCurrentItem(item)
            self.classLabelSelected.emit(item.text(0)) # Emit signal to update viewer

    def update_annotations(self, annotations):
        """
        Updates the tree view with annotations, grouped by class label (Feature 3).
        """
        # Clear previous annotations, but not the class labels themselves
        for class_item in self.class_labels.values():
            class_item.takeChildren()

        # Group annotations by label
        grouped_annotations = {}
        for ann in annotations:
            label = ann.get('label', 'Unlabeled')
            if label not in grouped_annotations:
                grouped_annotations[label] = []
            grouped_annotations[label].append(ann)

        # Populate the tree
        for label, ann_list in grouped_annotations.items():
            if label in self.class_labels:
                parent_item = self.class_labels[label]
                for i, ann in enumerate(ann_list):
                    # Displaying annotation type or coordinates as a child item
                    child_item = QTreeWidgetItem(parent_item)
                    child_item.setText(0, f"Annotation {i+1} [{ann.get('type','N/A')}]")

        self.annotation_tree.expandAll()
main
