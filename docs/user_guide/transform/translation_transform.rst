.. _translation_transform:

Translation Transformation
==========================

A translation transformation modifies the position of an object by shifting its origin without altering its orientation or shape.

Overview
--------

There are two translation modes:

- **Constant**:
  The object remains stationary in the scene. No translation is applied.

- **Linear**:
  A time-dependent translation is performed based on the object's Center of Mass (COM) trajectory. This mode requires a CSV file containing position data for each time step. The object moves along this specified path during the animation.

.. image:: ../../assets/images/linear_translation_transform.png
   :alt: Linear Translation Transform
   :align: center
   :width: 500px

Mathematical Model
------------------

When a translation transformation is applied, the origin \(O_B\) of the ``Sprite`` frame is shifted. The position vector \(\mathbf{P}_B\), representing a vertex in the local ``Sprite`` frame, undergoes the following transformation:

.. math::

   \mathbf{P}_{B}' = \mathbf{T}_{B} \cdot \mathbf{P}_{B}

where:

.. math::

   \mathbf{P}_{B} =
   \begin{bmatrix}
   x_{B} \\
   y_{B} \\
   z_{B} \\
   1
   \end{bmatrix}

is the homogeneous coordinate of the vertex before transformation, and \(\mathbf{T}_{B}\) is the translation matrix:

.. math::

   \mathbf{T}_{B} =
   \begin{bmatrix}
   1 & 0 & 0 & t_x \\
   0 & 1 & 0 & t_y \\
   0 & 0 & 1 & t_z \\
   0 & 0 & 0 & 1
   \end{bmatrix}

Here, \(t_x\), \(t_y\), and \(t_z\) represent the translation distances along the local \(\hat{\mathbf{b}}_1\), \(\hat{\mathbf{b}}_2\), and \(\hat{\mathbf{b}}_3\) axes, respectively.

Usage Notes
-----------

- The CSV file for **Linear** translation should contain columns corresponding to time steps and the COM positions: `time, x, y, z`.
- Ensure that the number of time steps in the CSV matches the total number of frames in the animation for smooth motion.
- Units for translation are consistent with the coordinate system defined in the project (typically meters or millimeters depending on STL scale).

Related Topics
--------------

- :ref:`rotation_transform`
- :ref:`transform_reference`
