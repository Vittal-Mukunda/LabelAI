# C:\LabelAI\ui\annotation_panel.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QLabel, 
                             QLineEdit, QPushButton, QHBoxLayout, QMessageBox)
from PyQt5.QtCore import pyqtSignal

class AnnotationPanel(QWidget):
    # Signal to notify MainWindow when the active label changes
    activeLabelChanged = pyqtSignal(str)
    # Signal to notify when the list of class labels has been modified
    classLabelsChanged = pyqtSignal()
    # Signal to send the updated annotation list back to MainWindow
    annotationsUpdated = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.setObjectName("AnnotationPanel")
        
        self.current_annotations = []
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        class_title = QLabel("Class Labels")
        self.label_list = QListWidget()
        self.label_list.currentItemChanged.connect(self.on_label_selection_changed)
        
        add_layout = QHBoxLayout()
        self.new_label_input = QLineEdit()
        self.new_label_input.setPlaceholderText("Enter new label...")
        self.new_label_input.returnPressed.connect(self.add_new_label)
        
        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_new_label)
        add_layout.addWidget(self.new_label_input)
        add_layout.addWidget(add_button)

        delete_label_button = QPushButton("Delete Selected Label")
        delete_label_button.clicked.connect(self.delete_selected_label)
        
        annotation_title = QLabel("Image Annotations")
        self.annotation_list = QListWidget()
        self.annotation_list.setSelectionMode(QListWidget.ExtendedSelection)

        delete_annotation_button = QPushButton("Delete Selected Annotation(s)")
        delete_annotation_button.clicked.connect(self.delete_selected_annotations)
        
        main_layout.addWidget(class_title)
        main_layout.addWidget(self.label_list)
        main_layout.addLayout(add_layout)
        main_layout.addWidget(delete_label_button)
        main_layout.addWidget(annotation_title)
        main_layout.addWidget(self.annotation_list)
        main_layout.addWidget(delete_annotation_button)

    def on_label_selection_changed(self, current, previous):
        if current:
            self.activeLabelChanged.emit(current.text())
        else:
            self.activeLabelChanged.emit("")

    def add_new_label(self):
        label_text = self.new_label_input.text().strip()
        if label_text:
            items = [self.label_list.item(i).text() for i in range(self.label_list.count())]
            if label_text not in items:
                self.label_list.addItem(label_text)
                self.label_list.setCurrentRow(self.label_list.count() - 1)
                self.classLabelsChanged.emit()
        self.new_label_input.clear()

    def delete_selected_label(self):
        selected_items = self.label_list.selectedItems()
        if not selected_items: return
        
        label_to_delete = selected_items[0].text()
        
        reply = QMessageBox.question(self, 'Delete Label', 
            f"You are about to delete the class label '{label_to_delete}'.\n\nDo you also want to remove all annotations with this label from the CURRENT image?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)

        if reply == QMessageBox.Cancel:
            return

        self.label_list.takeItem(self.label_list.row(selected_items[0]))
        self.classLabelsChanged.emit()

        if reply == QMessageBox.Yes:
            self.current_annotations = [ann for ann in self.current_annotations if ann.get("label") != label_to_delete]
            self.annotationsUpdated.emit(self.current_annotations)
            # --- FIX: Also update the panel's own view ---
            self.update_annotations(self.current_annotations)

    def delete_selected_annotations(self):
        """Deletes the selected items from the image annotation list."""
        selected_rows = sorted([self.annotation_list.row(item) for item in self.annotation_list.selectedItems()], reverse=True)
        if not selected_rows: return

        # Modify the underlying data model
        for row in selected_rows:
            del self.current_annotations[row]
            
        # Notify the rest of the application (e.g., the ImageViewer) of the change
        self.annotationsUpdated.emit(self.current_annotations)
        
        # --- FIX: Resynchronize the visual list with the updated data model ---
        self.update_annotations(self.current_annotations)

    def update_annotations(self, annotations):
        """Loads and stores the annotations for the current image, then updates the view."""
        self.current_annotations = annotations
        self.annotation_list.clear()
        for i, ann in enumerate(self.current_annotations):
            label = ann.get("label", "N/A")
            ann_type = ann.get("type", "N/A").upper()
            self.annotation_list.addItem(f"{i+1}: [{ann_type}] {label}")

    def get_class_labels(self):
        return [self.label_list.item(i).text() for i in range(self.label_list.count())]

    def load_class_labels(self, labels):
        self.label_list.clear()
        self.label_list.addItems(labels)

    def select_label_by_index(self, index):
        """Selects a class label in the list by its numerical index."""
        if 0 <= index < self.label_list.count():
            self.label_list.setCurrentRow(index)

    def clear_all(self):
        """Resets the panel to its initial state."""
        self.label_list.clear()
        self.annotation_list.clear()
        self.current_annotations = []
        self.new_label_input.clear()
