.. _translation_transform:

Translation Transformation
==========================

A translation transformation modifies the position of an object by shifting its origin without altering its orientation or shape.

.. list-table:: Translation Modes
   :widths: 20 30 50
   :header-rows: 1

   * - **Transform Type**
     - **Mode**
     - **Description**
   * - **Translation**
     - ``Constant``
     - The object remains stationary in the scene. No translation is applied.
   * -
     - ``COM``
     - See :ref:`COM-Based Translation <com_translation>` for details.


---

Mathematical Model
------------------

When a translation transformation is applied, the body origin :math:`O_B` of the ``Sprite`` frame is shifted. The position vector :math:`\mathbf{P}_B`, representing a vertex in the local ``Sprite`` frame, undergoes the following transformation:

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

and the translation matrix is:

.. math::

   \mathbf{T}_{B} =
   \begin{bmatrix}
   1 & 0 & 0 & t_x \\
   0 & 1 & 0 & t_y \\
   0 & 0 & 1 & t_z \\
   0 & 0 & 0 & 1
   \end{bmatrix}

Here, :math:`t_x`, :math:`t_y`, and :math:`t_z` represent the translation distances along the inertial :math:`\hat{\mathbf{e}}_1`, :math:`\hat{\mathbf{e}}_2`, and :math:`\hat{\mathbf{e}}_3` axes.

---

.. _com_translation:

COM-Based Translation
---------------------

This mode applies a **time-dependent translation** to the object using an external CSV file.

.. image:: ../../assets/images/linear_translation_transform.png
   :alt: Linear Translation Transform
   :align: center
   :width: 500px


Despite the name, the CSV does **not** contain the actual center of mass. Instead, it specifies the **position of the body frame origin** :math:`O_B` with respect to the **inertial frame** at each time step. This path is used to animate the object’s motion over time.

.. note::

   **CSV Format**

   The CSV file should contain:

   - Column 1: :math:`t_x` (X-position)
   - Column 2: :math:`t_y` (Y-position)
   - Column 3: :math:`t_z` (Z-position)

   Each row corresponds to one time step.

---

Usage Notes
-----------

- The number of rows in the CSV should match the number of animation frames.
- Ensure consistent units across STL models, scene setup, and trajectory data.
- COM translation is ideal for motion capture-based animations, CFD coupling, or prescribed kinematics.

---

Related Topics
--------------

- :ref:`rotation_transform`
- :ref:`transform_reference`
