import copy
import numpy as np
from stl import mesh
from src.core.transforms.translation import Translation_Transform
from src.core.transforms.rotation import Rotation_Transform
from src.core.transforms.flexibility import Flexibility_Transform

class Object3D:
    """
    Object3D Class
    ==============

    A class representing a 3D object with a mesh that can undergo transformations
    including flexibility, rotation, and translation.

    This class allows for the application of transformations to the mesh of a 3D object,
    which can include deformations (flexibility), rotations, and translations. The
    transformations are applied sequentially to the mesh data, and the transformed mesh
    is returned.

    Attributes
    ----------
    name : str
        The name of the 3D object.

    stl_mesh : mesh.Mesh
        The mesh of the 3D object, typically in the form of an STL file.

    translation_transform : Translation_Transform
        The transformation applied to the object for translation.

    rotation_transform : Rotation_Transform
        The transformation applied to the object for rotation.

    flexibility_transform : Flexibility_Transform
        The transformation applied to the object for flexibility (deformation).

    Methods
    -------
    __init__(name, stl_mesh, translation_transform, rotation_transform, flexibility_transform):
        Initializes the 3D object with its name, mesh, and transformation functions.

    transform(position, angles, t):
        Transforms the mesh by applying flexibility, rotation, and translation transformations
        at a given time.
    """

    def __init__(self, name:str, stl_mesh:mesh.Mesh, translation_transform:Translation_Transform, rotation_transform:Rotation_Transform, flexibility_transform:Flexibility_Transform):
        """
        Initialize the 3D object with its name, mesh, and transformation functions.

        This constructor takes the mesh data of the object, applies the specified
        transformations (translation, rotation, and flexibility), and stores them as
        attributes for later use when applying transformations.

        Parameters
        ----------
        name : str
            The name of the 3D object.

        stl_mesh : mesh.Mesh
            The mesh of the 3D object, typically in the form of an STL file.

        translation_transform : Translation_Transform
            The transformation applied to the object for translation.

        rotation_transform : Rotation_Transform
            The transformation applied to the object for rotation.

        flexibility_transform : Flexibility_Transform
            The transformation applied to the object for flexibility (deformation).

        Attributes
        ----------
        name : str
            Stores the name of the 3D object.

        stl_mesh : mesh.Mesh
            Stores the mesh data of the 3D object.

        translation_transform : Translation_Transform
            Stores the translation transformation function for the object.

        rotation_transform : Rotation_Transform
            Stores the rotation transformation function for the object.

        flexibility_transform : Flexibility_Transform
            Stores the flexibility transformation function for the object.
        """

        self.name = name
        self.stl_mesh = stl_mesh
        self.translation_transform = translation_transform
        self.rotation_transform = rotation_transform
        self.flexibility_transform = flexibility_transform

    def transform(self, position, angles, t):
        """
        Apply the specified transformations (flexibility, rotation, translation) to the mesh.

        This method applies the flexibility transformation, followed by the rotation and
        translation transformations to the mesh vertices. The transformed mesh is then returned.

        Parameters
        ----------
        position : np.array of shape (3,)
            The translation vector specifying the position (x, y, z) at time t.

        angles : np.array of shape (3,)
            The rotation angles (alpha, beta, gamma) at time t.

        t : float
            The current time, used to compute the flexibility transformation.

        Returns
        -------
        mesh.Mesh
            A new mesh object with the applied transformations (flexibility, rotation, translation).

        Methods Called
        --------------
        flexibility_transform()
            Applies the flexibility transformation to the mesh vertices.

        rotation_transform()
            Applies the rotation transformation to the mesh vertices.

        translation_transform()
            Applies the translation transformation to the mesh vertices.
        """
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
    """
    Sprite Class
    ============

    A class representing a 3D sprite object that can be transformed over time based on
    its positions and angles.

    This class uses an `Object3D` instance to represent the sprite and applies
    transformations (translation and rotation) over time. The sprite’s position and
    rotation are stored for each time step and can be used to compute its transformation.

    Attributes
    ----------
    object_ : Object3D
        The 3D object that represents the sprite.

    positions : np.array of shape (n, 3)
        An array of 3D positions (x, y, z) at different time steps.

    angles : np.array of shape (n, 3)
        An array of rotation angles (alpha, beta, gamma) at different time steps.

    frame_origin : list of length 3
        The origin of the sprite's local frame of reference (default is [0, 0, 0]).

    frame_orientation : list of length 3
        The orientation of the sprite's local frame of reference (default is [0, 0, 0]).

    Methods
    -------
    __init__(object_, positions, angles):
        Initializes the sprite object with a 3D object, position and angle arrays.

    transform(t):
        Transforms the sprite based on its position and rotation at the given time step `t`.
    """
    def __init__(self, object_: Object3D, positions: np.array, angles: np.array):
        """
        Initialize the sprite object with a 3D object, position, and angle arrays.

        This constructor takes an `Object3D` instance, positions, and angles, and reshapes
        them to ensure correct dimensions for later use in transformation computations.

        Parameters
        ----------
        object_ : Object3D
            The 3D object that represents the sprite.

        positions : np.array of shape (n, 3)
            An array of 3D positions (x, y, z) at different time steps.

        angles : np.array of shape (n, 3)
            An array of rotation angles (alpha, beta, gamma) at different time steps.

        Attributes
        ----------
        object_ : Object3D
            Stores the 3D object for the sprite.

        positions : np.array of shape (n, 3)
            Stores the array of positions for each time step.

        angles : np.array of shape (n, 3)
            Stores the array of rotation angles for each time step.

        frame_origin : list of length 3
            Stores the origin of the sprite's local frame of reference.

        frame_orientation : list of length 3
            Stores the orientation of the sprite's local frame of reference.
        """
        self.object_ = object_
        self.positions = positions.reshape(-1, 3)
        self.angles = angles.reshape(-1, 3)
        self.frame_origin = [0, 0, 0]
        self.frame_orientation = [0, 0, 0]


    def transform(self, t):
        """
        Apply the transformation to the sprite at the given time step.

        This method transforms the sprite using the stored `positions` and `angles` for the
        given time step `t`. It calls the `transform` method of the `Object3D` instance
        to apply translation, rotation, and any other transformations.

        Parameters
        ----------
        t : int
            The time step index used to select the position and angles for transformation.

        Returns
        -------
        mesh.Mesh
            The transformed mesh object after applying the transformations for the specified time step.

        Methods Called
        --------------
        object_.transform()
            Applies the position and rotation transformations based on the stored position and angles.
        """

        return self.object_.transform(self.positions[t,:] ,self.angles[t,:], t)

