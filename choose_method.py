import cv2
import numpy as np
import os

def calculate_edge_capacity(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError("Image not found")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)

    edge_pixels = np.sum(edges > 0)
    capacity_bytes = edge_pixels // 8

    return capacity_bytes


def choose_embedding_method(image_path, secret_file_path):
    secret_size = os.path.getsize(secret_file_path)

    edge_capacity = calculate_edge_capacity(image_path)

    print(f"\nSecret size: {secret_size} bytes")
    print(f"Edge capacity: {edge_capacity} bytes")

    if secret_size <= edge_capacity:
        print("Using EDGE method")
        return "00"   # EDGE
    else:
        print("Using HISTOGRAM method")
        return "01"   # HISTOGRAM