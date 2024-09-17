import streamlit as st
import os
import tempfile
from frame_differencing import capture_slides_frame_diff
from video_2_slides import capture_slides_bg_modeling
from post_process import remove_duplicates
from utils import create_output_directory, convert_slides_to_pdf

# Constants
FRAME_BUFFER_HISTORY = 15
DEC_THRESH = 0.75
DIST_THRESH = 100
MIN_PERCENT = 0.15
MAX_PERCENT = 0.01

# Streamlit app
st.set_page_config(page_title="Unisol to Unisup Training Migration", layout="wide")

st.markdown("""
<style>
.big-font {
    font-size:24px !important;
    font-weight: bold;
}
.medium-font {
    font-size:18px !important;
}
.small-font {
    font-size:14px !important;
}
.chat-message {
    padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex
}
.chat-message.user {
    background-color: #2b313e
}
.chat-message.bot {
    background-color: #475063
}
.chat-message .avatar {
  width: 20%;
}
.chat-message .avatar img {
  max-width: 78px;
  max-height: 78px;
  border-radius: 50%;
  object-fit: cover;
}
.chat-message .message {
  width: 80%;
  padding: 0 1.5rem;
  color: #fff;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">🚀 Unisol to Unisup Training Migration 🚀</p>', unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown('<p class="medium-font">📤 Upload Video</p>', unsafe_allow_html=True)
uploaded_file = st.sidebar.file_uploader("Choose a video file", type=["mp4", "avi", "mov"])

if uploaded_file:
    st.sidebar.markdown('<p class="medium-font">⚙️ Configuration</p>', unsafe_allow_html=True)
    type_bg_sub = st.sidebar.selectbox("Background Subtraction Type", ['Frame_Diff', 'GMG', 'KNN'])
    no_post_process = st.sidebar.checkbox("Skip Post-processing", value=False)
    convert_to_pdf = st.sidebar.checkbox("Convert to PDF", value=True)

    if st.sidebar.button("Process Video"):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_video_path = os.path.join(temp_dir, uploaded_file.name)
            with open(temp_video_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            output_dir_path = create_output_directory(temp_video_path, temp_dir, type_bg_sub)

            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.text("Processing video...")
            if type_bg_sub.lower() == 'frame_diff':
                capture_slides_frame_diff(temp_video_path, output_dir_path)
            else:
                thresh = DEC_THRESH if type_bg_sub.lower() == 'gmg' else DIST_THRESH
                capture_slides_bg_modeling(temp_video_path, output_dir_path, type_bgsub=type_bg_sub,
                                           history=FRAME_BUFFER_HISTORY, threshold=thresh,
                                           MIN_PERCENT_THRESH=MIN_PERCENT, MAX_PERCENT_THRESH=MAX_PERCENT)
            progress_bar.progress(50)

            if not no_post_process:
                status_text.text("Removing duplicate slides...")
                remove_duplicates(output_dir_path)
            progress_bar.progress(75)

            if convert_to_pdf:
                status_text.text("Converting to PDF...")
                pdf_path = convert_slides_to_pdf(temp_video_path, output_dir_path)
                progress_bar.progress(100)

            status_text.text("Processing complete!")

            st.markdown('<p class="medium-font">📊 Results</p>', unsafe_allow_html=True)
            st.write(f"Slides extracted and saved to: {output_dir_path}")
            if convert_to_pdf:
                st.write(f"PDF created: {pdf_path}")
                with open(pdf_path, "rb") as file:
                    st.download_button(
                        label="Download PDF",
                        data=file,
                        file_name="slides.pdf",
                        mime="application/pdf"
                    )

# Main chat interface
st.markdown('<p class="medium-font">💬 Multimodal RAG Video Chat</p>', unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What would you like to know about the video?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = f"Thank you for your question about the video: '{prompt}'. As an AI assistant, I don't have access to the specific video content, but I can provide general information about the Unisol to Unisup training migration process. Could you please provide more specific questions about the process or the video content?"

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

st.markdown('<p class="small-font">Powered by 🚀 Unisol to Unisup</p>', unsafe_allow_html=True)
