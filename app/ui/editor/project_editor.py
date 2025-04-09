import os
import pickle 
import numpy as np
import json

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from src.core.transforms.vtk_transform import *
from app.widgets.misc.render_config_edit import RenderConfig
import vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from app.widgets.misc.menu_bar import MenuBar
from app.widgets.main.frame_visualiser import Visualizer3DWidget


import os
import json
from PyQt5.QtCore import QThread, pyqtSignal, Qt
import bpy
        
from app.widgets.main.video_animation import VideoAnimation
from app.widgets.main.frame_visualiser import Visualizer3DWidget
from app.widgets.main.point_visualiser import PointScatterWidget
    

    
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

       # --- MAIN SPLITTER: Horizontal (Left and Right) ---
        main_splitter = QSplitter(Qt.Horizontal)

        # ------------------------ RIGHT PANE ------------------------
        self.right_group = PointScatterWidget(self.scene_data)
        main_splitter.addWidget(self.right_group)
        self.right_group.setMinimumSize(400, 800)

        # ------------------------ LEFT PANE ------------------------
        left_splitter = QSplitter(Qt.Vertical)

        # --- Top Left Group: Video Animation ---
        self.topleftgroup = VideoAnimation(self.project_folder, self.scene_data)
        topleft_groupbox = QGroupBox("Video Animation")
        topleft_layout = QVBoxLayout()
        topleft_layout.addWidget(self.topleftgroup)
        topleft_groupbox.setLayout(topleft_layout)
        topleft_groupbox.setMinimumSize(640, 400)

        # --- Bottom Left Group: 3D Visualizer ---
        self.bottomleftgroup = Visualizer3DWidget(self.scene_data, self.project_folder, self.angles)
        bottomleft_groupbox = QGroupBox("3D Visualizer")
        bottomleft_layout = QVBoxLayout()
        bottomleft_layout.addWidget(self.bottomleftgroup)
        bottomleft_groupbox.setLayout(bottomleft_layout)
        bottomleft_groupbox.setMinimumSize(640, 400)

        # Add grouped widgets to left splitter
        left_splitter.addWidget(topleft_groupbox)
        left_splitter.addWidget(bottomleft_groupbox)
        left_splitter.setSizes([400, 400])

        # Insert left side into main splitter
        main_splitter.insertWidget(0, left_splitter)
        main_splitter.setSizes([880, 400])  # Left pane wider

        # Add to main layout
        main_layout.addWidget(main_splitter)

    def process_project(self):
        scene_path = os.path.join(self.project_folder, 'scene.pkl')
        
        if not os.path.exists(scene_path):
            self.showErrorDialog('Error', f"No project found at: {self.project_folder}")
            
        else:
            with open(scene_path, 'rb') as scene_file:
                self.scene_data = pickle.load(scene_file)
                self.angles = self.scene_data.objects[0].angles


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