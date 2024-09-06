import streamlit as st
import os
import tempfile
import cv2
import imagehash
from PIL import Image
import time
import img2pdf
import glob

# Utility functions
def resize_image_frame(frame, resize_width):
    ht, wd, _ = frame.shape
    new_height = resize_width * ht / wd
    return cv2.resize(frame, (resize_width, int(new_height)), interpolation=cv2.INTER_AREA)

def find_similar_images(base_dir, hash_size=8):
    snapshots_files = sorted(os.listdir(base_dir))
    hash_dict = {}
    duplicates = []
    num_duplicates = 0

    for file in snapshots_files:
        read_file = Image.open(os.path.join(base_dir, file))
        comp_hash = str(imagehash.dhash(read_file, hash_size=hash_size))

        if comp_hash not in hash_dict:
            hash_dict[comp_hash] = file
        else:
            duplicates.append(file)
            num_duplicates += 1
    
    return hash_dict, duplicates

def remove_duplicates(base_dir):
    _, duplicates = find_similar_images(base_dir, hash_size=12)
    for dup_file in duplicates:
        file_path = os.path.join(base_dir, dup_file)
        if os.path.exists(file_path):
            os.remove(file_path)
    return len(duplicates)

def capture_slides(video_path, output_dir, method='frame_diff', min_percent_thresh=0.06, elapsed_frame_thresh=85):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        st.error(f'Unable to open video file: {video_path}')
        return

    prev_frame = None
    screenshots_count = 0
    capture_frame = False
    frame_elapsed = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if prev_frame is not None:
            if method == 'frame_diff':
                frame_diff = cv2.absdiff(frame_gray, prev_frame)
                _, frame_diff = cv2.threshold(frame_diff, 80, 255, cv2.THRESH_BINARY)
                p_non_zero = (cv2.countNonZero(frame_diff) / (1.0 * frame_gray.size)) * 100

                if p_non_zero >= min_percent_thresh and not capture_frame:
                    capture_frame = True
                elif capture_frame:
                    frame_elapsed += 1

                if frame_elapsed >= elapsed_frame_thresh:
                    capture_frame = False
                    frame_elapsed = 0
                    screenshots_count += 1
                    filename = f"{screenshots_count:03}.png"
                    cv2.imwrite(os.path.join(output_dir, filename), frame)

        prev_frame = frame_gray

    cap.release()
    return screenshots_count

def convert_slides_to_pdf(output_dir):
    pdf_file_name = 'slides.pdf'
    output_pdf_path = os.path.join(output_dir, pdf_file_name)
    with open(output_pdf_path, "wb") as f:
        f.write(img2pdf.convert(sorted(glob.glob(f"{output_dir}/*.png"))))
    return output_pdf_path

# Streamlit app
st.set_page_config(page_title="Video to Slides Converter", layout="wide")

st.markdown("""
<style>
.big-font {
    font-size:30px !important;
    font-weight: bold;
}
.medium-font {
    font-size:20px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">Video to Slides Converter</p>', unsafe_allow_html=True)

st.sidebar.markdown('<p class="medium-font">Configuration</p>', unsafe_allow_html=True)

uploaded_file = st.sidebar.file_uploader("Choose a video file", type=["mp4", "avi", "mov"])
method = st.sidebar.selectbox("Slide Extraction Method", ["Frame Differencing", "Background Subtraction"])
min_percent_thresh = st.sidebar.slider("Minimum Percent Threshold", 0.01, 0.20, 0.06, 0.01)
elapsed_frame_thresh = st.sidebar.slider("Elapsed Frame Threshold", 10, 200, 85, 5)
post_process = st.sidebar.checkbox("Remove Duplicate Slides", value=True)
convert_to_pdf = st.sidebar.checkbox("Convert to PDF", value=True)

if uploaded_file is not None:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_video_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        output_dir = os.path.join(temp_dir, "output")
        os.makedirs(output_dir, exist_ok=True)

        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text("Processing video...")
        start_time = time.time()
        screenshots_count = capture_slides(temp_video_path, output_dir, method.lower().replace(" ", "_"), min_percent_thresh, elapsed_frame_thresh)
        progress_bar.progress(50)

        if post_process:
            status_text.text("Removing duplicate slides...")
            removed_count = remove_duplicates(output_dir)
            progress_bar.progress(75)

        if convert_to_pdf:
            status_text.text("Converting to PDF...")
            pdf_path = convert_slides_to_pdf(output_dir)
            progress_bar.progress(100)

        end_time = time.time()
        processing_time = round(end_time - start_time, 2)

        status_text.text("Processing complete!")

        st.markdown('<p class="medium-font">Results</p>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"Total slides extracted: {screenshots_count}")
            if post_process:
                st.write(f"Duplicate slides removed: {removed_count}")
            st.write(f"Processing time: {processing_time} seconds")

        with col2:
            if convert_to_pdf:
                with open(pdf_path, "rb") as file:
                    st.download_button(
                        label="Download PDF",
                        data=file,
                        file_name="slides.pdf",
                        mime="application/pdf"
                    )

        st.markdown('<p class="medium-font">Preview</p>', unsafe_allow_html=True)
        image_files = sorted(glob.glob(f"{output_dir}/*.png"))
        if image_files:
            selected_image = st.selectbox("Select a slide to preview:", image_files)
            st.image(selected_image, use_column_width=True)
        else:
            st.write("No slides extracted.")

else:
    st.markdown('<p class="medium-font">Please upload a video file to begin.</p>', unsafe_allow_html=True)
