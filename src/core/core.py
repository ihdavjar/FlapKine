import copy
import numpy as np
from stl import mesh
from src.core.transforms.flexibility import Flexibility_Transform, Flexibility_type1, ConstantF
from src.core.transforms.rotation import Rotation_Transform, Rotation_EulerAngles, ConstantR

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
        angles: np.array of shape (3,) i.e (alpha, beta, gamma)
        '''

        # Get the vertices of the mesh
        vertices = self.stl_mesh.vectors.copy()
        vertices = np.reshape(vertices, (-1, 3))
        
        # Apply the translation transform
        vertices = self.translation_transform(vertices, t)

        # Apply the rotation transform
        vertices = self.rotation_transform(vertices, angles)

        # Return the transformed mesh copying the original mesh
        temp_stl_mesh = copy.deepcopy(self.stl_mesh)
        temp_stl_mesh.vectors = np.reshape(vertices, (-1, 3, 3))
        
        return temp_stl_mesh

class Scene:
    def __init__(self, objects: list):
        '''
        objects: list of Object3D
        '''
        self.objects = objects

    def transform(self, t, angles):
        '''
        t: float
        angles: np.array of shape (3,) i.e (alpha, beta, gamma)
        '''
        transformed_objects = []
        for i,obj in enumerate(self.objects):
            transformed_objects.append(obj.transform(t, angles[i]))
        return transformed_objects
    
    def save_stl(self, t, angles, path:str):
        '''
        Save the transformed meshes to STL files
        '''
        transformed_objects = self.transform(t, angles) 
        combined_mesh = mesh.Mesh(np.concatenate([obj.data for obj in transformed_objects]))  
        combined_mesh.save(path)  

