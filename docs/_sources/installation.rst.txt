📥 Installation
===============

🔹 Option A: Windows Installer
------------------------------

Download the latest release from the `Releases Page <https://github.com/ihdavjar/FlapKine/releases>`_ and run the installer. This will install FlapKine on your system with optional desktop shortcuts.

---

🔹 Option B: Developer Mode (Python)
------------------------------------

1. **Clone the Repository**

   .. code-block:: bash

      git clone https://github.com/ihdavjar/FlapKine.git
      cd FlapKine

2. **(Recommended) Create a Conda Virtual Environment**

   .. code-block:: bash

      conda create -n flapkine-env python=3.10.3

3. **Activate the Virtual Environment**

   .. code-block:: bash

      conda activate flapkine-env

4. **Install Required Dependencies**

   .. code-block:: bash

      pip install -e .

5. **Launch the Application**

   .. code-block:: bash

      python -m FlapKineLauncher.py

.. note::

   You can deactivate the virtual environment at any time by typing ``conda deactivate``.

---
