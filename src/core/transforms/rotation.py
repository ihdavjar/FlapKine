import numpy as np
from src.core.transforms.euler_angles import *

class Rotation_Transform:
    def __call__(self, input_, angles):
        raise NotImplementedError("Each transform must implement the __call__ method.")

class ConstantR(Rotation_Transform):
    def __call__(self, input_, angles=None):
        return input_                
    

class Rotation_EulerAngles(Rotation_Transform):
    def __init__(self, type):
        self.type = type
    
    def __call__(self, input_, angles):
        # input: np.array of shape (n, 3) i.e (x, y, z)
        # angles: np.array of shape (3,) i.e (alpha, beta, gamma)
        # output: np.array of shape (n, 3) i.e (x, y, z) at time t

        # Proper Euler angles (z-x-z, x-y-x, y-z-y, z-y-z, x-z-x, y-x-y)    
        if self.type == 'ZXZ':
            rotation_matrix = rotation_matrix_z_x_z(angles[0], angles[1], angles[2])

        elif self.type == 'XYX':
            rotation_matrix = rotation_matrix_x_y_x(angles[0], angles[1], angles[2])

        elif self.type == 'YZY':
            rotation_matrix = rotation_matrix_y_z_y(angles[0], angles[1], angles[2])

        elif self.type == 'ZYZ':
            rotation_matrix = rotation_matrix_z_y_z(angles[0], angles[1], angles[2])

        elif self.type == 'XZX':
            rotation_matrix = rotation_matrix_x_z_x(angles[0], angles[1], angles[2])

        elif self.type == 'YXY':
            rotation_matrix = rotation_matrix_y_x_y(angles[0], angles[1], angles[2])

        # Tait-Bryan angles (z-y-x, y-x-z, x-z-y, z-x-y, y-z-x, x-y-z)
        elif self.type == 'ZYX':
            rotation_matrix = rotation_matrix_z_y_x(angles[0], angles[1], angles[2])

        elif self.type == 'YXZ':
            rotation_matrix = rotation_matrix_y_x_z(angles[0], angles[1], angles[2])

        elif self.type == 'XZY':
            rotation_matrix = rotation_matrix_x_z_y(angles[0], angles[1], angles[2])

        elif self.type == 'ZXY':
            rotation_matrix = rotation_matrix_z_x_y(angles[0], angles[1], angles[2])

        elif self.type == 'YXZ':
            rotation_matrix = rotation_matrix_y_z_x(angles[0], angles[1], angles[2])

        elif self.type == 'XYZ':
            rotation_matrix = rotation_matrix_x_y_z(angles[0], angles[1], angles[2])

        temp_data = np.dot(input_, rotation_matrix.T)
        return temp_data
        
    

        
            
