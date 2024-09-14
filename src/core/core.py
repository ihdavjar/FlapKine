import copy
import numpy as np
from stl import mesh
from src.core.transforms.translation import Translation_Transform
from src.core.transforms.rotation import Rotation_Transform
from src.core.transforms.flexibility import Flexibility_Transform

class Object3D:
    def __init__(self, name:str, stl_mesh:mesh.Mesh, translation_transform:Translation_Transform, rotation_transform:Rotation_Transform, flexibility_transform:Flexibility_Transform):
        '''
        name: str
        stl_mesh: mesh.Mesh
        translation_transform: Translation_Transform
        rotation_transform: Rotation_Transform
        flexibility_transform: Flexibility_Transform
        '''
        
        self.name = name
        self.stl_mesh = stl_mesh
        self.translation_transform = translation_transform
        self.rotation_transform = rotation_transform
        self.flexibility_transform = flexibility_transform

    def transform(self, position, angles, t):
        '''
        t: float
        position: np.array of shape (3,) i.e (x, y, z)
        angles: np.array of shape (3,) i.e (alpha, beta, gamma)
        '''

        # Get the vertices of the mesh
        vertices = self.stl_mesh.vectors.copy()
        vertices = vertices.reshape(-1, 3)
        
        # Apply the flexibility transform
        vertices = self.flexibility_transform(vertices, t)

        # Apply the rotation transform
        vertices = self.rotation_transform(vertices, angles)

        # Apply the translation transform
        vertices = self.translation_transform(vertices, position) 

        # Return the transformed mesh copying the original mesh
        temp_stl_mesh = copy.deepcopy(self.stl_mesh)
        temp_stl_mesh.vectors = np.reshape(vertices, (-1, 3, 3))
        
        return temp_stl_mesh

class Sprite:
    def __init__(self, object_: Object3D, positions: np.array, angles: np.array):
        '''
        object: Object3D
        positions: np.array of shape (3,) i.e (x, y, z)
        angles: np.array of shape (3,) i.e (alpha, beta, gamma)
        '''
        self.object_ = object_
        self.positions = positions
        self.angles = angles
    
    def transform(self, t):
        '''
        t: integer
        '''
        return self.object_.transform(self.positions[t,:] ,self.angles[t,:], t)
        
class Scene:
    def __init__(self, objects: list):
        '''
        objects: list of Sprite
        '''
        self.objects = objects

    def transform(self, t):
        '''
        t: float
        angles: np.array of shape (3,) i.e (alpha, beta, gamma)
        '''
        transformed_objects = []
        for spr in self.objects:
            transformed_objects.append(spr.transform(t))
        return transformed_objects
    
    def save_stl(self, t, reflect_xy = False, reflect_yz = False, reflect_xz = False):
        '''
        Save the transformed meshes to STL files
        '''

        if reflect_xy:
            # Make reflection of the objects in the scene with respect to the xy-plane
            transformed_objects = self.transform(t)
            reflected_objects = []

            for obj in transformed_objects:
                    
                    temp_mesh_copy = copy.deepcopy(obj)
                    # Flip the y-coordinates of the vertices
                    temp_mesh_copy.vectors[:,:,1] = -temp_mesh_copy.vectors[:,:,1]
                    
                    # Append the reflected object to the list
                    reflected_objects.append(temp_mesh_copy)

            full_objects = transformed_objects + reflected_objects
            combined_mesh = mesh.Mesh(np.concatenate([obj.data for obj in full_objects]))

            return combined_mesh
        
        elif reflect_yz:
            # Make reflection of the objects in the scene with respect to the yz-plane
            transformed_objects = self.transform(t)
            reflected_objects = []

            for obj in transformed_objects:
                    
                    temp_mesh_copy = copy.deepcopy(obj)
                    # Flip the x-coordinates of the vertices
                    temp_mesh_copy.vectors[:,:,0] = -temp_mesh_copy.vectors[:,:,0]
                    
                    # Append the reflected object to the list
                    reflected_objects.append(temp_mesh_copy)

            full_objects = transformed_objects + reflected_objects
            combined_mesh = mesh.Mesh(np.concatenate([obj.data for obj in full_objects]))

            return combined_mesh

        elif reflect_xz:
            # Make reflection of the objects in the scene with respect to the xz-plane
            transformed_objects = self.transform(t)
            reflected_objects = []

            for obj in transformed_objects:
                    
                    temp_mesh_copy = copy.deepcopy(obj)
                    # Flip the y-coordinates of the vertices
                    temp_mesh_copy.vectors[:,:,1] = -temp_mesh_copy.vectors[:,:,1]
                    
                    # Append the reflected object to the list
                    reflected_objects.append(temp_mesh_copy)

            full_objects = transformed_objects + reflected_objects
            combined_mesh = mesh.Mesh(np.concatenate([obj.data for obj in full_objects]))

            return combined_mesh

        else:
            transformed_objects = self.transform(t)
            combined_mesh = mesh.Mesh(np.concatenate([obj.data for obj in transformed_objects]))
        
            return combined_mesh
        