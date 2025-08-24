# Placeholder for backend/yolo_inference.py

class YOLOAdapter:
    def __init__(self):
        # In a real implementation, you would load the YOLO model here.
        print("YOLOAdapter initialized.")

    def infer(self, image_path):
        print(f"YOLO inference on {image_path}")
        return [{"box": [20, 20, 60, 60], "label": "yolo_obj"}]