class Scene:
    """
    Scene Class
    ===========

    A class representing a 3D scene containing multiple sprite objects that can be
    transformed over time. Each sprite in the scene is an instance of the `Sprite` class,
    and the transformations applied to the scene depend on the time step.

    This class provides a `transform` method to apply transformations to each sprite in
    the scene, either returning their original or transformed meshes based on the time step.

    Attributes
    ----------
    objects : list of Sprite
        A list of `Sprite` objects that make up the 3D scene.

    Methods
    -------
    __init__(objects):
        Initializes the scene with a list of `Sprite` objects.

    transform(t):
        Applies transformations to all sprite objects in the scene at the given time step `t`.
    """
    def __init__(self, objects: list):
        """
        Initialize the scene with a list of sprite objects.

        This constructor takes a list of `Sprite` objects that represent the individual
        elements in the 3D scene. Each sprite in the scene can be transformed over time
        using the `transform` method.

        Parameters
        ----------
        objects : list of Sprite
            A list of `Sprite` objects that will be included in the scene.
        """
        self.objects = objects

    def transform(self, t):
        """
        Apply transformations to all sprite objects in the scene at the given time step.

        This method iterates through all `Sprite` objects in the scene and applies the
        corresponding transformations based on the provided time step `t`. If the time
        step is negative, it returns the original mesh for each sprite. Otherwise, it applies
        the transformation based on the current time step and returns the transformed meshes.

        Parameters
        ----------
        t : float
            The time step used to determine which transformation (original or transformed)
            to apply to the sprite objects in the scene.

        Returns
        -------
        transformed_objects : list of mesh.Mesh
            A list of transformed meshes corresponding to each sprite object in the scene.

        Methods Called
        --------------
        spr.transform()
            Transforms each sprite in the scene at the given time step `t`.
        """
        transformed_objects = []

        if t < 0:
            for spr in self.objects:
                transformed_objects.append(spr.object_.stl_mesh)

        else:
            for spr in self.objects:
                transformed_objects.append(spr.transform(t))

        return transformed_objects

    def save_stl(self, t, reflect_xy=False, reflect_yz=False, reflect_xz=False):
        """
        Save the transformed meshes to STL files with optional reflections.

        This method applies transformations to all objects in the scene at the given time step `t`.
        If reflection flags are set, it applies the corresponding reflection across the specified planes.
        The method then combines the original and reflected meshes into a single STL mesh.

        Parameters
        ----------
        t : float
            The time step used to apply transformations to the objects in the scene.

        reflect_xy : bool, optional
            If True, reflects objects across the XY plane (invert Z-axis).

        reflect_yz : bool, optional
            If True, reflects objects across the YZ plane (invert X-axis).

        reflect_xz : bool, optional
            If True, reflects objects across the XZ plane (invert Y-axis).

        Returns
        -------
        combined_mesh : mesh.Mesh
            A single `mesh.Mesh` object containing all the transformed and optionally reflected objects.
        """


        def reflect(objects, axis):
            axis_map = {'x': 0, 'y': 1, 'z': 2}
            axis_idx = axis_map[axis]
            reflected = []

            for obj in objects:
                temp = copy.deepcopy(obj)
                temp.vectors[:, :, axis_idx] *= -1
                # Reverse vertex winding to maintain normal orientation
                temp.vectors = temp.vectors[:, ::-1, :]
                reflected.append(temp)

            return reflected

        transformed_objects = self.transform(t)
        reflected_objects = []

        if reflect_xy:
            reflected_objects += reflect(transformed_objects, 'z')
        elif reflect_yz:
            reflected_objects += reflect(transformed_objects, 'x')
        elif reflect_xz:
            reflected_objects += reflect(transformed_objects, 'y')

        all_objects = transformed_objects + reflected_objects
        combined_data = np.concatenate([obj.data for obj in all_objects])
        return mesh.Mesh(combined_data)

