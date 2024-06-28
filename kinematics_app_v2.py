# Description:
# Inputs:
# 1)Axis to do the rotation in order 1-2-3 (To be given using the slider)
# 2)Angle given as alphabet such as theta etc for the rotation
# 3)Possible position in the rotating frame such as [r,xm,0]

import streamlit as st
import sympy as sp
import numpy as np

import pandas as pd
from sympy import init_printing
from sympy import Integral, Matrix, pi, pprint
init_printing() # for pretty printing

from manual_page import Manual_Page
from automatic_page import Auto_Page


if __name__ == "__main__":
    st.title('Kinematics App')


    temp = st.radio('Select the Input Type', ['Automatic', 'Manual'])

    if temp == 'Manual':
        Manual_Page()
    
    else:
        Auto_Page()
        



## Convention Used
# 3-2-1
# phi-beta-alpha
# x-y-z

# beta = -beta_max * sin(2*pi*f*ts)
# alpha

# beta = -beta_max * sin(2.0 * pi * f * ts);
# \alpha=\alpha_{m}/\tanh(c)*\tanh(c*\sin(2.0\cdot\pi\cdot1\cdot t+0.4));
# phi = phi_0 + phi_max * (cos(2.0 * pi * f * ts));

# alpha_0 = 90 * pi / 180;
# c = 2.9
# beta_max = 10 * pi / 180;
# alpha_max = 47 * pi / 180;
# phi_0 = 0;
# phi_max = 100 * pi / 180;


# # Substituting the values of the variables
# values = dict()
# for var in variables:
#     values[var] = st.text_input(f'Enter the value for {var}')


# # Substitute the values
# position_vector = position_vector.subs(values).evalf()
# velocity_vector = velocity_vector.subs(values).evalf()
# acceleration_vector = acceleration_vector.subs(values).evalf()

# # Display the position vector
# st.write('Position vector:')
# st.latex(sp.latex(position_vector))

# # Display the velocity vector
# st.write('Velocity vector:')
# st.latex(sp.latex(velocity_vector))

# # Display the acceleration vector
# st.write('Acceleration vector:')
# st.latex(sp.latex(acceleration_vector))