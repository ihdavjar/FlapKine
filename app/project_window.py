import os
import pickle 
import numpy as np
from stl import mesh  
import plotly.graph_objects as go
import plotly.io as pio
import subprocess

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from src.utils.utils import create_video_from_frames


class ProjectWindow(QMainWindow):
    def __init__(self, project_folder):
        super(ProjectWindow, self).__init__()

        # Maximize the window
        self.showMaximized()

        # Storing the project folder
        self.project_folder = project_folder

        # Place the window in the center of the screen
        self.setWindowTitle("FlapKine")
        self.setWindowIcon(QIcon('app/assets/flap_kine_icon.png'))

        # Add the menu bar
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu('File')
        self.open_action = self.file_menu.addAction('Open')
        self.save_action = self.file_menu.addAction('Save')
        self.exit_action = self.file_menu.addAction('Exit')

        self.edit_menu = self.menu.addMenu('Edit')
        self.undo_action = self.edit_menu.addAction('Undo')
        self.redo_action = self.edit_menu.addAction('Redo')

        self.window_menu = self.menu.addMenu('Window')
        self.minimize_action = self.window_menu.addAction('Minimize')
        self.maximize_action = self.window_menu.addAction('Maximize')
        self.restore_action = self.window_menu.addAction('Restore')

        self.render_menu = self.menu.addMenu('Render')
        self.render_option = self.render_menu.addAction('Configure Render')

        self.help_menu = self.menu.addMenu('Help')
        self.about_action = self.help_menu.addAction('About') 

        # Process the project
        self.process_project()
        
        # Create the main widget and set it as the central widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Create the main layout
        main_layout = QHBoxLayout()

        # Create the right group box
        right_group = QGroupBox("Right Group")
        right_layout = QVBoxLayout()
        right_button = QPushButton("Right Button")
        right_label = QLabel("This is the right group")
        right_layout.addWidget(right_label)
        right_layout.addWidget(right_button)
        right_group.setLayout(right_layout)

        self.createLeftGroupBox()
        self.createRightGroupBox()
        # Add the group boxes to the main layout
        main_layout.addWidget(self.leftGroupBox)
        main_layout.addWidget(self.rightGroupBox)

        # Set the layout for the main widget
        main_widget.setLayout(main_layout)
    
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

    def process_project(self):
        scene_path = os.path.join(self.project_folder, 'scene.pkl')
        
        if not os.path.exists(scene_path):
            self.showErrorDialog('Error', f"No project found at: {self.project_folder}")
            
        else:
            with open(scene_path, 'rb') as scene_file:
                self.scene_data = pickle.load(scene_file)
                self.angles = self.scene_data.objects[0].angles

        
        
    def createLeftGroupBox(self):
        self.leftGroupBox = QGroupBox("Group 1")

        self.slider = QSlider(Qt.Orientation.Horizontal, self.leftGroupBox)
        self.slider.valueChanged.connect(self.printSliderValue)
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(self.angles)-1)
        self.slider.setValue(0)

        self.plotly_chart_view = QWebEngineView(self.leftGroupBox)

        layout = QVBoxLayout()
        layout.addWidget(self.slider)
        layout.addWidget(self.plotly_chart_view, 3)
        layout.addStretch(1)

        self.leftGroupBox.setLayout(layout)

        self.printSliderValue()

    def printSliderValue(self):
        value = self.slider.value()
        self.scene_data.save_stl(value, os.path.join(self.project_folder, f'data/stl/ellipse_temp.stl'))

        stl_filename = os.path.join(self.project_folder, f'data/stl/ellipse_temp.stl')

        your_mesh = mesh.Mesh.from_file(stl_filename)

        # Extract the vertices and faces
        vertices = your_mesh.vectors.reshape(-1, 3)
        x, y, z = vertices[:, 0], vertices[:, 1], vertices[:, 2]

        # Create a unique set of vertices and a list of faces
        unique_vertices, unique_indices = np.unique(vertices, axis=0, return_inverse=True)
        i, j, k = unique_indices.reshape(-1, 3).T

        # Create a 3D mesh plot
        fig = go.Figure(data=[go.Mesh3d(
            x=unique_vertices[:, 0],
            y=unique_vertices[:, 1],
            z=unique_vertices[:, 2],
            i=i,
            j=j,
            k=k,
            opacity=1,
            color='lightblue'
        )])

        # Set plot layout
        fig.update_layout(
            title='STL Mesh Plot',
            scene=dict(
                xaxis=dict(title='X'),
                yaxis=dict(title='Y'),
                zaxis=dict(title='Z')
            )
        )
        # Freeze the axis so that they don't auto-scale
        fig.update_scenes(aspectmode='cube')

        # Set x, y, z axis limits
        fig.update_layout(scene=dict(xaxis=dict(range=[-10, 10]), yaxis=dict(range=[-10, 10]), zaxis=dict(range=[-10, 10])))

        # Set the camera on the x axis at 1,0,0
        fig.update_layout(scene_camera=dict(eye=dict(x=1, y=0, z=0)))

        # Switch of the grid
        fig.update_layout(
        scene=dict(
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
        zaxis=dict(showgrid=False, zeroline=False),
    )
)   # Customize layout for dark theme
        fig.update_layout(
            scene=dict(
                xaxis=dict(
                    backgroundcolor='rgba(0,0,0,0)',  # Background color of the scene
                    gridcolor='white',  # Color of gridlines
                    showbackground=False,  # Hide the background
                    showgrid=False,  # Hide gridlines
                    zeroline=False,  # Hide the zero line
                    linecolor='white',  # Color of axis lines
                    tickfont=dict(color='white'),  # Color of tick labels
                ),
                yaxis=dict(
                    backgroundcolor='rgba(0,0,0,0)',  # Background color of the scene
                    gridcolor='white',  # Color of gridlines
                    showbackground=False,  # Hide the background
                    showgrid=False,  # Hide gridlines
                    zeroline=False,  # Hide the zero line
                    linecolor='white',  # Color of axis lines
                    tickfont=dict(color='white'),  # Color of tick labels
                ),
                zaxis=dict(
                    backgroundcolor='rgba(0,0,0,0)',  # Background color of the scene
                    gridcolor='white',  # Color of gridlines
                    showbackground=False,  # Hide the background
                    showgrid=False,  # Hide gridlines
                    zeroline=False,  # Hide the zero line
                    linecolor='white',  # Color of axis lines
                    tickfont=dict(color='white'),  # Color of tick labels
                ),
            ),
            plot_bgcolor='rgba(0,0,0,0)',  # Background color of the plot
        )


        filename = os.path.join(self.project_folder, 'scene.html')

        html = pio.to_html(fig, full_html=True)

        # saving the html
        with open(filename, 'w') as f:
            f.write(html)

        self.plotly_chart_view.load(QUrl.fromLocalFile(filename))
        
    
    def createRightGroupBox(self):
        self.rightGroupBox = QGroupBox("Group 2")

        self.render_button = QPushButton("Render")
        self.render_button.clicked.connect(self.render_new_video)

        # Video Related Widgets
        # Video Widget
        self.video_widget = QVideoWidget(self.rightGroupBox)
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)

        # Create play button
        self.playButton = QPushButton('Play')
        self.playButton.clicked.connect(self.playVideo)

        # Create pause button
        self.pauseButton = QPushButton('Pause')
        self.pauseButton.clicked.connect(self.pauseVideo)

        # Create repeat button
        self.repeatButton = QPushButton('Repeat')
        self.repeatButton.setCheckable(True)
        self.repeatButton.clicked.connect(self.repeatVideo)

        # Create slider for video position
        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        # Connect media player signals
        self.media_player.durationChanged.connect(self.updateDuration)
        self.media_player.positionChanged.connect(self.updatePosition)
        self.media_player.stateChanged.connect(self.updateState)

        controlLayout = QHBoxLayout()
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.pauseButton)
        controlLayout.addWidget(self.repeatButton)  

        video_path = os.path.join(self.project_folder, 'data/videos/stl_animation_temp.mp4')

        if not os.path.exists(video_path):
            self.showErrorDialog('Alert', f"No render found at: {self.project_folder}")
        
        else:
            video_content = QMediaContent(QUrl.fromLocalFile(video_path))
            self.media_player.setMedia(video_content)
            self.media_player.play()
            
        layout = QVBoxLayout()
        layout.addWidget(self.render_button)
        layout.addLayout(controlLayout)
        layout.addWidget(self.positionSlider)
        layout.addWidget(self.video_widget)
        if self.repeatButton.isChecked():
            layout.addWidget(self.progress)
        layout.addStretch(1)
        self.rightGroupBox.setLayout(layout)

    def playVideo(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            return
        self.media_player.play()

    def pauseVideo(self):
        if self.media_player.state() == QMediaPlayer.PausedState:
            return
        self.media_player.pause()
    
    def repeatVideo(self):
        if self.repeatButton.isChecked():
            self.media_player.setPosition(0)
            self.media_player.play()

    def updateDuration(self, duration):
        self.positionSlider.setRange(0, duration)

    def updatePosition(self, position):
        self.positionSlider.setValue(position)
    
    def setPosition(self, position):
        self.media_player.setPosition(position)

    def updateState(self, state):
        if state == QMediaPlayer.StoppedState:
            if self.repeatButton.isChecked():
                self.media_player.setPosition(0)
                self.media_player.play()

    def render_new_video(self):
        stl_filename = os.path.join(self.project_folder, 'data/stl')
        
        # Progress bar
        self.progress = QProgressDialog("Rendering video...", "Cancel", 0, len(self.angles), self)
        # Save the STL files
        for i in range(len(self.angles)):
            self.scene_data.save_stl(i, os.path.join(stl_filename, f'ellipse_{i}.stl'))
            self.progress.setValue(i)

        blender_script = "src/blender/generate_frames.py"

        subprocess.run(["python", blender_script, '--project_path', self.project_folder])

        frames_path = os.path.join(self.project_folder, 'data/images')
        video_path = os.path.join(self.project_folder, "data/videos/stl_animation_temp.mp4")

        # Create the video
        create_video_from_frames(frames_path, video_path, frame_rate=20, width=640, height=480, libx264=False)

        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
        

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