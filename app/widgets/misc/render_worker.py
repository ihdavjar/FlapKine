import os
import json
import cv2
import numpy as np

from PyQt5.QtCore import QRunnable, pyqtSlot, QObject, pyqtSignal

from vtk import vtkActor, vtkCellArray, vtkPoints, vtkPolyData, vtkPolyDataMapper, vtkTriangle, vtkTransform, vtkTransformPolyDataFilter, vtkAppendPolyData
from vtkmodules.vtkRenderingCore import vtkRenderer, vtkRenderWindow, vtkCamera, vtkLight, vtkWindowToImageFilter
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.util.numpy_support import vtk_to_numpy

class RenderSignals(QObject):
    """
    RenderSignals Class
    ===================

    Defines custom signals for tracking the progress and completion status of the rendering process
    in the FlapKine application. This class is used to communicate between the rendering worker thread
    and the main GUI, allowing for real-time updates on rendering progress and notification upon completion.

    Attributes
    ----------
    progress_signal : pyqtSignal(float)
        Signal emitted periodically during rendering to indicate the progress percentage (0.0 to 100.0).

    finished : pyqtSignal()
        Signal emitted once the rendering task is fully completed.

    Methods
    -------
    None
        This class only defines signals and does not implement any methods.
    """
    progress_signal = pyqtSignal(float)
    finished = pyqtSignal()


