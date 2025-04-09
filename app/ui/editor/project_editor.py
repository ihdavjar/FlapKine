import os
import pickle 
import numpy as np
from stl import mesh  
import plotly.graph_objects as go
import plotly.io as pio
import bpy
import bmesh
import json

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from src.utils.utils import create_video_from_frames
from src.core.transforms.vtk_transform import *
from app.widgets.misc.render_config_edit import RenderConfig
import vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import qtawesome as qta
from app.widgets.misc.menu_bar import MenuBar
from app.widgets.main.visualiser import Visualizer3DWidget


import os
import json
from PyQt5.QtCore import QThread, pyqtSignal, QMetaObject, Qt
import bpy
        
from app.widgets.main.video_animation import VideoAnimation
    
class STLWorker(QThread):
    stl_ready = pyqtSignal(object)

    def __init__(self, scene_data, project_folder, value, reflect):
        super(STLWorker, self).__init__()
        self.scene_data = scene_data
        self.project_folder = project_folder
        self.value = value
        self.reflect = reflect
        self._is_running = True  # Add a running flag

    def run(self):
        try:
            with open(os.path.join(self.project_folder, 'config.json')) as f:
                config = json.load(f)

            reflect = [config['Reflect'] == "XY", config['Reflect'] == "YZ", config['Reflect'] == "XZ"]

            your_mesh = self.scene_data.save_stl(self.value, reflect_xy=reflect[0], reflect_yz=reflect[1], reflect_xz=reflect[2])

            if not self._is_running:
                return  # Stop if the thread was asked to exit

            poly_data = self.stl_mesh_to_vtk(your_mesh)
            self.stl_ready.emit(poly_data)

        except Exception as e:
            print(f"Error in STL processing thread: {e}")

    def stop(self):
        """Gracefully stop the thread."""
        self._is_running = False
            
    def stl_mesh_to_vtk(self, stl_mesh):
        """
        Convert an stl.mesh.Mesh (numpy-stl) object to vtkPolyData.
        """
        poly_data = vtk.vtkPolyData()
        points = vtk.vtkPoints()
        cells = vtk.vtkCellArray()

        # Extract unique vertices and create a mapping
        unique_vertices, indices = np.unique(stl_mesh.vectors.reshape(-1, 3), axis=0, return_inverse=True)

        # Insert vertices into vtkPoints
        for vertex in unique_vertices:
            points.InsertNextPoint(vertex[0], vertex[1], vertex[2])

        # Insert faces into vtkCellArray
        for i in range(0, len(indices), 3):
            triangle = vtk.vtkTriangle()
            for j in range(3):
                triangle.GetPointIds().SetId(j, indices[i + j])
            cells.InsertNextCell(triangle)

        # Assign points and cells to polydata
        poly_data.SetPoints(points)
        poly_data.SetPolys(cells)
        return poly_data
    
