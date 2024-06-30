import streamlit as st
import sympy as sp
import numpy as np
import plotly.graph_objects as go

import pandas as pd
from sympy import init_printing
from sympy import Integral, Matrix, pi, pprint
import os
import imageio
from PIL import Image
import cv2
from stl import mesh

init_printing() # for pretty printing

# Helper functions

# Rotation about x axis [P] = Rx(theta) * [P']
def Rx(theta):
    return sp.Matrix([[1, 0, 0], [0, sp.cos(theta), -sp.sin(theta)], [0, sp.sin(theta), sp.cos(theta)]])

# Rotation about y axis [P] = Ry(theta) * [P']
def Ry(theta):
    return sp.Matrix([[sp.cos(theta), 0, sp.sin(theta)], [0, 1, 0], [-sp.sin(theta), 0, sp.cos(theta)]])

# Rotation about z axis [P] = Rz(theta) * [P']
def Rz(theta):
    return sp.Matrix([[sp.cos(theta), -sp.sin(theta), 0], [sp.sin(theta), sp.cos(theta), 0], [0, 0, 1]])
        

def Manual_Page():

    major_axis = int(st.text_input('Enter the major axis of the ellipse for the wing'))
    minor_axis = int(st.text_input('Enter the minor axis of the ellipse for the wing'))


    uploaded_file = st.file_uploader("Upload a CSV file", type="csv")

    if uploaded_file is not None:
        
        data = pd.read_csv(uploaded_file)

        ## Creating a ellipse
        num_points = 500
        theta_temp = np.linspace(0, 2*np.pi, num_points)

        # I have to consider the internal points of the ellipse as at each x and y i have different z
        # Hence there will be many faces in the top surface

        # Creating the top surface of the ellipse
        x = major_axis * np.cos(theta_temp) + major_axis
        y = minor_axis * np.sin(theta_temp)

        top_surface = pd.DataFrame({'x':x, 'y':y})
        bottom_surface = pd.DataFrame({'x':x, 'y':y})
        top_surface['z'] = 0.05
        bottom_surface['z'] = -0.05

        vertices_top = np.array(top_surface)
        vertices_bottom = np.array(bottom_surface)

        init_vertices = np.vstack((vertices_top, vertices_bottom))
        faces = []

        for i in range(num_points - 1):
            faces.append([i, i + 1, num_points + i])
            faces.append([num_points + i, i + 1, num_points + i + 1])

        # Close the side surface
        faces.append([num_points - 1, 0, 2 * num_points - 1])
        faces.append([2 * num_points - 1, 0, num_points])

        # Define faces for the top and bottom surfaces
        for i in range(1, num_points - 1):
            faces.append([0, i, i + 1])
            faces.append([num_points, num_points + i, num_points + i + 1])

        # Convert faces to numpy array
        faces = np.array(faces)

        init_vertices_1 = init_vertices.copy()
        init_vertices_2 = init_vertices.copy()
        
        init_vertices_2[:, 0] = -init_vertices_2[:, 0]

        ellipse_mesh_1 = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
        for i, f in enumerate(faces):
            for j in range(3):
                ellipse_mesh_1.vectors[i][j] = init_vertices_1[f[j], :]
            
        ellipse_mesh_2 = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
        for i, f in enumerate(faces):
            for j in range(3):
                ellipse_mesh_2.vectors[i][j] = init_vertices_2[f[j], :]

        from src.core.core import Object3D, Scene, Sprite
        from src.core.transforms.flexibility import Flexibility_type1, ConstantF
        from src.core.transforms.rotation import Rotation_EulerAngles

        right_wing = Object3D('right_wing', ellipse_mesh_1, Flexibility_type1(False, False, True, major_axis, minor_axis), Rotation_EulerAngles('ZYX'))
        left_wing = Object3D('left_wing', ellipse_mesh_2, Flexibility_type1(False, False, True, major_axis, minor_axis), Rotation_EulerAngles('ZYX'))
        angles_2 = np.hstack((data['phi'].values.reshape(-1, 1), data['beta'].values.reshape(-1, 1), data['alpha'].values.reshape(-1, 1)))
        angles_1 = np.hstack((data['phi'].values.reshape(-1, 1) + np.pi/4, -data['beta'].values.reshape(-1, 1), data['alpha'].values.reshape(-1, 1)))
        left_sprite = Sprite(left_wing, angles_1)
        right_sprite = Sprite(right_wing, angles_2)

        # import pickle
        # with open('ellipse.pkl', 'wb') as f:
        #     pickle.dump(left_wing, f)
        
        # # Load the pickle file
        # with open('ellipse.pkl', 'rb') as f:
        #     left_wing = pickle.load(f)


        right_wing1 = right_wing.transform(0, np.array([np.pi/6, 0, 0]))
        right_wing1 = Object3D('right_wing1', right_wing1, Flexibility_type1(False, False, True, major_axis, minor_axis), Rotation_EulerAngles('ZYX'))
        right_sprite1 = Sprite(right_wing1, angles_2)

        left_wing1 = left_wing.transform(0, np.array([-np.pi/6, 0, 0]))
        left_wing1 = Object3D('left_wing1', left_wing1, Flexibility_type1(False, False, True, major_axis, minor_axis), Rotation_EulerAngles('ZYX'))
        left_sprite1 = Sprite(left_wing1, angles_1) 

        scene = Scene([left_sprite, right_sprite, left_sprite1, right_sprite1])


        for temp_i in range(0,data.shape[0]):
            scene.save_stl(temp_i, f'data/stl/ellipse_{temp_i}.stl')

        
        import subprocess

        # Path to the Blender script
        blender_script = "src/blender/generate_frames.py"

        # Run the Blender script
        subprocess.run(["python", blender_script])

        # Paths
        frames_path = os.path.join(os.getcwd(), 'data/images')  # Frames directory
        video_path = os.path.join(os.getcwd(), "data/videos/stl_animation_temp.mp4")  # Video path

        from src.utils.utils import create_video_from_frames

        # Create the video
        create_video_from_frames(frames_path, video_path, frame_rate=20, width=640, height=480, libx264=True)

        video_path = video_path.rsplit(".", 1)[0] + "_compressed.mp4"   

        video_file = open(video_path, 'rb') #enter the filename with filepath

        video_bytes = video_file.read() #reading the file

        st.video(video_bytes) #displaying the video


        # Adding a slider to the page
        frame_number = st.slider('Select the frame number', 0, data.shape[0]-1, 0)
        scene.save_stl(frame_number, f'data/stl/ellipse_temp.stl')

        # Load the stl file and show it using plotly
        stl_filename = f'data/stl/ellipse_temp.stl'

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

        # Set the camera on the x axis at 10,0,0
        fig.update_layout(scene_camera=dict(eye=dict(x=1, y=0, z=0)))

        st.plotly_chart(fig)
