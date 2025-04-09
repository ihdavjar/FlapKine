import copy
import numpy as np
from src.core.transforms.functional_flexibility import *

class Flexibility_Transform:
    """
    Flexibility_Transform Class
    ===========================

    Abstract base class for all time-dependent flexibility transforms in the FlapKine framework.

    This class serves as a blueprint for defining spatial deformation transforms that vary
    over time. It enforces implementation of the `__call__` method in subclasses, where the
    actual transformation logic is defined.

    Attributes
    ----------
    (None)

    Methods
    -------
    __call__(input_, t):
        Abstract method to apply the deformation to a 3D input array at time `t`.
        Must be implemented by derived classes.
    """
    def __call__(self, input_, t):
        """
        Applies the flexibility transform to the input data at a given time step.

        Parameters
        ----------
        input_ : np.ndarray
            An array of shape (n, 3) representing 3D points.
        t : int or float
            Time index or value at which to evaluate the transformation.

        Raises
        ------
        NotImplementedError
            If not implemented in the subclass.
        """
        raise NotImplementedError("Each transform must implement the __call__ method.")

class ConstantF(Flexibility_Transform):
    """
    ConstantF Class
    ===============

    No-operation (identity) flexibility transform.

    This transform returns the input 3D point array unchanged. It can be used in contexts
    where no deformation is required but the pipeline expects a transform instance.

    Attributes
    ----------
    (None)

    Methods
    -------
    __call__(input_, t):
        Returns the input array without applying any deformation.
    """

    def __call__(self, input_, t=None):
        """
        Returns the input 3D point array unchanged.

        Parameters
        ----------
        input_ : np.ndarray
            An array of shape (n, 3) representing 3D points.
        t : int or float, optional
            Time index (ignored in this implementation).

        Returns
        -------
        np.ndarray
            The same input array, unmodified.
        """
        return input_

    
