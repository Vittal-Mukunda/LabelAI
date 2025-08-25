# C:\LabelAI\backend\project_manager.py

import os
import json
import shutil
from datetime import datetime
class ProjectManager:
    def __init__(self, base_projects_dir="LabelAI_Projects"):
        self.base_dir = os.path.abspath(base_projects_dir)
        self.current_project_path = None
        self.current_project_name = None
        
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
            
    def is_project_active(self):
        return self.current_project_path is not None

    def create_project(self, name, annotation_task):
        """
        Creates a new project with a specified annotation task.
        Initializes directory structure and the project.json state file.
        """
        project_path = os.path.join(self.base_dir, name)
        
        if os.path.exists(project_path):
            print(f"Error: Project '{name}' already exists.")
            return None

        # Create project structure
        os.makedirs(project_path)
        os.makedirs(os.path.join(project_path, "images"))
        os.makedirs(os.path.join(project_path, "annotations"))
        
        # Initialize project state file with the annotation task
        initial_state = {"annotation_task": annotation_task}
        self.current_project_path = project_path # Temporarily set path to save state
        self.save_state(initial_state)
        self.current_project_path = None # Reset after saving

        print(f"Project '{name}' created with task '{annotation_task}'")
        return project_path

    def open_project(self, name):
        """
        Opens an existing project and loads its state.
        """
        project_path = os.path.join(self.base_dir, name)
        
        if not os.path.exists(project_path):
            print(f"Error: Project '{name}' not found.")
            return None
            
        print(f"Opening existing project '{name}'")
        self.current_project_path = project_path
        self.current_project_name = name
        return project_path

    def close_project(self):
        """Closes the current project, resetting the manager's state."""
        self.current_project_path = None
        self.current_project_name = None
        print("Project closed.")
        
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
        """
        Saves the given data dictionary to project.json, preserving existing keys
        that are not present in the new data (like 'annotation_task').
        """
        state_file = self._get_state_file_path()
        if not state_file: return

        try:
            # Read existing state first to preserve untouched values
            existing_state = self.load_state()
            # Update with new data
            existing_state.update(data)
            
            with open(state_file, 'w') as f:
                json.dump(existing_state, f, indent=4)
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

    def get_project_details(self, project_name):
        """Gathers detailed information about a specific project."""
        project_path = os.path.join(self.base_dir, project_name)
        if not os.path.isdir(project_path):
            return None

        details = {
            "name": project_name,
            "path": project_path,
            "annotation_task": "Unknown",
            "image_count": 0,
            "last_modified": None
        }

        # Get last modified date
        try:
            mod_time = os.path.getmtime(project_path)
            details["last_modified"] = datetime.fromtimestamp(mod_time)
        except OSError:
            pass

        # Get image count
        images_dir = os.path.join(project_path, "images")
        if os.path.isdir(images_dir):
            details["image_count"] = len([f for f in os.listdir(images_dir) if os.path.isfile(os.path.join(images_dir, f))])

        # Get annotation task from project.json
        project_json_path = os.path.join(project_path, "project.json")
        if os.path.exists(project_json_path):
            try:
                with open(project_json_path, 'r') as f:
                    data = json.load(f)
                    details["annotation_task"] = data.get("annotation_task", "Unknown")
            except (json.JSONDecodeError, IOError):
                pass
        
        return details

    def get_all_project_details(self):
        """Returns detailed information for all projects, sorted by name."""
        projects = self.list_projects()
        all_details = [self.get_project_details(p) for p in projects]
        # Filter out any None results in case a project directory is invalid
        all_details = [d for d in all_details if d is not None]
        # Sort by project name alphabetically
        all_details.sort(key=lambda x: x['name'])
        return all_details

    def get_recent_projects(self, count=5):
        """Returns the most recently modified projects."""
        all_details = self.get_all_project_details()
        # Sort by last_modified date, descending
        all_details.sort(key=lambda x: x['last_modified'], reverse=True)
        return all_details[:count]

    def delete_project(self, project_name):
        """Permanently deletes a project directory and all its contents."""
        project_path = os.path.join(self.base_dir, project_name)
        if not os.path.isdir(project_path):
            print(f"Error: Project '{project_name}' not found for deletion.")
            return False
        
        try:
            shutil.rmtree(project_path)
            print(f"Project '{project_name}' deleted successfully.")
            return True
        except OSError as e:
            print(f"Error deleting project '{project_name}': {e}")
            return False

    def save_annotations(self, image_filename, annotations, image_path, image_width, image_height):
        """Saves annotations for a specific image using the neutral JSON schema."""
        if not self.is_project_active(): return
        
        annotation_dir = self.get_annotation_dir()
        annotation_filename = f"{os.path.splitext(image_filename)[0]}.json"
        annotation_path = os.path.join(annotation_dir, annotation_filename)

        # Convert relative coordinates to absolute and keys to 'points'
        abs_annotations = []
        for ann in annotations:
            new_ann = ann.copy()
            coords = new_ann.pop('coords')
            
            if new_ann['type'] == 'bbox' and len(coords) == 4:
                rel_x, rel_y, rel_w, rel_h = coords
                x_min = int(rel_x * image_width)
                y_min = int(rel_y * image_height)
                x_max = int((rel_x + rel_w) * image_width)
                y_max = int((rel_y + rel_h) * image_height)
                new_ann['points'] = [x_min, y_min, x_max, y_max]
            elif new_ann['type'] == 'polygon':
                abs_points = []
                for p in coords:
                    abs_x = int(p[0] * image_width)
                    abs_y = int(p[1] * image_height)
                    abs_points.append([abs_x, abs_y])
                new_ann['points'] = abs_points
            
            abs_annotations.append(new_ann)

        # Create the final JSON structure
        output_data = {
            "image_path": image_path,
            "image_height": image_height,
            "image_width": image_width,
            "annotations": abs_annotations
        }
        
        try:
            with open(annotation_path, 'w') as f:
                json.dump(output_data, f, indent=4)
        except Exception as e:
            print(f"Error saving annotations for {image_filename}: {e}")

    def load_annotations(self, image_filename):
        """Loads annotations from the neutral JSON schema and converts them for the viewer."""
        if not self.is_project_active(): return []

        annotation_dir = self.get_annotation_dir()
        annotation_filename = f"{os.path.splitext(image_filename)[0]}.json"
        annotation_path = os.path.join(annotation_dir, annotation_filename)

        if not os.path.exists(annotation_path):
            return []

        try:
            with open(annotation_path, 'r') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error loading annotations for {image_filename}: {e}")
            return []

        image_width = data.get("image_width")
        image_height = data.get("image_height")
        
        if not image_width or not image_height:
            print(f"Warning: Image dimensions missing in {annotation_filename}. Cannot convert coordinates.")
            # Attempt to return old format if it exists, otherwise empty.
            return data if isinstance(data, list) else []

        # Convert absolute coordinates back to relative for the viewer
        relative_annotations = []
        for ann in data.get("annotations", []):
            new_ann = ann.copy()
            points = new_ann.pop('points')

            if new_ann['type'] == 'bbox' and len(points) == 4:
                x_min, y_min, x_max, y_max = points
                rel_x = x_min / image_width
                rel_y = y_min / image_height
                rel_w = (x_max - x_min) / image_width
                rel_h = (y_max - y_min) / image_height
                new_ann['coords'] = [rel_x, rel_y, rel_w, rel_h]
            elif new_ann['type'] == 'polygon':
                rel_points = []
                for p in points:
                    rel_x = p[0] / image_width
                    rel_y = p[1] / image_height
                    rel_points.append([rel_x, rel_y])
                new_ann['coords'] = rel_points
            
            relative_annotations.append(new_ann)
            
        return relative_annotations
            
    def delete_annotations(self, image_filename):
        """Deletes the annotation file for a given image."""
        if not self.is_project_active(): return

        annotation_dir = self.get_annotation_dir()
        annotation_filename = f"{image_filename}.json"
        annotation_path = os.path.join(annotation_dir, annotation_filename)

        if os.path.exists(annotation_path):
            try:
                os.remove(annotation_path)
                print(f"Deleted annotation file: {annotation_path}")
            except OSError as e:
                print(f"Error deleting annotation file {annotation_path}: {e}")
