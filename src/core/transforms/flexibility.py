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
    def __init__(self, x, y, z, major_axis, minor_axis, time_period=100, p=0.5):
        # x: bool
        # y: bool
        # z: bool
        # major_axis: bool
        # minor_axis: bool
        # time_period: float
        # p: float

        self.x = x
        self.y = y
        self.z = z
        self.major_axis = major_axis
        self.minor_axis = minor_axis
        self.time_period = time_period
        self.p = p
    
    def __call__(self, input_, t):
        # input: np.array of shape (n, 3) i.e (x, y, z)
        # output: np.array of shape (n, 3) i.e (x, y, z) at time t
        temp_input = copy.deepcopy(input_)

        if self.x:
            for i in range(len(input_)):
                temp_input[:, 0] = input_[:, 0] + functional_Flexibility_type1(input_[i,1], input_[i,2], t, self.major_axis, self.minor_axis, self.time_period, self.p)

        if self.y:
            for i in range(len(input_)):
                temp_input[:, 1] = input_[:, 1] + functional_Flexibility_type1(input_[i,0], input_[i,2], t, self.major_axis, self.minor_axis, self.time_period, self.p)
    
        if self.z:
            for i in range(len(input_)):
                temp_input[:, 2] = input_[:, 2] + functional_Flexibility_type1(input_[i,0], input_[i,1], t, self.major_axis, self.minor_axis, self.time_period, self.p)
                
        return temp_input

class Flexibility_type2(Flexibility_Transform):
    def __init__(self, x, y, z, min_minor_axis, major_axis, minor_axis, array_values, time_period=100, p=0.5):
        # x: bool
        # y: bool
        # z: bool
        # min_minor_axis: float
        # major_axis: float
        # minor_axis: float
        # array_values: np.array of shape (n, 1)
        # time_period: float
        # p: float

        self.x = x
        self.y = y
        self.z = z
        self.min_minor_axis = min_minor_axis
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
            for i in range(len(input_)):
                temp_input[:, 0] = input_[:, 0] + functional_Flexibility_type2(input_[i,1], input_[i,2], self.min_minor_axis, Z_M_x_t, self.major_axis, self.minor_axis, self.time_period, self.p)

        if self.y:
            for i in range(len(input_)):    
                temp_input[:, 1] = input_[:, 1] + functional_Flexibility_type2(input_[i,0], input_[i,2], self.min_minor_axis, Z_M_x_t, self.major_axis, self.minor_axis, self.time_period, self.p)

        if self.z:
            for i in range(len(input_)):
                temp_input[i, 2] = input_[i, 2] + functional_Flexibility_type2(input_[i,0], input_[i,1], self.min_minor_axis, Z_M_x_t, self.major_axis, self.minor_axis, self.time_period, self.p)
        
        return temp_input
    
