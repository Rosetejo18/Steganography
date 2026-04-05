import cv2
import numpy as np
from cryptography.fernet import Fernet
import os

def bytes_to_bits(data):
    return ''.join(format(byte, '08b') for byte in data)

def bits_to_bytes(bits):
    byte_count = len(bits) // 8
    return bytes(int(bits[i:i+8], 2) for i in range(0, byte_count * 8, 8))


def encode_edge(image_path, file_path, output_image, key_file="secret.key"):
    with open(file_path, "rb") as f:
        secret_data = f.read()

    key = Fernet.generate_key()
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(secret_data)

    with open(key_file, "wb") as kf:
        kf.write(key)

    binary_data = bytes_to_bits(encrypted_data)
    length_header = format(len(binary_data), '032b')
    full_data = length_header + binary_data

    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Image not found")

    # STORE METHOD HEADER (00)
    flat = img.reshape(-1, 3)
    flat[0][0] = (flat[0][0] & 254) | 0
    flat[1][0] = (flat[1][0] & 254) | 0

    green = img[:, :, 1]
    stable = green & 248
    edges = cv2.Canny(stable, 100, 200)

    coords = np.argwhere(edges > 0)

    if len(full_data) > len(coords) * 3:
        raise ValueError("Image too small")

    data_idx = 0

    for y, x in coords:
        if data_idx >= len(full_data):
            break

        chunk = full_data[data_idx:data_idx+3]
        chunk_val = int(chunk.rjust(3, '0'), 2)

        img[y, x, 0] = (img[y, x, 0] & 248) | chunk_val
        data_idx += 3

    if not output_image.endswith(".png"):
        output_image += ".png"

    cv2.imwrite(output_image, img)
    print("Edge encoding complete")


def decode_edge(stego_image, output_file, key_file="secret.key"):
    img = cv2.imread(stego_image)
    if img is None:
        raise ValueError("Image not found")

    # READ METHOD HEADER
    flat = img.reshape(-1, 3)
    method = str(flat[0][0] & 1) + str(flat[1][0] & 1)

    if method != "00":
        raise ValueError("Not an edge-based image")

    with open(key_file, "rb") as kf:
        key = kf.read()

    green = img[:, :, 1]
    stable = green & 248
    edges = cv2.Canny(stable, 100, 200)

    coords = np.argwhere(edges > 0)
    bits = ""

    for y, x in coords:
        bits += format(img[y, x, 0] & 7, '03b')

    length = int(bits[:32], 2)
    data_bits = bits[32:32+length]

    encrypted = bits_to_bytes(data_bits)

    cipher = Fernet(key)
    decrypted = cipher.decrypt(encrypted)

    with open(output_file, "wb") as f:
        f.write(decrypted)

    print("Edge decoding complete")