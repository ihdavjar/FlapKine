import numpy as np
from src.core.transforms.functional_flexibility import functional_Flexibility_type1 

class Flexibility_Transform:
    def __call__(self, input, t):
        raise NotImplementedError("Each transform must implement the __call__ method.")

class ConstantF(Flexibility_Transform):
    def __call__(self, input, t):
        return input
    
class Flexibility_type1(Flexibility_Transform):
    def __init__(self, x, y, z, major_axis, minor_axis):
        # x: bool
        # y: bool
        # z: bool
        # major_axis: bool
        # minor_axis: bool

        self.x = x
        self.y = y
        self.z = z
        self.major_axis = major_axis
        self.minor_axis = minor_axis
    
    def __call__(self, input, t):
        # input: np.array of shape (n, 3) i.e (x, y, z)
        # output: np.array of shape (n, 3) i.e (x, y, z) at time t
        if self.x:
            input[:, 0] = input[:, 0] + np.array([functional_Flexibility_type1(y, z, t, self.major_axis, self.minor_axis) for y, z in input[:, 1:]])

        if self.y:
            input[:, 1] = input[:, 1] + np.array([functional_Flexibility_type1(x, z, t, self.major_axis, self.minor_axis) for x, z in input[:, [0,2]]])

        if self.z:
            input[:, 2] = input[:, 2] + np.array([functional_Flexibility_type1(x, y, t, self.major_axis, self.minor_axis) for x, y in input[:, [0,1]]])

        
        return input
    
