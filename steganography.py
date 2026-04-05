import cv2
import numpy as np
from cryptography.fernet import Fernet
import sys

def bytes_to_bits(data):
    return ''.join(format(byte, '08b') for byte in data)

def bits_to_bytes(bits):
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))


def encode_histogram(image_path, file_path, output_image, key_file="secret.key"):
    with open(file_path, "rb") as f:
        secret_data = f.read()

    key = Fernet.generate_key()
    cipher = Fernet(key)
    encrypted = cipher.encrypt(secret_data)

    with open(key_file, "wb") as kf:
        kf.write(key)

    binary_data = bytes_to_bits(encrypted)
    length_header = format(len(binary_data), '032b')
    full_data = length_header + binary_data

    img_color = cv2.imread(image_path)

    # STORE METHOD HEADER (01)
    flat = img_color.reshape(-1, 3)
    flat[0][0] = (flat[0][0] & 254) | 0
    flat[1][0] = (flat[1][0] & 254) | 1

    cv2.imwrite("temp.png", img_color)

    img = cv2.imread("temp.png", 0)
    flat = img.flatten()

    data_idx = 0
    i = 0

    while i < len(flat)-1 and data_idx < len(full_data):
        p1, p2 = int(flat[i]), int(flat[i+1])

        if abs(p1 - p2) <= 2:
            i += 2
            continue

        avg = (p1 + p2) // 2

        bit = int(full_data[data_idx])

        if bit == 0:
            flat[i], flat[i+1] = avg, avg-1
        else:
            flat[i], flat[i+1] = avg+1, avg-1

        data_idx += 1
        i += 2

    stego = flat.reshape(img.shape)
    cv2.imwrite(output_image, stego)

    print("Histogram encoding complete")


def decode_histogram(stego_image, output_file, key_file="secret.key"):
    img_color = cv2.imread(stego_image)

    # READ METHOD HEADER
    flat = img_color.reshape(-1, 3)
    method = str(flat[0][0] & 1) + str(flat[1][0] & 1)

    if method != "01":
        raise ValueError("Not a histogram image")

    img = cv2.imread(stego_image, 0)
    flat = img.flatten()

    bits = ""
    i = 0

    while i < len(flat)-1:
        p1, p2 = int(flat[i]), int(flat[i+1])

        if abs(p1 - p2) <= 2:
            i += 2
            continue

        diff = p1 - p2

        if diff == 1:
            bits += "0"
        elif diff == 2:
            bits += "1"

        i += 2

    length = int(bits[:32], 2)
    data_bits = bits[32:32+length]

    encrypted = bits_to_bytes(data_bits)

    with open(key_file, "rb") as kf:
        key = kf.read()

    cipher = Fernet(key)
    decrypted = cipher.decrypt(encrypted)

    with open(output_file, "wb") as f:
        f.write(decrypted)

    print("Histogram decoding complete")