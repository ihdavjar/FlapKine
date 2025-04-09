import numpy as np

def functional_Flexibility_type1(x, y, t, major_axis, minor_axis, time_period, p):
    """
    Computes the Z-axis displacement of a point on a flexible surface using an elliptical deformation model.

    This function models the time-dependent vertical displacement `Z_M_x_y_t` of a surface
    (e.g., a flexible wing or membrane) based on its spatial coordinates `(x, y)`, time `t`,
    and geometric parameters such as `major_axis`, `minor_axis`, and a curvature parameter `p`.
    The deformation is modulated using a sinusoidal waveform and normalized using `tanh` shaping.

    Parameters
    ----------
    x : float
        X-coordinate of the point on the surface (along the major axis).

    y : float
        Y-coordinate of the point on the surface (along the minor axis).

    t : float
        Time variable controlling the phase of the deformation waveform.

    major_axis : float
        Length of the semi-major axis of the elliptical surface.

    minor_axis : float
        Length of the semi-minor axis of the elliptical surface.

    time_period : float
        Period over which the waveform completes one oscillation.

    p : float
        Curvature parameter (typically in range [0, 1]) defining the shape profile 
        across the surface span.

    Returns
    -------
    float
        The computed Z-axis displacement `Z_M_x_y_t` at position `(x, y)` and time `t`.
    """
    C_R = 2*minor_axis
    R = 2*major_axis

    t = t/time_period
    
    C_r = C_R*((1-((x-major_axis)/major_axis)**2)**(0.5)) # Local chord length

    Z_M_Root = 0.125*C_r

    Z_M_x = (Z_M_Root/C_R)*(1-x/R)*(C_r)

    Z_M_x_t = Z_M_x/np.tanh(2.9)*np.tanh(2.9*np.sin(2*np.pi*t + 0.4))   

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
    """
    Computes the Z-axis displacement of a point using a modified elliptical deformation model (Type 2).

    This function calculates the vertical displacement `Z_M_x_y_t` for a point on a flexible structure
    (such as a deformable wing) based on its spatial location `(x, y)`, a minimum Y reference (`y_min`),
    and a time-dependent displacement amplitude `Z_M_x_t`. This Type 2 variation suppresses motion
    for span-wise locations below a threshold defined by the parameter `p`.

    Parameters
    ----------
    x : float
        X-coordinate of the point on the surface (along the major axis). (Not used in current formula.)

    y : float
        Y-coordinate of the point on the surface (along the minor axis).

    y_min : float
        Minimum Y-coordinate on the surface (used to normalize `y` across span).

    Z_M_x_t : float
        Time-varying amplitude at the given X-location, typically precomputed for each time frame.

    major_axis : float
        Length of the semi-major axis of the elliptical surface.

    minor_axis : float
        Length of the semi-minor axis of the elliptical surface.

    time_period : float
        Oscillation period of the deformation waveform (not directly used in this implementation).

    p : float, optional
        Curvature parameter (default is 0.5) that controls the span-wise shaping of the deformation.

    Returns
    -------
    float
        The computed Z-axis displacement `Z_M_x_y_t` at the given `(x, y)` and time `t`.
    """
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