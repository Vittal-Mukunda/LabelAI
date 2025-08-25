# C:\LabelAI\backend\model_database.py

"""
Centralized database for all supported AI models.

This file acts as a single source of truth for which models are available
for each specific annotation task. This allows for dynamic UI generation
and a scalable way to add new models.
"""

# Define constants for the main annotation tasks
OBJECT_DETECTION = "Object Detection Models"
SEGMENTATION = "Segmentation Models"
TRACKING = "Tracking Models"
POSE_KEYPOINTS = "Pose / Keypoints Models"
FOUNDATION_VLM = "Foundation / Vision-Language Models"

# The core model database
# Each key is a task category, and the value is a list of model dictionaries.
# Each model dictionary contains:
#   - 'name': The display name of the model in the UI.
#   - 'adapter': The class name of the adapter responsible for its inference.
#   - 'tool': The name of the drawing tool associated with this model.
MODEL_DATABASE = {
    OBJECT_DETECTION: [
        {
            "name": "YOLOv8",
            "adapter": "YOLOAdapter",
            "tool": "bbox"
        },
        {
            "name": "Detectron2",
            "adapter": "Detectron2Adapter", # Hypothetical future adapter
            "tool": "bbox"
        }
    ],
    SEGMENTATION: [
        {
            "name": "Segment Anything (SAM)",
            "adapter": "SAMAdapter",
            "tool": "MagicWand" # This tool is not yet implemented in the viewer
        },
        {
            "name": "Mask R-CNN",
            "adapter": "MaskRCNNAdapter", # Hypothetical
            "tool": "polygon"
        }
    ],
    TRACKING: [
        # To be populated in the future
    ],
    POSE_KEYPOINTS: [
        # To be populated in the future
    ],
    FOUNDATION_VLM: [
        # To be populated in the future
    ]
}

def get_tasks():
    """Returns a list of all available annotation tasks."""
    return list(MODEL_DATABASE.keys())

def get_models_for_task(task_name):
    """Returns a list of models for a given annotation task."""
    return MODEL_DATABASE.get(task_name, [])
