import streamlit as st
import os
from main import encode, decode

st.set_page_config(page_title="Steganography Tool", layout="wide")

st.title("🔐 Image Steganography Tool")
st.write("Hide and extract secret files inside images using Edge & Histogram methods.")

# ------------------ SESSION STATE ------------------
if "encoded_file" not in st.session_state:
    st.session_state.encoded_file = None

if "key_file" not in st.session_state:
    st.session_state.key_file = None

if "decoded_file" not in st.session_state:
    st.session_state.decoded_file = None

# Sidebar
option = st.sidebar.selectbox("Choose Mode", ["Encode", "Decode"])

# ------------------ ENCODE ------------------
if option == "Encode":
    st.header("📤 Encode (Hide Data)")

    image_file = st.file_uploader("Upload Cover Image", type=["png", "jpg", "jpeg"])
    secret_file = st.file_uploader("Upload Secret File", type=None)

    output_name = st.text_input("Output Image Name", "stego_output.png")

    if st.button("Encode"):
        if image_file and secret_file:
            # Save uploaded files temporarily
            with open("temp_image.png", "wb") as f:
                f.write(image_file.read())

            with open("temp_secret", "wb") as f:
                f.write(secret_file.read())

            try:
                encode("temp_image.png", "temp_secret", output_name)

                # Store files in session state
                with open(output_name, "rb") as f:
                    st.session_state.encoded_file = f.read()

                with open("secret.key", "rb") as k:
                    st.session_state.key_file = k.read()

                st.success("✅ Encoding successful!")

            except Exception as e:
                st.error(f"❌ Error: {e}")

        else:
            st.warning("Please upload both image and secret file.")

    # Persistent Download Buttons
    if st.session_state.encoded_file:
        st.download_button(
            label="📥 Download Stego Image",
            data=st.session_state.encoded_file,
            file_name=output_name,
            mime="image/png"
        )

    if st.session_state.key_file:
        st.download_button(
            label="🔑 Download Key",
            data=st.session_state.key_file,
            file_name="secret.key"
        )

# ------------------ DECODE ------------------
elif option == "Decode":
    st.header("📥 Decode (Extract Data)")

    stego_image = st.file_uploader("Upload Stego Image", type=["png"])
    key_file = st.file_uploader("Upload Secret Key", type=["key"])

    output_file_name = st.text_input("Recovered File Name", "recovered_output")

    if st.button("Decode"):
        if stego_image and key_file:
            # Save files
            with open("stego.png", "wb") as f:
                f.write(stego_image.read())

            with open("secret.key", "wb") as f:
                f.write(key_file.read())

            try:
                decode("stego.png", output_file_name)

                # Store decoded file
                with open(output_file_name, "rb") as f:
                    st.session_state.decoded_file = f.read()

                st.success("✅ Decoding successful!")

            except Exception as e:
                st.error(f"❌ Error: {e}")

        else:
            st.warning("Please upload both stego image and key file.")

    # Persistent Download Button
    if st.session_state.decoded_file:
        st.download_button(
            label="📥 Download Recovered File",
            data=st.session_state.decoded_file,
            file_name=output_file_name
        )