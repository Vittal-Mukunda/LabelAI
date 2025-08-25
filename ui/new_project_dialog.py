# C:\LabelAI\ui\new_project_dialog.py

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QPushButton, QDialogButtonBox,
                             QMessageBox)

from backend.model_database import get_tasks

class NewProjectDialog(QDialog):
    def __init__(self, existing_projects, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Project")
        self.setMinimumWidth(400)
        
        self.existing_projects = [p.lower() for p in existing_projects]
        self.project_name = ""
        self.annotation_task = ""

        # Layouts
        layout = QVBoxLayout(self)
        form_layout = QVBoxLayout()
        
        # Project Name
        name_label = QLabel("Project Name:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., 'City_Traffic_Analysis'")
        
        # Annotation Task
        task_label = QLabel("Annotation Task:")
        self.task_combo = QComboBox()
        self.task_combo.addItems(get_tasks())

        # Add to form layout
        form_layout.addWidget(name_label)
        form_layout.addWidget(self.name_input)
        form_layout.addSpacing(15)
        form_layout.addWidget(task_label)
        form_layout.addWidget(self.task_combo)

        # Dialog Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Add layouts to main dialog
        layout.addLayout(form_layout)
        layout.addSpacing(20)
        layout.addWidget(button_box)

    def accept(self):
        """
        Overrides the default accept behavior to perform validation.
        """
        project_name = self.name_input.text().strip()
        
        # Validation
        if not project_name:
            QMessageBox.warning(self, "Validation Error", "Project name cannot be empty.")
            return
            
        if project_name.lower() in self.existing_projects:
            QMessageBox.warning(self, "Validation Error", "A project with this name already exists.")
            return

        # If validation passes, store the values and accept the dialog
        self.project_name = project_name
        self.annotation_task = self.task_combo.currentText()
        super().accept()

    def get_project_details(self):
        """
        Returns the captured project details if the dialog was accepted.
        """
        return self.project_name, self.annotation_task
