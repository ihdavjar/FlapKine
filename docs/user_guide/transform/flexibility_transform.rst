.. _flexibility_transform:

Flexibility Transform (Experimental)
====================================

.. warning::

   **This feature is currently under development.**
   Functionality is experimental and subject to change in future releases.

The :code:`FlapKine` application supports flexible body transformations in addition to standard translation and rotation. This feature enables realistic modeling of deformable structures such as flapping wings. Flexibility is introduced via spatially varying transformation matrices applied per-vertex, enabling time-dependent and location-specific deformation.

.. list-table:: Flexibility Transform Modes
   :widths: 20 20 50
   :header-rows: 1

   * - **Transform Type**
     - **Mode**
     - **Description**
   * - **Flexibility**
     - ``Constant``
     - No deformation; the object behaves as a rigid body.
   * -
     - ``FlexibilityType1``
     - First mode of flexibility inspired by Dong *et al.* [#dong2022]_ where deformation occurs only along the wing thickness direction. Described in detail below.
   * -
     - ``FlexibilityType2``
     - *(Description to be added in future.)*

Mathematical Formulation
------------------------

Flexibility is modeled by applying a deformation matrix to each vertex in the body frame. The resulting transformation is expressed as:

.. math::

   \mathbf{P}_{B}''' = \mathbf{F}_{B} \cdot \mathbf{P}_{B}'',

where:

- :math:`\mathbf{P}_{B}''` is the vertex after translation and rotation.

- :math:`\mathbf{F}_{B}` is the **flexibility transformation matrix**, defined as:

  .. math::

     \mathbf{F}_{B} =
     \begin{bmatrix}
     1 & 0 & 0 & f_x(x_B, y_B, z_B) \\
     0 & 1 & 0 & f_y(x_B, y_B, z_B) \\
     0 & 0 & 1 & f_z(x_B, y_B, z_B) \\
     0 & 0 & 0 & 1
     \end{bmatrix}

Each function :math:`f_x`, :math:`f_y`, and :math:`f_z` defines the vertex-specific deformation in the respective directions based on the local body coordinates.

Flexibility Type 1: Flapping-Induced Deformation
------------------------------------------------

This mode simulates a time-dependent spanwise deformation modeled after flapping wing kinematics. Assuming:

- Wing span along :math:`\hat{\mathbf{b}}_1`
- Chord along :math:`\hat{\mathbf{b}}_2`
- Thickness along :math:`\hat{\mathbf{b}}_3`

The deformation is introduced only along :math:`\hat{\mathbf{b}}_3`, defined by:

.. math::

   \begin{aligned}
   f_x(x_B, y_B, z_B) &= 0 \\
   f_y(x_B, y_B, z_B) &= 0 \\
   f_z(x_B, y_B, z_B) &= h_m(x_B, y_B, t)
   \end{aligned}

The deflection :math:`h_m(x_B, y_B, t)` is computed using a piecewise function over the span (normalized coordinate :math:`x_B`):

.. math::

   h_m(x_B, y_B, t) =
   \begin{cases}
   \frac{h_m(y_B, t)}{p^2} (2p x_B - x_B^2), & 0 \leq x_B < p \\
   \frac{h_m(y_B, t)}{1 - p^2} (1 - 2p + 2p x_B - x_B^2), & p \leq x_B \leq 1
   \end{cases}

Where:

- :math:`p` is a user-defined inflection point on the span.
- :math:`h_m(y_B, t)` is the spanwise-time deformation function:

  .. math::

     h_m(y_B, t) =
     \frac{C(r) \cdot h_{m,\text{root}}}{\tanh(C_{\tau})} \cdot \frac{\tanh(C_{\tau} \cdot \sin(2\pi f t))}{C_{R}} \cdot \left(1 - \frac{r}{R} \right)

Here:

- :math:`C(r)` is the local chord length at spanwise position :math:`r`
- :math:`h_{m,\text{root}}` is the root deflection amplitude
- :math:`f` is the flapping frequency
- :math:`C_{\tau}` is the temporal shaping factor
- :math:`R` is the total wing span
- :math:`C_R` is the reference chord

Final Transformation
--------------------

After applying translation (:math:`\mathbf{T}_B`), rotation (:math:`\mathbf{R}_B`), and flexibility (:math:`\mathbf{F}_B`), the final vertex position in the inertial frame is:

.. math::

   \mathbf{P}_E = \mathbf{F}_B \cdot \mathbf{R}_B \cdot \mathbf{T}_B \cdot \mathbf{P}_B

Where:

- :math:`\mathbf{P}_E = \begin{bmatrix} x_E & y_E & z_E & 1 \end{bmatrix}^T` is the transformed vertex in inertial frame
- :math:`\mathbf{P}_B` is the original vertex in body frame

Implementation Notes
--------------------

- The flexibility transformation is computed **per vertex** using vertex-local body coordinates.
- Flexibility is applied **after** translation and rotation.
- The framework is designed to support real-time deformation in simulations, with flexibility functions updated each frame.

.. rubric:: References

.. [#dong2022] Dong, H., et al. *"Thrust performance of a flexible flapping wing."* Journal of Fluids and Structures, 2022.
