.. _render_config:

Render Settings Window
======================

The **Render Settings Window** allows you to configure all rendering parameters, including video output, camera setup, lighting, STL export, and reflection settings.

You can access it in two contexts:

.. list-table::
   :header-rows: 1
   :widths: 25 50 25

   * - **Window**
     - **Description**
     - **Preview**
   * - **Project Creator**
     - Accessed during new project creation. Set up all render options before project initialization.
     - .. image:: ../assets/images/render_window_project_creator.png
        :alt: Render Settings in Project Creator
        :width: 300
   * - **Project Editor**
     - Accessed via **Render → Configure Render** from top menubar. Modify settings for an existing project without restarting.
     - .. image:: ../assets/images/render_window_project_editor.png
        :alt: Render Settings in Project Editor
        :width: 300

---

Video Settings
--------------

- **Frame Format**:
  Choose the image format for each rendered frame (e.g., **PNG**, **JPEG**).

- **Resolution**:
  Specify the output dimensions of each frame in **width × height** (pixels).

---

Camera Settings
---------------

- **Location**:
  Set the camera's position in the global coordinate space (**X**, **Y**, **Z**).

- **Focal Point**:
  Specify the point in 3D space that the camera looks at. This defines the **direction of view** and is typically set relative to the object of interest (**X**, **Y**, **Z**).

- **Up Vector**:
  Defines the **camera’s upward direction**, used to control the roll and orientation of the view. Commonly set as (0, 1, 0) for a vertical Y-axis alignment.


---

Light Settings
--------------

- **Position**:
  Specify the position of the scene light source in **X**, **Y**, and **Z**.

- **Power**:
  Control the intensity (brightness) of the light illuminating the scene.

---

Other Options
-------------

- **STL Export**:
  Enable **Save STL per Frame** to export geometry at each frame—useful for CFD workflows and mesh-based post-processing.

- **Reflection Plane**:
  Mirror the rendered geometry across a selected plane (**XY**, **YZ**, or **XZ**).
  This is particularly useful for simulating symmetrical wing pairs without duplicating sprite definitions.

---
