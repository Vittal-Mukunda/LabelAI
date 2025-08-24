# C:\LabelAI\backend\yolo_inference.py

class YOLOAdapter:
    """
    Adapter for the YOLO model. This is the single source of truth for YOLO.
    """
    def infer(self, image_path):
        print(f"Running YOLO on {image_path}")
        # In the future, the real YOLO model logic will go here.
        return {
            "boxes": [[50, 50, 200, 200]],
            "labels": ["object"],
            "scores": [0.95]
        }