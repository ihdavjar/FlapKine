import numpy as np

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QSplitter

from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtk import (
    vtkActor, vtkAxesActor, vtkCellArray, vtkCellPicker, vtkGlyph3D,
    vtkInteractorStyleImage, vtkPoints, vtkPolyData, vtkPolyDataMapper,
    vtkRenderer, vtkSphereSource, vtkTriangle
)

class PointScatterWidget(QWidget):
    """
    PointScatterWidget Class
    =========================

    A composite PyQt5 widget that enables interactive point selection on a flattened STL mesh
    and visualizes the 3D transformed trajectory of the selected point across animation frames.

    The interface is vertically split into two VTK-based views:
    - A 2D flattened STL view for selecting points.
    - A 3D scatter plot for observing the point’s transformation over time using scene data.

    This widget is designed to plug into the main FlapKine interface for analyzing how specific
    points evolve under dynamic transformations like translation, rotation, and flexibility.

    Attributes
    ----------
    scene_data : SceneData
        The scene object containing STL mesh data and time-varying transformation functions
        (translation, rotation, flexibility) used to compute point trajectories.

    splitter : QSplitter
        Vertical splitter separating the selection view (top) from the 3D scatter view (bottom).

    toprightgroup : QGroupBox
        Container for the top VTK viewport showing the flattened STL mesh for point selection.

    bottomrightgroup : QGroupBox
        Container for the bottom VTK viewport displaying the 3D scatter plot of transformed points.

    vtk_widget_1 : QVTKRenderWindowInteractor
        VTK widget for displaying and interacting with the flattened STL mesh.

    vtk_widget_2 : QVTKRenderWindowInteractor
        VTK widget for displaying the resulting 3D point trajectory visualization.

    ren_1 : vtkRenderer
        VTK renderer for the flattened STL mesh view.

    ren_2 : vtkRenderer
        VTK renderer for the 3D scatter plot view.

    iren_1 : vtkRenderWindowInteractor
        Interactor for handling mouse events in the selection viewport.

    iren_2 : vtkRenderWindowInteractor
        Interactor for the 3D scatter plot view.

    interactor_style_1 : vtkInteractorStyleImage
        Interactor style configured for precise point picking on the STL mesh.

    last_marker_actor : vtkActor or None
        Actor representing the most recently selected point as a sphere.

    last_outline_actor : vtkActor or None
        Outline actor surrounding the last marker for visual emphasis.

    scatter_actor : vtkActor or None
        Actor representing the full 3D trajectory of the selected point across animation frames.

    Methods
    -------
    __init__(scene_data, parent=None)
        Initializes the widget with the scene data and invokes the UI construction.

    init_ui()
        Constructs the layout, initializes the VTK viewports, and renders the STL mesh.

    on_click(obj, event)
        Handles mouse click events on the STL mesh and computes the 3D point trajectory.

    add_marker_to_vtk(position)
        Places a visual marker and outline at the selected point in the 2D STL view.

    create_3d_scatter_plot(initial_point)
        Computes and renders the 3D trajectory of the selected point using transformation functions.

    stl_mesh_to_vtk(stl_mesh)
        Converts a NumPy-based STL mesh into a VTK PolyData object for rendering.
    """


    def __init__(self, scene_data, parent=None):
        """
        Initializes the PointScatterWidget class.

        Sets up the internal state for the interactive point selection and trajectory visualization
        tool within the FlapKine GUI. Stores the provided scene data and invokes the UI construction method
        to set up the split layout and VTK visualization panels.

        Parameters
        ----------
        scene_data : SceneData
            Deserialized scene data containing the STL mesh and transformation functions
            (translation, rotation, flexibility) across animation frames.

        parent : QWidget, optional
            The parent widget to which this scatter widget belongs. Default is None.

        Components Initialized
        ----------------------
        - Internal attributes for rendering actors (marker, outline, scatter).
        - Calls `init_ui()` to build the VTK-enabled point selection and visualization views.
        """
        super().__init__(parent)
        self.scene_data = scene_data

        self.last_marker_actor = None
        self.last_outline_actor = None
        self.scatter_actor = None

        self.init_ui()


    def init_ui(self):
        """
        Builds the UI layout and initializes VTK visualization panels.

        This method constructs the vertical layout of the PointScatterWidget, including two main
        interactive viewports arranged using a QSplitter. The top panel displays a flattened 2D
        projection of the STL mesh for point selection, while the bottom panel is configured to render
        the 3D trajectory scatter plot corresponding to the selected point. The method also sets up the
        required VTK renderers, interactor styles, and loads the STL mesh from the provided scene data.

        UI Components
        -------------
        - QSplitter (Vertical):
            - Top GroupBox ("Selected Point"):
                - Contains QVTKRenderWindowInteractor for showing 2D STL projection
                - Handles mouse click events for point picking
            - Bottom GroupBox ("3D Scatter Plot"):
                - Contains QVTKRenderWindowInteractor for rendering 3D trajectories

        VTK Setup
        ---------
        - Renderer for top view (`ren_1`) with background color set
        - Interactor style set to `vtkInteractorStyleImage` for 2D point interaction
        - STL mesh converted via `stl_mesh_to_vtk()` and flattened along Z-axis
        - Loaded mesh displayed using `vtkPolyDataMapper` and `vtkActor`
        - Renderer for bottom view (`ren_2`) initialized for dynamic scatter plotting

        Notes
        -----
        - The left mouse button is connected to `on_click()` to allow user-driven point selection
        - The bottom view remains empty until a point is selected and a trajectory is computed
        - Stretch factors control the vertical space allocated to each panel (top: 3, bottom: 2)
        """

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.splitter = QSplitter(Qt.Vertical)
        layout.addWidget(self.splitter)

        # --- Top Right Group: Point Selection View ---
        self.toprightgroup = QGroupBox("Point Selector")
        self.toprightgroup.setFont(QFont('Times', 9))
        topright_layout = QVBoxLayout()
        self.vtk_widget_1 = QVTKRenderWindowInteractor(self)
        topright_layout.addWidget(self.vtk_widget_1)
        self.toprightgroup.setLayout(topright_layout)

        self.ren_1 = vtkRenderer()
        self.ren_1.SetBackground(0.95, 0.95, 0.95)
        self.vtk_widget_1.GetRenderWindow().AddRenderer(self.ren_1)
        self.iren_1 = self.vtk_widget_1.GetRenderWindow().GetInteractor()
        self.interactor_style_1 = vtkInteractorStyleImage()
        self.iren_1.SetInteractorStyle(self.interactor_style_1)
        self.iren_1.AddObserver("LeftButtonPressEvent", self.on_click)

        self.splitter.addWidget(self.toprightgroup)

        # Load and display flattened STL
        mesh = self.scene_data.objects[0].object_.stl_mesh
        poly_data = self.stl_mesh_to_vtk(mesh)

        points = np.array([poly_data.GetPoint(i) for i in range(poly_data.GetNumberOfPoints())])

        min_coords = points.min(axis=0)
        max_coords = points.max(axis=0)
        extents = max_coords - min_coords

        flatten_axis = np.argmin(extents)
        project_axes = [i for i in range(3) if i != flatten_axis]

        points[:, flatten_axis] = points[:, project_axes[1]]
        points[:, 2] = 0.0

        new_points = vtkPoints()
        for p in points:
            new_points.InsertNextPoint(p)
        poly_data.SetPoints(new_points)

        mapper = vtkPolyDataMapper()
        mapper.SetInputData(poly_data)
        self.actor_1 = vtkActor()
        self.actor_1.SetMapper(mapper)
        self.actor_1.GetProperty().SetColor(0.5, 0.7, 1)

        self.ren_1.AddActor(self.actor_1)
        self.ren_1.ResetCamera()
        self.vtk_widget_1.GetRenderWindow().Render()

        # --- Bottom Right Group: Scatter Plot View ---
        self.bottomrightgroup = QGroupBox("3D Scatter Plot")
        self.bottomrightgroup.setFont(QFont('Times', 9))
        bottomright_layout = QVBoxLayout()
        self.vtk_widget_2 = QVTKRenderWindowInteractor(self)
        bottomright_layout.addWidget(self.vtk_widget_2)
        self.bottomrightgroup.setLayout(bottomright_layout)

        self.ren_2 = vtkRenderer()
        self.ren_2.SetBackground(0.95, 0.95, 0.95)
        self.vtk_widget_2.GetRenderWindow().AddRenderer(self.ren_2)
        self.iren_2 = self.vtk_widget_2.GetRenderWindow().GetInteractor()

        self.splitter.addWidget(self.bottomrightgroup)

        # Set initial space each panel takes
        self.splitter.setStretchFactor(0, 3)  # Top
        self.splitter.setStretchFactor(1, 2)  # Bottom

    def on_click(self, obj, event):
        """
        Handles left mouse button click event on the 2D STL view.

        This method is triggered when the user clicks on the top VTK viewport displaying
        the 2D projection of the STL mesh. It uses `vtkCellPicker` to convert the screen
        click coordinates into a 3D position on the mesh surface. The selected point is
        then used to both visualize a trajectory scatter plot in 3D space and mark the
        clicked location on the mesh.

        Parameters
        ----------
        obj : vtkObject
            The VTK interactor object that captured the click event.

        event : str
            A string describing the type of VTK event (e.g., "LeftButtonPressEvent").

        Processing Flow
        ---------------
        - Extract screen-space click coordinates from the VTK interactor
        - Use `vtkCellPicker` with a tolerance to map the 2D click to a 3D point
        - Retrieve the picked 3D world coordinates
        - Call `create_3d_scatter_plot(picked_pos)` to display trajectories
        - Call `add_marker_to_vtk(picked_pos)` to highlight the selected point

        Notes
        -----
        - Picker tolerance is set to 0.005 for precision in point selection
        - This method assumes that a valid STL mesh is already rendered in `ren_1`
        """
        click_pos = self.iren_1.GetEventPosition()
        picker = vtkCellPicker()
        picker.SetTolerance(0.005)
        picker.Pick(click_pos[0], click_pos[1], 0, self.ren_1)
        picked_pos = picker.GetPickPosition()

        self.create_3d_scatter_plot(picked_pos)
        self.add_marker_to_vtk(picked_pos)

    def add_marker_to_vtk(self, position):
        """
        Adds a visual marker to the 2D STL view at the selected 3D position.

        This method renders a red 3D sphere and a semi-transparent white outline
        sphere at the specified `position` to visually indicate a user-selected
        point on the mesh. If a previous marker exists, it is removed before
        placing the new one. This enhances visual feedback for user interactions.

        Parameters
        ----------
        position : tuple[float, float, float]
            A 3D coordinate (x, y, z) representing the location where the marker
            should be placed on the STL mesh.

        Visual Elements
        ---------------
        - Main Marker:
            - Shape: Red sphere
            - Radius: 0.08 units
            - Appearance: Glossy with specular highlights

        - Outline:
            - Shape: Larger semi-transparent white sphere
            - Radius: 0.1 units
            - Appearance: Faint glow effect to increase visibility

        Behavior
        --------
        - Replaces any previously placed marker by removing old actors.
        - Adds both new actors to the renderer `ren_1`.
        - Refreshes the render window for immediate visual update.

        Notes
        -----
        - Marker is placed in the same renderer (`ren_1`) used for the STL mesh.
        - Used in conjunction with `on_click()` for interactive point selection.
        """
        if self.last_marker_actor:
            self.ren_1.RemoveActor(self.last_marker_actor)
        if self.last_outline_actor:
            self.ren_1.RemoveActor(self.last_outline_actor)

        sphere = vtkSphereSource()
        sphere.SetCenter(position)
        sphere.SetRadius(0.08)
        sphere.SetPhiResolution(30)
        sphere.SetThetaResolution(30)

        sphere_mapper = vtkPolyDataMapper()
        sphere_mapper.SetInputConnection(sphere.GetOutputPort())

        sphere_actor = vtkActor()
        sphere_actor.SetMapper(sphere_mapper)
        sphere_actor.GetProperty().SetColor(1.0, 0.2, 0.2)
        sphere_actor.GetProperty().SetAmbient(0.3)
        sphere_actor.GetProperty().SetSpecular(1.0)
        sphere_actor.GetProperty().SetSpecularPower(50)

        outline_sphere = vtkSphereSource()
        outline_sphere.SetCenter(position)
        outline_sphere.SetRadius(0.1)

        outline_mapper = vtkPolyDataMapper()
        outline_mapper.SetInputConnection(outline_sphere.GetOutputPort())

        outline_actor = vtkActor()
        outline_actor.SetMapper(outline_mapper)
        outline_actor.GetProperty().SetColor(1.0, 1.0, 1.0)
        outline_actor.GetProperty().SetOpacity(0.5)

        self.last_marker_actor = sphere_actor
        self.last_outline_actor = outline_actor

        self.ren_1.AddActor(outline_actor)
        self.ren_1.AddActor(sphere_actor)
        self.vtk_widget_1.GetRenderWindow().Render()

    def create_3d_scatter_plot(self, initial_point):
        """
        Generates and renders a 3D scatter plot of a selected point's trajectory over time.

        This method computes and visualizes the dynamic 3D trajectory of a selected point from
        its 2D projection using the object's transformation pipeline: flexibility, rotation, and
        translation. It draws the resulting points as blue spheres and overlays 3D axes for
        spatial reference.

        Parameters
        ----------
        initial_point : tuple[float, float, float]
            The initial 3D coordinates (flattened on the Z-axis) selected from the STL mesh.

        Transformation Pipeline
        -----------------------
        - flexibility_transform: Deforms the selected point based on time step.
        - rotation_transform: Rotates the point using the current orientation angles.
        - translation_transform: Moves the point to the correct world-space position.

        Visualization Details
        ---------------------
        - Each transformed point is rendered as a blue sphere.
        - All points form a dynamic scatter plot indicating the point's temporal evolution.
        - A 3D axes actor is added to aid with orientation:
            - X-axis: Red
            - Y-axis: Green
            - Z-axis: Blue

        Behavior
        --------
        - Removes any existing scatter plot actor before drawing the new one.
        - Adds the generated actor and axes to the secondary VTK renderer (`ren_2`).
        - Resets and updates the camera to ensure proper view of the rendered plot.

        Notes
        -----
        - Intended to be triggered after a point selection in the top STL view.
        - Integrates tightly with transformation data embedded in the scene structure.
        """
        if self.scatter_actor:
            self.ren_2.RemoveActor(self.scatter_actor)

        initial_point = np.array(initial_point).reshape(1, 3)

        translation = self.scene_data.objects[0].object_.translation_transform
        rotation = self.scene_data.objects[0].object_.rotation_transform
        flexibility = self.scene_data.objects[0].object_.flexibility_transform
        positions = self.scene_data.objects[0].positions
        angles = self.scene_data.objects[0].angles

        new_points = []
        for t in range(len(angles)):
            p = flexibility(initial_point, t)
            p = rotation(p, angles[t])
            p = translation(p, positions[t])
            if p is not None:
                new_points.append(p)

        vtk_points = vtkPoints()
        for point in new_points:
            vtk_points.InsertNextPoint(point[0])

        polydata = vtkPolyData()
        polydata.SetPoints(vtk_points)

        sphere_source = vtkSphereSource()
        sphere_source.SetRadius(0.1)
        sphere_source.SetPhiResolution(20)
        sphere_source.SetThetaResolution(20)

        glyph = vtkGlyph3D()
        glyph.SetInputData(polydata)
        glyph.SetSourceConnection(sphere_source.GetOutputPort())
        glyph.SetScaleModeToDataScalingOff()

        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(glyph.GetOutputPort())

        self.scatter_actor = vtkActor()
        self.scatter_actor.SetMapper(mapper)
        self.scatter_actor.GetProperty().SetColor(0.0, 0.0, 1.0)

        self.ren_2.AddActor(self.scatter_actor)

        axes = vtkAxesActor()
        axes.SetTotalLength(2.0, 2.0, 2.0)
        axes.GetXAxisCaptionActor2D().GetTextActor().GetTextProperty().SetColor(1, 0, 0)
        axes.GetYAxisCaptionActor2D().GetTextActor().GetTextProperty().SetColor(0, 1, 0)
        axes.GetZAxisCaptionActor2D().GetTextActor().GetTextProperty().SetColor(0, 0, 1)

        self.ren_2.AddActor(axes)
        self.ren_2.ResetCamera()
        self.vtk_widget_2.GetRenderWindow().Render()

    def stl_mesh_to_vtk(self, stl_mesh):
        """
        Converts an STL mesh into a VTK-compatible `vtkPolyData` object.

        This method transforms a NumPy-based STL mesh, typically from `numpy-stl`, into
        VTK’s `vtkPolyData` format. It ensures unique vertex mapping and constructs triangular
        cell connectivity for accurate 3D rendering within the VTK pipeline.

        Parameters
        ----------
        stl_mesh : stl.mesh.Mesh
            The STL mesh object containing 3D geometry as triangle vectors, usually loaded using
            the `numpy-stl` library (`stl.mesh.Mesh.from_file()`).

        Returns
        -------
        vtk.vtkPolyData
            A `vtkPolyData` object representing the same geometry, with deduplicated vertices and
            properly constructed triangle cells suitable for VTK visualization.

        Process
        -------
        - Deduplicates all vertices in the STL using `np.unique` to ensure compact geometry.
        - Reconstructs triangle connectivity using the deduplicated vertex indices.
        - Stores all vertex and triangle data in a new `vtkPolyData` object.

        Notes
        -----
        - Ensures VTK-friendly format for further processing such as rendering or transformation.
        - Especially useful when integrating STL models into PyQt + VTK GUI applications.
        """
        poly_data = vtkPolyData()
        points = vtkPoints()
        cells = vtkCellArray()

        unique_vertices, indices = np.unique(stl_mesh.vectors.reshape(-1, 3), axis=0, return_inverse=True)

        for vertex in unique_vertices:
            points.InsertNextPoint(vertex[0], vertex[1], vertex[2])

        for i in range(0, len(indices), 3):
            triangle = vtkTriangle()
            for j in range(3):
                triangle.GetPointIds().SetId(j, indices[i + j])
            cells.InsertNextCell(triangle)

        poly_data.SetPoints(points)
        poly_data.SetPolys(cells)
        return poly_data
