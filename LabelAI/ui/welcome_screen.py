# C:\LabelAI\ui\welcome_screen.py

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QListWidget,
                             QPushButton, QInputDialog, QHBoxLayout)
from PyQt5.QtCore import Qt, pyqtSignal

class WelcomeScreen(QWidget):
    projectSelected = pyqtSignal(str)

    def __init__(self, projects_dir, parent=None):
        super().__init__(parent)
        self.projects_dir = projects_dir

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("LabelAI Projects")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            "font-size: 28px; font-weight: bold; margin-bottom: 20px; color: #EAEAEA;"
        )

        self.project_list = QListWidget()
        self.project_list.setMaximumWidth(450)
        self.project_list.itemDoubleClicked.connect(self.open_selected_project)

        new_project_btn = QPushButton("Create New Project")
        new_project_btn.clicked.connect(self.create_new_project)

        open_project_btn = QPushButton("Open Selected Project")
        open_project_btn.clicked.connect(self.open_selected_project)

        button_layout = QHBoxLayout()
        button_layout.addWidget(new_project_btn)
        button_layout.addWidget(open_project_btn)

        layout.addWidget(title)
        layout.addWidget(self.project_list)
        layout.addLayout(button_layout)

        self.refresh_project_list()

    def refresh_project_list(self):
        self.project_list.clear()
        if not os.path.exists(self.projects_dir):
            os.makedirs(self.projects_dir)

        for item in os.listdir(self.projects_dir):
            if os.path.isdir(os.path.join(self.projects_dir, item)):
                self.project_list.addItem(item)

    def create_new_project(self):
        project_name, ok = QInputDialog.getText(self, "New Project", "Enter project name:")
        if ok and project_name:
            self.projectSelected.emit(project_name)

    def open_selected_project(self):
        selected_items = self.project_list.selectedItems()
        if selected_items:
            project_name = selected_items[0].text()
            self.projectSelected.emit(project_name)
