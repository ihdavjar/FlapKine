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
from app.widgets.render_config import RenderConfig
import vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import qtawesome as qta

import os
import json
from PyQt5.QtCore import QThread, pyqtSignal, QMetaObject, Qt
import bpy
        
class VideoPlayer(QWidget):
    def __init__(self, width=640, height=480):  # Default size
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create video widget
        self.video_widget = QVideoWidget(self)
        self.video_widget.setSizePolicy(QWidget.sizePolicy(self).Expanding, QWidget.sizePolicy(self).Expanding)
        self.video_widget.setMinimumSize(400, 225)  # Ensuring a minimum size

        layout.addWidget(self.video_widget)

        # Setup media player
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)

        # Set initial size
        self.setMinimumSize(width, height)

    def setMedia(self, video_path):
        media = QMediaContent(QUrl.fromLocalFile(video_path))
        self.media_player.setMedia(media)
        self.media_player.pause()

    def resizeEvent(self, event):
        """Ensure the video widget resizes properly and maintains aspect ratio."""
        self.video_widget.setGeometry(self.rect())  # Stretch to fit full screen
        super().resizeEvent(event)
        
class Worker(QThread):
    progress_signal = pyqtSignal(float)

    def __init__(self, project_folder, angles, scene_data, reflect, parent=None):
        super(Worker, self).__init__(parent)
        self.project_folder = project_folder    
        self.angles = angles
        self.scene_data_ = scene_data
        self.reflect = reflect
        self.stl_files = []

    def run(self):
        
        # Load the Blender project
        with open(os.path.join(self.project_folder, 'config.json')) as f:
            config = json.load(f)

        
        # Set rendering parameters
        bpy.context.scene.render.image_settings.file_format = config['VideoRender']['FrameFormat']  # Output image format
        bpy.context.scene.render.resolution_x = config['VideoRender']['resolution_x']  # Output resolution X
        bpy.context.scene.render.resolution_y = config['VideoRender']['resolution_y']  # Output resolution Y
        bpy.context.scene.render.film_transparent = config['VideoRender']['film_transparent']  # Enable transparent background

        # Set the camera parameters
        bpy.context.scene.camera.location = tuple(config['Camera']['location'])  # Camera location
        bpy.context.scene.camera.rotation_euler = tuple(config['Camera']['rotation_euler'])  # Camera rotation

        bpy.context.scene.camera.data.type = 'PERSP'
        bpy.context.scene.camera.data.lens = 140

        # Set the light parameters
        bpy.data.objects['Light'].location = tuple(config['Light']['location'])  # Light location
        bpy.data.objects['Light'].data.energy = config['Light']['energy']  # Light energy

        # Remove the default cube
        if 'Cube' in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects['Cube'], do_unlink=True)

        # Set the scene frame rate
        bpy.context.scene.render.fps = 24  # Frame rate

         # Set the world background color to white
        bpy.context.scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.95, 0.95, 0.95, 1)
        # Create a blue material
        blue_material = bpy.data.materials.new(name="BlueMaterial")
        blue_material.use_nodes = True
        bsdf = blue_material.node_tree.nodes.get('Principled BSDF')
        bsdf.inputs['Base Color'].default_value = (0, 0, 1, 1)  # Blue color
        
        # stl_files_dir = os.path.join(self.project_folder, 'data/stl')
        output_dir = os.path.join(self.project_folder, 'data/images')
        stl_dir = os.path.join(self.project_folder, 'data/stl')

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        if config["STL"]:
            if not os.path.exists(stl_dir):
                os.makedirs(stl_dir)

        # Loop through each STL file
        for i in range(len(self.angles)):
            stl_file = self.scene_data_.save_stl(i, reflect_xy=self.reflect[0], reflect_yz=self.reflect[1], reflect_xz=self.reflect[2])
            
            if config["STL"]:
                stl_file.save(os.path.join(stl_dir, f"stl_mesh_{i}.stl"))
            
            # Import STL file and render in the main thread
            QMetaObject.invokeMethod(self, "import_and_render", Qt.BlockingQueuedConnection,
                                     Q_ARG(object, stl_file), Q_ARG(str, output_dir), Q_ARG(int, i+1))

            self.progress_signal.emit((i + 1)/len(self.angles) * 100)
            
        frames_path = os.path.join(self.project_folder, 'data/images')
        project_name = os.path.basename(self.project_folder)
        video_path = os.path.join(self.project_folder, f"data/videos/{project_name}.mp4")

        create_video_from_frames(frames_path, video_path, frame_rate=20,
                                 width=config['VideoRender']['resolution_x'], height=config['VideoRender']['resolution_y'], libx264=False)

    @pyqtSlot(object, str, int)
    def import_and_render(self, stl_mesh, output_dir, frame_index):
        """ Handle numpy-stl mesh directly instead of file path """
        
        # Create a new Blender mesh and object
        new_mesh = bpy.data.meshes.new("imported_mesh")
        new_object = bpy.data.objects.new("ImportedObject", new_mesh)
        bpy.context.collection.objects.link(new_object)
        
        # Create BMesh to build geometry from numpy-stl mesh
        bm = bmesh.new()
        for face in stl_mesh.vectors:
            verts = [bm.verts.new(v) for v in face]
            bm.faces.new(verts)
        
        bm.to_mesh(new_mesh)
        bm.free()

        # Add material to the object
        blue_material_name = "BlueMaterial"
        if not any(mat.name == blue_material_name for mat in new_mesh.materials):
            # Create the blue material if it doesn't exist
            if blue_material_name not in bpy.data.materials:
                blue_material = bpy.data.materials.new(name=blue_material_name)
                blue_material.use_nodes = True
                bsdf = blue_material.node_tree.nodes.get('Principled BSDF')
                bsdf.inputs['Base Color'].default_value = (0, 0, 1, 1)  # Blue color
            else:
                blue_material = bpy.data.materials.get(blue_material_name)
            
            # Assign the material to the object
            new_mesh.materials.append(blue_material)

        # Set the render output file path and render
        output_filename = f'frame_{frame_index}.png'
        output_path = os.path.join(output_dir, output_filename)
        
        bpy.context.scene.render.filepath = output_path
        bpy.ops.render.render(write_still=True)

        # Clean up the object after rendering
        bpy.ops.object.select_all(action='DESELECT')
        new_object.select_set(True)
        bpy.ops.object.delete()

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

        # Storing the project folder
        self.project_folder = project_folder

        # Place the window in the center of the screen
        self.setWindowTitle("FlapKine")

        # Set the window geometry
        self.resize(1200, 800)

        # Set the icon
        self.setWindowIcon(QIcon(os.path.join('app', 'assets', 'flap_kine_icon.png')))
        
        ############################ Menu Bar ################################
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu('File')
        self.new_action = self.file_menu.addAction('New')
        self.new_action.setEnabled(False)
        self.open_action = self.file_menu.addAction('Open')
        self.open_action.setEnabled(False)
        self.exit_action = self.file_menu.addAction('Exit')
        self.exit_action.triggered.connect(self.close)

        self.edit_menu = self.menu.addMenu('Edit')
        self.undo_action = self.edit_menu.addAction('Undo')
        self.undo_action.setEnabled(False)
        self.redo_action = self.edit_menu.addAction('Redo')
        self.redo_action.setEnabled(False)

        self.window_menu = self.menu.addMenu('Window')
        self.minimize_action = self.window_menu.addAction('Minimize')
        self.minimize_action.triggered.connect(self.showMinimized)
        self.maximize_action = self.window_menu.addAction('Maximize')
        self.maximize_action.triggered.connect(self.showMaximized)
        self.restore_action = self.window_menu.addAction('Restore')
        self.restore_action.triggered.connect(self.showNormal)
        self.new_window_action = self.window_menu.addAction('New Window')
        self.new_window_action.setEnabled(False)

        self.render_menu = self.menu.addMenu('Render')
        self.render_option = self.render_menu.addAction('Configure Render')
        self.render_option.triggered.connect(self.change_render_config)

        self.help_menu = self.menu.addMenu('Help')
        self.about_action = self.help_menu.addAction('About') 
        self.about_action.triggered.connect(self.about_button_fun)

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
                                    
        self.CreateAnimation()
        self.create_3d_visualiser()
        self.point_selected()
        self.create_3d_scatter_plot([0, 0, 0])

        # Adding widgets to top row
        top_splitter.addWidget(self.topleftgroup)  # Top left (Main controls)
        top_splitter.addWidget(self.toprightgroup)  # Placeholder for future expansion

        # Adding widgets to bottom row
        bottom_splitter.addWidget(self.bottomleftgroup)  # Bottom left (Output/Logs)
        bottom_splitter.addWidget(self.bottomrightgroup)  # Placeholder for future expansion

        # Add both rows to main vertical splitter
        main_splitter.addWidget(top_splitter)
        main_splitter.addWidget(bottom_splitter)

        # Set minimum size for each section
        self.topleftgroup.setMinimumSize(600, 400)
        self.toprightgroup.setMinimumSize(400, 400)
        self.bottomleftgroup.setMinimumSize(600, 400)
        self.bottomrightgroup.setMinimumSize(400, 400)

        # Set the exact sizes for each splitter
        top_splitter.setSizes([600, 600])    # Each half is 600px wide
        bottom_splitter.setSizes([600, 600]) # Each half is 600px wide
        main_splitter.setSizes([400, 400])   # Each half is 400px tall

        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)
        
        # Add the main splitter to the layout
        main_layout.addWidget(main_splitter)

        # Maximize the window
        # self.showMaximized()

    ############################ Project Functions ################################
    def process_project(self):
        scene_path = os.path.join(self.project_folder, 'scene.pkl')
        
        if not os.path.exists(scene_path):
            self.showErrorDialog('Error', f"No project found at: {self.project_folder}")
            
        else:
            with open(scene_path, 'rb') as scene_file:
                self.scene_data = pickle.load(scene_file)
                self.angles = self.scene_data.objects[0].angles
    
    def create_3d_visualiser(self):
        primary_color = self.palette().color(self.foregroundRole()).name()  # Get the primary color
        self.bottomleftgroup = QGroupBox("3D Frame Viewer")
        self.bottomleftgroup.setFont(QFont('Times', 9))

        layout = QVBoxLayout()
        slider_layout = QHBoxLayout()

        # Label to display current slider value with updated style
        self.slider_label = QLabel("Frame: 0", self.bottomleftgroup)
        self.slider_label.setFont(QFont('Arial', 8, QFont.Weight.Bold))
        self.slider_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slider_label.setStyleSheet("color: #333;")  # Darker color for better visibility

        # Slider with updated style and smoother handle
        self.slider = QSlider(Qt.Orientation.Horizontal, self.bottomleftgroup)
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

        # Add a Play/Pause button (if necessary)
        self.play_button = QPushButton("", self.bottomleftgroup)
        self.play_button.setIcon(qta.icon("mdi.play", color=primary_color))
        self.playing = False
        self.play_button.clicked.connect(self.toggle_play)

        # Add a next frame button
        self.next_button = QPushButton("", self.bottomleftgroup)
        self.next_button.setIcon(qta.icon("mdi.skip-next", color=primary_color))
        self.next_button.clicked.connect(lambda: self.slider.setValue(self.slider.value() + 1))

        slider_layout.addWidget(self.play_button)
        slider_layout.addWidget(self.next_button)
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.slider_label)
        layout.addLayout(slider_layout)

        self.vtkWidget = QVTKRenderWindowInteractor(self)

        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)

        self.ren.SetBackground(0.95, 0.95, 0.95)  # Slightly lighter background

        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        self.iren.Initialize()

        layout.addWidget(self.vtkWidget)

        self.vtkWidget.setStyleSheet("""
            background-color: #fafafa;
            border: 1px solid #bbb;
            border-radius: 10px;
        """)

        self.bottomleftgroup.setLayout(layout)

        self.process_STL()
    # Add play/pause functionality
    def toggle_play(self):
        primary_color = self.palette().color(self.foregroundRole()).name()  

        if self.playing:

            self.playing = False
        else:
            self.play_button.setIcon(qta.icon("mdi.pause", color=primary_color))
            self.playing = True
            self.play_frames()

    def play_frames(self):
        if self.playing:
            current_frame = self.slider.value()
            if current_frame < len(self.angles) - 1:
                self.slider.setValue(current_frame + 1)
                self.on_slider_value_changed()
                QTimer.singleShot(50, self.play_frames)

    def on_slider_value_changed(self):
        value = self.slider.value()
        self.slider_label.setText(f"Frame: {value}")
        self.slider_label.setFont(QFont('Times', 8, QFont.Weight.Bold))
        
        
        # Gracefully stop the previous thread if running
        if hasattr(self, 'stl_worker') and self.stl_worker.isRunning():
            self.stl_worker.stop()
            self.stl_worker.wait()  # Wait for it to stop properly

        # Start new worker
        self.stl_worker = STLWorker(self.scene_data, self.project_folder, value, self.reflect)
        self.stl_worker.stl_ready.connect(self.update_STL)
        self.stl_worker.start()

    def update_STL(self, poly_data):
        """Update the VTK scene with the new STL data (runs in the main thread)."""
        try:
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputData(poly_data)

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetColor(0.5, 0.7, 1)  # Light blue

            # Clear previous actors and add new one
            self.ren.RemoveAllViewProps()
            self.ren.AddActor(actor)
            self.ren.ResetCamera()

            # Render the scene
            self.vtkWidget.GetRenderWindow().Render()
        except Exception as e:
            print(f"Error updating STL: {e}")
    # Create the bottom left group
    def CreateAnimation(self):

        primary_color = self.palette().color(self.foregroundRole()).name()  # Get the primary color
        
        self.topleftgroup = QGroupBox("Animation Window")
        self.topleftgroup.setFont(QFont('Times', 9))

        # Video Related Widget
        self.playButton = QPushButton('')
        self.playButton.setIcon(qta.icon("mdi.play", color=primary_color))
        self.video_playing = False
        self.playButton.clicked.connect(self.playVideo)

        self.repeatButton = QPushButton('')
        self.repeatButton.setIcon(qta.icon("mdi.repeat", color=primary_color))
        self.repeatButton.setCheckable(True)
        self.repeatButton.clicked.connect(self.repeatVideo)

        # Create slider for video position
        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.setStyleSheet("""
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
        self.positionSlider.sliderMoved.connect(self.setPosition)
        


        # render options
        self.render_button = QPushButton("Render")
        self.render_button.setFont(QFont('Times', 8))
        
        self.render_button.setIcon(qta.icon("mdi.printer-3d", color = primary_color))
        self.render_button.clicked.connect(self.genframes)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
    QProgressBar {
        border: 2px solid #005a9e;
        border-radius: 5px;
        text-align: center;
        font-size: 10pt;
        background-color: #ddd;
        padding: 2px;
    }

    QProgressBar::chunk {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00aaff, stop:1 #005a9e);
        border-radius: 5px;
    }
""")

        # Create label for displaying status
        self.statusLabel = QLabel('')
        self.statusLabel.setFont(QFont('Times', 8))

        render_layout = QHBoxLayout()
        render_layout.addWidget(self.render_button)
        render_layout.addWidget(self.progress_bar)
        

        controlLayout = QHBoxLayout()
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.repeatButton) 
        controlLayout.addWidget(self.positionSlider) 

        with open(os.path.join(self.project_folder, 'config.json')) as f:
            config = json.load(f)

        # Connect media player signals
        self.video_widget = VideoPlayer(config['VideoRender']['resolution_x'], config['VideoRender']['resolution_y'])

        # Connect media player signals
        self.video_widget.media_player.durationChanged.connect(self.updateDuration)
        self.video_widget.media_player.positionChanged.connect(self.updatePosition)
        self.video_widget.media_player.stateChanged.connect(self.updateState)


        project_name = os.path.basename(self.project_folder)

        video_path = os.path.join(self.project_folder, f'data/videos/{project_name}.mp4')

        if not os.path.exists(video_path):
            self.showErrorDialog('Alert', f"No render found at: {self.project_folder}")
        
        else:
            self.video_widget.setMedia(video_path)
            
        layout = QVBoxLayout()
        layout.addWidget(self.video_widget)
        layout.addLayout(controlLayout)
        layout.addLayout(render_layout)

        self.topleftgroup.setLayout(layout)
    
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

    def genframes(self):

        self.render_button.setEnabled(False)

        self.worker = Worker(self.project_folder, self.angles, self.scene_data, self.reflect)

        self.worker.progress_signal.connect(self.update_progress)

        self.worker.start()

        self.worker.finished.connect(self.complete_render)

    def complete_render(self):
        self.render_button.setEnabled(True)
        project_name = os.path.basename(self.project_folder)
        video_path = os.path.join(self.project_folder, f'data/videos/{project_name}.mp4')
        self.showAlertDialog('Alert', f"Video rendered successfully at: {video_path}")
        self.video_widget.setMedia(video_path)

    def update_progress(self, value):
        self.progress_bar.setValue(int(value))

    ############################ Video Functions ################################
    # Define same function to play and pause removing pause button update the play button
    def playVideo(self):
        primary_color = self.palette().color(self.foregroundRole()).name()  # Get the primary color 
        if self.video_playing:
            self.video_widget.media_player.pause()
            self.playButton.setIcon(qta.icon("mdi.play", color=primary_color))
            self.video_playing = False
        else:
            self.video_widget.media_player.play()
            self.playButton.setIcon(qta.icon("mdi.pause", color=primary_color))
            self.video_playing = True
        
    def repeatVideo(self):
        primary_color = self.palette().color(self.foregroundRole()).name()  # Get the primary color
        if self.repeatButton.isChecked():
            self.repeatButton.setIcon(qta.icon("mdi.repeat-off", color=primary_color))
            self.video_widget.media_player.setPosition(0)
            self.video_widget.media_player.play()
            self.playButton.setIcon(qta.icon("mdi.pause", color=primary_color))
        else:
            self.repeatButton.setIcon(qta.icon("mdi.repeat", color=primary_color))

    def updateDuration(self, duration):
        self.positionSlider.setRange(0, duration)

    def updatePosition(self, position):
        self.positionSlider.setValue(position)
    
    def setPosition(self, position):
        self.video_widget.media_player.setPosition(position)

    def updateState(self, state):
        if state == QMediaPlayer.PlayingState:
            self.statusLabel.setText('Playing')
        elif state == QMediaPlayer.PausedState:
            self.statusLabel.setText('Paused')
        elif state == QMediaPlayer.StoppedState:
            self.statusLabel.setText('Stopped')
            if self.repeatButton.isChecked():
                self.video_widget.media_player.setPosition(0)
                self.video_widget.media_player.play()   

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