<p align="center">
  <img src="https://github.com/ihdavjar/FlapKine/blob/b4c54fb05f3480f55b8fb947e20f077168936d0e/app/assets/flapkine_icon.png" alt="FlapKine Logo" width="200"/>
</p>

---

# FlapKine – A Simulation Toolkit for the Kinematics of Flapping-Wing Micro Aerial Vehicles

![Platform](https://img.shields.io/badge/platform-windows-blue)
![Repo Size](https://img.shields.io/github/repo-size/ihdavjar/FlapKine)
[![PyPI version](https://img.shields.io/pypi/v/flapkine.svg)](https://pypi.org/project/flapkine/)
![GitHub License](https://img.shields.io/github/license/ihdavjar/FlapKine)
![GitHub Release](https://img.shields.io/github/v/release/ihdavjar/FlapKine?include_prereleases)
[![Docs](https://img.shields.io/badge/docs-online-brightgreen.svg)](https://ihdavjar.github.io/FlapKine/)
[![codecov](https://codecov.io/gh/ihdavjar/FlapKine/branch/master/graph/badge.svg)](https://codecov.io/gh/ihdavjar/FlapKine)


## Overview

**FlapKine** is a modular, PyQt5-based application designed for 3D visualization of forward and inverse kinematics in flapping-wing systems. Its hybrid architecture allows it to operate as both an intuitive graphical user interface (GUI) and a Python library, enabling researchers to simulate and animate flapping-wing motion either interactively or through code using FlapKine’s core classes.

The GUI is built to assist researchers who may not be proficient in programming, offering an accessible platform for scientific exploration and analysis.

FlapKine is lightweight and relies on a few essential libraries:

- [NumPy](https://numpy.org/)
- [Pandas](https://pandas.pydata.org/)
- [PyQt5](https://riverbankcomputing.com/software/pyqt/intro)
- [VTK (Visualization Toolkit)](https://vtk.org/)

Key Features:

- **Inverse Kinematics Engine** — Compute and visualize 3D joint trajectories using custom analytical models.
- Control timelines, playback speed, and rendering in real time.
- Import and display STL files with real-time transformation tracking.
- **Project Setup Panel** — Configure video, camera paths, STL export, lighting, and reflections.
- **Optimized Performance** — Built on VTK + PyQt5 with multithreaded rendering for speed.

For the full **documentation**, tutorials, and API reference, visit the [FlapKine Docs](https://ihdavjar.github.io/FlapKine)!

The source code can be found in the [GitHub repository](https://github.com/ihdavjar/FlapKine) and is fully open source under **MIT license**. Consider starring FlapKine to support its development.

## Installation

### 🔹 Option A: Windows Installer

Download the latest release from the [Releases Page](https://github.com/ihdavjar/FlapKine/releases) and run the installer. This will install Flapkine on your system with optional desktop shortcuts.

## 🔹 Option B: Developer Mode (Python)

Set up FlapKine locally for development using the steps below:

---

1. **Clone the Repository**

   ```bash
   git clone https://github.com/ihdavjar/FlapKine.git
   cd FlapKine
   ```
2. **(Recommended) Create a Conda Virtual Environment**

   ```bash
   conda create -n flapkine-env python=3.10.3
   ```
3. **Activate the Virtual Environment:**

   ```bash
   conda activate flapkine-env
   ```
4. **Install Required Dependencies:**

   ```bash
   pip install -e.
   ```
5. **Launch the Application:**

   ```bash
   python -m FlapKineLauncher.py
   ```

> **Note:** For proper video rendering support, you **must install** the [K-Lite Codec Pack](https://codecguide.com/download_kl.htm) (Basic or Standard version is enough).
> Without it, some video player features may not work, due to missing codec issues.
---

## Example

Get started with **FlapKine** using ready-to-run example projects. Each example showcases a different kinematic configuration and demonstrates how to:

- Set up and simulate motion
- Visualize results using the FlapKine interface
- Reproduce the setup entirely from scratch

Each project includes:

- A pre-configured scene file (`scene.pkl`)
- A complete simulation config (`config.json`)
- Required resources to build the project from scratch
- Instructions to both **run** and **rebuild** the project

For detailed insights into the project structure and usage patterns, check out the **[Examples](https://ihdavjar.github.io/FlapKine/examples.html)** section in the **FlapKine** documentation. It showcases practical implementations and helps you understand how the components fit together seamlessly.

## **1-DOF Flapping Wing System**

Download the [project.zip](https://github.com/ihdavjar/FlapKine/raw/refs/heads/main/examples/1_DOF_1/project.zip?download=)

This example simulates a wing structure undergoing:

- Rotation about a single axis (z-axis)
- Visualization of a 3D wing mesh loaded from an STL file

It includes all necessary configuration settings, time-varying angle inputs, and STL files required to run and reproduce the simulation in FlapKine.

**Files Included**

- `project.zip`: A compressed archive containing both the full simulation project and the necessary resource files.

Upon extraction, the contents of `project.zip` are organized into two main folders:

- `1_DOF_1/`: Contains the actual project setup, which can be loaded into FlapKine.
- `resources/`: Contains supporting files required for reproducing the project from scratch, such as STL meshes, angle time series, and plots.

**`resources/` Contents**

```python
resources/
├── angles/
│ ├── alpha_data.csv             # Rotation about the x-axis (all zeros)
│ ├── beta_data.csv              # Rotation about the y-axis (all zeros)
│ └── gamma_data.csv             # Rotation about the z-axis (time-series values)
│
├── stl/
│ └── wing.stl                   # 3D mesh of the wing
│
└── angle_plot.png               # Plot of the rotation angles over time
```

**Simulation Details**

This is a single degree-of-freedom system, where only the rotation about the z-axis (`gamma_data.csv`) is active. The alpha and beta angles (which can also be verified by visualizing the CSV files in `resources/angles`) remain zero throughout the simulation.

Below is a plot showing the time-series data for each rotation angle given in the `angles/` folder:

<p align="center">
  <img src="docs\assets\images\angles_plot.png" alt="Angle Plot" width="800">
</p>

<p align="center">
  <em>Figure: Time-series plot of the rotation angles (alpha, beta & gamma) used in this example.</em>
</p>

**Running the Example**

1. Extract the `project.zip` archive to your desired directory.
2. Launch the FlapKine application and select **Load Project**.
3. Navigate to the `1_DOF_1/` folder and select the directory.
4. The project will load with a pre-configured scene. Below is a video of the simulation output:

<p align="center">
  <img src="docs/_images/project_video.gif" alt="Flapping Wing Render Preview" width="800">
</p>
<p align="center">
  <em>Figure: Animation showing the flapping wing simulation rendered by FlapKine.</em>
</p>

For more examples and detailed steps to rebuild the project from scratch, please visit the official documentation:
[FlapKine Examples and Tutorials](https://ihdavjar.github.io/FlapKine/examples.html)

## Acknowledgements

FlapKine has been developed as part of an undergraduate research initiative with strong interdisciplinary underpinnings spanning mechanical design, computer vision, and applied machine learning. Special thanks to:

- **Professors and Mentors** at *IIT Jodhpur* for their constant guidance and feedback during the development of the analytical models and kinematic pipelines.
- The open-source communities behind **VTK**, **PyQt5**, and **NumPy**, whose robust libraries form the backbone of this simulation toolkit.
- Researchers and users of **DLTdv** tools for inspiring the need for a modern, standalone 3D tracking solution tailored to flapping-wing MAVs.
- **ChatGPT** by *OpenAI*, for serving as an AI assistant in drafting high-quality documentation, generating professional Sphinx-style docstrings, and assisting with the creation of the FlapKine logo.


## Contributing and Future Roadmap

Contributions to **FlapKine** are welcome and encouraged! Whether it's code, bug reports, feature suggestions, or documentation improvements — feel free to open a [GitHub Issue](https://github.com/ihdavjar/FlapKine/issues) or submit a [Pull Request](https://github.com/ihdavjar/FlapKine/pulls).

### Planned Enhancements

- **Flexible Wing Models (in progress):** Enable simulation of deformable and compliant wing structures, moving beyond rigid-body assumptions.
- **Multi-View Calibration System:** Integrate multi-stereo camera calibration tools natively within the GUI for seamless experimental video setup.
- **DLTdv Replacement Pipeline:** Implement a modern Direct Linear Transform-based module to reconstruct 3D points from video footage, eliminating reliance on software like **DLTdv**.
- **Plugin Architecture:** Enable external researchers to contribute new kinematic models or analysis tools as plug-and-play modules.

The long-term goal is to position FlapKine as a **self-sufficient, GUI-driven alternative** to legacy motion tracking tools used in flapping-wing biomechanics and robotics, while retaining code-level access for power users.

If you're passionate about bio-inspired flight, computer vision, or robotics — your contribution can shape the next chapter of FlapKine.

## ✅ To-Do List

- [X] Add example projects
- [X] Improve the documentation
- [ ] Finalise paper.md
- [X] Link all referenced sections consistently across README
- [X] Add algorithm references (e.g., DLT explanation) with citations
