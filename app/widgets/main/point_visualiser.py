from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QSplitter
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import numpy as np

class PointScatterWidget(QWidget):
    """
    A composite widget that displays:
    1. A VTK viewport for selecting points on a flattened STL mesh.
    2. A VTK-based 3D scatter plot showing transformed points.
    The views are split vertically using a QSplitter.
    """

    def __init__(self, scene_data, parent=None):
        super().__init__(parent)
        self.scene_data = scene_data

        self.last_marker_actor = None
        self.last_outline_actor = None
        self.scatter_actor = None

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create a vertical splitter
        self.splitter = QSplitter(Qt.Vertical)
        layout.addWidget(self.splitter)

        # --- Top Right Group: Point Selection View ---
        self.toprightgroup = QGroupBox("Selected Point")
        self.toprightgroup.setFont(QFont('Times', 9))
        topright_layout = QVBoxLayout()
        self.vtk_widget_1 = QVTKRenderWindowInteractor(self)
        topright_layout.addWidget(self.vtk_widget_1)
        self.toprightgroup.setLayout(topright_layout)

        self.ren_1 = vtk.vtkRenderer()
        self.ren_1.SetBackground(0.95, 0.95, 0.95)
        self.vtk_widget_1.GetRenderWindow().AddRenderer(self.ren_1)
        self.iren_1 = self.vtk_widget_1.GetRenderWindow().GetInteractor()
        self.interactor_style_1 = vtk.vtkInteractorStyleImage()
        self.iren_1.SetInteractorStyle(self.interactor_style_1)
        self.iren_1.AddObserver("LeftButtonPressEvent", self.on_click)

        self.splitter.addWidget(self.toprightgroup)

        # Load and display flattened STL
        mesh = self.scene_data.objects[0].object_.stl_mesh
        poly_data = self.stl_mesh_to_vtk(mesh)
        points = np.array([poly_data.GetPoint(i) for i in range(poly_data.GetNumberOfPoints())])
        points[:, 2] = 0  # Flatten Z-axis

        new_points = vtk.vtkPoints()
        for p in points:
            new_points.InsertNextPoint(p)
        poly_data.SetPoints(new_points)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly_data)
        self.actor_1 = vtk.vtkActor()
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

        self.ren_2 = vtk.vtkRenderer()
        self.ren_2.SetBackground(0.95, 0.95, 0.95)
        self.vtk_widget_2.GetRenderWindow().AddRenderer(self.ren_2)
        self.iren_2 = self.vtk_widget_2.GetRenderWindow().GetInteractor()

        self.splitter.addWidget(self.bottomrightgroup)

        # Optional: Adjust initial space each panel takes
        self.splitter.setStretchFactor(0, 3)  # Top
        self.splitter.setStretchFactor(1, 2)  # Bottom

    def on_click(self, obj, event):
        click_pos = self.iren_1.GetEventPosition()
        picker = vtk.vtkCellPicker()
        picker.SetTolerance(0.005)
        picker.Pick(click_pos[0], click_pos[1], 0, self.ren_1)
        picked_pos = picker.GetPickPosition()

        self.create_3d_scatter_plot(picked_pos)
        self.add_marker_to_vtk(picked_pos)

    def add_marker_to_vtk(self, position):
        if self.last_marker_actor:
            self.ren_1.RemoveActor(self.last_marker_actor)
        if self.last_outline_actor:
            self.ren_1.RemoveActor(self.last_outline_actor)

        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(position)
        sphere.SetRadius(0.08)
        sphere.SetPhiResolution(30)
        sphere.SetThetaResolution(30)

        sphere_mapper = vtk.vtkPolyDataMapper()
        sphere_mapper.SetInputConnection(sphere.GetOutputPort())

        sphere_actor = vtk.vtkActor()
        sphere_actor.SetMapper(sphere_mapper)
        sphere_actor.GetProperty().SetColor(1.0, 0.2, 0.2)
        sphere_actor.GetProperty().SetAmbient(0.3)
        sphere_actor.GetProperty().SetSpecular(1.0)
        sphere_actor.GetProperty().SetSpecularPower(50)

        outline_sphere = vtk.vtkSphereSource()
        outline_sphere.SetCenter(position)
        outline_sphere.SetRadius(0.1)

        outline_mapper = vtk.vtkPolyDataMapper()
        outline_mapper.SetInputConnection(outline_sphere.GetOutputPort())

        outline_actor = vtk.vtkActor()
        outline_actor.SetMapper(outline_mapper)
        outline_actor.GetProperty().SetColor(1.0, 1.0, 1.0)
        outline_actor.GetProperty().SetOpacity(0.5)

        self.last_marker_actor = sphere_actor
        self.last_outline_actor = outline_actor

        self.ren_1.AddActor(outline_actor)
        self.ren_1.AddActor(sphere_actor)
        self.vtk_widget_1.GetRenderWindow().Render()

    def create_3d_scatter_plot(self, initial_point):
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

        vtk_points = vtk.vtkPoints()
        for point in new_points:
            vtk_points.InsertNextPoint(point[0])

        polydata = vtk.vtkPolyData()
        polydata.SetPoints(vtk_points)

        sphere_source = vtk.vtkSphereSource()
        sphere_source.SetRadius(0.1)
        sphere_source.SetPhiResolution(20)
        sphere_source.SetThetaResolution(20)

        glyph = vtk.vtkGlyph3D()
        glyph.SetInputData(polydata)
        glyph.SetSourceConnection(sphere_source.GetOutputPort())
        glyph.SetScaleModeToDataScalingOff()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(glyph.GetOutputPort())

        self.scatter_actor = vtk.vtkActor()
        self.scatter_actor.SetMapper(mapper)
        self.scatter_actor.GetProperty().SetColor(0.0, 0.0, 1.0)

        self.ren_2.AddActor(self.scatter_actor)

        axes = vtk.vtkAxesActor()
        axes.SetTotalLength(2.0, 2.0, 2.0)
        axes.GetXAxisCaptionActor2D().GetTextActor().GetTextProperty().SetColor(1, 0, 0)
        axes.GetYAxisCaptionActor2D().GetTextActor().GetTextProperty().SetColor(0, 1, 0)
        axes.GetZAxisCaptionActor2D().GetTextActor().GetTextProperty().SetColor(0, 0, 1)

        self.ren_2.AddActor(axes)
        self.ren_2.ResetCamera()
        self.vtk_widget_2.GetRenderWindow().Render()

    def stl_mesh_to_vtk(self, stl_mesh):
        poly_data = vtk.vtkPolyData()
        points = vtk.vtkPoints()
        cells = vtk.vtkCellArray()

        unique_vertices, indices = np.unique(stl_mesh.vectors.reshape(-1, 3), axis=0, return_inverse=True)

        for vertex in unique_vertices:
            points.InsertNextPoint(vertex[0], vertex[1], vertex[2])

        for i in range(0, len(indices), 3):
            triangle = vtk.vtkTriangle()
            for j in range(3):
                triangle.GetPointIds().SetId(j, indices[i + j])
            cells.InsertNextCell(triangle)

        poly_data.SetPoints(points)
        poly_data.SetPolys(cells)
        return poly_data
