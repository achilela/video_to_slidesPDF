**Video to PDF Slides Converter using OpenCV**

This repository contains code for converting videos to slides using background subtraction techniques from OpenCV.

## Installation

After unzipping the file, run in your virtual environment:
```bash
pip install -r requirements.txt
```

## Usage

Run the script with:
```bash
python video_2_slides.py -v <video_path> -o <output_dir> --type <method> [--no_post_process] [--convert_to_pdf]
```

- `video_path`: Path to input video.
- `output_dir`: Directory for output.
- `method`: Background subtraction method (Frame_Diff, GMG, KNN).
- `no_post_process`: Skip post-processing (optional).
- `convert_to_pdf`: Convert slides to PDF (optional).

Example:
```bash
python video_2_slides.py -v ./samples/vid_test.mp4 -o output_results --type GMG --convert_to_pdf
```

# Built and curated by ValonyLabsz

Interested in AI? Start with [AI Courses by ValonyLabsz](https://valonylabzs.com/courses/).

<a href="https://valonylabzs.com/courses/">
<p align="center"> 
<img src="https://learnopencv.com/wp-content/uploads/2023/01/AI-Courses-By-OpenCV-Github.png">
</p>
</a>
