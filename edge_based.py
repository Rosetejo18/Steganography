import cv2
import numpy as np
from cryptography.fernet import Fernet
import os

def bytes_to_bits(data):
    return ''.join(format(byte, '08b') for byte in data)

def bits_to_bytes(bits):
    # process complete bytes; ignore trailing bits
    byte_count = len(bits) // 8
    return bytes(int(bits[i:i+8], 2) for i in range(0, byte_count * 8, 8))

def encode_edge(image_path, file_path, output_image, key_file="secret.key"):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Secret file not found: {file_path}")

    with open(file_path, "rb") as f:
        secret_data = f.read()

    key = Fernet.generate_key()
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(secret_data)
    
    with open(key_file, "wb") as kf:
        kf.write(key)

    binary_data = bytes_to_bits(encrypted_data)
    # 32-bit header for length
    length_header = format(len(binary_data), '032b')
    full_data = length_header + binary_data

    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Could not open image.")

    green_channel = img[:, :, 1]
    stable_green = green_channel & 248 
    edges = cv2.Canny(stable_green, 100, 200)

    edge_coords = np.argwhere(edges > 0)
    
    if len(edge_coords) == 0:
        raise ValueError("No edges detected in this image. Try a more detailed photo.")

    # Capacity Check
    if len(full_data) > len(edge_coords) * 3:
        raise MemoryError(f"Image too small. Need {len(full_data)} bits, have {len(edge_coords)*3}.")

    # hiding data in blue 
    data_idx = 0
    for y, x in edge_coords:
        if data_idx >= len(full_data):
            break
        
        chunk = full_data[data_idx:data_idx+3]
        chunk_val = int(chunk.rjust(3, '0'), 2)
        
        img[y, x, 0] = (img[y, x, 0] & 248) | chunk_val
        data_idx += 3

    # Force PNG extension(compression will mess with the encoding)
    if not output_image.lower().endswith('.png'):
        output_image += ".png"

    cv2.imwrite(output_image, img)
    print(f"Success! Key saved to {key_file}. Stego image: {output_image}")

def decode_edge(stego_image, output_file, key_path="secret.key"):
    img = cv2.imread(stego_image)
    if img is None:
        raise ValueError("Stego image not found.")
    
    with open(key_path, "rb") as kf:
        key = kf.read()

    green_channel = img[:, :, 1]
    stable_green = green_channel & 248
    edges = cv2.Canny(stable_green, 100, 200)
    
    edge_coords = np.argwhere(edges > 0)
    extracted_bits = ""

    # Extract data from blue channel
    for y, x in edge_coords:
        chunk = format(img[y, x, 0] & 7, '03b')
        extracted_bits += chunk

    if len(extracted_bits) < 32:
        raise ValueError("Image contains no valid bitstream.")

    data_len = int(extracted_bits[:32], 2)
    
    if data_len > len(extracted_bits) - 32 or data_len <= 0:
        raise ValueError("Invalid data length header. Image may not contain hidden data.")

    actual_bits = extracted_bits[32:32+data_len]
    encrypted_bytes = bits_to_bytes(actual_bits)

    cipher = Fernet(key)
    try:
        decrypted_data = cipher.decrypt(encrypted_bytes)
    except Exception:
        raise ValueError("Decryption failed. Data is likely corrupted or key is wrong.")

    with open(output_file, "wb") as f:
        f.write(decrypted_data)
    print(f"File extracted to {output_file}")

