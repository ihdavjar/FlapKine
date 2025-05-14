.. _rotation_transform:

Rotation Transformation
=======================

A rotation transformation modifies the orientation of an object by applying time-dependent or static rotations to its local frame.

.. list-table:: Rotation Modes
   :widths: 20 30 50
   :header-rows: 1

   * - **Transform Type**
     - **Mode**
     - **Description**
   * - **Rotation**
     - ``Constant``
     - The object retains its original orientation throughout the simulation.
   * -
     - ``Euler_Angle``
     - Applies a time-dependent rotation using Euler angles. See :ref:`Euler Angle <euler_angle>` section below.

---

Mathematical Model
------------------

If a rotation transformation is applied, the position vector :math:`\mathbf{P}_{B}`` (resulting from translation) is further transformed by the rotation matrix :math:`\mathbf{R}_{B}`:

.. math::

   \mathbf{P}_{B}'' = \mathbf{R}_{B} \cdot \mathbf{P}_{B}'


The rotation matrix is computed from Euler angles if the ``Euler_Angle`` mode is selected. The rotation matrix is defined as:

.. math::

   \mathbf{R}_{B} = \mathbf{R}_{\text{axis}_1}(\alpha) \cdot \mathbf{R}_{\text{axis}_2}(\beta) \cdot \mathbf{R}_{\text{axis}_3}(\gamma)

Here, :math:`\mathbf{R}_{\text{axis}_i}(\theta)` denotes the rotation matrix for a rotation of angle :math:`\theta` about the body-fixed axis :math:`\text{axis}_i`, constructed so that it operates exclusively on that axis—i.e., it ignores any rotations about the other axes :math:`\text{axis}_j` for :math:`j \neq i`.

Example: For rotation sequence (X, Y, Z):

.. math::

   \mathbf{R}_{B} = \mathbf{R}_{X}(\alpha) \cdot \mathbf{R}_{Y}(\beta) \cdot \mathbf{R}_{Z}(\gamma)

---

Else if the ``Constant`` mode is selected, the rotation matrix is set to the identity matrix:

.. math::

   \mathbf{R}_{B} =
   \begin{bmatrix}
   1 & 0 & 0 & 0 \\
   0 & 1 & 0 & 0 \\
   0 & 0 & 1 & 0 \\
   0 & 0 & 0 & 1
   \end{bmatrix}



.. _euler_angle:

Euler Angle
-----------

The ``Euler_Angle`` mode applies time-dependent rotations using Euler angles. This mode allows for detailed control of an object’s orientation over time by specifying a rotation sequence and supplying angle data for each frame.

Overview
^^^^^^^^

Rotation is applied through a user-defined sequence of three intrinsic (body-fixed) rotations—commonly ZYX, XYZ, etc. In body frame terms X - :math:`\hat{\mathbf{b}}_1`, Y - :math:`\hat{\mathbf{b}}_2`, and Z - :math:`\hat{\mathbf{b}}_3`. The rotation sequence is defined as:

- :math:`\alpha`: Rotation about :math:`\mathbf{axis}_1`.
- :math:`\beta`: Rotation about :math:`\mathbf{axis}_2`.
- :math:`\gamma`: Rotation about :math:`\mathbf{axis}_3`.

The rotation matrix is computed as:

.. math::

   \mathbf{R}_{B} = \mathbf{R}_{\text{axis}_1}(\alpha) \cdot \mathbf{R}_{\text{axis}_2}(\beta) \cdot \mathbf{R}_{\text{axis}_3}(\gamma)

Example: For rotation sequence (Z, Y, X):

.. math::

   \mathbf{R}_{B} = \mathbf{R}_{Z}(\alpha) \cdot \mathbf{R}_{Y}(\beta) \cdot \mathbf{R}_{X}(\gamma)

Input Options
^^^^^^^^^^^^^

Users may provide Euler angle sequences in two ways:

- **CSV File Input**: Upload a file with time-varying angle values.
- **Automatic Import**: Import angle sequences directly from the :ref:`Inverse kinematics <inverse_kinematics_window>` module.

This flexibility supports both manual design and automated workflows.

.. image:: ../../assets/images/euler_angle_rotation_transform.png
   :alt: Euler Angle Rotation Transform
   :align: center
   :width: 500px


.. note::

   **Euler Angle CSV Format**

   Each Euler angle (`alpha`, `beta`, `gamma`) must be provided in a **separate CSV file**.

   The format of each file should be:

   - A single column containing the angle values in degrees.
   - Each row represents the value of the angle at a specific time step.
   - No header row is required.

   Example (`alpha.csv`):

   .. code-block:: csv

      0.0
      12.5
      25.0
      18.2
      ...

   Similarly, create `beta.csv` and `gamma.csv` with the corresponding angle sequences.
---


Usage Notes
-----------

- Euler angles must be in **degrees**
- Rotation sequence must match the physical setup or simulation logic
- Ensure time series length matches the number of animation frames

---

Related Topics
--------------

- :ref:`translation_transform`
- :ref:`transform_reference`
- :ref:`Inverse kinematics <inverse_kinematics_window>`
