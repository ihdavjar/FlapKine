# Flapkine

**Flapkine** is a modular, high-performance PyQt5-based application for 3D inverse kinematics visualization and animation control — built for researchers, roboticists, and engineers who need **precision**, **control**, and **speed** in one sleek GUI.

<p align="left">
  <img src="app\assets\flapkine_icon.png" alt="Main Window" width="250"/>
</p>


---

## 🔧 Features

- 🧠 **Inverse Kinematics Engine** — Compute and visualize 3D joint trajectories using custom analytical models.
- 🎮 **Interactive Animation Playback** — Control timelines, playback speed, and rendering in real time.
- 🧭 **STL Mesh Visualization** — Import and display STL files with real-time transformation tracking.
- 🛠️ **Project Setup Panel** — Configure video, camera paths, STL export, lighting, and reflections.
- 💾 **Video Export** — Export animations as high-quality JPEG sequences.
- ⚡ **Optimized Performance** — Built on VTK + PyQt5 with multithreaded rendering for speed.

---

## 📥 Installation

### 🔹 Option A: Windows Installer

Download the latest release from the [Releases Page](https://github.com/ihdavjar/FlapKine/releases) and run the installer. This will install Flapkine on your system with optional desktop shortcuts.

---

### 🔹 Option B: Developer Mode (Python)

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/your-username/flapkine.git
   cd FlapKine
   ```
2. **(Optional but Recommended) Create a Virtual Environment:**

   ```bash
   python -m venv venv
   ```
3. **Activate the Virtual Environment:**

   <details>
    <summary><strong>Windows PowerShell</strong></summary>

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

   </details>

   <details>
    <summary><strong>Windows CMD</strong></summary>

   ```cmd
   venv\Scripts\activate.bat
   ```

   </details>

   <details>
    <summary><strong>macOS / Linux</strong></summary>

   ```bash
   source venv/bin/activate
   ```

   </details>
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

## 🚀 User Guide: Flapkine

Welcome to **Flapkine**, your GUI-based platform for 3D kinematic visualization and point tracking on STL models. This guide walks you through launching the application, managing projects, and understanding key features.

---

## 🧭 1. Launching the Application

When you launch **Flapkine**, the **Main Window** appears.

You can either:

- 🔓 **Open an Existing Project**
- 🆕 **Create a New Project**

Each button includes tooltips explaining its function.  
➡️ *For details on components in this interface, see [🔎 Main Window](#main-window).*

---

## 📂 2. Opening an Existing Project

To load a saved project:

1. Click **Open Project**.
2. Select your **project directory**.
3. The app loads:
   - Your **STL model**
   - Saved **camera, lighting, and render settings**
   - Rendered animation (if available)

You’ll be redirected to the **Project Editor Window**.  
➡️ *See [🔎 Project Editor Window](#project-editor-window) for layout, features, and tools.*

### ⚙️ Rendering Options

- ✅ **Auto Load**: Loads previous animation if available.
- 🧮 **Manual Render**: Click the **Render** button to generate animations.
- ⚡ Features:
  - In-situ memory rendering (no disk I/O bottlenecks)
  - Multithreading using `QThreadPool`
  - High-performance VTK pipeline
  - Non-essential UI widgets are disabled during rendering

➡️ *For render configuration options, see [🎛️ Render Configuration](#render-configuration).*

### 🎯 Point Selection

To visualize a point’s trajectory:

1. Click a point in the **Point Selector** (top-right).
2. Its 3D motion appears in the **Scatter Plot Viewer** (bottom-right).

---

## 🆕 3. Creating a New Project

To create a new project:

1. Click **New Project**.
2. Choose a **project directory** and name.
3. You’ll enter the **Project Creator Window**.  
   ➡️ *Details: [🔎 Project Creator Window](#project-creator-window)*

Steps:

4. **Scene Setup**:
   - 📁 Import existing scene **OR**
   - ✨ Create a new scene  
     ➡️ *See [🎬 Creating a Scene](#creating-a-scene)*

5. **Render Settings**:
   - ✅ Load default settings (via checkbox)
   - ⚙️ Customize manually if needed  
     ➡️ *See [🎛️ Render Configuration](#render-configuration)*

6. Hit **Create Project** to proceed to the **Project Editor Window**.

---

## 🏗️ 4. Creating a Scene

To create a new scene:

1. In the **Project Creator Window**, click **Create** under Scene.
2. You’ll be redirected to the **Scene Creator Window**.  
   ➡️ *See [🔎 Scene Creator Window](#scene-creator-window)*

Steps:

3. Add or drop `Sprites` via the dropdown.
4. You may:
   - Load existing `Sprite` files
   - Or create new ones  
     ➡️ *See [🧩 Creating a Sprite](#creating-a-sprite)*

---

## 🧩 5. Creating a Sprite

To define a new `Sprite`:

1. In the **Scene Creator Window**, click **Add Sprite**.
2. Under the `Sprite`, click **Create**.
3. The **Sprite Creator Window** opens.  
   ➡️ *See [🔎 Sprite Creator Window](#sprite-creator-window)*

Components:

- Section 1: `3DObject` properties
- Section 2: Initial orientation settings

---

## 🔎 6. Windows Overview

Here are all the interface windows used in Flapkine. Each has a dedicated section:

| Window | Description |
|--------|-------------|
| [Main Window](#main-window) | Entry point for opening or creating projects |
| [Project Editor Window](#project-editor-window) | View STL, select points, preview animations |
| [Project Creator Window](#project-creator-window) | Setup scenes, adjust render settings |
| [Scene Creator Window](#scene-creator-window) | Compose scenes using sprites |
| [Sprite Creator Window](#sprite-creator-window) | Define object properties and orientation |
| [InverseKinematics Window](#inverse-kinematics-window) | (Coming Soon) For solving IK problems |

---

## 🎛️ 7. Render Configuration

Available through the **Configure Render** option in the menu bar:

| Option | Description |
|--------|-------------|
| Camera | Set perspective, view angle, and projection |
| Lighting | Position, intensity, and type (ambient, directional, etc.) |
| Resolution | Adjust frame output resolution |
| Output Format | Choose frame format (JPEG recommended) |
| STL Export | Toggle STL export for each frame |
| Multisampling | Disable for faster rendering |
| Frame Count | Set number of steps for animation |

---

## 🔬 8. Creating a Scene

Detailed in [Scene Creator Window](#scene-creator-window). Summary:

- Add multiple sprites
- Configure their types and layout
- Save for future reuse

---

## 🧠 9. Creating a Sprite

Detailed in [Sprite Creator Window](#sprite-creator-window). Summary:

- Assign geometry to the sprite
- Define its transformation behavior
- Link to the kinematics pipeline

---

## 🪟 Window Reference Sections

### 🪟 Main Window
> Interface for launching projects. Features:
- **Open Project** button
- **New Project** button
- Tooltips on hover
- Minimal layout to encourage fast start

---

### 🪟 Project Editor Window
> Central workspace for interacting with STL scenes and animations.

| Section | Purpose |
|---------|---------|
| 🎥 Video Preview | Shows rendered animation |
| 🧊 3D Visualizer | Displays STL model |
| 🎯 Point Selector | Selects 2D points |
| 📊 Scatter Plot | Shows trajectory of selected points |

---

### 🪟 Project Creator Window
> Used when starting a new project.

Features:
- Scene loading/creation interface
- Render settings configuration
- Reflection and STL export options
- Final "Create Project" action

---

### 🪟 Scene Creator Window
> Lets you build a scene by adding sprites.

Features:
- Drag and drop sprite input
- Scene name input
- Sprite table with status and controls

---

### 🪟 Sprite Creator Window
> Used to define individual sprite geometry and behavior.

Features:
- Object mesh selection
- Orientation settings
- Transformation preview

---

### 🪟 Inverse Kinematics Window
> *(Feature under development)*  
Planned to allow solving kinematic equations interactively.

---





---

> For help or advanced usage, refer to the full documentation or press `Help → User Guide` in the top menu.

---

## 📸 Screenshots

- **Animation Preview**
- **Project Setup Panel**

*(Add or replace the images with your own screenshots as needed.)*

---

## 📚 Documentation

Full API and user documentation is available at:
[https://ihdavjar.github.io/FlapKine](https://ihdavjar.github.io/FlapKine)

## Acknowledgements
