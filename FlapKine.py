import streamlit as st
import sympy as sp
import numpy as np

import pandas as pd
from sympy import init_printing
from sympy import Integral, Matrix, pi, pprint
init_printing() # for pretty printing

from app.manual_page import Manual_Page
from app.automatic_page import Auto_Page
from app.open_project import open_current_project


if __name__ == "__main__":
    st.title('Kinematics App')

    open_current_project() 
        