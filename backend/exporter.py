import os
import json

def export_annotations(annotations, output_dir, model_name, class_map):
    """
    Main dispatcher function for exporting annotations.
    """
    if model_name.startswith("YOLO"):
        export_to_yolo(annotations, output_dir, class_map)
    elif model_name == "COCO":
        export_to_coco(annotations, output_dir, class_map)
    elif model_name == "Pascal VOC":
        export_to_voc(annotations, output_dir)
    else:
        raise ValueError(f"Unknown model format: {model_name}")

def export_to_yolo(annotations_data, output_dir, class_map):
    """
    Exports annotations to YOLO format.
    - One .txt file per image.
    - Each line in a file is: <class_id> <x_center> <y_center> <width> <height> (normalized)
    """
    print("Exporting to YOLO format...")
    os.makedirs(output_dir, exist_ok=True)

    for item in annotations_data:
        image_path = item.get("image_path")
        if not image_path:
            continue

        image_filename = os.path.basename(image_path)
        output_filename = f"{os.path.splitext(image_filename)[0]}.txt"
        output_filepath = os.path.join(output_dir, output_filename)

        image_width = item.get("image_width")
        image_height = item.get("image_height")

        if not image_width or not image_height:
            print(f"Skipping {image_filename} due to missing dimensions.")
            continue

        yolo_lines = []
        for ann in item.get("annotations", []):
            if ann.get("type") != "bbox":
                continue

            label = ann.get("label")
            if label not in class_map:
                continue
            
            class_id = class_map[label]
            points = ann.get("points")
            
            if not points or len(points) != 4:
                continue

            x_min, y_min, x_max, y_max = points

            # Convert to YOLO format
            x_center = ((x_min + x_max) / 2) / image_width
            y_center = ((y_min + y_max) / 2) / image_height
            width = (x_max - x_min) / image_width
            height = (y_max - y_min) / image_height

            yolo_lines.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")

        # Write the .txt file for this image
        if yolo_lines:
            with open(output_filepath, 'w') as f:
                f.write("\n".join(yolo_lines))
            print(f"Created YOLO file: {output_filepath}")

def export_to_coco(annotations, output_dir, class_map):
    """
    Exports annotations to COCO format.
    - A single JSON file for the entire dataset.
    """
    print("Exporting to COCO format...")
    # Implementation will be added in a later step.
    pass

def export_to_voc(annotations, output_dir):
    """
    Exports annotations to Pascal VOC format.
    - One .xml file per image.
    """
    print("Exporting to Pascal VOC format...")
    # Implementation will be added in a later step.
    pass
