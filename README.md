<p align="center">
  <img src="app/assets/flapkine_icon.png" alt="FlapKine Logo" width="200"/>
</p>

---

# FlapKine – A Simulation Toolkit for the Kinematics of Flapping-Wing Micro Aerial Vehicles

[![DOI](https://joss.theoj.org/papers/10.21105/joss.08158/status.svg)](https://doi.org/10.21105/joss.08158)
![GitHub License](https://img.shields.io/github/license/ihdavjar/FlapKine)
![GitHub Release](https://img.shields.io/github/v/release/ihdavjar/FlapKine?include_prereleases)
[![Docs](https://img.shields.io/badge/docs-online-brightgreen.svg)](https://ihdavjar.github.io/FlapKine/)
[![codecov](https://codecov.io/gh/ihdavjar/FlapKine/branch/master/graph/badge.svg)](https://codecov.io/gh/ihdavjar/FlapKine)

## Overview

**FlapKine** is a modular, PyQt5-based application designed for 3D visualization of forward and inverse kinematics in flapping-wing systems. Its hybrid architecture allows it to operate as both an intuitive graphical user interface (GUI) and a Python library, enabling researchers to simulate and animate flapping-wing motion either interactively or through code using FlapKine’s core classes.

The GUI is built to assist researchers who may not be proficient in programming, offering an accessible platform for scientific exploration and analysis.

FlapKine is lightweight and relies on a few essential libraries:

- `numpy`
- `pandas`
- `PyQt5`
- `vtk`

Key Features:

- **Inverse Kinematics Engine** — Compute and visualize 3D joint trajectories using custom analytical models.
- Control timelines, playback speed, and rendering in real time.
- Import and display STL files with real-time transformation tracking.
- **Project Setup Panel** — Configure video, camera paths, STL export, lighting, and reflections.
- Export animations as high-quality JPEG sequences.
- **Optimized Performance** — Built on VTK + PyQt5 with multithreaded rendering for speed.

For the full **documentation**, tutorials, and API reference, visit the [FlapKine Docs](https://ihdavjar.github.io/FlapKine)!

The source code can be found in the [GitHub repository](https://github.com/ihdavjar/FlapKine) and is fully open source under **MIT license**. Consider starring PathSim to support its development.

## 📥 Installation

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

> **Tip:** You can deactivate the virtual environment at any time by typing `deactivate`.

---

## Example

## Acknowledgements

## Contributing and Future

## ✅ To-Do List

- [ ] Add example projects
- [X] Improve the documentation
- [ ] Finalise paper.md
- [X] Link all referenced sections consistently across README
- [X] Add algorithm references (e.g., DLT explanation) with citations
