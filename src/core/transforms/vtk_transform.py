import vtk

def vtk_rotation(rotation_type: str, angles: tuple):
    '''
    Returns a vtkTransform object that applies the specified rotation sequence.
    '''
    transform = vtk.vtkTransform()
    transform_1 = vtk.vtkTransform()
    transform_2 = vtk.vtkTransform()
    transform_3 = vtk.vtkTransform()

    angles = [angle * 180 / 3.141592653589793 for angle in angles] # Convert angles to degrees

    if rotation_type == 'ZXZ':
        transform_1.RotateZ(angles[0])
        transform_2.RotateX(angles[1])
        transform_3.RotateZ(angles[2])
    elif rotation_type == 'XYX':
        transform_1.RotateX(angles[0])
        transform_2.RotateY(angles[1])
        transform_3.RotateX(angles[2])
    elif rotation_type == 'YZY':
        transform_1.RotateY(angles[0])
        transform_2.RotateZ(angles[1])
        transform_3.RotateY(angles[2])
    elif rotation_type == 'ZYZ':
        transform_1.RotateZ(angles[0])
        transform_2.RotateY(angles[1])
        transform_3.RotateZ(angles[2])
    elif rotation_type == 'XZX':
        transform_1.RotateX(angles[0])
        transform_2.RotateZ(angles[1])
        transform_3.RotateX(angles[2])
    elif rotation_type == 'YXY':
        transform_1.RotateY(angles[0])
        transform_2.RotateX(angles[1])
        transform_3.RotateY(angles[2])
    elif rotation_type == 'ZYX':
        transform_1.RotateZ(angles[0])
        transform_2.RotateY(angles[1])
        transform_3.RotateX(angles[2])
    elif rotation_type == 'YXZ':
        transform_1.RotateY(angles[0])
        transform_2.RotateX(angles[1])
        transform_3.RotateZ(angles[2])
    elif rotation_type == 'XZY':
        transform_1.RotateX(angles[0])
        transform_2.RotateZ(angles[1])
        transform_3.RotateY(angles[2])
    elif rotation_type == 'ZXY':
        transform_1.RotateZ(angles[0])
        transform_2.RotateX(angles[1])
        transform_3.RotateY(angles[2])
    elif rotation_type == 'YZX':
        transform_1.RotateY(angles[0])
        transform_2.RotateZ(angles[1])
        transform_3.RotateX(angles[2])
    elif rotation_type == 'XYZ':
        transform_1.RotateX(angles[0])
        transform_2.RotateY(angles[1])
        transform_3.RotateZ(angles[2])
    else:
        raise ValueError(f"Invalid rotation type: {rotation_type}")
    
    # Concatenate transformations in order
    transform.Concatenate(transform_1)
    transform.Concatenate(transform_2)
    transform.Concatenate(transform_3)
    
    return transform
