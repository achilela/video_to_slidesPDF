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
    if not cap.isOpened():
        st.error(f'Error opening video file: {video_path}')
        return 0

    frame_count = 0
   _count = 0
    prev_frame = None

    while True:
        ret, frame = cap.read()
        if not ret:  This line was causing the syntax error
            break
        
        if frame_count % frame_skip == 0:
            gray_frame = cv2.
