# C:\LabelAI\ui\welcome_screen.py

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QListWidget,
                             QPushButton, QHBoxLayout, QFrame, QDialog)
from PyQt5.QtCore import Qt, pyqtSignal

from .new_project_dialog import NewProjectDialog
from backend.project_manager import ProjectManager

class WelcomeScreen(QWidget):
    projectSelected = pyqtSignal(str)

    def __init__(self, project_manager: ProjectManager, parent=None):
        super().__init__(parent)
        self.project_manager = project_manager
        self.setObjectName("WelcomeScreen")

        # Main layout that centers the content
        main_layout = QHBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        # Card-like container for the content
        container = QFrame()
        container.setObjectName("container")
        container.setMaximumWidth(500)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(40, 40, 40, 40)
        container_layout.setSpacing(20)

        # Title
        title = QLabel("Welcome to LabelAI")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)

        # Subtitle
        subtitle = QLabel("Select a project to open or create a new one to begin.")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)

        # Project list
        self.project_list = QListWidget()
        self.project_list.itemDoubleClicked.connect(self.open_selected_project)

        # Buttons
        new_project_btn = QPushButton("Create New Project")
        new_project_btn.clicked.connect(self.create_new_project)
        
        open_project_btn = QPushButton("Open Selected Project")
        open_project_btn.clicked.connect(self.open_selected_project)
        open_project_btn.setObjectName("primaryButton") # For special styling

        button_layout = QHBoxLayout()
        button_layout.addWidget(new_project_btn)
        button_layout.addStretch()
        button_layout.addWidget(open_project_btn)

        # Add widgets to container
        container_layout.addWidget(title)
        container_layout.addWidget(subtitle)
        container_layout.addWidget(self.project_list)
        container_layout.addLayout(button_layout)
        
        # Add container to the main layout
        main_layout.addWidget(container)

        self.refresh_project_list()

    def refresh_project_list(self):
        self.project_list.clear()
        projects = self.project_manager.list_projects()
        self.project_list.addItems(projects)

    def create_new_project(self):
        existing_projects = self.project_manager.list_projects()
        dialog = NewProjectDialog(existing_projects, self)
        
        if dialog.exec_() == QDialog.Accepted:
            project_name, annotation_task = dialog.get_project_details()
            
            # Create the project using the manager
            project_path = self.project_manager.create_project(project_name, annotation_task)
            
            if project_path:
                self.refresh_project_list()
                # Now open the newly created project
                self.projectSelected.emit(project_name)

    def open_selected_project(self):
        selected_items = self.project_list.selectedItems()
        if selected_items:
            project_name = selected_items[0].text()
            self.projectSelected.emit(project_name)
