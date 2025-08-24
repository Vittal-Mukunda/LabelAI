# Placeholder for backend/model_manager.py

class ModelManager:
    def __init__(self):
        self._models = {}
        self.active_model = None

    def register_model(self, name, adapter_class):
        self._models[name] = adapter_class
        print(f"Model '{name}' registered.")

    def set_active_model(self, name):
        if name in self._models:
            self.active_model = name
            print(f"Active model set to: {name}")
        else:
            raise RuntimeError(f"Model '{name}' is not registered.")

    def run(self, image_path):
        if not self.active_model:
            raise RuntimeError("No active model selected.")

        adapter_class = self._models[self.active_model]
        model_instance = adapter_class()

        print(f"Running model '{self.active_model}' on '{image_path}'...")
        # In a real implementation, this would return actual inference results.
        return [{"box": [10, 10, 50, 50], "label": "dummy"}]
