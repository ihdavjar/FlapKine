📘 Examples
===========

This section showcases a variety of example projects built with **FlapKine**, each crafted to demonstrate different kinematic configurations and application scenarios. These hands-on examples provide a practical understanding of how to configure, simulate, and visualize kinematic chains using the **FlapKine** interface.

Each example includes:

- A brief description of the kinematic configuration
- A project file with a pre-configured scene
- In addition to the project file, it contains data required to reproduce the project from scratch.
- Instructions on how to run the simulation and visualize the results
- Instruction on how to reproduce the results by making a entirely new project from scratch

These examples are ideal for users looking to quickly familiarize themselves with **FlapKine** features and experiment with real setups.

Before beginning, let's first review what a **FlapKine** project folder typically contains.

Project Folder Structure
-------------------------

Each example project follows a standardized structure automatically created by **FlapKine** during project finalization. Below is an outline of the folder contents:

.. code-block:: text

    <project_folder>/
    ├── scene.pkl          # Scene Class object saved as a pickle file
    ├── config.json        # Configuration file with simulation and rendering settings
    └── data/
        ├── inv_results/   # Inverse kinematics results (angles)
        ├── stl/           # STL files for the model at each time step
        └── videos/        # Output folder for rendered simulation frames or video

Configuration Details (`config.json`)
-------------------------------------

The configuration file stores the complete simulation setup derived from the GUI. It includes:

- **VideoRender**

  - ``OutputPath``: Path to the folder where rendered frames will be saved (e.g., ``data/images``)

  - ``STLPath``: Path where STL data will be written if enabled (e.g., ``data/stl``)

  - ``FrameFormat``: Format for output frames (e.g., ``PNG``, ``JPG``)

  - ``resolution_x/y``: Horizontal and vertical resolution values

  - ``film_transparent``: Boolean indicating background transparency (currently set to ``false``)

- **Camera**

  - ``location``: Position of the camera in 3D space ``[x, y, z]``

  - ``focal``: Point in space the camera is looking at ``[x, y, z]``

  - ``up``: Camera's up direction vector ``[x, y, z]``

- **Light**

  - ``location``: Light source position ``[x, y, z]``

  - ``energy``: Scalar representing light intensity

- **STL**: Boolean flag indicating whether STL export is enabled

- **Reflect**: Axis of reflection applied to the scene (``"XY"``, ``"YZ"``, ``"XZ"``), or ``null`` for no reflection


The `scene.pkl` file is the pickled version of the ``Scene`` class, which contains all the information about the simulation. This file is loaded when the project is opened in **FlapKine**.

See :ref:`Methodology <methodology>` for more details on ``Scene`` and other classes in **Flapkine**.


.. toctree::
   :maxdepth: 1
   :caption: Example Projects

   examples/1_DOF_1
   examples/2_DOF_Translation
   examples/3_DOF_1
   examples/3_DOF_2
   examples/2_DOF_INV