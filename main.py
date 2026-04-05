from choose_method import choose_embedding_method
from edge_based import encode_edge, decode_edge
from steganography import encode_histogram, decode_histogram
import cv2


def encode(image, secret, output):
    method = choose_embedding_method(image, secret)

    if method == "00":
        encode_edge(image, secret, output)

    elif method == "01":
        encode_histogram(image, secret, output)


def decode(stego_image, output_file):
    img = cv2.imread(stego_image)
    flat = img.reshape(-1, 3)

    method = str(flat[0][0] & 1) + str(flat[1][0] & 1)

    if method == "00":
        print("Detected EDGE method")
        decode_edge(stego_image, output_file)

    elif method == "01":
        print("Detected HISTOGRAM method")
        decode_histogram(stego_image, output_file)

    else:
        raise ValueError("Unknown method")


if __name__ == "__main__":
    choice = input("1. Encode\n2. Decode\nChoose: ")

    if choice == "1":
        img = input("Input image: ")
        secret = input("Secret file: ")
        output = input("Output image: ")
        encode(img, secret, output)

    elif choice == "2":
        stego = input("Stego image: ")
        output = input("Recovered file: ")
        decode(stego, output)