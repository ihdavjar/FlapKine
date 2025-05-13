.. _sprite_creator_window:

Sprite Creator Window
========================

.. image:: ../../assets/images/sprite_creator.png
   :alt: Sprite Creator Window
   :align: center
   :width: 500px

Overview
--------

Define individual sprites by configuring their geometry, transforms, and initial placement in 3D space.

---

3D Object Configuration
-----------------------

- **Name**
  Enter a unique identifier for your 3D object.

- **STL File**
  Click **Browse** to select the `.stl` mesh file from disk. Once loaded, the built‑in visualizer renders the object with overlapping **Body Axes** (A, B, C) and **Inertial Axes** (X, Y, Z), showing their initial alignment.

- **Transforms**
  Choose how the object will move or deform during animation:
  - **Translation**: Select a preset (e.g., Constant, Linear).
  - **Rotation**: Select a preset (e.g., Constant, Euler Angles).
  - **Flexibility**: Choose a deformation model (e.g., _Constant/Rigid, FlexibilityType1, FlexibilityType2).

---

Body Origin Position
--------------------

Adjust the origin of the body axes relative to the inertial frame by setting:

- **X Offset**
- **Y Offset**
- **Z Offset**

All zeroes (`0, 0, 0`) will place the body origin exactly at the inertial origin. Any changes are reflected live in the visualizer.

---

Body Orientation (Euler Angles)
-------------------------------

Set the initial orientation with right‑handed Euler angles (in degrees):

1. **α (Alpha)** – Rotation about the body’s A (roll) axis
2. **β (Beta)** – Rotation about the body’s B (pitch) axis
3. **γ (Gamma)** – Rotation about the body’s C (yaw) axis

Adjusting these angles reorients the body axes in real time.

---

Finalize Your Sprite
--------------------

When you’re satisfied with the 3D object parameters, origin position, and orientation, click **Finish**.
This creates the sprite with your specified settings and returns you to the **Scene Creator Window**.

---

Transform Reference
-------------------

For detailed descriptions of each transform type, see the full **Transform Reference** in the :doc:`../transform_reference` section.

