import numpy as np

class Translation_Transform:
    """
    Translation_Transform Class
    ===========================

    Abstract base class for translation transformations.

    This class serves as a base for all translation transformations, requiring subclasses 
    to implement the `__call__` method to perform the translation operation. The translation
    is applied to the input data, typically shifting points in a 3D space by a specified position.

    Methods
    -------
    __call__(input_, position):
        Applies the translation to the input data based on the specified position.
        Must be implemented by subclasses.
    """

    def __call__(self, input_, position):
        """
        Abstract method for performing a translation on the input data.

        Parameters
        ----------
        input_ : np.ndarray
            The input data points to be translated. The shape is typically (n, 3), where 
            each row represents a 3D point (x, y, z).

        position : np.ndarray
            The translation vector that specifies the shift in the x, y, and z directions.
            The shape is (3,).

        Returns
        -------
        np.ndarray
            The translated input data, with each point shifted by the given position vector.

        Notes
        -----
        This method must be implemented by subclasses of `Translation_Transform`. 
        The translation operation should adjust the position of each point in the input data 
        by adding the translation vector.
        """
        raise NotImplementedError("Each transform must implement the __call__ method.")


class ConstantT(Translation_Transform):
    """
    ConstantT Class
    ===============

    A translation transform that applies no translation to the input data.

    This class overrides the `__call__` method of the `Translation_Transform` base class 
    and simply returns the input data unchanged, effectively performing no translation. 
    It is useful when a no-op translation is needed, or as a placeholder in cases where 
    translation might be conditionally applied.

    Methods
    -------
    __call__(input_, position):
        Returns the input data without any changes, effectively applying no translation.
    """

    def __call__(self, input_, position):
        """
        Applies no translation to the input data.

        Parameters
        ----------
        input_ : np.ndarray
            The input data points to be translated. The shape is typically (n, 3), where 
            each row represents a 3D point (x, y, z).

        position : np.ndarray
            The translation vector. This parameter is ignored as no translation is applied.

        Returns
        -------
        np.ndarray
            The input data, unchanged.

        Notes
        -----
        This class is a no-op for the translation transform. The `position` parameter
        is provided to match the interface of the base class, but it has no effect on 
        the output.
        """
        return input_


class Translation_COM(Translation_Transform):
    """
    Translation_COM Class
    =====================

    A translation transform that applies a constant translation to the input data based on 
    a specified position vector.

    This class implements the `__call__` method of the `Translation_Transform` base class 
    by adding a translation vector (position) to each of the input data points. The position 
    is applied to all points in the input data, effectively shifting them in 3D space by the 
    specified vector.

    Methods
    -------
    __call__(input_, position):
        Translates the input data by adding the specified position vector to each point.
    """

    def __call__(self, input_, position):
        """
        Applies a translation to the input data by adding a position vector to each point.

        Parameters
        ----------
        input_ : np.ndarray
            The input data points to be translated. The shape should be (n, 3), where 
            each row represents a 3D point (x, y, z).

        position : np.ndarray
            The translation vector to be added to each input data point. The shape should 
            be (3,) representing the translation in the x, y, and z axes.

        Returns
        -------
        np.ndarray
            The translated data, with the same shape as the input (n, 3).

        Raises
        ------
        AssertionError
            If the input data does not have shape (n, 3) or the position does not have 
            shape (3,).

        Notes
        -----
        The translation is applied element-wise, meaning each input point is shifted by 
        the same position vector, effectively performing a global translation in 3D space.
        """
        input_ = np.array(input_).reshape(-1, 3)
        position = np.array(position).reshape(3)

        assert input_.shape[1] == 3, "Input must have shape (n, 3)"
        assert position.shape[0] == 3, "Position must have shape (3,)"
        
        return input_ + position
