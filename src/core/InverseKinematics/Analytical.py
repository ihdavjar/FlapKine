import numpy as np

def model_analytical(rotation_axis, final_vectors):
    '''rotation_axis: str, rotation type
    final_vectors: list of sympy matrices, final vectors after rotation

    Returns:
    angles: angles of rotation
    '''

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

    