# C:\LabelAI\backend\project_manager.py

import os
import json

class ProjectManager:
    def __init__(self, base_projects_dir="LabelAI_Projects"):
        self.base_dir = os.path.abspath(base_projects_dir)
        self.current_project_path = None
        self.current_project_name = None
        
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
            
    def is_project_active(self):
        return self.current_project_path is not None

    def open_or_create_project(self, name):
        project_path = os.path.join(self.base_dir, name)
        
        if not os.path.exists(project_path):
            os.makedirs(project_path)
            os.makedirs(os.path.join(project_path, "images"))
            os.makedirs(os.path.join(project_path, "annotations"))
            print(f"Project '{name}' created at '{project_path}'")
        else:
            print(f"Opening existing project '{name}'")
            
        self.current_project_path = project_path
        self.current_project_name = name
        return project_path
        
    def get_image_dir(self):
        if not self.is_project_active(): return None
        return os.path.join(self.current_project_path, "images")

    def get_annotation_dir(self):
        if not self.is_project_active(): return None
        return os.path.join(self.current_project_path, "annotations")

    # --- NEW METHODS FOR STATE MANAGEMENT ---
    def _get_state_file_path(self):
        """Returns the path to the project's state file."""
        if not self.is_project_active(): return None
        return os.path.join(self.current_project_path, "project.json")

    def save_state(self, data):
        """Saves the given data dictionary to project.json."""
        state_file = self._get_state_file_path()
        if not state_file: return
        
        try:
            with open(state_file, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Project state saved to {state_file}")
        except Exception as e:
            print(f"Error saving project state: {e}")

    def load_state(self):
        """Loads and returns the data from project.json."""
        state_file = self._get_state_file_path()
        if not state_file or not os.path.exists(state_file):
            return {} # Return empty dict if no state file exists
        
        try:
            with open(state_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading project state: {e}")
            return {}

    def list_projects(self):
        """Returns a list of all project names."""
        return [d for d in os.listdir(self.base_dir) if os.path.isdir(os.path.join(self.base_dir, d))]

    def save_annotations(self, image_filename, annotations):
        """Saves annotations for a specific image to a JSON file."""
        if not self.is_project_active(): return
        
        annotation_dir = self.get_annotation_dir()
        # Create a JSON filename from the image filename, e.g., "cat.jpg" -> "cat.jpg.json"
        annotation_filename = f"{image_filename}.json"
        annotation_path = os.path.join(annotation_dir, annotation_filename)
        
        try:
            with open(annotation_path, 'w') as f:
                json.dump(annotations, f, indent=4)
        except Exception as e:
            print(f"Error saving annotations for {image_filename}: {e}")

    def load_annotations(self, image_filename):
        """Loads annotations for a specific image from a JSON file."""
        if not self.is_project_active(): return []

        annotation_dir = self.get_annotation_dir()
        annotation_filename = f"{image_filename}.json"
        annotation_path = os.path.join(annotation_dir, annotation_filename)

        if not os.path.exists(annotation_path):
            return [] # Return empty list if no annotation file exists

        try:
            with open(annotation_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading annotations for {image_filename}: {e}")
            return []
