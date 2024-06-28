class transform:
    def __init__(self, type):
        self.x = x
        self.y = y
        self.z = z

    de

    def forward(self, transform):
        pass

    

class Object3D:
    def __init__(self, name, stl_mesh, translation_transform, rotation_transform):
        '''
        name: str
        stl_mesh: mesh.Mesh
        translation_transform: function
        rotation_transform: function
        '''

        self.name = name
        self.stl_mesh = stl_mesh
        self.translation_transform = translation_transform
        self.rotation_transform = rotation_transform


    def __str__(self):
        return f"Object3D: {self.name} with {self.stl_mesh} mesh. Translation: {self.translation_transform}, Rotation: {self.rotation_transform}"