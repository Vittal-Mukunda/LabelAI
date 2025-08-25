# C:\LabelAI\ui\main_window.py

import os
import json
import shutil
from PyQt5.QtWidgets import (QMainWindow, QAction, QFileDialog, QTabWidget, 
                             QWidget, QHBoxLayout, QSplitter, QStackedWidget, QMessageBox, QActionGroup, QStyle)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from .image_viewer import ImageViewer
from .annotation_panel import AnnotationPanel
from .welcome_screen import WelcomeScreen
from .image_sidebar import ImageSidebar # Import the new sidebar
from backend.model_manager import ModelManager
from backend.project_manager import ProjectManager
from backend.yolo_inference import YOLOAdapter
from backend.sam_inference import SAMAdapter

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.project_manager = ProjectManager(base_projects_dir="LabelAI_Projects")
        self.model_manager = ModelManager()
        self.model_manager.register_model("YOLO", YOLOAdapter)
        self.model_manager.register_model("SAM", SAMAdapter)
        
        self.current_active_label = None
        
        self.setWindowTitle("LabelAI")
        self.resize(1400, 900) # Increased default size for the new layout

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        self.welcome_screen = WelcomeScreen(self.project_manager.base_dir)
        self.welcome_screen.projectSelected.connect(self.load_project_ui)
        
        self.main_widget = QWidget()
        self.setup_main_ui(self.main_widget)
        
        self.stack.addWidget(self.welcome_screen)
        self.stack.addWidget(self.main_widget)
        
        self.stack.setCurrentWidget(self.welcome_screen)
        self.menuBar().setVisible(False)

    def setup_main_ui(self, parent_widget):
        main_layout = QHBoxLayout(parent_widget)
        
        # --- NEW 3-PANEL LAYOUT ---
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)

        # 1. Left Sidebar for Image Previews
        self.image_sidebar = ImageSidebar()
        self.image_sidebar.addImagesClicked.connect(self.add_images_to_project)
        self.image_sidebar.imageSelected.connect(self.open_image_tab)

        # 2. Nested splitter for the main work area
        work_area_splitter = QSplitter(Qt.Horizontal)
        
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)

        self.annotation_panel = AnnotationPanel()
        self.annotation_panel.activeLabelChanged.connect(self.on_active_label_changed)
        self.annotation_panel.classLabelsChanged.connect(self.save_project_state)
        self.annotation_panel.annotationsUpdated.connect(self.on_annotations_updated_from_panel)
        
        work_area_splitter.addWidget(self.tabs)
        work_area_splitter.addWidget(self.annotation_panel)
        work_area_splitter.setSizes([900, 300])

        main_splitter.addWidget(self.image_sidebar)
        main_splitter.addWidget(work_area_splitter)
        main_splitter.setSizes([200, 1200])
        # --- END OF NEW LAYOUT ---
        
        menubar = self.menuBar()
        self.file_menu = menubar.addMenu("File")
        style = self.style()
        # Renamed action for clarity
        add_images_action = QAction(style.standardIcon(QStyle.SP_DialogOpenButton), "Add Images to Project...", self)
        add_images_action.triggered.connect(self.add_images_to_project)
        self.file_menu.addAction(add_images_action)
        
        save_action = QAction(style.standardIcon(QStyle.SP_DialogSaveButton), "Save All Annotations", self)
        save_action.triggered.connect(self.save_all_annotations)
        self.file_menu.addAction(save_action)
        
        # Other menus remain the same
        self.tools_menu = menubar.addMenu("Tools")
        #... (rest of menu setup)

    def load_project_ui(self, project_name):
        self.project_manager.open_or_create_project(project_name)
        self.setWindowTitle(f"LabelAI - {project_name}")
        self.stack.setCurrentWidget(self.main_widget)
        self.menuBar().setVisible(True)
        
        # Populate the sidebar with existing images
        self.image_sidebar.populate_from_directory(self.project_manager.get_image_dir())
        
        state = self.project_manager.load_state()
        class_labels = state.get("class_labels", [])
        self.annotation_panel.load_class_labels(class_labels)
        
        self.load_project_state(state)

    def add_images_to_project(self):
        """Opens a dialog to select multiple images and copies them to the project."""
        if not self.project_manager.is_project_active(): return
        
        image_dir = self.project_manager.get_image_dir()
        file_filter = "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        
        # Use getOpenFileNames for multi-selection
        paths, _ = QFileDialog.getOpenFileNames(self, "Add Images", os.path.expanduser("~"), file_filter, options=QFileDialog.DontUseNativeDialog)
        
        if paths:
            copied_count = 0
            for path in paths:
                try:
                    shutil.copy(path, image_dir)
                    copied_count += 1
                except shutil.SameFileError:
                    pass # File is already in the project
                except Exception as e:
                    print(f"Could not copy file {path}: {e}")
            
            if copied_count > 0:
                self.image_sidebar.populate_from_directory(image_dir)
            
            QMessageBox.information(self, "Success", f"Added {copied_count} new image(s) to the project.")

    def open_image_tab(self, path):
        """Opens an image from a given path (called by the sidebar)."""
        if path and os.path.exists(path):
            # Check if this image is already open in a tab
            for i in range(self.tabs.count()):
                if self.tabs.widget(i).property("image_path") == path:
                    self.tabs.setCurrentIndex(i)
                    return

            viewer = ImageViewer()
            viewer.load_image(path)
            viewer.setProperty("image_path", path)
            viewer.annotationsChanged.connect(lambda v=viewer: self.on_annotations_changed_in_viewer(v))
            
            self.load_annotations_for_viewer(viewer, path)
            filename = os.path.basename(path)
            self.tabs.addTab(viewer, filename)
            self.tabs.setCurrentWidget(viewer)
            self.on_annotations_changed_in_viewer(viewer)

    def save_all_annotations(self):
        """Saves annotations for all currently open tabs."""
        if not self.project_manager.is_project_active(): return
        for i in range(self.tabs.count()):
            viewer = self.tabs.widget(i)
            self._save_annotations_for_viewer(viewer)
        QMessageBox.information(self, "Saved", "All open annotations have been saved.")

    def closeEvent(self, event):
        """Saves everything before closing the application."""
        if self.project_manager.is_project_active():
            self.save_all_annotations()
            self.save_project_state()
            print("Project saved. Closing application.")
        
        event.accept()

    # --- Other methods like on_active_label_changed, set_active_tool, etc. remain largely the same ---
    # Minor changes might be needed to adapt to the new auto-save logic.
    def on_active_label_changed(self, label):
        self.current_active_label = label
        active_viewer = self.tabs.currentWidget()
        if isinstance(active_viewer, ImageViewer):
            active_viewer.set_active_label(label)

    def on_tab_changed(self, index):
        self.on_active_label_changed(self.current_active_label)
        active_viewer = self.tabs.currentWidget()
        if isinstance(active_viewer, ImageViewer):
             self.annotation_panel.update_annotations(active_viewer.annotations)

    def save_project_state(self):
        if not self.project_manager.is_project_active(): return
        open_files = [self.tabs.widget(i).property("image_path") for i in range(self.tabs.count())]
        class_labels = self.annotation_panel.get_class_labels()
        state_data = { "open_files": open_files, "class_labels": class_labels }
        self.project_manager.save_state(state_data)

    def on_annotations_changed_in_viewer(self, viewer):
        if viewer:
            self.annotation_panel.update_annotations(viewer.annotations)
            self._save_annotations_for_viewer(viewer)

    def on_annotations_updated_from_panel(self, annotations):
        viewer = self.tabs.currentWidget()
        if isinstance(viewer, ImageViewer):
            viewer.load_annotations(annotations)
            self._save_annotations_for_viewer(viewer)

    def _save_annotations_for_viewer(self, viewer):
        if not (viewer and self.project_manager.is_project_active()): return
        image_path = viewer.property("image_path")
        if image_path:
            image_filename = os.path.basename(image_path)
            self.project_manager.save_annotations(image_filename, viewer.annotations)

    def load_annotations_for_viewer(self, viewer, image_path):
        if not self.project_manager.is_project_active(): return
        image_filename = os.path.basename(image_path)
        annotations = self.project_manager.load_annotations(image_filename)
        if annotations:
            viewer.load_annotations(annotations)

    def close_tab(self, index):
        widget = self.tabs.widget(index)
        if widget:
            widget.deleteLater()
        self.tabs.removeTab(index)

    def run_model(self):
        pass

    def load_project_state(self, state=None):
        if state is None:
            state = self.project_manager.load_state()
        open_files = state.get("open_files", [])
        for file_path in open_files:
            if os.path.exists(file_path):
                self.open_image_tab(file_path)
