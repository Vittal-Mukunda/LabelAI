# C:\LabelAI\ui\main_window.py

import os
import json
from PyQt5.QtWidgets import (
    QMainWindow, QAction, QFileDialog, QTabWidget,
    QWidget, QHBoxLayout, QSplitter, QStackedWidget,
    QMessageBox, QActionGroup, QStyle
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from .image_viewer import ImageViewer
from .annotation_panel import AnnotationPanel
from .welcome_screen import WelcomeScreen
from .image_sidebar import ImageSidebar
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

        self.setWindowTitle("LabelAI")
        self.resize(1200, 800)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.welcome_screen = WelcomeScreen(self.project_manager.base_dir)
        self.welcome_screen.projectSelected.connect(self.load_project_ui)

        self.main_widget = QWidget()
        self.setup_main_ui(self.main_widget)

        self.stack.addWidget(self.welcome_screen)
        self.stack.addWidget(self.main_widget)

        self.stack.setCurrentWidget(self.welcome_screen)
        self.set_menus_enabled(False)

    def setup_main_ui(self, parent_widget):
        main_layout = QHBoxLayout(parent_widget)

        # New Image Sidebar (Feature 1)
        self.image_sidebar = ImageSidebar()
        self.image_sidebar.imageSelected.connect(self.open_image_in_tab)
        main_layout.addWidget(self.image_sidebar)

        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        # Annotation panel setup
        self.annotation_panel = AnnotationPanel()
        # Connect signal for active label change (Bug 2 Fix)
        self.annotation_panel.classLabelSelected.connect(self.set_active_class_label_for_viewer)

        splitter.addWidget(self.tabs)
        splitter.addWidget(self.annotation_panel)
        splitter.setSizes([800, 250])

        # Set main layout stretch factors
        main_layout.setStretch(0, 1) # Sidebar
        main_layout.setStretch(1, 4) # Main splitter

        menubar = self.menuBar()
        self.file_menu = menubar.addMenu("File")

        style = self.style()
        open_icon = style.standardIcon(QStyle.SP_DialogOpenButton)
        save_icon = style.standardIcon(QStyle.SP_DialogSaveButton)

        # Connect to open_images (Bug 1 Fix & Feature 1)
        open_action = QAction(open_icon, "Open Images", self) # Renamed for clarity
        open_action.triggered.connect(self.open_images)
        self.file_menu.addAction(open_action)

        save_action = QAction(save_icon, "Save Annotations", self)
        save_action.triggered.connect(self.save_current_tab_annotations)
        self.file_menu.addAction(save_action)

        self.tools_menu = menubar.addMenu("Tools")

        tool_action_group = QActionGroup(self)
        tool_action_group.setExclusive(True)

        bbox_action = QAction("Bounding Box", self)
        bbox_action.setCheckable(True)
        bbox_action.setChecked(True)
        bbox_action.triggered.connect(lambda: self.set_active_tool("bbox"))
        tool_action_group.addAction(bbox_action)
        self.tools_menu.addAction(bbox_action)

        polygon_action = QAction("Polygon", self)
        polygon_action.setCheckable(True)
        polygon_action.triggered.connect(lambda: self.set_active_tool("polygon"))
        tool_action_group.addAction(polygon_action)
        self.tools_menu.addAction(polygon_action)

        self.model_menu = menubar.addMenu("Models")
        yolo_action = QAction("Use YOLO", self)
        yolo_action.triggered.connect(lambda: self.model_manager.set_active_model("YOLO"))
        self.model_menu.addAction(yolo_action)

        sam_action = QAction("Use SAM", self)
        sam_action.triggered.connect(lambda: self.model_manager.set_active_model("SAM"))
        self.model_menu.addAction(sam_action)

        self.run_menu = menubar.addMenu("Run")
        run_action = QAction("Run Model", self)
        run_action.triggered.connect(self.run_model)
        self.run_menu.addAction(run_action)

    def set_menus_enabled(self, enabled):
        self.file_menu.setEnabled(enabled)
        self.tools_menu.setEnabled(enabled)
        self.model_menu.setEnabled(enabled)
        self.run_menu.setEnabled(enabled)

    def load_project_ui(self, project_name):
        self.project_manager.open_or_create_project(project_name)
        self.setWindowTitle(f"LabelAI - {project_name}")
        self.stack.setCurrentWidget(self.main_widget)
        self.set_menus_enabled(True)
        self.load_project_state()

    def set_active_tool(self, tool_name):
        active_viewer = self.tabs.currentWidget()
        if isinstance(active_viewer, ImageViewer):
            active_viewer.set_tool(tool_name)

    def open_images(self):
        """
        Opens a file dialog to select multiple images and adds them to the sidebar.
        (Fixes Bug 1 and implements part of Feature 1).
        """
        image_dir = self.project_manager.get_image_dir()
        if not image_dir:
            QMessageBox.warning(self, "Project Error", "Could not find the project's image directory.")
            return

        file_filter = "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)"
        # Use getOpenFileNames to allow multi-selection
        paths, _ = QFileDialog.getOpenFileNames(self, "Open Images", image_dir, file_filter)

        if paths:
            self.image_sidebar.clear_images()
            self.image_sidebar.add_images(paths)

    def open_image_in_tab(self, path):
        """
        Opens a single image (selected from the sidebar) in a new tab.
        (Implements part of Feature 1).
        """
        if not (path and os.path.exists(path)):
            return

        # Prevent opening the same image in multiple tabs
        for i in range(self.tabs.count()):
            viewer = self.tabs.widget(i)
            if viewer.property("image_path") == path:
                self.tabs.setCurrentIndex(i)
                return

        viewer = ImageViewer()
        # Fix: Set the active label directly on the new viewer instance
        # before it's added to the tab widget. This prevents the crash.
        selected_label = self.annotation_panel.get_selected_class_label()
        viewer.set_active_class_label(selected_label)
        viewer.load_image(path)
        viewer.setProperty("image_path", path)
        viewer.annotationsChanged.connect(lambda: self.update_panel_for_viewer(viewer))
        self.load_annotations_for_viewer(viewer, path)

        filename = os.path.basename(path)
        self.tabs.addTab(viewer, filename)
        self.tabs.setCurrentWidget(viewer)
        self.update_panel_for_viewer(viewer)

    def set_active_class_label_for_viewer(self, label):
        """
        Sets the active class label on the current image viewer.
        (Fixes Bug 2).
        """
        active_viewer = self.tabs.currentWidget()
        if isinstance(active_viewer, ImageViewer):
            active_viewer.set_active_class_label(label)

    def update_panel_for_viewer(self, viewer):
        if viewer:
            self.annotation_panel.update_annotations(viewer.annotations)

    def save_current_tab_annotations(self):
        active_viewer = self.tabs.currentWidget()
        if not active_viewer: return
        self._save_annotations_for_viewer(active_viewer)

    def _save_annotations_for_viewer(self, viewer):
        annotation_dir = self.project_manager.get_annotation_dir()
        if not annotation_dir: return
        image_path = viewer.property("image_path")
        annotations = viewer.annotations
        filename = os.path.splitext(os.path.basename(image_path))[0] + ".json"
        save_path = os.path.join(annotation_dir, filename)
        with open(save_path, "w") as f:
            json.dump(annotations, f, indent=4)
        print(f"Annotations saved to {save_path}")

    def load_annotations_for_viewer(self, viewer, image_path):
        annotation_dir = self.project_manager.get_annotation_dir()
        if not annotation_dir: return
        filename = os.path.splitext(os.path.basename(image_path))[0] + ".json"
        load_path = os.path.join(annotation_dir, filename)
        if os.path.exists(load_path):
            with open(load_path, "r") as f:
                annotations = json.load(f)
                viewer.load_annotations(annotations)
            print(f"Loaded annotations from {load_path}")

    def close_tab(self, index):
        widget = self.tabs.widget(index)
        if widget:
            widget.deleteLater()
        self.tabs.removeTab(index)

    def run_model(self):
        # ... (implementation omitted for brevity)
        pass

    def load_project_state(self):
        """
        Loads the project state, including the list of images for the sidebar.
        """
        state = self.project_manager.load_state()
        image_paths = state.get("image_paths", [])
        if image_paths:
            self.image_sidebar.add_images(image_paths)

        # We don't reopen tabs automatically anymore to avoid clutter.
        # The user can click thumbnails to open images.

    def save_project_state(self):
        if not self.project_manager.is_project_active():
            return

        # Save the list of all images currently in the sidebar (Feature 1)
        image_paths = []
        for i in range(self.image_sidebar.count()):
            item = self.image_sidebar.item(i)
            path = item.data(1) # Recall we stored the path in data role 1
            if path:
                image_paths.append(path)

        state_data = {"image_paths": image_paths}
        self.project_manager.save_state(state_data)

    def closeEvent(self, event):
        self.save_project_state()
        event.accept()

    def keyPressEvent(self, event):
        """
        Handles keyboard shortcuts for selecting class labels.
        (Implements Feature 2).
        """
        key = event.key()
        # Check for number keys 1-9
        if Qt.Key_1 <= key <= Qt.Key_9:
            index = key - Qt.Key_0 # Convert key to integer
            self.annotation_panel.select_label_by_index(index)
        else:
            # Pass the event to the parent class to handle other keys
            super().keyPressEvent(event)
