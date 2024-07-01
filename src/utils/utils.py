import os
import cv2
import subprocess
import numpy as np

def create_video_from_frames(frames_path, video_path, frame_rate=24, width=640, height=480, libx264=False):

    '''
    Create a video from a folder of frames

    Parameters:
    frames_path (str): The path to the folder containing the frames
    video_path (str): The path to save the video
    frame_rate (int): The frame rate of the video
    width (int): The width of the video
    height (int): The height of the video
    libx264 (bool): Whether to use the libx264 codec to compress the video
    '''

    # Get the list of frames
    frames = sorted([f for f in os.listdir(frames_path) if f.endswith('.png')])

    
    # Initialize the video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Ensure this is correct for your OpenCV version
    video_writer = cv2.VideoWriter(video_path, fourcc, frame_rate, (width, height))

    # Loop through each frame and add it to the video
    for i in range(len(frames)):
        frame = "frame_" + str(i+1) + ".png"
        frame_path = os.path.join(frames_path, frame)
        img = cv2.imread(frame_path)
        if img is not None:
            img = cv2.resize(img, (width, height))
            video_writer.write(img)

    # Release the video writer
    video_writer.release()
    # subprocess.run(["ffmpeg", "-i", video_path, "-vcodec", "libx264", "output_video.mp4"])
    output_video_path = video_path.rsplit(".", 1)[0] + "_compressed.mp4"

    if (libx264):
        subprocess.run([
    "ffmpeg", "-i", video_path, 
    "-vcodec", "libx264", 
    "-crf", "0",  # Adjust the CRF value for quality (lower is better quality, range is 0-51)
    "-preset", "medium",  # Adjust the preset for speed (options: ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow)
    output_video_path
    ])
