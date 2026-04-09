import cv2
import numpy as np
from cryptography.fernet import Fernet

def bytes_to_bits(data):
    return ''.join(format(byte, '08b') for byte in data)

def bits_to_bytes(bits):
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))


def encode_histogram(image_path, file_path, output_image, key_file="secret.key"):
    # READ SECRET
    with open(file_path, "rb") as f:
        secret_data = f.read()

    # ENCRYPT
    key = Fernet.generate_key()
    cipher = Fernet(key)
    encrypted = cipher.encrypt(secret_data)

    with open(key_file, "wb") as kf:
        kf.write(key)

    # PREPARE DATA
    binary_data = bytes_to_bits(encrypted)
    length_header = format(len(binary_data), '032b')
    full_data = length_header + binary_data

    # LOAD IMAGE
    img_color = cv2.imread(image_path)
    if img_color is None:
        raise ValueError("Image not found")

    # STORE METHOD HEADER (01)
    flat_color = img_color.reshape(-1, 3)
    flat_color[0][0] = (flat_color[0][0] & 254) | 0
    flat_color[1][0] = (flat_color[1][0] & 254) | 1

    # USE BLUE CHANNEL
    blue_channel = img_color[:, :, 0].copy()
    flat = blue_channel.flatten()

    data_idx = 0
    i = 0

    # EMBEDDING
    while i < len(flat) - 1 and data_idx < len(full_data):
        p1, p2 = int(flat[i]), int(flat[i+1])

        # ✅ FIXED CONDITION
        if abs(p1 - p2) == 0:
            i += 2
            continue

        avg = (p1 + p2) // 2
        bit = int(full_data[data_idx])

        if bit == 0:
            flat[i], flat[i+1] = avg, avg - 1
        else:
            flat[i], flat[i+1] = avg + 1, avg - 1

        data_idx += 1
        i += 2

    if data_idx < len(full_data):
        raise ValueError("Not enough capacity in image")

    # REBUILD IMAGE
    stego_blue = flat.reshape(blue_channel.shape)

    stego_color = img_color.copy()
    stego_color[:, :, 0] = stego_blue

    # 🔥 RESTORE HEADER AGAIN
    flat_color = stego_color.reshape(-1, 3)
    flat_color[0][0] = (flat_color[0][0] & 254) | 0
    flat_color[1][0] = (flat_color[1][0] & 254) | 1

    # SAVE
    if not output_image.endswith(".png"):
        output_image += ".png"

    cv2.imwrite(output_image, stego_color)

    print("Histogram encoding complete")


def decode_histogram(stego_image, output_file, key_file="secret.key"):
    img_color = cv2.imread(stego_image)
    if img_color is None:
        raise ValueError("Image not found")

    # READ HEADER
    flat_color = img_color.reshape(-1, 3)
    method = str(flat_color[0][0] & 1) + str(flat_color[1][0] & 1)

    if method != "01":
        raise ValueError("Not a histogram image")

    # BLUE CHANNEL
    blue_channel = img_color[:, :, 0]
    flat = blue_channel.flatten()

    bits = ""
    i = 0

    # READ LENGTH (32 bits)
    while i < len(flat) - 1 and len(bits) < 32:
        p1, p2 = int(flat[i]), int(flat[i+1])

        # ✅ FIXED CONDITION
        if abs(p1 - p2) == 0:
            i += 2
            continue

        diff = p1 - p2

        if diff == 1:
            bits += "0"
        elif diff == 2:
            bits += "1"

        i += 2

    if len(bits) < 32:
        raise ValueError("Failed to read data length")

    length = int(bits[:32], 2)

    # READ DATA
    while i < len(flat) - 1 and len(bits) < 32 + length:
        p1, p2 = int(flat[i]), int(flat[i+1])

        if abs(p1 - p2) == 0:
            i += 2
            continue

        diff = p1 - p2

        if diff == 1:
            bits += "0"
        elif diff == 2:
            bits += "1"

        i += 2

    data_bits = bits[32:32 + length]

    encrypted = bits_to_bytes(data_bits)

    # DECRYPT
    with open(key_file, "rb") as kf:
        key = kf.read()

    cipher = Fernet(key)
    decrypted = cipher.decrypt(encrypted)

    # SAVE OUTPUT
    with open(output_file, "wb") as f:
        f.write(decrypted)

    print("Histogram decoding complete")