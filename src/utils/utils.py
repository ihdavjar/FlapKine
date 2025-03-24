import os
import cv2
import subprocess

def create_video_from_frames(frames_path, video_path, frame_rate=10, width=640, height=480, libx264=True):
    """
    Create a video from a folder of frames.

    Parameters:
    frames_path (str): The path to the folder containing the frames.
    video_path (str): The path to save the video.
    frame_rate (int): The frame rate of the video.
    width (int): The width of the video.
    height (int): The height of the video.
    libx264 (bool): Whether to use the libx264 codec to compress the video.
    """

    # Get and sort frames numerically (handles cases where sorting fails)
    frames = sorted(
        [f for f in os.listdir(frames_path) if f.endswith('.png')],
        key=lambda x: int(x.split('_')[-1].split('.')[0])  # Extract numerical part
    )

    if not frames:
        raise ValueError("No frames found in the directory.")

    temp_video_path = video_path

    # Initialize OpenCV Video Writer (using raw format first)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(temp_video_path, fourcc, frame_rate, (width, height))

    # Loop through frames and add to the video
    for frame in frames:
        frame_path = os.path.join(frames_path, frame)
        img = cv2.imread(frame_path)
        if img is not None:
            img = cv2.resize(img, (width, height))
            video_writer.write(img)

    # Release OpenCV writer
    video_writer.release()

    # Use FFmpeg for better compatibility (H.264 encoding)
    if libx264:
        output_video_path = video_path
        ffmpeg_command = [
            "ffmpeg", "-y", "-i", temp_video_path, 
            "-vcodec", "libx264", "-pix_fmt", "yuv420p",  # Proper pixel format for PyQt
            "-crf", "23",  # Adjust CRF (lower = better quality, 0 = lossless)
            "-preset", "medium", 
            output_video_path
        ]
        subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Remove temporary file
        os.remove(temp_video_path)
        return output_video_path

    return temp_video_path

