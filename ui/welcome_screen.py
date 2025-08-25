# C:\LabelAI\ui\welcome_screen.py

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QListWidget,
                             QPushButton, QHBoxLayout, QFrame, QDialog,
                             QLineEdit, QSplitter, QListWidgetItem, QMenu,
                             QMessageBox, QAction)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QPainter, QColor # We'll need icons later

from .new_project_dialog import NewProjectDialog
from backend.project_manager import ProjectManager


class ProjectCard(QWidget):
    """
    A custom widget to display project information in a card-like format.
    """
    def __init__(self, project_details, parent=None):
        super().__init__(parent)
        self.project_name = project_details['name']
        self.annotation_task = project_details['annotation_task']
        self.image_count = project_details['image_count']
        self.last_modified = project_details['last_modified'].strftime("%Y-%m-%d %H:%M")

        self.setMinimumHeight(80)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 10, 15, 10)
        self.layout.setSpacing(15)

        # Annotation Icon (Placeholder)
        self.icon = QLabel(self.annotation_task[0]) # First letter as icon
        self.icon.setObjectName("taskIcon")
        self.icon.setFixedSize(40, 40)
        self.icon.setAlignment(Qt.AlignCenter)

        # Project Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        self.name_label = QLabel(self.project_name)
        self.name_label.setObjectName("projectName")
        self.meta_label = QLabel(f"{self.image_count} images - Last modified: {self.last_modified}")
        self.meta_label.setObjectName("projectMeta")
        
        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.meta_label)
        info_layout.addStretch()

        self.layout.addWidget(self.icon)
        self.layout.addLayout(info_layout)
        self.layout.addStretch()

        # Hover effect setup
        self.hovered = False
        self.setAutoFillBackground(True)
        self.update_background()

    def enterEvent(self, event):
        self.hovered = True
        self.update_background()

    def leaveEvent(self, event):
        self.hovered = False
        self.update_background()

    def update_background(self):
        p = self.palette()
        if self.hovered:
            p.setColor(self.backgroundRole(), QColor("#3A3A3C"))
        else:
            p.setColor(self.backgroundRole(), QColor("#2C2C2E"))
        self.setPalette(p)

class WelcomeScreen(QWidget):
    projectSelected = pyqtSignal(str)

    def __init__(self, project_manager: ProjectManager, parent=None):
        super().__init__(parent)
        self.project_manager = project_manager
        self.all_projects = []
        self.setObjectName("WelcomeScreen")

        # Main layout is a horizontal splitter
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        splitter = QSplitter(Qt.Horizontal)
        
        # --- Left Panel (Action Hub) ---
        left_panel = QFrame()
        left_panel.setObjectName("actionHub")
        left_panel.setFixedWidth(250)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(15)

        app_title = QLabel("LabelAI")
        app_title.setObjectName("appTitle")

        new_project_btn = QPushButton("Create New Project")
        new_project_btn.setObjectName("primaryButton")
        new_project_btn.clicked.connect(self.create_new_project)

        open_project_btn = QPushButton("Open Project...")
        open_project_btn.clicked.connect(self.open_project_from_disk) # New method needed

        recent_projects_label = QLabel("Recent Projects")
        recent_projects_label.setObjectName("sectionTitle")
        self.recent_projects_list = QListWidget()
        self.recent_projects_list.itemClicked.connect(self.open_selected_project)

        left_layout.addWidget(app_title)
        left_layout.addWidget(new_project_btn)
        left_layout.addWidget(open_project_btn)
        left_layout.addStretch(1)
        left_layout.addWidget(recent_projects_label)
        left_layout.addWidget(self.recent_projects_list, 5)

        # --- Right Panel (Project Browser) ---
        right_panel = QFrame()
        right_panel.setObjectName("projectBrowser")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(15)

        browser_title = QLabel("All Projects")
        browser_title.setObjectName("browserTitle")
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search projects...")
        self.search_bar.textChanged.connect(self.filter_projects)

        self.project_browser_list = QListWidget()
        self.project_browser_list.setObjectName("projectCardList")
        self.project_browser_list.itemDoubleClicked.connect(self.open_selected_project)
        # We'll need a custom context menu for deletion
        self.project_browser_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.project_browser_list.customContextMenuRequested.connect(self.show_project_context_menu)


        right_layout.addWidget(browser_title)
        right_layout.addWidget(self.search_bar)
        right_layout.addWidget(self.project_browser_list)

        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(1, 1) # Make right panel expand

        main_layout.addWidget(splitter)
        
        self.refresh_all_lists()

    def refresh_all_lists(self):
        """Refreshes both the main project browser and the recent projects list."""
        self.all_projects = self.project_manager.get_all_project_details()
        recent_projects = self.project_manager.get_recent_projects()

        # Populate recent projects
        self.recent_projects_list.clear()
        for proj in recent_projects:
            self.recent_projects_list.addItem(proj['name'])

        # Populate the main project browser (initially with all projects)
        self.filter_projects("")

    def filter_projects(self, query):
        """Filters the project browser based on the search query."""
        self.project_browser_list.clear()
        query = query.lower()
        
        filtered_projects = [p for p in self.all_projects if query in p['name'].lower()]

        for proj in filtered_projects:
            card = ProjectCard(proj)
            item = QListWidgetItem(self.project_browser_list)
            item.setSizeHint(card.sizeHint())
            item.setData(Qt.UserRole, proj['name']) # Store project name for selection logic
            self.project_browser_list.addItem(item)
            self.project_browser_list.setItemWidget(item, card)

    def create_new_project(self):
        # This method remains largely the same but refreshes all lists on success
        existing_projects = [p['name'] for p in self.all_projects]
        dialog = NewProjectDialog(existing_projects, self)
        
        if dialog.exec_() == QDialog.Accepted:
            project_name, annotation_task = dialog.get_project_details()
            project_path = self.project_manager.create_project(project_name, annotation_task)
            
            if project_path:
                self.refresh_all_lists()
                # Optionally, open the project immediately
                self.projectSelected.emit(project_name)

    def open_selected_project(self, item):
        # This now works for both lists.
        # For the recent projects list, text() is fine.
        # For the project browser, we must use the data role.
        project_name = item.data(Qt.UserRole)
        if project_name is None:
            project_name = item.text() # Fallback for recent list
        
        if project_name:
            self.projectSelected.emit(project_name)

    def open_project_from_disk(self):
        # This is a placeholder for the "Open Project..." functionality.
        # For now, it doesn't do anything as it's a significant change.
        print("Open project from disk - functionality to be implemented.")
        pass

    def show_project_context_menu(self, pos):
        item = self.project_browser_list.itemAt(pos)
        if not item:
            return

        project_name = item.data(Qt.UserRole)
        if not project_name:
            return

        menu = QMenu()
        delete_action = menu.addAction("Delete Project")
        
        action = menu.exec_(self.project_browser_list.mapToGlobal(pos))
        
        if action == delete_action:
            self.delete_project(project_name)

    def delete_project(self, project_name):
        reply = QMessageBox.warning(
            self,
            'Confirm Deletion',
            f"Are you sure you want to permanently delete the project '{project_name}'?\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success = self.project_manager.delete_project(project_name)
            if success:
                self.refresh_all_lists()
            else:
                QMessageBox.critical(
                    self, 'Error', f"Failed to delete project '{project_name}'."
                )
