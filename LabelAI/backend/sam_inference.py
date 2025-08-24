# Placeholder for backend/sam_inference.py

class SAMAdapter:
    def __init__(self):
        # In a real implementation, you would load the SAM model here.
        print("SAMAdapter initialized.")

    def infer(self, image_path):
        print(f"SAM inference on {image_path}")
        return [{"mask": [100, 100, 150, 150, 100, 150], "label": "sam_obj"}]
