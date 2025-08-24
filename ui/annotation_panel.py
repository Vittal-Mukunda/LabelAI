# C:\LabelAI\ui\annotation_panel.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel

class AnnotationPanel(QWidget):
    def __init__(self):
        super().__init__()
        
        # Set object name for specific styling from style.qss
        self.setObjectName("AnnotationPanel")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        
        self.title = QLabel("Annotations")
        self.annotation_list = QListWidget()
        
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.annotation_list)

    def update_annotations(self, annotations):
        self.annotation_list.clear()
        for i, annotation in enumerate(annotations):
            label = annotation.get("label", "N/A")
            bbox = annotation.get("bbox", [])
            self.annotation_list.addItem(f"{i+1}: {label} {bbox}")
