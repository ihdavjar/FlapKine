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

      git clone https://github.com/your-username/flapkine.git
      cd FlapKine

2. **(Optional but Recommended) Create a Virtual Environment**

   .. code-block:: bash

      python -m venv venv

3. **Activate the Virtual Environment**

   - **Windows PowerShell**

     .. code-block:: powershell

        .\venv\Scripts\Activate.ps1

   - **Windows CMD**

     .. code-block:: batch

        venv\Scripts\activate.bat

   - **macOS / Linux**

     .. code-block:: bash

        source venv/bin/activate

4. **Install Required Dependencies**

   .. code-block:: bash

      pip install -e .

5. **Launch the Application**

   .. code-block:: bash

      python -m FlapKineLauncher.py

.. note::

   You can deactivate the virtual environment at any time by typing ``deactivate``.

---
