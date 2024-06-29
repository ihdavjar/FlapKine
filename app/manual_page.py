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

        from src.core.core import Object3D, Scene
        from src.core.transforms.flexibility import Flexibility_type1, ConstantF
        from src.core.transforms.rotation import Rotation_EulerAngles

        right_wing = Object3D('right_wing', ellipse_mesh_1, Flexibility_type1(False, False, True, major_axis, minor_axis), Rotation_EulerAngles('ZYX'))
        left_wing = Object3D('left_wing', ellipse_mesh_2, Flexibility_type1(False, False, True, major_axis, minor_axis), Rotation_EulerAngles('ZYX'))
        
        right_wing1 = right_wing.transform(0, np.array([np.pi/6, 0, 0]))
        right_wing1 = Object3D('right_wing1', right_wing1, Flexibility_type1(False, False, True, major_axis, minor_axis), Rotation_EulerAngles('ZYX'))
        left_wing1 = left_wing.transform(0, np.array([-np.pi/6, 0, 0]))
        left_wing1 = Object3D('left_wing1', left_wing1, Flexibility_type1(False, False, True, major_axis, minor_axis), Rotation_EulerAngles('ZYX'))
        
        scene = Scene([right_wing, left_wing, right_wing1, left_wing1])


        for temp_i in range(0,data.shape[0]):
            
            phi = data['phi'][temp_i]
            beta = data['beta'][temp_i]
            alpha = data['alpha'][temp_i]

            angle1 = np.array([phi, beta, alpha])
            angle2 = np.array([np.pi/4+1*phi, -1*beta, alpha])

            scene.save_stl(temp_i, [angle1, angle2, angle1, angle2], f'data/stl/ellipse_{temp_i}.stl')

        
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
