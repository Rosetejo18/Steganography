import cv2
import numpy as np
import os

# Delimiter is already defined in your code
DELIMITER = "1111111111111110"

def bytes_to_bits(data):
    return ''.join(format(byte, '08b') for byte in data)

def calculate_edge_capacity(image_path):
    """
    Calculate edge-based LSB capacity of an image in bytes.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError("Image not found")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    edge_pixels = np.sum(edges > 0)

    # Each edge pixel can store 1 bit
    capacity_bits = edge_pixels
    capacity_bytes = capacity_bits // 8
    return capacity_bytes

def choose_embedding_method(image_path, secret_file_path):
    """
    Decide which steganography method to use based on file size and edge capacity.
    Returns: 'edge-based' or 'histogram-based'
    """
    # Size of secret file in bytes
    secret_size = os.path.getsize(secret_file_path)

    # Include delimiter size
    delimiter_size = len(DELIMITER) // 8
    total_secret_size = secret_size + delimiter_size

    # Calculate edge-based capacity
    edge_capacity = calculate_edge_capacity(image_path)

    print(f"\nSecret size: {total_secret_size} bytes")
    print(f"Edge-based capacity: {edge_capacity} bytes")

    # Decision
    if total_secret_size <= edge_capacity:
        print("Using Edge-Based LSB Steganography")
        return "edge-based"
    else:
        print("Using Histogram-Based Steganography")
        return "histogram-based"