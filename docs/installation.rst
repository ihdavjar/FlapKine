📥 Installation
===============

🔹 Option A: Windows Installer
------------------------------

Download the latest release from the `Releases Page <https://github.com/ihdavjar/FlapKine/releases>`_ and run the installer. This will install FlapKine on your system with a desktop shortcuts.

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

.. tip::

   You can deactivate the Conda virtual environment anytime using:

   .. code-block:: bash

      conda deactivate

.. note::

   To ensure proper playback of rendered videos within the application, make sure your system has the necessary codecs installed.
   If you encounter playback issues, you can download and install the **K-Lite Codec Pack** from the official website:
   `K-Lite Codec Pack Download Page <https://codecguide.com/download_kl.htm>`_.



