import os
import json
import numpy as np

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel, QPushButton
)

from vtk import (
    vtkPolyDataMapper, vtkActor, vtkAxesActor, vtkRenderer,
    vtkTransform, vtkCellArray, vtkTriangle, vtkPoints, vtkPolyData, vtkMatrix4x4,
    vtkTransformPolyDataFilter
)
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from qtawesome import icon

from src.core.transforms.vtk_transform import vtk_rotation


class Visualizer3DWidget(QWidget):
    """
    Visualizer3DWidget Class
    ========================

    A PyQt5-based widget for interactive 3D visualization and playback of
    flapping-wing Micro Aerial Vehicle (MAV) simulation data. This widget
    serves as a real-time visual tool to inspect spatial orientation,
    transformations, and local/global coordinate systems derived from simulation frames.

    The widget includes:
    - A VTK-based 3D scene viewer.
    - Playback controls (play, pause, next frame).
    - A slider to scrub through simulation frames.
    - Global and per-object body axes visualizations.

    Attributes
    ----------
    scene_data : object
        Parsed simulation object containing geometry, frame orientations,
        and object transformations.

    project_folder : str
        Path to the project directory containing configuration and assets.

    angles : List[float]
        List of orientation angles for animation frames.

    reflect : List[bool]
        Boolean flags indicating whether XY, YZ, or XZ axis reflections are active,
        derived from the project's config file.

    actor : vtk.vtkActor
        The VTK actor representing the primary STL mesh of the scene.

    body_axes : List[vtk.vtkAxesActor]
        List of per-object axes actors, visualizing local coordinate systems.

    vtkWidget : QVTKRenderWindowInteractor
        VTK widget integrated into the PyQt5 layout for rendering the 3D scene.

    ren : vtk.vtkRenderer
        Renderer instance that manages visual elements and camera.

    iren : vtkRenderWindowInteractor
        Interactor for handling user input and real-time navigation.

    slider : QSlider
        Slider for frame-by-frame navigation through animation data.

    slider_label : QLabel
        Label displaying the currently selected frame index.

    play_button : QPushButton
        Button to toggle playback of the simulation.

    next_button : QPushButton
        Button to jump to the next frame in the sequence.

    playing : bool
        Internal flag indicating whether playback is active.

    Methods
    -------
    __init__(scene_data, project_folder, angles, parent=None)
        Initialize the widget and prepare UI and visualization pipeline.

    init_ui()
        Set up the UI layout, controls, slider, buttons, and VTK window.

    setup_visualization()
        Load configuration, generate VTK mesh and actors, initialize the scene.

    create_axes_actor(poly_data)
        Create a global coordinate axes actor scaled to mesh bounds.

    create_body_axes(sprite)
        Generate a local coordinate system actor for a given object.

    toggle_play()
        Toggle animation playback state and update play button icon.

    play_frames()
        Play the animation by advancing the frame slider on a timer.

    on_slider_value_changed()
        Update the scene actors according to the selected frame.

    stl_mesh_to_vtk(stl_mesh)
        Convert an STL mesh from numpy-stl format to VTK polydata.
    """

    def __init__(self, scene_data, project_folder, angles, parent=None):
        """
        Initialize the 3D visualizer widget.

        Sets up the internal state and initializes the user interface
        for playback and visualization of the flapping wing MAV simulation.

        Parameters
        ----------
        scene_data : object
            Parsed simulation object containing geometry, frame orientations,
            and object transformations.
        project_folder : str
            Path to the project directory containing configuration and assets.
        angles : list
            List of orientation angles for animation frames.
        parent : QWidget, optional
            Optional parent widget for GUI nesting (default is None).
        """
        super().__init__(parent)

        self.scene_data = scene_data
        self.project_folder = project_folder
        self.angles = angles
        self.playing = False

        self.init_ui()

    def init_ui(self):
        """
        Initialize the user interface components of the 3D visualizer widget.

        Sets up the layout, playback controls, VTK rendering window, and
        prepares the visualization pipeline for the flapping MAV simulation.

        UI Components:
        --------------
        - Frame slider with frame label for time-step control.
        - Play/pause button and next-frame button.
        - Embedded VTK render window for 3D scene visualization.

        This method also calls `setup_visualization()` to initialize the rendering pipeline.
        """
        primary_color = self.palette().color(self.foregroundRole()).name()


        layout = QVBoxLayout(self)
        control_layout = QHBoxLayout()

        self.slider_label = QLabel("Frame: 0")
        self.slider_label.setFont(QFont('Arial', 8, QFont.Weight.Bold))
        self.slider_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slider_label.setStyleSheet("color: #333;")

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(self.angles) - 1)
        self.slider.setValue(0)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(max(1, len(self.angles) // 10))
        self.slider.valueChanged.connect(self.on_slider_value_changed)
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: none;
                background: #ddd;
                height: 8px;
                border-radius: 4px;
            }

            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00aaff, stop:1 #005a9e);
                border: 2px solid #005a9e;
                width: 18px;
                height: 18px;
                margin: -7px 0;
                border-radius: 9px;
            }

            QSlider::handle:horizontal:hover {
                background: #005a9e;
            }

            QSlider::sub-page:horizontal {
                background: #00aaff;
                border-radius: 4px;
            }

            QSlider::add-page:horizontal {
                background: #ccc;
                border-radius: 4px;
            }
        """)

        self.play_button = QPushButton()
        self.play_button.setIcon(icon("mdi.play", color=primary_color))
        self.play_button.clicked.connect(self.toggle_play)

        self.next_button = QPushButton()
        self.next_button.setIcon(icon("mdi.skip-next", color=primary_color))
        self.next_button.clicked.connect(lambda: self.slider.setValue(self.slider.value() + 1))

        self.refresh_button = QPushButton()
        self.refresh_button.setIcon(icon("mdi.refresh", color=primary_color))
        self.refresh_button.clicked.connect(self.refresh_fun)

        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.next_button)
        control_layout.addWidget(self.slider)
        control_layout.addWidget(self.slider_label)
        control_layout.addWidget(self.refresh_button)



        self.vtkWidget = QVTKRenderWindowInteractor(self)
        self.ren = vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.vtkWidget.setStyleSheet("background-color: #fafafa; border: 1px solid #bbb; border-radius: 10px;")

        layout.addLayout(control_layout)
        layout.addWidget(self.vtkWidget)

        self.setLayout(layout)

        self.setup_visualization()

    def setup_visualization(self):
        """
        Set up the 3D visualization environment using VTK.

        This method loads the reflection configuration from the project JSON,
        converts the scene's STL mesh to VTK-compatible format, initializes
        the main actor and coordinate axes, and prepares the interactor for rendering.

        Steps performed:
        ----------------
        - Load `config.json` to determine reflection plane settings.
        - Generate and convert the scene mesh using `save_stl()` and `stl_mesh_to_vtk()`.
        - Create and configure the VTK actor with color and opacity.
        - Initialize global coordinate axes and per-object body axes.
        - Add all actors to the renderer and reset the camera.
        - Initialize the VTK interactor for user interaction.

        Raises:
        -------
        FileNotFoundError
            If `config.json` does not exist in the project folder.
        JSONDecodeError
            If the JSON configuration file is improperly formatted.
        """
        with open(os.path.join(self.project_folder, 'config.json')) as f:
            config = json.load(f)

        reflect = [config['Reflect'] == "XY", config['Reflect'] == "YZ", config['Reflect'] == "XZ"]
        self.reflect = reflect

        mesh = self.scene_data.save_stl(-1)
        poly_data = self.stl_mesh_to_vtk(mesh)

        self.slider.setValue(0)
        self.playing = False
        self.play_button.setIcon(icon("mdi.play", color=self.palette().color(self.foregroundRole()).name()))

        mapper = vtkPolyDataMapper()
        mapper.SetInputData(poly_data)

        self.actor = vtkActor()
        self.actor.SetMapper(mapper)
        self.actor.GetProperty().SetColor(0.5, 0.7, 1)
        self.actor.GetProperty().SetOpacity(0.7)

        if any(self.reflect):

            reflected_polydata = self.get_reflected_polydata(poly_data, reflect_xy=self.reflect[0], reflect_yz=self.reflect[1], reflect_xz=self.reflect[2])
            mapper_reflected = vtkPolyDataMapper()
            mapper_reflected.SetInputData(reflected_polydata)

            self.actor_reflected = vtkActor()
            self.actor_reflected.SetMapper(mapper)
            self.actor_reflected.GetProperty().SetColor(0.5, 0.7, 1)
            self.actor_reflected.GetProperty().SetOpacity(0.7)
            self.ren.AddActor(self.actor_reflected)

            self.temp_actor = vtkActor()
            self.temp_actor.SetMapper(mapper_reflected)
            self.temp_actor.GetProperty().SetColor(0.5, 0.7, 1)
            self.temp_actor.GetProperty().SetOpacity(0.7)
            self.ren.AddActor(self.temp_actor)


        self.ren.SetBackground(0.95, 0.95, 0.95)
        self.ren.AddActor(self.actor)
        self.ren.AddActor(self.create_axes_actor(poly_data))

        self.body_axes = []
        for sprite in self.scene_data.objects:
            self.body_axes.append(self.create_body_axes(sprite))

        for axes in self.body_axes:
            self.ren.AddActor(axes)

        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        self.iren.Initialize()

        camera = self.ren.GetActiveCamera()
        camera.SetPosition(*(-1*np.array(config['Camera']['location'])))
        camera.SetFocalPoint(*(-1*np.array(config['Camera']['focal'])))
        camera.SetViewUp(*(-1*np.array(config['Camera']['up'])))
        camera.Modified()
        camera.SetParallelProjection(False)
        self.ren.ResetCameraClippingRange()

    def create_axes_actor(self, poly_data):
        """
        Create and configure a global coordinate axes actor based on the bounding box of the given mesh.

        Parameters
        ----------
        poly_data : vtk.vtkPolyData
            The VTK polydata object representing the mesh from which the bounds are calculated.

        Returns
        -------
        vtk.vtkAxesActor
            The axes actor with scaled dimensions and labeled axes ('X', 'Y', 'Z').

        Notes
        -----
        - The axes size is set to 10% of the maximum bounding box dimension.
        - Axis labels are set and styled with black color for readability.
        - This actor provides a visual reference for global orientation in the 3D scene.
        """
        bounds = poly_data.GetBounds()
        max_length = max(bounds[1]-bounds[0], bounds[3]-bounds[2], bounds[5]-bounds[4])
        axes = vtkAxesActor()
        axes.SetTotalLength(max_length * 0.05, max_length * 0.05, max_length * 0.05)
        axes.SetShaftType(0)
        axes.SetAxisLabels(1)
        axes.SetXAxisLabelText("X")
        axes.SetYAxisLabelText("Y")
        axes.SetZAxisLabelText("Z")
        for caption in [axes.GetXAxisCaptionActor2D(), axes.GetYAxisCaptionActor2D(), axes.GetZAxisCaptionActor2D()]:
            caption.GetCaptionTextProperty().SetColor(0, 0, 0)

        color = (0, 0, 0)   # Light blue
        opacity = 0.7

        shaft_actors = [
            axes.GetXAxisShaftProperty(),
            axes.GetYAxisShaftProperty(),
            axes.GetZAxisShaftProperty()
        ]

        for prop in shaft_actors:
            prop.SetColor(*color)
            prop.SetOpacity(opacity)

        return axes

    def create_body_axes(self, sprite):
        """
        Create a local coordinate axes actor for a given sprite object, oriented and positioned
        based on its frame orientation and origin.

        Parameters
        ----------
        sprite : object
            A sprite object from the scene containing frame orientation and origin attributes.

        Returns
        -------
        vtk.vtkAxesActor
            A VTK axes actor positioned and rotated according to the sprite's local frame.

        Notes
        -----
        - The axis labels are set to 'A', 'B', and 'C' to represent the object's local coordinate system.
        - The axis size is scaled relative to the mesh bounds for proportional rendering.
        - Orientation is applied using Euler angles (in radians), converted to degrees for VTK.
        - This actor visually represents the local transformation of each object in the scene.
    """
        max_length = max(self.actor.GetBounds()[1::2]) * 0.1
        axes = vtkAxesActor()
        axes.SetTotalLength(max_length, max_length, max_length)
        axes.SetShaftType(0)
        axes.SetAxisLabels(1)
        axes.SetXAxisLabelText("A")
        axes.SetYAxisLabelText("B")
        axes.SetZAxisLabelText("C")
        for caption in [axes.GetXAxisCaptionActor2D(), axes.GetYAxisCaptionActor2D(), axes.GetZAxisCaptionActor2D()]:
            caption.GetCaptionTextProperty().SetColor(0, 0, 0)

        angles = sprite.frame_orientation
        position = sprite.frame_origin

        transform = vtkTransform()
        transform.Translate(position)
        transform.RotateX(np.degrees(angles[0]))
        transform.RotateY(np.degrees(angles[1]))
        transform.RotateZ(np.degrees(angles[2]))
        axes.SetUserTransform(transform)

        return axes

    def toggle_play(self):
        """
        Toggle the playback state of the animation and update the play button icon accordingly.

        This method switches between playing and paused states. When toggled to play,
        it initiates the frame-by-frame animation using the `play_frames()` method.

        Side Effects
        ------------
        - Updates `self.playing` to reflect the current playback state.
        - Changes the play button icon to either a play or pause symbol depending on the state.
        - Starts frame playback if toggled to playing.

        Notes
        -----
        - The icon is styled using the widget's foreground color for visual consistency.
        """
        primary_color = self.palette().color(self.foregroundRole()).name()
        self.playing = not self.playing
        self.play_button.setIcon(icon("mdi.pause" if self.playing else "mdi.play", color=primary_color))
        if self.playing:
            self.play_frames()

    def play_frames(self):
        """
        Advance the animation by one frame and schedule the next frame if playing.

        This method increments the frame slider to the next value, wraps around at the end,
        and updates the visualization accordingly. If playback is active, it recursively
        schedules the next frame update using a `QTimer`.

        Notes
        -----
        - Frame updates occur every 50 milliseconds.
        - The method stops updating if `self.playing` is set to False.
        """
        if self.playing:
            next_frame = (self.slider.value() + 1) % len(self.angles)
            self.slider.setValue(next_frame)
            self.on_slider_value_changed()
            QTimer.singleShot(50, self.play_frames)

    def on_slider_value_changed(self):
        """
        Update the visualization based on the current slider frame index.

        This method retrieves the frame-specific orientation and position data for each object,
        computes their transformation matrices, and updates the corresponding VTK actors accordingly.
        The slider label is also updated to reflect the current frame index.

        Notes
        -----
        - Applies both translation and rotation to each actor and its associated body axes.
        - Updates the main mesh actor (`self.actor`) transformation based on the last processed object.
        - Triggers a re-render of the VTK render window.
        """

        if hasattr(self, 'temp_actor'):
            self.ren.RemoveActor(self.temp_actor)
            del self.temp_actor

        index = self.slider.value()
        self.slider_label.setText(f"Frame: {index}")

        for i, sprite in enumerate(self.scene_data.objects):
            angle = sprite.angles[index]

            position = sprite.positions[index]
            axes_pos = sprite.frame_origin
            axes_pos = np.array(axes_pos)
            position = np.array(position)

            actor_trans = vtkTransform()
            axes_trans = vtkTransform()

            actor_trans.Translate(position)
            axes_trans.Translate(position + axes_pos)

            if hasattr(sprite.object_.rotation_transform, 'type'):
                rot_trans = vtk_rotation(sprite.object_.rotation_transform.type, angle)
                actor_trans.Concatenate(rot_trans)
                axes_trans.Concatenate(rot_trans)

            self.body_axes[i].SetUserTransform(axes_trans)

        self.actor.SetUserTransform(actor_trans)

        if hasattr(self, 'actor_reflected') and self.actor_reflected:
            reflect_trans = self.get_reflection_transform(
                reflect_xy=self.reflect[0],
                reflect_yz=self.reflect[1],
                reflect_xz=self.reflect[2]
            )

            reflected_actor_trans = vtkTransform()

            reflected_actor_trans.Concatenate(reflect_trans)
            reflected_actor_trans.Concatenate(actor_trans)


            self.actor_reflected.SetUserTransform(reflected_actor_trans)

        self.vtkWidget.GetRenderWindow().Render()

    def get_reflection_transform(self, reflect_xy=False, reflect_yz=False, reflect_xz=False):
        """
        Create a vtkTransform that performs reflection across specified planes.
        """
        reflection_matrix = vtkMatrix4x4()
        reflection_matrix.Identity()

        if reflect_xy:
            reflection_matrix.SetElement(2, 2, -1)  # Reflect Z
        elif reflect_yz:
            reflection_matrix.SetElement(0, 0, -1)  # Reflect X
        elif reflect_xz:
            reflection_matrix.SetElement(1, 1, -1)  # Reflect Y

        transform = vtkTransform()
        transform.SetMatrix(reflection_matrix)
        return transform


    def get_reflected_polydata(self, poly_data, reflect_xy=False, reflect_yz=False, reflect_xz=False):
        """
        Returns a reflected copy of the input vtkPolyData based on specified reflection plane.

        Parameters
        ----------
        poly_data : vtk.vtkPolyData
            The original mesh to reflect.

        reflect_xy : bool
            Reflect across the XY plane (invert Z).

        reflect_yz : bool
            Reflect across the YZ plane (invert X).

        reflect_xz : bool
            Reflect across the XZ plane (invert Y).

        Returns
        -------
        reflected_poly : vtk.vtkPolyData or None
            The reflected mesh, or None if no reflection flag is set.
        """
        if not (reflect_xy or reflect_yz or reflect_xz):
            return None

        transform = vtkTransform()
        scale_x, scale_y, scale_z = 1, 1, 1

        if reflect_xy:
            scale_z = -1
        elif reflect_yz:
            scale_x = -1
        elif reflect_xz:
            scale_y = -1

        transform.Scale(scale_x, scale_y, scale_z)

        filter = vtkTransformPolyDataFilter()
        filter.SetInputData(poly_data)
        filter.SetTransform(transform)
        filter.Update()

        return filter.GetOutput()

    def stl_mesh_to_vtk(self, stl_mesh):
        """
        Convert an STL mesh (numpy-stl) into a VTK `vtkPolyData` object.

        Parameters
        ----------
        stl_mesh : stl.mesh.Mesh
            The mesh object from the numpy-stl library containing triangle vectors.

        Returns
        -------
        vtk.vtkPolyData
            The converted mesh as a VTK polydata object with points and triangle cells.

        Notes
        -----
        - Deduplicates vertices before inserting them into the VTK point list.
        - Ensures mesh connectivity by using indexed triangles.
        """
        poly_data = vtkPolyData()
        points = vtkPoints()
        cells = vtkCellArray()

        # Extract unique vertices and create a mapping
        unique_vertices, indices = np.unique(stl_mesh.vectors.reshape(-1, 3), axis=0, return_inverse=True)

        # Insert vertices into vtkPoints
        for vertex in unique_vertices:
            points.InsertNextPoint(vertex[0], vertex[1], vertex[2])

        # Insert faces into vtkCellArray
        for i in range(0, len(indices), 3):
            triangle = vtkTriangle()
            for j in range(3):
                triangle.GetPointIds().SetId(j, indices[i + j])
            cells.InsertNextCell(triangle)

        # Assign points and cells to polydata
        poly_data.SetPoints(points)
        poly_data.SetPolys(cells)
        return poly_data

    def refresh_fun(self):
        """
        Refresh the visualization by reloading the config file and updating the reflect options.

        This method is called when the refresh button is clicked. It reinitializes the
        visualization pipeline, including the mesh and axes actors, based on the current
        """

        for actor in self.ren.GetActors():
            self.ren.RemoveActor(actor)

        for axes in self.body_axes:
            self.ren.RemoveActor(axes)

        self.setup_visualization()