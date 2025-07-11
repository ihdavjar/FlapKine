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
     - ``Linear``
     - See :ref:`Linear Translation <linear_translation>` for details.


---

Mathematical Model
------------------

When a translation transformation is applied, the body origin :math:`O_B` of the ``Sprite`` frame is shifted. The position vector :math:`\mathbf{P}_B'''`, representing a vertex after flexibility and rotation transform, undergoes the following transformation:

.. math::

   \mathbf{P}_{B}''' = \mathbf{T}_{B} \cdot \mathbf{P}_{B}''

where the translation matrix (:math:`\mathbf{T}_{B}`) is:

.. math::

   \mathbf{T}_{B} =
   \begin{bmatrix}
   1 & 0 & 0 & t_x \\
   0 & 1 & 0 & t_y \\
   0 & 0 & 1 & t_z \\
   0 & 0 & 0 & 1
   \end{bmatrix}

Here, :math:`t_x`, :math:`t_y`, and :math:`t_z` represent the translation distances along the inertial :math:`\hat{\mathbf{e}}_1`, :math:`\hat{\mathbf{e}}_2`, and :math:`\hat{\mathbf{e}}_3` axes.


.. _linear_translation:

Linear Translation
------------------

This mode applies a **time-dependent translation** to the object using an external CSV file.

.. image:: ../../assets/images/linear_translation_transform.png
   :alt: Linear Translation Transform
   :align: center
   :width: 500px


The CSV specifies the **position of the body frame origin** :math:`O_B` with respect to the **inertial frame** at each time step. This path is used to animate the object’s motion over time.

.. note::

   **CSV Format**

   The CSV file should contain:

   - Column 1: :math:`t_x` (X-position)
   - Column 2: :math:`t_y` (Y-position)
   - Column 3: :math:`t_z` (Z-position)

   Each row corresponds to one time step.


Final Transformation
--------------------

After applying flexibility (:math:`\mathbf{F}_B`), rotation (:math:`\mathbf{R}_B`), and translation (:math:`\mathbf{T}_B`), the final vertex position in the inertial frame is:

.. math::

   \mathbf{P}_E = \mathbf{T}_B \cdot \mathbf{R}_B \cdot \mathbf{F}_B \cdot \mathbf{P}_B

Where:

- :math:`\mathbf{P}_E = \begin{bmatrix} x_E & y_E & z_E & 1 \end{bmatrix}^T` is the transformed vertex in inertial frame
- :math:`\mathbf{P}_B` is the original vertex in body frame

Usage Notes
-----------

- The number of rows in the CSV should match the number of animation frames.
- Ensure consistent units across STL models, scene setup, and trajectory data.

---

Related Topics
--------------

- :ref:`rotation_transform`
- :ref:`transform_reference`
