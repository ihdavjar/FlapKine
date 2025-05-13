import numpy as np

def model_analytical(rotation_axis, final_vectors)-> tuple:
    """
    Computes Euler rotation angles based on the specified rotation axis convention.

    This function analytically determines the three Euler angles (alpha, beta, gamma)
    that rotate a reference frame to match the given final vectors, according to the
    specified Euler rotation convention (e.g., 'ZXZ', 'XYZ', etc.).

    The method assumes that the `final_vectors` represent the axes of the rotated frame
    (typically X, Y, and Z unit vectors) expressed in the original reference frame after transformation.

    Parameters
    ----------
    rotation_axis : str
        The Euler rotation sequence (e.g., 'XYZ', 'ZXZ', 'ZYX', etc.) that defines
        the axis order of the rotations to be solved.

    final_vectors : list of sympy.Matrix
        A list containing three SymPy 3D vectors representing the rotated axes after transformation.
        These vectors are used to analytically compute the rotation angles.

    Returns
    -------
    alpha : float
        The first Euler angle (in degrees), representing rotation about the first axis.

    beta : float
        The second Euler angle (in degrees), representing rotation about the second axis.

    gamma : float
        The third Euler angle (in degrees), representing rotation about the third axis.

    Notes
    -----
    - The function supports various Euler angle conventions including Tait-Bryan and classical Euler types.
    - Assumes that the input vectors are orthonormal and represent valid rotations.
    - All trigonometric computations are performed using `numpy`.

    Raises
    ------
    ValueError
        If an unsupported rotation axis is provided.
    """

    vector_1, vector_2, vector_3 = final_vectors

    if rotation_axis == 'ZXZ':
        alpha = np.arctan2(vector_2[2], -1*vector_1[2])
        beta = np.arcsin(vector_2[2]/np.sin(alpha))
        gamma = np.arctan2(vector_3[1], vector_3[0])

    elif rotation_axis == 'XYX':
        alpha = np.arctan2(vector_2[2], vector_3[2])
        beta = np.arccos(vector_3[2]/np.cos(alpha))
        gamma = np.arctan2(vector_1[1], vector_1[0])

    elif rotation_axis == 'YZY':
        alpha = np.arctan2(vector_3[1], vector_1[0])
        beta = np.arcsin(vector_3[1]/np.sin(alpha))
        gamma = np.arctan2(vector_2[2], -1*vector_2[0])

    elif rotation_axis == 'ZYZ':
        alpha = np.arctan2(vector_2[2], -1*vector_1[2])
        gamma = np.arctan2(vector_3[1], vector_3[0])
        beta = np.arcsin(vector_3[0]/np.cos(gamma))

    elif rotation_axis == 'XZX':
        alpha = np.arctan2(vector_3[0], -1*vector_1[0])
        gamma = np.arctan2(vector_1[2], vector_1[1])
        beta = np.arcsin(vector_3[0]/np.sin(gamma))

    elif rotation_axis == 'YXY':
        alpha = np.arctan2(vector_1[0], -1*vector_3[1])
        gamma = np.arctan2(vector_2[0], vector_2[2])
        beta = np.arcsin(vector_1[1]/np.sin(alpha))

    elif rotation_axis == 'ZYX':
        alpha = np.arctan2(-1*vector_2[0], vector_1[0])
        beta = np.arccos(vector_1[0]/np.cos(alpha))
        gamma = np.arctan2(-1*vector_3[1], vector_3[0])

    elif rotation_axis == 'YXZ':
        alpha = np.arctan2(-1*vector_1[2], vector_3[2])
        gamma = np.arctan2(-1*vector_2[0], vector_2[1])
        beta = np.arccos(vector_1[2]/np.cos(alpha))

    elif rotation_axis == 'XZY':
        alpha = np.arctan2(-1*vector_3[1], vector_2[1])
        beta = np.arccos(vector_1[1]/np.cos(alpha))
        gamma = np.arctan2(-1*vector_3[2], vector_3[0])

    elif rotation_axis == 'ZXY':
        alpha = np.arctan2(vector_1[1], vector_2[1])
        beta = np.arccos(vector_3[0]/np.sin(alpha))
        gamma = np.arctan2(vector_3[0], vector_3[2])

    elif rotation_axis == 'YXZ':
        alpha = np.arctan2(-1*vector_1[2], vector_3[2])
        gamma = np.arctan2(-1*vector_2[0], vector_2[1])
        beta = np.arccos(vector_1[2]/np.cos(alpha))

    elif rotation_axis == 'XYZ':
        alpha = np.arctan2(vector_2[2], vector_3[2])
        beta = np.arccos(vector_2[2]/np.sin(alpha))
        gamma = np.arctan2(vector_1[1], vector_1[0])

    # Convert the angles to degrees
    alpha = np.degrees(alpha)
    beta = np.degrees(beta)
    gamma = np.degrees(gamma)

    return alpha, beta, gamma
