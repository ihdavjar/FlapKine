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




def give_the_z_for_flexible_wing(x, y, t, major_axis, minor_axis):
    C_R = 2*minor_axis
    R = 2*major_axis

    t = t/100
    
    C_r = C_R*((1-((x-major_axis)/major_axis)**2)**(0.5)) # Local chord length

    Z_M_Root = 0.125*C_r

    Z_M_x = (Z_M_Root/C_R)*(1-x/R)*(C_r)

    Z_M_x_t = Z_M_x/np.tanh(2.9)*np.tanh(2.9*np.sin(2*np.pi*t + 0.4))   

    p = 0.5

    if (C_r != 0):
        y_0 = (minor_axis-y)/C_r
    
    else: # At wingroot where C_r = 0
        y_0 = 0

    if (y_0<p):
        Z_M_x_y_t = (Z_M_x_t/(p**2))*(2*p*y_0 - y_0**2)
    
    else:
        Z_M_x_y_t = (Z_M_x_t/((1-p)**2))*(1-2*p+2*p*y_0-y_0**2)

    return Z_M_x_y_t
        

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

        z = np.array([give_the_z_for_flexible_wing(x[i], y[i], 0, major_axis, minor_axis) for i in range(0,num_points)])


        top_surface = pd.DataFrame({'x':x, 'y':y, 'z':z + 0.05})
        bottom_surface = pd.DataFrame({'x':x, 'y':y, 'z':z - 0.05})

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

        import matplotlib.pyplot as plt

        data = pd.read_csv("data.csv")


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
        
        combined_mesh = mesh.Mesh(np.concatenate([ellipse_mesh_1.data, ellipse_mesh_2.data]))

        combined_mesh.save(f'data/stl/ellipse.stl')


        for temp_i in range(0,data.shape[0]):
            
            theta_temp = np.linspace(0, 2*np.pi, num_points)

            # Creating the top surface of the ellipse
            x = major_axis * np.cos(theta_temp) + major_axis
            y = minor_axis * np.sin(theta_temp)

            z = np.array([give_the_z_for_flexible_wing(x[i_temp ], y[i_temp], temp_i, major_axis, minor_axis) for i_temp in range(0,num_points)])

            top_surface = pd.DataFrame({'x':x, 'y':y, 'z':z + 0.05})
            bottom_surface = pd.DataFrame({'x':x, 'y':y, 'z':z - 0.05})

            vertices_top = np.array(top_surface)
            vertices_bottom = np.array(bottom_surface)

            init_vertices = np.vstack((vertices_top, vertices_bottom))

            init_vertices_1 =  init_vertices.copy()
            init_vertices_2 =  init_vertices.copy()

            init_vertices_2[:, 0] = -init_vertices_2[:, 0]


            phi = data['phi'][temp_i]
            beta = data['beta'][temp_i]
            alpha = data['alpha'][temp_i]

            from src.transforms.euler_angles import rotation_matrix_z_y_x
            from src.utils.utils import transform_data

            Rotation_matrix_1 = rotation_matrix_z_y_x(phi, beta, alpha)
            Rotation_matrix_2 = rotation_matrix_z_y_x(np.pi/4+1*phi, -1*beta, alpha)

            vertices_1 = transform_data(init_vertices_1, Rotation_matrix_1)
            vertices_2 = transform_data(init_vertices_2, Rotation_matrix_2)
            

            ellipse_mesh_1 = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
            for i, f in enumerate(faces):
                for j in range(3):
                    ellipse_mesh_1.vectors[i][j] = vertices_1[f[j], :]

            ellipse_mesh_2 = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
            for i, f in enumerate(faces):
                for j in range(3):
                    ellipse_mesh_2.vectors[i][j] = vertices_2[f[j], :]

            combined_mesh = mesh.Mesh(np.concatenate([ellipse_mesh_1.data, ellipse_mesh_2.data]))
            # Save the mesh to an STL file
            combined_mesh.save(f'data/stl/ellipse_{temp_i}.stl')
        
        
        import subprocess

        # Path to the Blender executable
        blender_executable = "blender"

        # Path to the Blender script
        blender_script = "blenderanimationcode2.py"

        # Run the Blender script
        subprocess.run([blender_executable, "--background", "--python", blender_script])

        print(100*"=")
        print(os.getcwd())
        print(100*"=")

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