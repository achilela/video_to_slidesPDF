import streamlit as st
import os
import tempfile
import cv2
from PIL import Image
import imagehash
import img2pdf
import glob
import time

# Utility functions
def resize_image(frame, width):
    height, width, _ = frame.shape
    aspect_ratio = height / width
    new_height = int(width * aspect_ratio)
    return cv2.resize(frame, (width, new_height), interpolation=cv2.INTER_AREA)

def hash_images(directory, hash_size=8):
    hash_dict = {}
    for img_path in glob.glob(os.path.join(directory, '*')):
        with Image.open(img_path) as img:
            hash = imagehash.dhash(img, hash_size)
            if hash not in hash_dict:
                hash_dict[hash] = img_path
    return hash_dict

def remove_duplicates(directory, hash_size=12):
    hash_dict = hash_images(directory, hash_size)
    duplicates = len(hash_dict) - 1  # Number of duplicates removed
    for img_path in list(hash_dict.values())[1:]:  # Skip the first image which is kept as original
        os.remove(img_path)
    return duplicates

def capture_slides(video_path, output_dir, threshold=0.06, frame_skip=85):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():  # Corrected line
        st.error(f'Error opening video file: {video_path}')
        return 0

    frame_count = 0
    slide_count = 0
    prev_frame = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % frame_skip == 0:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if prev_frame is not None:
                frame_diff = cv2.absdiff(gray_frame, prev_frame)
                _, thresh = cv2.threshold(frame_diff, 30, 255, cv2.THRESH_BINARY)
                non_zero_count = cv2.countNonZero(thresh)
                if (non_zero_count / (gray_frame.size * 1.0)) > threshold:
                    cv2.imwrite(os.path.join(output_dir, f'{slide_count:03}.png'), frame)
                    slide_count += 1
            prev_frame = gray_frame
        
        frame_count += 1

    cap.release()
    return slide_count

def convert_to_pdf(output_dir):
    pdf_path = os.path.join(output_dir, 'slides.pdf')  # Added the missing '='
    with open(pdf_path, 'wb') as f:
        f.write(img2pdf.convert([i for i in glob.glob(f'{output_dir}/*.png') if i.endswith('.png')]))
    return pdf_path

# Stream UI
st.set_page_config(page_title="Video to Slides", layout="wide")

st.title("Video to Slides Converter")

uploaded_file = st.file_uploader("Upload a video", type=["mp4", "avi", "mov"])

if uploaded_file:
    with tempfile.TemporaryDirectory as temp_dir:
         temp_video_path = os.path.join(temp_dir, 'video' + os.path.splitext(uploaded_file.name)[0] + os.path.splitext(uploaded_file.name)[1])
         with open(temp_video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

         output_dir = os.join(temp_dir, "slides")
         os.makedirs(output_dir, exist_ok=True)

         if st.button('Process Video'):
            with st.sp('Processing video...'):
                start_time = time.time()
                slide_count = capture_slides(temp_video_path, output_dir)
                if st.checkbox('Remove Duplicates'):
                    removed_count = remove_duplicates(output_dir)
                    st.write(f"Removed {removed_count} duplicates                if st.checkbox('Convert to PDF'):
                    pdf_path = convert_to_pdf(output_dir)

            st.success(f'Processed in {.time() - start_time:.2f} seconds. {slide_count} slides extracted.')
            if 'pdf_path' in locals():
                st_button(label="Download PDF", data=open(pdf_path, 'rb'), file_name="slides.pdf")

else:
    st.write("Please a video to start.")
