import os
import pickle

import streamlit as st
from stl import mesh
import numpy as np
import plotly.graph_objects as go

from src.core.core import Object3D, Scene, Sprite
from src.utils.utils import create_video_from_frames


def open_existing_project(project_path):
    scene_path = os.path.join(project_path, 'scene.pkl')
    if not os.path.exists(scene_path):
        raise FileNotFoundError(f"No project found at: {project_path}")

    # Load the scene.pkl file
    with open(scene_path, 'rb') as scene_file:
        scene_data = pickle.load(scene_file)

    print(f"Project loaded from: {project_path}")
    return scene_data

def open_current_project():
    project_path = st.text_input('Enter the path of the project')
    
    scene = open_existing_project(project_path)
    
    angles = scene.objects[0].angles

    for temp_i in range(0,angles.shape[0]):
        scene.save_stl(temp_i, os.path.join(project_path,f'data/stl/ellipse_{temp_i}.stl'))
    
    if st.button('Render Animation'):
        import subprocess

        # Path to the Blender script
        blender_script = "src/blender/generate_frames.py"

        # Run the Blender script
        subprocess.run(["python", blender_script, "--project_path", project_path])

        # Paths
        frames_path = os.path.join(project_path, 'data/images')
        video_path = os.path.join(project_path, "data/videos/stl_animation_temp.mp4")  # Video path
    
        # Create the video
        create_video_from_frames(frames_path, video_path, frame_rate=20, width=640, height=480, libx264=True)


    frames_path = os.path.join(project_path, 'data/images')
    video_path = os.path.join(project_path, "data/videos/stl_animation_temp.mp4")  # Video path
    
    video_path = video_path.rsplit(".", 1)[0] + "_compressed.mp4"   

    if os.path.exists(video_path):
        video_file = open(video_path, 'rb') #enter the filename with filepath

        video_bytes = video_file.read() #reading the file

        st.video(video_bytes)

    # Adding a slider to the page
    frame_number = st.slider('Select the frame number', 0, angles.shape[0]-1, 0)
    scene.save_stl(frame_number, os.path.join(project_path, f'data/stl/ellipse_temp.stl'))

    # Load the stl file and show it using plotly
    stl_filename = os.path.join(project_path, f'data/stl/ellipse_temp.stl')

    # Load the STL file
    your_mesh = mesh.Mesh.from_file(stl_filename)

    # Extract the vertices and faces
    vertices = your_mesh.vectors.reshape(-1, 3)
    x, y, z = vertices[:, 0], vertices[:, 1], vertices[:, 2]

    # Create a unique set of vertices and a list of faces
    unique_vertices, unique_indices = np.unique(vertices, axis=0, return_inverse=True)
    i, j, k = unique_indices.reshape(-1, 3).T

    # Create a 3D mesh plot
    fig = go.Figure(data=[go.Mesh3d(
        x=unique_vertices[:, 0],
        y=unique_vertices[:, 1],
        z=unique_vertices[:, 2],
        i=i,
        j=j,
        k=k,
        opacity=1,
        color='lightblue'
    )])

    # Set plot layout
    fig.update_layout(
        title='STL Mesh Plot',
        scene=dict(
            xaxis=dict(title='X'),
            yaxis=dict(title='Y'),
            zaxis=dict(title='Z')
        )
    )
    # Freeze the axis so that they don't auto-scale
    fig.update_scenes(aspectmode='cube')

    # Set x, y, z axis limits
    fig.update_layout(scene=dict(xaxis=dict(range=[-10, 10]), yaxis=dict(range=[-10, 10]), zaxis=dict(range=[-10, 10])))

    # Set the camera on the x axis at 1,0,0
    fig.update_layout(scene_camera=dict(eye=dict(x=1, y=0, z=0)))

    st.plotly_chart(fig)
    

    