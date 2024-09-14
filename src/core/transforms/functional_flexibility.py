import numpy as np

def functional_Flexibility_type1(x, y, t, major_axis, minor_axis, time_period):
    C_R = 2*minor_axis
    R = 2*major_axis

    # Ensure x and y are positive
    x = abs(x)
    y = abs(y)

    t = t/time_period
    
    C_r = C_R*((1-((x-major_axis)/major_axis)**2)**(0.5)) # Local chord length

    Z_M_Root = 0.125*C_r

    Z_M_x = (Z_M_Root/C_R)*(1-x/R)*(C_r)

    Z_M_x_t = Z_M_x/np.tanh(2.9)*np.tanh(2.9*np.sin(2*np.pi*t + 0.4))   

    p = 0.5

    if (C_r != 0):
        y_0 = (minor_axis-y)/C_r
    
    else: # At wingroot where C_r = 0
        y_0 = 0

    if (y_0<p):
        Z_M_x_y_t = (Z_M_x_t/(p**2))*(2*p*y_0 - y_0**2)
    
    else:
        Z_M_x_y_t = (Z_M_x_t/((1-p)**2))*(1-2*p+2*p*y_0-y_0**2)

    return Z_M_x_y_t

def functional_Flexibility_type2(x, y, y_min, Z_M_x_t, major_axis, minor_axis, time_period, p=0.5):
    C_R = 2*minor_axis
    R = 2*major_axis

    # Ensure x and y are positive
    # x = abs(x)
    # y = abs(y)

    y_0 = (y-y_min)/C_R
    

    if (y_0<p):
        # Z_M_x_y_t = (Z_M_x_t/(p**2))*(2*p*y_0 - y_0**2)
        Z_M_x_y_t = 0
    
    else:
        Z_M_x_y_t = (Z_M_x_t/((1-p)**2))*(1-2*p+2*p*y_0-y_0**2) - Z_M_x_t


    return Z_M_x_y_t