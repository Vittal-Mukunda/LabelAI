# C:\LabelAI\ui\main_window.py

import os
import json
from PyQt5.QtWidgets import (QMainWindow, QAction, QFileDialog, QTabWidget, 
                             QWidget, QHBoxLayout, QSplitter, QStackedWidget, QMessageBox, QActionGroup, QStyle)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from .image_viewer import ImageViewer
from .annotation_panel import AnnotationPanel
from .welcome_screen import WelcomeScreen
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
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        self.annotation_panel = AnnotationPanel()
        self.annotation_panel.activeLabelChanged.connect(self.on_active_label_changed)
        self.annotation_panel.classLabelsChanged.connect(self.save_project_state)
        self.annotation_panel.annotationsUpdated.connect(self.on_annotations_updated_from_panel)
        
        splitter.addWidget(self.tabs)
        splitter.addWidget(self.annotation_panel)
        splitter.setSizes([900, 300])
        
        menubar = self.menuBar()
        self.file_menu = menubar.addMenu("File")
        style = self.style()
        open_icon = style.standardIcon(QStyle.SP_DialogOpenButton)
        save_icon = style.standardIcon(QStyle.SP_DialogSaveButton)
        open_action = QAction(open_icon, "Open Image", self)
        open_action.triggered.connect(self.open_image_tab)
        self.file_menu.addAction(open_action)
        save_action = QAction(save_icon, "Save Annotations", self)
        save_action.triggered.connect(self.save_current_tab_annotations)
        self.file_menu.addAction(save_action)
        self.tools_menu = menubar.addMenu("Tools")
        tool_action_group = QActionGroup(self)
        tool_action_group.setExclusive(True)
        bbox_action = QAction("Bounding Box", self); bbox_action.setCheckable(True); bbox_action.setChecked(True)
        bbox_action.triggered.connect(lambda: self.set_active_tool("bbox"))
        tool_action_group.addAction(bbox_action)
        self.tools_menu.addAction(bbox_action)
        polygon_action = QAction("Polygon", self); polygon_action.setCheckable(True)
        polygon_action.triggered.connect(lambda: self.set_active_tool("polygon"))
        tool_action_group.addAction(polygon_action)
        self.tools_menu.addAction(polygon_action)
        self.model_menu = menubar.addMenu("Models")
        model_action_group = QActionGroup(self)
        model_action_group.setExclusive(True)
        yolo_action = QAction("Use YOLO", self)
        yolo_action.setCheckable(True)
        yolo_action.triggered.connect(lambda: self.model_manager.set_active_model("YOLO"))
        model_action_group.addAction(yolo_action)
        self.model_menu.addAction(yolo_action)
        sam_action = QAction("Use SAM", self)
        sam_action.setCheckable(True)
        sam_action.triggered.connect(lambda: self.model_manager.set_active_model("SAM"))
        model_action_group.addAction(sam_action)
        self.model_menu.addAction(sam_action)
        self.run_menu = menubar.addMenu("Run")
        run_action = QAction("Run Model", self)
        run_action.triggered.connect(self.run_model)
        self.run_menu.addAction(run_action)

    def on_active_label_changed(self, label):
        self.current_active_label = label
        active_viewer = self.tabs.currentWidget()
        if isinstance(active_viewer, ImageViewer):
            active_viewer.set_active_label(label)

    def on_tab_changed(self, index):
        self.on_active_label_changed(self.current_active_label)

    def load_project_ui(self, project_name):
        self.project_manager.open_or_create_project(project_name)
        self.setWindowTitle(f"LabelAI - {project_name}")
        self.stack.setCurrentWidget(self.main_widget)
        self.set_menus_enabled(True)
        
        state = self.project_manager.load_state()
        class_labels = state.get("class_labels", [])
        self.annotation_panel.load_class_labels(class_labels)
        
        self.load_project_state(state)

    def save_project_state(self):
        if not self.project_manager.is_project_active():
            return
        
        open_files = []
        for i in range(self.tabs.count()):
            viewer = self.tabs.widget(i)
            path = viewer.property("image_path")
            if path:
                open_files.append(path)
        
        class_labels = self.annotation_panel.get_class_labels()
        state_data = {
            "open_files": open_files,
            "class_labels": class_labels
        }
        self.project_manager.save_state(state_data)

    def set_menus_enabled(self, enabled):
        self.file_menu.setEnabled(enabled)
        self.tools_menu.setEnabled(enabled)
        self.model_menu.setEnabled(enabled)
        self.run_menu.setEnabled(enabled)

    def set_active_tool(self, tool_name):
        active_viewer = self.tabs.currentWidget()
        if isinstance(active_viewer, ImageViewer):
            active_viewer.set_tool(tool_name)

    def open_image_tab(self, path=None):
        print("DEBUG: 'Open Image' action triggered.")
        if path is None:
            if not self.project_manager.is_project_active():
                QMessageBox.warning(self, "No Project Active", "Please open or create a project first.")
                return

            image_dir = self.project_manager.get_image_dir()
            if not image_dir or not os.path.exists(image_dir):
                QMessageBox.critical(self, "Error", f"Could not find the 'images' directory for the current project.\nExpected at: {image_dir}")
                return

            file_filter = "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)"
            
            # --- THIS IS THE DEFINITIVE FIX ---
            # Use the static method with the DontUseNativeDialog option for maximum reliability.
            path, _ = QFileDialog.getOpenFileName(
                self, 
                "Open Image", 
                image_dir, 
                file_filter,
                options=QFileDialog.DontUseNativeDialog
            )
            print(f"DEBUG: QFileDialog returned path: {path}") # Add this new debug log
            # --- END OF FIX ---
        
        if path and os.path.exists(path):
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

    def on_annotations_changed_in_viewer(self, viewer):
        if viewer:
            self.annotation_panel.update_annotations(viewer.annotations)
            self._save_annotations_for_viewer(viewer)

    def on_annotations_updated_from_panel(self, annotations):
        viewer = self.tabs.currentWidget()
        if isinstance(viewer, ImageViewer):
            viewer.load_annotations(annotations)
            self._save_annotations_for_viewer(viewer)

    def save_current_tab_annotations(self):
        active_viewer = self.tabs.currentWidget()
        if not active_viewer: return
        self._save_annotations_for_viewer(active_viewer)

    def _save_annotations_for_viewer(self, viewer):
        if not (viewer and self.project_manager.is_project_active()):
            return
        
        image_path = viewer.property("image_path")
        if image_path:
            image_filename = os.path.basename(image_path)
            self.project_manager.save_annotations(image_filename, viewer.annotations)
            print(f"Annotations saved for {image_filename}")

    def load_annotations_for_viewer(self, viewer, image_path):
        if not self.project_manager.is_project_active():
            return
            
        image_filename = os.path.basename(image_path)
        annotations = self.project_manager.load_annotations(image_filename)
        if annotations:
            viewer.load_annotations(annotations)
            print(f"Loaded {len(annotations)} annotations for {image_filename}")

    def close_tab(self, index):
        widget = self.tabs.widget(index)
        if widget:
            widget.deleteLater()
        self.tabs.removeTab(index)

    def run_model(self):
        active_viewer = self.tabs.currentWidget()
        if not isinstance(active_viewer, ImageViewer):
            QMessageBox.warning(self, "Error", "Please open an image first.")
            return

        image_path = active_viewer.property("image_path")
        if not image_path:
            QMessageBox.warning(self, "Error", "Could not find the image path for the current tab.")
            return

        try:
            new_annotations = self.model_manager.run(image_path)
            if new_annotations:
                for ann in new_annotations:
                    if 'label' not in ann or not ann['label']:
                        ann['label'] = self.current_active_label if self.current_active_label else "model_prediction"
                active_viewer.annotations.extend(new_annotations)
                active_viewer.annotationsChanged.emit()
                QMessageBox.information(self, "Success", f"Model run complete. Added {len(new_annotations)} new annotation(s).")
            else:
                QMessageBox.information(self, "Finished", "Model run complete. No objects detected.")
        except RuntimeError as e:
            QMessageBox.critical(self, "Model Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

    def load_project_state(self, state=None):
        if state is None:
            state = self.project_manager.load_state()
        open_files = state.get("open_files", [])
        for file_path in open_files:
            if os.path.exists(file_path):
                self.open_image_tab(path=file_path)

    def closeEvent(self, event):
        if self.project_manager.is_project_active():
            for i in range(self.tabs.count()):
                viewer = self.tabs.widget(i)
                self._save_annotations_for_viewer(viewer)
            
            self.save_project_state()
            print("Project saved. Closing application.")
        
        event.accept()