class ProjectWindow(QMainWindow):

    def __init__(self, project_folder):
        super(ProjectWindow, self).__init__()
        
        self.project_folder = project_folder
        self.setWindowTitle("FlapKine")
        self.resize(1280, 800)
        self.setWindowIcon(QIcon(os.path.join('app', 'assets', 'flapkine_icon.png')))
        
        ############################ Menu Bar ################################
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)

        self.menu_bar.connect_actions({
            'exit': self.close,
            'minimize': self.showMinimized,
            'maximize': self.showMaximized,
            'restore': self.showNormal,
            'about': self.about_button_fun,
            'configure_render': self.change_render_config,
        })
        
        # Process the project
        self.process_project()
        
        ############################ Main Layout ################################
        # Create the main widget and set it as the central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create the main layout
        main_layout = QHBoxLayout(central_widget)

        # Create a QSplitter for 4-way splitting
        main_splitter = QSplitter(Qt.Vertical)

        # Create horizontal splitters for the top and bottom rows
        top_splitter = QSplitter(Qt.Horizontal)
        bottom_splitter = QSplitter(Qt.Horizontal)
                                    
        self.point_selected()
        self.create_3d_scatter_plot([0, 0, 0])

        # Adding widgets to top row
        self.topleftgroup = VideoAnimation(self.project_folder, self.scene_data)  # Video animation widget
        self.bottomleftgroup = Visualizer3DWidget(self.scene_data, self.project_folder, self.angles)  # 3D visualizer widget

        top_splitter.addWidget(self.topleftgroup)  # Top left (Main controls)
        top_splitter.addWidget(self.toprightgroup)  # Placeholder for future expansion

        # Adding widgets to bottom row
        bottom_splitter.addWidget(self.bottomleftgroup)  # Bottom left (Output/Logs)
        bottom_splitter.addWidget(self.bottomrightgroup)  # Placeholder for future expansion

        # Add both rows to main vertical splitter
        main_splitter.addWidget(top_splitter)
        main_splitter.addWidget(bottom_splitter)

        # Set minimum size for each section
        self.topleftgroup.setMinimumSize(640, 400)
        self.toprightgroup.setMinimumSize(400, 400)
        self.bottomleftgroup.setMinimumSize(640, 400)
        self.bottomrightgroup.setMinimumSize(400, 400)

        # Set the exact sizes for each splitter
        top_splitter.setSizes([640, 640])    # Each half is 600px wide
        bottom_splitter.setSizes([640, 640]) # Each half is 600px wide
        main_splitter.setSizes([400, 400])   # Each half is 400px tall

        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)
        
        # Add the main splitter to the layout
        main_layout.addWidget(main_splitter)

    def process_project(self):
        scene_path = os.path.join(self.project_folder, 'scene.pkl')
        
        if not os.path.exists(scene_path):
            self.showErrorDialog('Error', f"No project found at: {self.project_folder}")
            
        else:
            with open(scene_path, 'rb') as scene_file:
                self.scene_data = pickle.load(scene_file)
                self.angles = self.scene_data.objects[0].angles

    def point_selected(self):
        
        primary_color = self.palette().color(self.foregroundRole()).name()  # Get the primary color

        self.toprightgroup = QGroupBox("Selected Point")
        self.toprightgroup.setFont(QFont('Times', 9))

        layout = QVBoxLayout()

        # VTK Widget for rendering
        self.vtk_widget_1 = QVTKRenderWindowInteractor(self)
        layout.addWidget(self.vtk_widget_1)

        # VTK Renderer
        self.ren_1 = vtk.vtkRenderer()
        self.ren_1.SetBackground(0.95, 0.95, 0.95)  # Light grey background
        self.vtk_widget_1.GetRenderWindow().AddRenderer(self.ren_1)
        self.iren_1 = self.vtk_widget_1.GetRenderWindow().GetInteractor()

        # **Disable Rotation: Use Image Style**
        self.interactor_style_1 = vtk.vtkInteractorStyleImage()
        self.iren_1.SetInteractorStyle(self.interactor_style_1)

        # Mouse click event
        self.iren_1.AddObserver("LeftButtonPressEvent", self.on_click)

        mesh = self.scene_data.objects[0].object_.stl_mesh

        poly_data = self.stl_mesh_to_vtk(mesh)

        points = np.array([poly_data.GetPoint(i) for i in range(poly_data.GetNumberOfPoints())])
        points[:, 2] = 0  # Flatten Z-axis

        # Update VTK polydata with 2D points
        new_points = vtk.vtkPoints()
        for p in points:
            new_points.InsertNextPoint(p)

        poly_data.SetPoints(new_points)

        # **Main Actor (Surface)**
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly_data)

        self.actor_1 = vtk.vtkActor()
        self.actor_1.SetMapper(mapper)
        self.actor_1.GetProperty().SetColor(0.5, 0.7, 1)  # Light blue

        # **Outline Actor (Black Edges)**
        edges_filter = vtk.vtkFeatureEdges()
        edges_filter.SetInputData(poly_data)
        edges_filter.BoundaryEdgesOn()
        edges_filter.FeatureEdgesOff()
        edges_filter.ManifoldEdgesOff()
        edges_filter.NonManifoldEdgesOff()
        edges_filter.Update()

        # Render
        self.ren_1.RemoveAllViewProps()
        self.ren_1.AddActor(self.actor_1)  # Add surface
        self.ren_1.ResetCamera()
        self.vtk_widget_1.GetRenderWindow().Render()

        self.show()
        self.toprightgroup.setLayout(layout)
        
    def on_click(self, obj, event):
        """Handles mouse click and prints the clicked coordinates."""
        click_pos = self.iren_1.GetEventPosition()

        picker = vtk.vtkCellPicker()
        picker.SetTolerance(0.005)
        picker.Pick(click_pos[0], click_pos[1], 0, self.ren_1)

        picked_pos = picker.GetPickPosition()

        self.create_3d_scatter_plot(picked_pos)
        self.add_marker_to_vtk(picked_pos)

    def add_marker_to_vtk(self, position):
        """
        Adds a red sphere marker at the given (x, y, z) position in the VTK 3D visualization.
        Removes the previous marker before adding a new one.
        
        :param position: Tuple (x, y, z) representing the world coordinates.
        """
        # Remove previous marker if it exists
        if hasattr(self, "last_marker_actor"):
            self.ren_1.RemoveActor(self.last_marker_actor)
        if hasattr(self, "last_outline_actor"):
            self.ren_1.RemoveActor(self.last_outline_actor)

        # Create a sphere marker
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(position)
        sphere.SetRadius(0.08)  # Adjust size (smaller for a marker)
        sphere.SetPhiResolution(30)  # Increase resolution for smoothness
        sphere.SetThetaResolution(30)

        sphere_mapper = vtk.vtkPolyDataMapper()
        sphere_mapper.SetInputConnection(sphere.GetOutputPort())

        sphere_actor = vtk.vtkActor()
        sphere_actor.SetMapper(sphere_mapper)
        sphere_actor.GetProperty().SetColor(1.0, 0.2, 0.2)  # Red marker
        sphere_actor.GetProperty().SetAmbient(0.3)  # Glow effect
        sphere_actor.GetProperty().SetSpecular(1.0)  # Strong reflection
        sphere_actor.GetProperty().SetSpecularPower(50)  # Glossy look

        # Create an outline for better visibility
        outline_sphere = vtk.vtkSphereSource()
        outline_sphere.SetCenter(position)
        outline_sphere.SetRadius(0.1)  # Slightly larger than the main sphere

        outline_mapper = vtk.vtkPolyDataMapper()
        outline_mapper.SetInputConnection(outline_sphere.GetOutputPort())

        outline_actor = vtk.vtkActor()
        outline_actor.SetMapper(outline_mapper)
        outline_actor.GetProperty().SetColor(1.0, 1.0, 1.0)  # White outline
        outline_actor.GetProperty().SetOpacity(0.5)  # Semi-transparent effect

        # Store reference to remove later
        self.last_marker_actor = sphere_actor
        self.last_outline_actor = outline_actor

        # Add the marker to the renderer
        self.ren_1.AddActor(outline_actor)
        self.ren_1.AddActor(sphere_actor)

        # Refresh the VTK display
        self.vtk_widget_1.GetRenderWindow().Render()

    def create_3d_scatter_plot(self, initial_point):
        """
        Creates or updates a 3D scatter plot using VTK.
        
        :param initial_point: List [x, y, z] representing the initial point in 3D space.
        """
        if not hasattr(self, 'bottomrightgroup'):
            self.bottomrightgroup = QGroupBox("3D Scatter Plot")
            self.bottomrightgroup.setFont(QFont('Times', 9))
            layout = QVBoxLayout()
            self.vtk_widget_2 = QVTKRenderWindowInteractor(self)
            layout.addWidget(self.vtk_widget_2)
            self.bottomrightgroup.setLayout(layout)

            # Setup VTK Renderer
            self.ren_2 = vtk.vtkRenderer()
            self.ren_2.SetBackground(0.95, 0.95, 0.95)  # Light grey background
            self.vtk_widget_2.GetRenderWindow().AddRenderer(self.ren_2)
            self.iren_2 = self.vtk_widget_2.GetRenderWindow().GetInteractor()

            # Store reference to scatter actor (for removal later)
            self.scatter_actor = None

        # Remove previous scatter actor if it exists
        if self.scatter_actor:
            self.ren_2.RemoveActor(self.scatter_actor)

        # Convert initial point to NumPy array
        initial_point = np.array(initial_point).reshape(1, 3)

        # Retrieve transformations
        translation_transform = self.scene_data.objects[0].object_.translation_transform
        rotation_transform = self.scene_data.objects[0].object_.rotation_transform
        flexibility_transform = self.scene_data.objects[0].object_.flexibility_transform
        positions = self.scene_data.objects[0].positions
        angles = self.scene_data.objects[0].angles

        # Compute transformed points
        new_points = []
        for t in range(len(angles)):
            temp_point = flexibility_transform(initial_point, t)
            temp_point = rotation_transform(temp_point, angles[t])
            temp_point = translation_transform(temp_point, positions[t])

            if temp_point is not None:
                new_points.append(temp_point)

        # Convert points to VTK format
        vtk_points = vtk.vtkPoints()
        for point in new_points:
            vtk_points.InsertNextPoint(point[0])  # Ensure it's a tuple (x, y, z)

        # Create polydata object
        polydata = vtk.vtkPolyData()
        polydata.SetPoints(vtk_points)

        # Create a sphere glyph for scatter plot points
        sphere_source = vtk.vtkSphereSource()
        sphere_source.SetRadius(0.1)  # Marker size
        sphere_source.SetPhiResolution(20)
        sphere_source.SetThetaResolution(20)

        glyph = vtk.vtkGlyph3D()
        glyph.SetInputData(polydata)
        glyph.SetSourceConnection(sphere_source.GetOutputPort())
        glyph.SetScaleModeToDataScalingOff()  # Keep uniform size

        # Mapper and Actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(glyph.GetOutputPort())

        self.scatter_actor = vtk.vtkActor()
        self.scatter_actor.SetMapper(mapper)
        self.scatter_actor.GetProperty().SetColor(0.0, 0.0, 1.0)  # Blue color

        # Add new scatter plot
        self.ren_2.AddActor(self.scatter_actor)

        axes = vtk.vtkAxesActor()
        axes.SetTotalLength(2.0, 2.0, 2.0)
        axes.GetXAxisCaptionActor2D().GetTextActor().GetTextProperty().SetColor(1, 0, 0)
        axes.GetYAxisCaptionActor2D().GetTextActor().GetTextProperty().SetColor(0, 1, 0)
        axes.GetZAxisCaptionActor2D().GetTextActor().GetTextProperty().SetColor(0, 0, 1)
        self.ren_2.AddActor(axes)

        # Adjust Camera & Render
        self.ren_2.ResetCamera()
        self.vtk_widget_2.GetRenderWindow().Render()

    # Print the STL based on the slider value
    def process_STL(self):
        # Load the config file
        with open(os.path.join(self.project_folder, 'config.json')) as f:
            config = json.load(f)
        reflect = [config['Reflect'] == "XY", config['Reflect'] == "YZ", config['Reflect'] == "XZ"]

        self.reflect = reflect  

        value = self.slider.value()

        your_mesh = self.scene_data.save_stl(value, reflect_xy=self.reflect[0], reflect_yz=self.reflect[1], reflect_xz=self.reflect[2])

        poly_data = self.stl_mesh_to_vtk(your_mesh)

        # Load STL file

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly_data) 

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.5, 0.7, 1)  # Light blue

        # Clear previous actors and add new one
        self.ren.RemoveAllViewProps()
        self.ren.AddActor(actor)
        # self.add_grid()  # Re-add grid after clearing scene
        self.ren.ResetCamera()

        # Render the scene
        self.vtkWidget.GetRenderWindow().Render()
            
    def stl_mesh_to_vtk(self, stl_mesh):
        """
        Convert an stl.mesh.Mesh (numpy-stl) object to vtkPolyData.
        """
        poly_data = vtk.vtkPolyData()
        points = vtk.vtkPoints()
        cells = vtk.vtkCellArray()

        # Extract unique vertices and create a mapping
        unique_vertices, indices = np.unique(stl_mesh.vectors.reshape(-1, 3), axis=0, return_inverse=True)

        # Insert vertices into vtkPoints
        for vertex in unique_vertices:
            points.InsertNextPoint(vertex[0], vertex[1], vertex[2])

        # Insert faces into vtkCellArray
        for i in range(0, len(indices), 3):
            triangle = vtk.vtkTriangle()
            for j in range(3):
                triangle.GetPointIds().SetId(j, indices[i + j])
            cells.InsertNextCell(triangle)

        # Assign points and cells to polydata
        poly_data.SetPoints(points)
        poly_data.SetPolys(cells)
        return poly_data

    ############################ Video Functions ################################
    # Define same function to play and pause removing pause button update the play button
      

    ############################ Window Related Functions ################################
    def center(self):
        # Get the screen resolution
        screen_resolution = QDesktopWidget().screenGeometry()
        screen_width, screen_height = screen_resolution.width(), screen_resolution.height()
        # Get the window size
        window_size = self.geometry()
        window_width, window_height = window_size.width(), window_size.height()
        # Calculate the center of the screen
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        # Move the window to the center
        self.move(x, y)

    ############################ Message Box ################################  
    def showErrorDialog(self, title, message):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle(title)
        error_dialog.setText(message)
        error_dialog.exec_()

    def showAlertDialog(self, title, message):
        alert_dialog = QMessageBox()
        alert_dialog.setIcon(QMessageBox.Information)
        alert_dialog.setWindowTitle(title)
        alert_dialog.setText(message)
        alert_dialog.exec_()
    
    ######################################## MENU BAR ########################################
    def change_render_config(self):
        self.window2 = RenderConfig(self.project_folder)
        self.window2.show()

    def about_button_fun(self):
        QMessageBox.about(self, "About FlapKine", '''
        <h1>FlapKine</h1>
        <p>Developed by: Kalbhavi Vadhiraj</p>                  
        <p>Version 0.0.1</p>
        <p>FlapKine provides a visual representation and simulation of the kinematics and aerodynamics of flapping wing micro-aerial vehicles (MAVs). It allows users to analyze and optimize MAV designs with precision and clarity, revealing the intricate mechanics of flapping flight. Whether for research, development, or educational purposes, this tool offers valuable insights into the performance and behavior of MAVs, facilitating advanced design and innovation.</p> 
''')

    def closeEvent(self, event):
        """
        Ensures that VTK renderers and interactor windows close instantly when the application exits.
        """
        try:
            # Properly finalize VTK widgets and render windows
            if hasattr(self, "vtk_widget_1") and self.vtk_widget_1:
                self.vtk_widget_1.GetRenderWindow().Finalize()
                self.vtk_widget_1.setParent(None)
                del self.vtk_widget_1

            if hasattr(self, "vtk_widget_2") and self.vtk_widget_2:
                self.vtk_widget_2.GetRenderWindow().Finalize()
                self.vtk_widget_2.setParent(None)
                del self.vtk_widget_2

            # Stop and destroy VTK interactors if they exist
            if hasattr(self, "iren_1") and self.iren_1:
                self.iren_1.GetRenderWindow().Finalize()
                self.iren_1.TerminateApp()
                self.iren_1.GetRenderWindow().SetMapped(0)  # Hide the window instantly
                self.iren_1 = None

            if hasattr(self, "iren_2") and self.iren_2:
                self.iren_2.GetRenderWindow().Finalize()
                self.iren_2.TerminateApp()
                self.iren_2.GetRenderWindow().SetMapped(0)  # Hide the window instantly
                self.iren_2 = None

            # Remove and delete renderers
            if hasattr(self, "ren_1") and self.ren_1:
                self.ren_1.RemoveAllViewProps()
                del self.ren_1

            if hasattr(self, "ren_2") and self.ren_2:
                self.ren_2.RemoveAllViewProps()
                del self.ren_2

            # Force event processing to clean up remaining VTK windows instantly
            from PyQt5.QtWidgets import QApplication
            QApplication.processEvents()

        except Exception as e:
            print(f"Error while closing VTK renderers: {e}")

        event.accept()  # Ensures the window actually closes instantly

        
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = ProjectWindow('D:\Research\Kinematics_App\project_final')
    window.show()
    sys.exit(app.exec_())