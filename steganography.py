import cv2
import numpy as np
import matplotlib.pyplot as plt
from cryptography.fernet import Fernet
import sys

# -------------------------------
# Convert bytes to binary string
# -------------------------------
def bytes_to_bits(data):
    return ''.join(format(byte, '08b') for byte in data)

# -------------------------------
# Convert binary string to bytes
# -------------------------------
def bits_to_bytes(bits):
    byte_array = bytearray()
    for i in range(0, len(bits), 8):
        byte_array.append(int(bits[i:i+8], 2))
    return bytes(byte_array)

# -------------------------------
# Show Histogram
# -------------------------------
def show_histogram(image, title):
    plt.figure()
    plt.title(title)
    plt.xlabel("Pixel Value")
    plt.ylabel("Frequency")
    plt.hist(image.flatten(), bins=256, range=[0, 256])
    plt.show()

# -------------------------------
# ENCODE FUNCTION
# -------------------------------
def encode_histogram(image_path, file_path, output_image, key_file="secret.key"):

    # Read secret file
    with open(file_path, "rb") as f:
        secret_data = f.read()

    # Encrypt data
    key = Fernet.generate_key()
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(secret_data)

    # Save key
    with open(key_file, "wb") as kf:
        kf.write(key)

    print(f"Encryption key saved as {key_file}")

    # Convert to binary
    binary_data = bytes_to_bits(encrypted_data)

    # Add 32-bit header (length)
    length_header = format(len(binary_data), '032b')
    full_data = length_header + binary_data

    # Read image
    img = cv2.imread(image_path, 0)
    if img is None:
        print("Error: Image not found")
        sys.exit()

    # BEFORE Histogram
    show_histogram(img, "Original Image Histogram")

    flat = img.flatten()

    # Capacity check
    max_bits = len(flat) // 2
    if len(full_data) > max_bits:
        print("Error: Data too large for image")
        sys.exit()

    data_index = 0
    i = 0

    # Embed using pixel pairs
    while i < len(flat) - 1 and data_index < len(full_data):

        p1 = int(flat[i])
        p2 = int(flat[i + 1])

        # Skip identical pixels
        if p1 == p2:
            i += 2
            continue

        bit = int(full_data[data_index])
        avg = (p1 + p2) // 2

        # Embed bit
        if bit == 0:
            new_p1 = avg
            new_p2 = avg - 1
        else:
            new_p1 = avg + 1
            new_p2 = avg - 1

        # Ensure valid range
        if 0 <= new_p1 <= 255 and 0 <= new_p2 <= 255:
            flat[i] = new_p1
            flat[i + 1] = new_p2
            data_index += 1

        i += 2

    # Reshape image
    stego = flat.reshape(img.shape)

    # AFTER Histogram
    show_histogram(stego, "Stego Image Histogram")

    # Save image
    cv2.imwrite(output_image, stego)

    print("\nEmbedding completed")
    print("Total bits embedded:", data_index)


# -------------------------------
# DECODE FUNCTION
# -------------------------------
def decode_histogram(stego_image, output_file, key_file="secret.key"):

    # Read image
    img = cv2.imread(stego_image, 0)
    if img is None:
        print("Error: Image not found")
        sys.exit()

    flat = img.flatten()
    extracted_bits = ""
    i = 0

    # Extract bits
    while i < len(flat) - 1:

        p1 = int(flat[i])
        p2 = int(flat[i + 1])

        # Skip identical pixels
        if p1 == p2:
            i += 2
            continue

        diff = p1 - p2

        if diff == 1:
            extracted_bits += "0"
        elif diff == 2:
            extracted_bits += "1"

        i += 2

    # Extract length (first 32 bits)
    length = int(extracted_bits[:32], 2)

    # Extract actual data
    data_bits = extracted_bits[32:32 + length]

    # Convert to bytes
    encrypted_bytes = bits_to_bytes(data_bits)

    # Load key and decrypt
    try:
        with open(key_file, "rb") as kf:
            key = kf.read()

        cipher = Fernet(key)
        decrypted_data = cipher.decrypt(encrypted_bytes)

    except:
        print("Decryption failed! Wrong key or corrupted data.")
        return

    # Save output file
    with open(output_file, "wb") as f:
        f.write(decrypted_data)

    print("\nFile successfully extracted and decrypted!")
