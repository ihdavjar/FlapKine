import streamlit as st
import sympy as sp
import numpy as np

import pandas as pd
from sympy import init_printing
from sympy import Integral, Matrix, pi, pprint
init_printing() # for pretty printing

# Helper functions
# Rotation about x axis
def Rx(theta):
    return sp.Matrix([[1, 0, 0], [0, sp.cos(theta), sp.sin(theta)], [0, -sp.sin(theta), sp.cos(theta)]])

# Rotation about y axis
def Ry(theta):
    return sp.Matrix([[sp.cos(theta), 0, -sp.sin(theta)], [0, 1, 0], [sp.sin(theta), 0, sp.cos(theta)]])

# Rotation about z axis
def Rz(theta):
    return sp.Matrix([[sp.cos(theta), sp.sin(theta), 0], [-sp.sin(theta), sp.cos(theta), 0], [0, 0, 1]])



def Auto_Page():
    # Let us take the sequence of rotation as input from the user
    # An example sequence 1-2-3
    seq_axis = st.text_input('Enter the axis sequence of rotation')

    # An example sequence alpha-beta-gamma
    seq_angle = st.text_input('Enter the angle sequence of rotation')

    # Get the position in the rotating frame
    # Here position is a vector with 3 components
    # Ex: r-xm-0
    position = st.text_input('Position in the rotating frame')


    # Take the input for considering the flexibility
    # Ex- 1-1-1 would mean the system is flexible in all the three directions
    # Ex- 0-0-1 would mean the system is flexible in the z direction
    flexibility = st.text_input('Enter the flexibility of the system')

    flexibility_sequence = flexibility.split('-')
    axis_sequence = seq_axis.split('-')
    angle_sequence = seq_angle.split('-')


    # Declare the time
    t = sp.symbols('t')

    # Initialize the rotation matrix
    R_T = sp.eye(3)

    for i in range(len(axis_sequence)):
        if axis_sequence[i] == '1':
            theta = sp.Function(angle_sequence[i])(t)
            R_T = R_T * Rx(theta).T

        elif axis_sequence[i] == '2':
            theta = sp.Function(angle_sequence[i])(t)
            R_T = R_T * Ry(theta).T

        elif axis_sequence[i] == '3':
            theta = sp.Function(angle_sequence[i])(t)
            R_T = R_T * Rz(theta).T

    # Display Rotation Matrix
    st.write('Rotation matrix:')
    st.latex(sp.latex(sp.simplify(sp.diff(R_T,t))))

    # Input vector
    input_vector = [temp.strip() for temp in position.split('-')]

    # Initialize the position vector by filling it with 1s
    position_vector = sp.ones(3,1)

    for i in range(len(input_vector)):
        if (input_vector[i] == '0'):
            position_vector[i] = 0
        
        else:
            if (flexibility_sequence[i] == '1'):
                position_vector[i] = sp.Function(input_vector[i])(t)
            
            else:
                position_vector[i] = sp.Symbol(input_vector[i])

    # Copy the position vector
    position_vector_1 = position_vector

    # Display the position vector
    position_vector = R_T * position_vector
    st.write('Position vector:')
    st.latex(sp.latex(position_vector))

    # Calculating the velocity vector
    velocity_vector = sp.diff(position_vector,t)

    # Display the velocity vector
    st.write('Velocity vector:')
    st.latex(sp.latex(velocity_vector))

    # Calculating the acceleration vector
    acceleration_vector = sp.diff(velocity_vector,t)

    # Display the acceleration vector
    st.write('Acceleration vector:')
    st.latex(sp.latex(acceleration_vector))

    st.container()
    # Give initial point on the wing
    initial_pos = st.text_input('Enter the initial position of the wing')

    # Processing the initial position
    initial_pos = initial_pos.split('-')
    initial_pos = [float(temp) for temp in initial_pos]

    