class Flexibility_type1(Flexibility_Transform):
    """
    Flexibility_type1 Class
    =======================

    Sinusoidal deformation transform along selectable axes.

    Applies periodic sinusoidal deformations to a 3D point cloud based on time `t` and
    configurable parameters such as axis selection, time period, and waveform shape.
    The deformation magnitude at each point depends on its cross-axes (e.g., YZ affects X).

    Attributes
    ----------
    x : bool
        Whether to apply deformation along the X-axis.

    y : bool
        Whether to apply deformation along the Y-axis.

    z : bool
        Whether to apply deformation along the Z-axis.

    major_axis : bool
        Controls the primary axis for sinusoidal wave generation.

    minor_axis : bool
        Controls the secondary axis used in wave generation.

    time_period : float
        Period of the sinusoidal deformation in time steps.

    p : float
        Controls the steepness and sharpness of the waveform.

    Methods
    -------
    __init__(x, y, z, major_axis, minor_axis, time_period=100, p=0.5):
        Initializes the transform with axis configuration and waveform parameters.

    __call__(input_, t):
        Applies the sinusoidal deformation along enabled axes at time `t`.
    """
    def __init__(self, x, y, z, major_axis, minor_axis, time_period=100, p=0.5):
        """
        Initializes the Flexibility_type1 transform.

        This constructor sets up the sinusoidal deformation transform with axis enablement
        and waveform configuration for time-varying deformations of 3D point arrays.

        Parameters
        ----------
        x : bool
            Whether to apply deformation along the X-axis.

        y : bool
            Whether to apply deformation along the Y-axis.

        z : bool
            Whether to apply deformation along the Z-axis.

        major_axis : bool
            Specifies if the major axis is used in sinusoidal calculation.

        minor_axis : bool
            Specifies if the minor axis is used in sinusoidal calculation.

        time_period : float, optional
            Time period of the sinusoidal wave (default is 100).

        p : float, optional
            Sharpness or curvature control of the wave (default is 0.5).
        """

        self.x = x
        self.y = y
        self.z = z
        self.major_axis = major_axis
        self.minor_axis = minor_axis
        self.time_period = time_period
        self.p = p
    
    def __call__(self, input_, t):
        """
        Applies sinusoidal deformation to 3D coordinates based on the selected axes.

        This method modifies the input array by applying sinusoidal transformations 
        to each coordinate axis (X, Y, Z) based on the other two axes. The deformation 
        depends on the specified waveform parameters and is time-dependent.

        Parameters
        ----------
        input_ : np.ndarray
            Input array of shape (n, 3), representing a list of 3D coordinates (x, y, z).

        t : float
            Time step at which to evaluate the transformation.

        Returns
        -------
        np.ndarray
            Transformed array of shape (n, 3), representing deformed 3D coordinates at time `t`.
        """
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
    """
    Flexibility_type2 Class
    =======================

    Empirical deformation transform driven by a time-dependent value array.

    Applies deformative forces to a 3D point cloud based on a user-provided `array_values`,
    which modulates the waveform amplitude over time. Useful for applying non-analytical or
    externally generated flexibility profiles (e.g., sensor or simulation data).

    Attributes
    ----------
    x : bool
        Whether to apply deformation along the X-axis.

    y : bool
        Whether to apply deformation along the Y-axis.

    z : bool
        Whether to apply deformation along the Z-axis.

    min_minor_axis : float
        Lower bound for the minor axis parameter in waveform generation.

    major_axis : float
        Primary shaping parameter for the sinusoidal wave.

    minor_axis : float
        Secondary shaping parameter for the sinusoidal wave.

    array_values : np.ndarray
        Time-indexed array containing modulation values for the waveform.

    time_period : float
        Period of the waveform over time.

    p : float
        Shape parameter for the waveform's slope and intensity.

    Methods
    -------
    __init__(x, y, z, min_minor_axis, major_axis, minor_axis, array_values, time_period=100, p=0.5):
        Initializes the transform with axis settings, waveform configuration, and dynamic amplitude data.

    __call__(input_, t):
        Applies deformation at time `t` using values from the external array.
    """
    def __init__(self, x, y, z, min_minor_axis, major_axis, minor_axis, array_values, time_period=100, p=0.5):
        """
        Initializes the Flexibility_type2 transformation with axis flags and waveform parameters.

        This constructor sets up the deformation behavior for each axis using parameters 
        such as major and minor radii, dynamic waveform values, and deformation frequency. 
        The `array_values` parameter enables time-varying flexibility by introducing 
        an additional temporal influence on the transformation.

        Parameters
        ----------
        x : bool
            Whether to apply deformation along the X-axis.

        y : bool
            Whether to apply deformation along the Y-axis.

        z : bool
            Whether to apply deformation along the Z-axis.

        min_minor_axis : float
            Minimum amplitude of the minor axis for deformation.

        major_axis : float
            Major radius for the elliptical transformation function.

        minor_axis : float
            Minor radius for the elliptical transformation function.

        array_values : np.ndarray
            Array of shape (n, 1) representing time-dependent modulation values.

        time_period : float, optional
            Period of the waveform cycle, by default 100.

        p : float, optional
            Phase or power modulation factor for the waveform, by default 0.5.
        """
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
        """
        Applies a time-dependent non-linear deformation to the input 3D coordinates.

        This method modifies the input point cloud along selected axes using a 
        parametric transformation based on elliptical waveforms and a dynamic 
        `array_values` lookup for time-varying modulation. Each axis is selectively 
        deformed by evaluating a custom waveform influenced by neighboring axes 
        and time `t`.

        Parameters
        ----------
        input_ : np.ndarray
            Array of shape (n, 3) representing n 3D points to be transformed.

        t : int
            Current time index used to fetch modulation amplitude from `array_values`.

        Returns
        -------
        np.ndarray
            Transformed array of shape (n, 3) with deformations applied at time `t`.
        """
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
    
