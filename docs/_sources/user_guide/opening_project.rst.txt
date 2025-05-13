Opening an Existing Project
===========================

To load a saved project:

1. Click **Open Project**.
2. Select your **project directory**.
3. The app loads:
   - Your **STL model**
   - Saved **camera, lighting, and render settings**
   - Rendered animation (if available)

You’ll be redirected to the **Project Editor Window**.

For layout, features, and tools, see the :doc:`Project Editor Window <window/project_editor_window>`.

⚙️ Rendering Options
---------------------

- ✅ **Auto Load**: Loads previous animation if available.
- 🧮 **Manual Render**: Click the **Render** button to generate animations.
- ⚡ Features:

  - In-situ memory rendering (no disk I/O bottlenecks)
  - Multithreading using ``QThreadPool``
  - High-performance VTK pipeline
  - Non-essential UI widgets are disabled during rendering

For render configuration options, see the :doc:`Render Configuration <window/main_window>`
