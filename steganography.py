import cv2
import numpy as np
import matplotlib.pyplot as plt
from cryptography.fernet import Fernet
import sys

def bytes_to_bits(data):
    return ''.join(format(byte, '08b') for byte in data)

def bits_to_bytes(bits):
    byte_array = bytearray()
    for i in range(0, len(bits), 8):
        byte_array.append(int(bits[i:i+8], 2))
    return bytes(byte_array)

def show_histogram(image, title):
    plt.figure()
    plt.title(title)
    plt.xlabel("Pixel Value")
    plt.ylabel("Frequency")
    plt.hist(image.flatten(), bins=256, range=[0, 256])
    plt.show()

def encode_histogram(image_path, file_path, output_image, key_file="secret.key"):

    with open(file_path, "rb") as f:
        secret_data = f.read()

    key = Fernet.generate_key()
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(secret_data)

    with open(key_file, "wb") as kf:
        kf.write(key)

    print(f"Encryption key saved as {key_file}")

    binary_data = bytes_to_bits(encrypted_data)

    length_header = format(len(binary_data), '032b')
    full_data = length_header + binary_data

    img = cv2.imread(image_path, 0)
    if img is None:
        print("Error: Image not found")
        sys.exit()

    show_histogram(img, "Original Image Histogram")

    flat = img.flatten()

    max_bits = len(flat) // 2
    if len(full_data) > max_bits:
        print("Error: Data too large for image")
        sys.exit()

    data_index = 0
    i = 0

    while i < len(flat) - 1 and data_index < len(full_data):

        p1 = int(flat[i])
        p2 = int(flat[i + 1])
    
        if abs(p1 - p2) <= 2:
            i += 2
            continue
    
        avg = (p1 + p2) // 2
    
        if avg < 1 or avg > 254:
            i += 2
            continue
    
        bit = int(full_data[data_index])
    
        if bit == 0:
            new_p1 = avg
            new_p2 = avg - 1
        else:
            new_p1 = avg + 1
            new_p2 = avg - 1
    
        flat[i] = new_p1
        flat[i + 1] = new_p2
        data_index += 1
    
        i += 2

    stego = flat.reshape(img.shape)

    show_histogram(stego, "Stego Image Histogram")

    cv2.imwrite(output_image, stego)

    print("\nEmbedding completed")
    print("Total bits embedded:", data_index)


def decode_histogram(stego_image, output_file, key_file="secret.key"):

    img = cv2.imread(stego_image, 0)
    if img is None:
        print("Error: Image not found")
        sys.exit()

    flat = img.flatten()
    extracted_bits = ""
    i = 0

    while i < len(flat) - 1:

        p1 = int(flat[i])
        p2 = int(flat[i + 1])
    
        if abs(p1 - p2) <= 2:
            i += 2
            continue
    
        diff = p1 - p2
    
        if diff == 1:
            extracted_bits += "0"
        elif diff == 2:
            extracted_bits += "1"
    
        i += 2

    length = int(extracted_bits[:32], 2)

    data_bits = extracted_bits[32:32 + length]

    encrypted_bytes = bits_to_bytes(data_bits)

    try:
        with open(key_file, "rb") as kf:
            key = kf.read()

        cipher = Fernet(key)
        decrypted_data = cipher.decrypt(encrypted_bytes)

    except:
        print("Decryption failed! Wrong key or corrupted data.")
        return

    with open(output_file, "wb") as f:
        f.write(decrypted_data)

    print("\nFile successfully extracted and decrypted!")
