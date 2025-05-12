🪟 Inverse Kinematics Window
=============================

.. image:: ../../assets/images/Inv_kinematics_window.png
   :alt: Inverse Kinematics Window
   :align: center
   :width: 600

The **Inverse Kinematics Window** is designed to extract time‐series Euler angles from your wing’s 3D point data. Follow these steps to import, visualize, and export your kinematics:

---

1. **Import 3D Point Data**

- Prepare a CSV file with columns:  
  `time, Ax, Ay, Az, Bx, By, Bz, Cx, Cy, Cz, Dx, Dy, Dz`  
  where A, B, C, D are the four points on the wing plane.
- Click **Import Data** and select your CSV.  
- The 3D coordinates are reconstructed using the Direct Linear Transformation (DLT) algorithm (see reference below).

.. image:: ../../assets/images/wing_diagram.jpg
   :alt: Wing Point Configuration
   :align: center
   :width: 400

---

2. **Choose Euler Sequence**

- In the **Euler Order** dropdown, pick your desired rotation sequence (e.g., `ZYX`, `XYZ`, etc.).  
- This order determines how α (alpha), β (beta), and γ (gamma) are computed.

---

3. **Visualize Point Trajectories**

- On the **Left Panel**, select point **A**, **B**, **C**, or **D** to see its 3D trajectory plot over time.  
- Use this to verify tracking accuracy before computing angles.

---

4. **Compute & Preview Euler Angles**

- Once the sequence is selected, the window auto‐calculates α, β, γ at each timestamp.  
- Real‐time line plots appear below the 3D view for each angle component.

---

5. **Export to Sprite Creator**

- When you’re satisfied with the results, click **Finish**.  
- The computed Euler angles and selected sequence are sent directly to the **Sprite Creator Window** for further processing.

---

References
----------

- **DLT (Direct Linear Transformation)** – A standard method for reconstructing 3D coordinates from multi‐camera stereo views.

---
