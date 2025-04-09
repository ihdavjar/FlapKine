import numpy as np
from src.core.transforms.euler_angles import *

class Rotation_Transform:
    """
    Rotation_Transform Class
    =========================

    Base class for rotational transformations.

    This class serves as an abstract base for all rotational transformations.
    Any subclass must implement the `__call__` method to apply a specific
    rotation transformation to an input data (e.g., 3D coordinates) based on given angles.

    Methods
    -------
    __call__(self, input_, angles):
        Applies the rotation transformation to the given input data using the provided angles.
        This method must be implemented by subclasses.
    """
    def __call__(self, input_, angles):
        """
        Applies the rotation transformation to the input data.

        This method should be implemented by subclasses to perform specific rotation 
        transformations. It accepts the input data and angles, and returns the transformed 
        data after applying the rotation.

        Parameters
        ----------
        input_ : array-like
            The input data to be transformed, typically a 3D coordinate or set of points.

        angles : array-like or float
            The angles (in radians or degrees) for rotation, which may represent 
            rotation along different axes (e.g., x, y, z) depending on the specific 
            implementation.

        Raises
        ------
        NotImplementedError
            If called directly from this base class, since the method must be 
            implemented by a subclass.
        """
        raise NotImplementedError("Each transform must implement the __call__ method.")

class ConstantR(Rotation_Transform):
    """
    ConstantR Class
    ===============

    A subclass of `Rotation_Transform` that performs no rotation on the input data.

    This transform simply returns the input data without any modifications, 
    effectively serving as a placeholder for situations where no rotation is desired.

    Methods
    -------
    __call__(input_, angles=None):
        Returns the input data as-is without applying any rotation.

    """
    
    def __call__(self, input_, angles=None):
        """
        Returns the input data without applying any rotation.

        Parameters
        ----------
        input_ : array-like
            The input data to be returned unchanged.

        angles : array-like or None, optional
            Rotation angles, which are ignored in this transform. The default is None.

        Returns
        -------
        array-like
            The unchanged input data.
        """
        return input_
             
    

class Rotation_EulerAngles(Rotation_Transform):
    """
    Rotation_EulerAngles Class
    ==========================

    A subclass of `Rotation_Transform` that applies a rotation to input data using Euler angles.

    This transform performs a rotation on the input data based on the specified Euler angle sequence.
    The available rotation sequences are Proper Euler angles (e.g., 'ZXZ', 'XYX', 'ZYZ') and Tait-Bryan angles 
    (e.g., 'ZYX', 'YXZ'). The rotation is achieved by multiplying the input data by the corresponding rotation matrix.

    Attributes
    ----------
    type : str
        The type of Euler angle rotation, such as 'ZXZ', 'XYX', 'ZYZ', etc.

    Methods
    -------
    __init__(type):
        Initializes the rotation transform with a specified Euler angle sequence type.

    __call__(input_, angles):
        Applies the rotation on the input data using the specified Euler angle sequence.

    """
    
    def __init__(self, type):
        """
        Initializes the rotation transform with a specified Euler angle sequence type.

        Parameters
        ----------
        type : str
            The type of Euler angle rotation (e.g., 'ZXZ', 'XYX', 'ZYZ', 'ZYX', etc.).
        """
        self.type = type
    
    def __call__(self, input_, angles):
        """
        Applies the rotation to the input data using the specified Euler angle sequence.

        Parameters
        ----------
        input_ : np.ndarray, shape (n, 3)
            The input data points to be rotated, with each row representing a 3D point (x, y, z).

        angles : np.ndarray, shape (3,)
            The Euler angles (alpha, beta, gamma) to apply for the rotation.

        Returns
        -------
        np.ndarray, shape (n, 3)
            The rotated input data after applying the specified Euler angle rotation.

        Notes
        -----
        This method supports both Proper Euler angles (e.g., 'ZXZ', 'XYX', etc.) and Tait-Bryan angles 
        (e.g., 'ZYX', 'YXZ', etc.). The rotation is performed using the corresponding rotation matrix 
        for the specified sequence of Euler angles.
        """
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

        # Apply the rotation matrix to the input data
        temp_data = np.dot(input_, rotation_matrix.T)
        return temp_data

        
    

        
            
