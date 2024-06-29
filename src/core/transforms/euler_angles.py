
import numpy as np

# Rotation about x axis
def Rx(theta):
    '''Theta: angle in radians

    Returns:
    3x3 rotation matrix about x axis
    '''

    return np.array([[1, 0, 0],
                     [0, np.cos(theta), -np.sin(theta)],
                     [0, np.sin(theta), np.cos(theta)]])
# Rotation about y axis
def Ry(theta):
    '''Theta: angle in radians

    Returns:
    3x3 rotation matrix about y axis
    '''

    return np.array([[np.cos(theta), 0, np.sin(theta)],
                     [0, 1, 0],
                     [-np.sin(theta), 0, np.cos(theta)]])
# Rotation about z axis
def  Rz(theta):
    '''Theta: angle in radians

    Returns:
    3x3 rotation matrix about z axis
    '''

    return np.array([[np.cos(theta), -np.sin(theta), 0],
                     [np.sin(theta), np.cos(theta), 0],
                     [0, 0, 1]])

# Proper Euler angles (z-x-z, x-y-x, y-z-y, z-y-z, x-z-x, y-x-y)
def rotation_matrix_z_x_z(alpha, beta, gamma):
    return Rz(alpha) @ Rx(beta) @ Rz(gamma)

def rotation_matrix_x_y_x(alpha, beta, gamma):
    return Rx(alpha) @ Ry(beta) @ Rx(gamma)

def rotation_matrix_y_z_y(alpha, beta, gamma):
    return Ry(alpha) @ Rz(beta) @ Ry(gamma)

def rotation_matrix_z_y_z(alpha, beta, gamma):
    return Rz(alpha) @ Ry(beta) @ Rz(gamma)

def rotation_matrix_x_z_x(alpha, beta, gamma):
    return Rx(alpha) @ Rz(beta) @ Rx(gamma)

def rotation_matrix_y_x_y(alpha, beta, gamma):
    return Ry(alpha) @ Rx(beta) @ Ry(gamma)

# Tait-Bryan angles (z-y-x, y-x-z, x-z-y, z-x-y, y-z-x, x-y-z)
def rotation_matrix_z_y_x(alpha, beta, gamma):
    return Rz(alpha) @ Ry(beta) @ Rx(gamma)

def rotation_matrix_y_x_z(alpha, beta, gamma):
    return Ry(alpha) @ Rx(beta) @ Rz(gamma)

def rotation_matrix_x_z_y(alpha, beta, gamma):
    return Rx(alpha) @ Rz(beta) @ Ry(gamma)

def rotation_matrix_z_x_y(alpha, beta, gamma):
    return Rz(alpha) @ Rx(beta) @ Ry(gamma)

def rotation_matrix_y_z_x(alpha, beta, gamma):
    return Ry(alpha) @ Rz(beta) @ Rx(gamma)

def rotation_matrix_x_y_z(alpha, beta, gamma):
    return Rx(alpha) @ Ry(beta) @ Rz(gamma)