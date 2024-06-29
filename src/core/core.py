from stl import mesh
from transforms.flexibility import Flexibility_Transform, Constant
from transforms.rotation import Rotation_Transform, Constant

class Object3D:
    def __init__(self, name:str, stl_mesh:mesh.Mesh, translation_transform:Flexibility_Transform, rotation_transform:Rotation_Transform):
        '''
        name: str
        stl_mesh: mesh.Mesh
        translation_transform: transform.flexibility.Flexibility_Transform
        rotation_transform: transform.rotation.Rotation_Transform
        '''

        self.name = name
        self.stl_mesh = stl_mesh
        self.translation_transform = translation_transform
        self.rotation_transform = rotation_transform

    def transform(self, t, angles):
        '''
        t: float
        '''
        return 0


import numpy as np
import pandas as pd

major_axis = 5
minor_axis = 3

num_points = 500
theta_temp = np.linspace(0, 2*np.pi, num_points)

# I have to consider the internal points of the ellipse as at each x and y i have different z
# Hence there will be many faces in the top surface

# Creating the top surface of the ellipse
x = major_axis * np.cos(theta_temp) + major_axis
y = minor_axis * np.sin(theta_temp)

top_surface = pd.DataFrame({'x':x, 'y':y, 'z':0.05})
bottom_surface = pd.DataFrame({'x':x, 'y':y, 'z':0.05})

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


object_3d = Object3D("wing", combined_mesh, Constant, Constant)