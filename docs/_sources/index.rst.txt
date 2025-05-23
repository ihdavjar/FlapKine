.. FlapKine documentation master file, created by
   sphinx-quickstart on Mon May 12 18:06:40 2025.

FlapKine
========

**FlapKine** is a modular, high-performance PyQt5-based application for 3D forward and inverse kinematics visualization. Designed for **researchers**, **roboticists**, and **engineers**, it enables precise visualization, and export of flapping-wing kinematics using STL models and camera-tracked experimental data.

Built with PyQt5 and VTK | Research-grade accuracy | Bio-inspired robotics ready

.. image:: https://img.shields.io/badge/platform-windows-blue
   :alt: Platform Windows

.. image:: https://img.shields.io/github/repo-size/ihdavjar/FlapKine
   :alt: Repository Size

.. image:: https://github.com/ihdavjar/FlapKine/actions/workflows/test.yml/badge.svg
   :alt: Build Status
   :target: https://github.com/ihdavjar/FlapKine/actions/workflows/test.yml

.. image:: https://img.shields.io/pypi/v/flapkine.svg
   :alt: PyPI Version
   :target: https://pypi.org/project/flapkine/

.. image:: https://img.shields.io/github/license/ihdavjar/FlapKine
   :alt: GitHub License

.. image:: https://img.shields.io/github/v/release/ihdavjar/FlapKine?include_prereleases
   :alt: GitHub Release

.. image:: https://img.shields.io/badge/docs-online-brightgreen.svg
   :alt: Documentation
   :target: https://ihdavjar.github.io/FlapKine/


---


🔧 Features
-----------

- **Inverse Kinematics Engine** – Compute euler angles and visualize 3D point trajectories using custom analytical models.
- **3D STL Mesh Viewer** – Load STL files and observe real-time kinematic transformations.
- **Project Configuration** – Customize video resolution, camera settings, lighting parameters, and export options.
- **In-Situ Rendering** – Generate animations directly in memory without removing I/O overhead, enabling significantly faster execution.


---

📚 Table of Contents
--------------------

.. toctree::
   :maxdepth: 1
   :caption: Getting Started

   installation
   user_guide
   examples
   api_reference/index