class Worker(QRunnable):
    """
    Worker Class
    ============

    High-performance `QRunnable` designed to handle offscreen VTK rendering and real-time video encoding
    for the FlapKine application. The class avoids disk-based frame dumps by directly feeding rendered frames
    to OpenCV’s video writer. It supports STL export, real-time progress updates, and efficient rendering
    pipeline integration with PyQt5’s multithreading model.

    Attributes
    ----------
    project_folder : str
        Path to the project directory containing configuration and data folders.

    angles : list of float
        List of angles (typically camera azimuth or rotation values) used to render frames.

    scene_data : Any
        Scene object responsible for generating STL meshes for each frame.

    reflect : tuple of bool
        A 3-element tuple indicating whether to reflect the STL mesh along the XY, YZ, and XZ planes respectively.

    signals : RenderSignals
        Custom signal object to emit rendering progress and completion signals.

    Methods
    -------
    __init__(project_folder, angles, scene_data, reflect):
        Initializes the worker with project-specific configuration and rendering parameters.

    run():
        Executes the rendering pipeline. Renders each frame using VTK, optionally saves STL files, and writes
        each rendered frame to a video file using OpenCV. Emits progress and completion signals accordingly.

    stl_mesh_to_vtk(stl_mesh):
        Converts a mesh object into `vtkPolyData` using deduplicated vertices via NumPy for efficient rendering.
    """

    def __init__(self, project_folder, angles, scene_data, reflect):
        """
        Initializes the rendering worker for the FlapKine application.

        Prepares the QRunnable-based background task responsible for high-performance rendering
        and video encoding. Loads essential project parameters such as output folder, rendering
        angles, scene data generator, and mesh reflection configuration. Also sets up the
        custom signal handler to communicate rendering progress and completion with the main GUI.

        Components Initialized:
            - `project_folder` : Project root directory where output files (videos, STLs) are stored.
            - `angles` : List of frame angles to iterate through for rendering.
            - `scene_data` : Provides STL mesh generation for each frame.
            - `reflect` : Tuple indicating per-axis mesh reflection before rendering or export.
            - `signals` : `RenderSignals` instance used to emit `progress_signal` and `finished` events.
        """
        super().__init__()
        self.project_folder = project_folder
        self.angles = angles
        self.scene_data = scene_data
        self.reflect = reflect
        self.signals = RenderSignals()

    @pyqtSlot()
    def run(self):
        """
        Executes the background rendering and encoding process.

        This method is invoked when the `Worker` QRunnable is started via a thread pool.
        It performs offscreen rendering of a 3D scene using VTK, generates STL meshes
        frame-by-frame, and directly encodes each rendered frame into an `.mp4` video using OpenCV.
        It also optionally exports STL files and emits real-time progress updates through
        `RenderSignals`.

        Workflow:
            1. Loads rendering configuration from `config.json` in the project folder.
            2. Prepares output directories for STL and video data.
            3. Initializes the VTK rendering pipeline (renderer, camera, lighting, actor).
            4. Iterates over the list of specified angles to:
                - Generate STL mesh using `scene_data`
                - Optionally save STL to disk
                - Convert mesh to `vtkPolyData`
                - Render the scene offscreen and capture frame
                - Convert VTK image to NumPy array and write to video
            5. Emits `progress_signal` every two frames (or final frame).
            6. Releases the OpenCV writer and emits `finished` signal on completion.

        Signals Emitted:
            - `progress_signal (float)`: Percentage of frames rendered.
            - `finished`: Emitted once rendering and encoding are complete.
        """
        config_path = os.path.join(self.project_folder, 'config.json')
        with open(config_path) as f:
            config = json.load(f)

        if config["STL"]:
            os.makedirs(os.path.join(self.project_folder, 'data/stl'), exist_ok=True)

        os.makedirs(os.path.join(self.project_folder, 'data/videos'), exist_ok=True)
        project_name = os.path.basename(self.project_folder)
        video_path = os.path.join(self.project_folder, f"data/videos/{project_name}.mp4")

        width = config['VideoRender']['resolution_x']
        height = config['VideoRender']['resolution_y']
        fps = 20

        # OpenCV video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))

        # VTK setup
        renderer = vtkRenderer()
        render_window = vtkRenderWindow()
        render_window.SetOffScreenRendering(True)
        render_window.AddRenderer(renderer)
        render_window.SetMultiSamples(0)
        render_window.SetSize(width, height)

        cam = vtkCamera()
        cam.SetPosition(*(-1 * np.array(config['Camera']['location'])))
        cam.SetFocalPoint(*(-1 * np.array(config['Camera']['focal'])))
        cam.SetViewUp(*(-1 * np.array(config['Camera']['up'])))
        cam.SetParallelProjection(False)

        renderer.SetActiveCamera(None)
        renderer.SetActiveCamera(cam)
        cam.Modified()
        renderer.ResetCameraClippingRange()

        light = vtkLight()
        light.SetLightTypeToSceneLight()
        light.SetPosition(*(-1 * np.array(config['Light']['location'])))
        light.SetIntensity(config['Light']['energy'])
        renderer.AddLight(light)

        mapper = vtkPolyDataMapper()
        actor = vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(vtkNamedColors().GetColor3d("RoyalBlue"))
        actor.GetProperty().SetFrontfaceCulling(False)
        actor.GetProperty().SetBackfaceCulling(False)

        renderer.AddActor(actor)
        renderer.SetBackground(0.95, 0.95, 0.95)

        window_to_image = vtkWindowToImageFilter()
        window_to_image.SetInput(render_window)
        window_to_image.ReadFrontBufferOff()

        total = len(self.angles)
        for i, angle in enumerate(self.angles):

            stl_mesh = self.scene_data.save_stl(i, reflect_xy = self.reflect[0], reflect_yz = self.reflect[1], reflect_xz = self.reflect[2])

            if config["STL"]:
                stl_mesh.save(os.path.join(self.project_folder, f"data/stl/stl_mesh_{i}.stl"))

            # Convert mesh to VTK polydata
            poly_data = self.stl_mesh_to_vtk(stl_mesh)
            mapper.SetInputData(poly_data)

            render_window.Render()
            window_to_image.Modified()
            window_to_image.Update()

            vtk_image = window_to_image.GetOutput()
            width, height, _ = vtk_image.GetDimensions()

            vtk_array = vtk_image.GetPointData().GetScalars()
            np_image = vtk_to_numpy(vtk_array).reshape((height, width, -1))
            np_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)

            out.write(np_image)

            if (i + 1) % 2 == 0 or i == total - 1:
                self.signals.progress_signal.emit((i + 1) / total * 100)

        out.release()
        self.signals.finished.emit()

    def stl_mesh_to_vtk(self, stl_mesh):
        poly_data = vtkPolyData()
        points = vtkPoints()
        cells = vtkCellArray()

        point_id = 0
        for triangle in stl_mesh.vectors:
            ids = []
            for vertex in triangle:
                points.InsertNextPoint(vertex[0], vertex[1], vertex[2])
                ids.append(point_id)
                point_id += 1
            vtk_triangle = vtkTriangle()
            for i in range(3):
                vtk_triangle.GetPointIds().SetId(i, ids[i])
            cells.InsertNextCell(vtk_triangle)

        poly_data.SetPoints(points)
        poly_data.SetPolys(cells)
        return poly_data