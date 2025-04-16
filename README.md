# 🚀 Flapkine

**Flapkine** is a modular, high-performance PyQt5-based application for 3D inverse kinematics visualization and animation control — built for researchers, roboticists, and engineers who need **precision**, **control**, and **speed** in one sleek GUI.

![Flapkine Banner](app\assets\flapkine_icon.png)

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

## 🚀 Quick Start

1. **Launch the App.**
2. **Load Your STL File:** Use the file selector to load a 3D STL model.
3. **Configure Your Project:** Set up camera paths, lighting, reflections, and more.
4. **Play and Preview:** Control the animation timeline and preview the motion.
5. **Export:** Save rendered outputs as a JPEG sequence or video file.

---

## 📸 Screenshots

- **Animation Preview**
- **Project Setup Panel**

*(Add or replace the images with your own screenshots as needed.)*

---

## 📚 Documentation

Full API and user documentation is available at:  
[https://ihdavjar.github.io/FlapKine](https://ihdavjar.github.io/FlapKine)

