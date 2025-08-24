# C:\LabelAI\backend\model_manager.py

# --- MODIFICATION START ---
# Import the adapters from their dedicated files
from backend.yolo_inference import YOLOAdapter
from backend.sam_inference import SAMAdapter
# --- MODIFICATION END ---

class ModelManager:
    def __init__(self):
        self.models = {}
        self.active_model = None

    def register_model(self, name, model_class):
        self.models[name] = model_class

    def set_active_model(self, name):
        if name in self.models:
            # Instantiate the class when it's set as active
            self.active_model = self.models[name]()
            print(f"Active model set to {name}")
        else:
            raise ValueError(f"Model {name} not found!")

    def run(self, image_path):
        if self.active_model is None:
            raise RuntimeError("No model selected!")
        return self.active_model.infer(image_path)

# --- MODIFICATION START ---
# The dummy adapters have been removed from this file.
# They now live in their own respective files.
# --- MODIFICATION END ---