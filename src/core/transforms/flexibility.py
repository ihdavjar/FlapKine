import copy
import numpy as np
from src.core.transforms.functional_flexibility import *

class Flexibility_Transform:
    def __call__(self, input_, t):
        raise NotImplementedError("Each transform must implement the __call__ method.")

class ConstantF(Flexibility_Transform):
    def __call__(self, input_, t=None):
        return input_
    
class Flexibility_type1(Flexibility_Transform):
    def __init__(self, x, y, z, major_axis, minor_axis, time_period=100):
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
        self.time_period = time_period
    
    def __call__(self, input_, t):
        # input: np.array of shape (n, 3) i.e (x, y, z)
        # output: np.array of shape (n, 3) i.e (x, y, z) at time t
        temp_input = copy.deepcopy(input_)

        if self.x:
            temp_input[:, 0] = input_[:, 0] + np.array([functional_Flexibility_type1(y, z, t, self.major_axis, self.minor_axis, self.time_period) for y, z in input_[:, 1:]])

        if self.y:
            temp_input[:, 1] = input_[:, 1] + np.array([functional_Flexibility_type1(x, z, t, self.major_axis, self.minor_axis, self.time_period) for x, z in input_[:, [0,2]]])

        if self.z:
            temp_input[:, 2] = input_[:, 2] + np.array([functional_Flexibility_type1(x, y, t, self.major_axis, self.minor_axis, self.time_period) for x, y in input_[:, [0,1]]])

        return temp_input

class Flexibility_type2(Flexibility_Transform):
    def __init__(self, x, y, z, major_axis, minor_axis, array_values, time_period=100, p=0.5):
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
        self.array_values = array_values
        self.time_period = time_period
        self.p = p
    
    def __call__(self, input_, t):
        # input: np.array of shape (n, 3) i.e (x, y, z)
        # output: np.array of shape (n, 3) i.e (x, y, z) at time t
        temp_input = copy.deepcopy(input_)

        Z_M_x_t = self.array_values[t]

        if self.x:
            temp_input[:, 0] = input_[:, 0] + np.array([functional_Flexibility_type2(y, z, Z_M_x_t, self.major_axis, self.minor_axis, self.time_period, self.p) for y, z in input_[:, 1:]])

        if self.y:
            temp_input[:, 1] = input_[:, 1] + np.array([functional_Flexibility_type2(x, z, Z_M_x_t, self.major_axis, self.minor_axis, self.time_period, self.p) for x, z in input_[:, [0,2]]])

        if self.z:
            temp_input[:, 2] = input_[:, 2] + np.array([functional_Flexibility_type2(x, y, Z_M_x_t, self.major_axis, self.minor_axis, self.time_period, self.p) for x, y in input_[:, [0,1]]]).reshape(-1,)
        
        return temp_input
    
