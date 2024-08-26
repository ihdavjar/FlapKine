import os
import json
import pickle
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from app.project_window.open_project.project_window import ProjectWindow
from app.project_window.create_project.create_scene import CreateScene

class CreateProjectWin(QMainWindow):
    def __init__(self, project_folder):
        super(CreateProjectWin, self).__init__()
        # Place the window in the center of the screen
        self.setWindowTitle("Import Scene")

        # Set the icon
        self.setWindowIcon(QIcon(os.path.join('app', 'assets', 'flap_kine_icon.png')))

        self.project_folder = project_folder
        
        # Add the menu bar
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu('File')
        self.open_action = self.file_menu.addAction('New')
        self.open_action.setEnabled(False)
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

        self.render_menu = self.menu.addMenu('Render')
        self.render_option = self.render_menu.addAction('Configure Render')
        self.render_option.setEnabled(False)

        self.help_menu = self.menu.addMenu('Help')
        self.about_action = self.help_menu.addAction('About')  
        self.about_action.triggered.connect(self.about_button_fun)

        self.initUI()

    def initUI(self):
            self.center()

            # Central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            # Create the main layout
            self.main_layout = QVBoxLayout(central_widget)

            box1 = QHBoxLayout()
            box2 = QHBoxLayout()

            # SCENE
            # Add text
            label = QLabel('Import Scene', self)
            # Add the two buttons side by side
            self.open_button = QPushButton('Open', self)
            self.open_button.clicked.connect(self.import_scene)

            self.text_editor_scene = QLineEdit()
            
            self.create_button = QPushButton('Create', self)
            self.create_button.clicked.connect(self.create_scene)

            # CONFIG
            self.default_config_checkbox = QCheckBox('Use Default Config', self)
            self.default_config_checkbox.setChecked(False)
            self.default_config_checkbox.stateChanged.connect(self.process_default_config)

            self.import_config_button = QPushButton('New Config', self)
            self.import_config_button.setCheckable(True)
            self.import_config_button.setChecked(False)
            self.import_config_button.toggled.connect(self.create_new_config)

            box1.addWidget(label)
            box1.addWidget(self.text_editor_scene)
            box1.addWidget(self.open_button)
            box1.addWidget(self.create_button)

            box2.addWidget(self.default_config_checkbox)
            box2.addWidget(self.import_config_button)


            ############################ CONFIG WINDOW ############################
            self.config_group = QGroupBox("Configurations")
            self.config_group.setFont(QFont('Times', 9))

            self.config_layout = QVBoxLayout()

            # VIDEORENDER
            Video_settings = QVBoxLayout()
            self.video_label = QLabel('Video Settings')
            self.video_label.setFont(QFont('Times', 9))

            self.frame_format = QComboBox()
            self.frame_format.addItems(['PNG', 'JPEG', 'TIFF'])
            self.frame_format.setCurrentIndex(0)

            self.resolution_settings = QHBoxLayout()    
            self.resolution_x = QSpinBox()
            self.resolution_x.setMinimum(0)
            self.resolution_x.setMaximum(1920)

            self.resolution_y = QSpinBox()
            self.resolution_y.setMinimum(0)
            self.resolution_y.setMaximum(1080)

            self.resolution_settings.addWidget(QLabel('Resolution'))
            self.resolution_settings.addWidget(self.resolution_x)
            self.resolution_settings.addWidget(self.resolution_y)

            Video_settings.addWidget(self.video_label)
            Video_settings.addWidget(self.frame_format)
            Video_settings.addLayout(self.resolution_settings)

            # CAMERA
            Camera_settings = QVBoxLayout()
            self.camera_label = QLabel('Camera Settings')
            self.camera_label.setFont(QFont('Times', 9))

            camera_location = QHBoxLayout()
            camera_rotation = QHBoxLayout()

            self.camera_location_x = QDoubleSpinBox()
            self.camera_location_x.setRange(-1000, 1000)
            self.camera_location_y = QDoubleSpinBox()
            self.camera_location_y.setRange(-1000, 1000)
            self.camera_location_z = QDoubleSpinBox()
            self.camera_location_z.setRange(-1000, 1000)

            self.camera_rotation_alpha = QDoubleSpinBox()
            self.camera_rotation_alpha.setRange(-360, 360)
            self.camera_rotation_beta = QDoubleSpinBox()
            self.camera_rotation_beta.setRange(-360, 360)
            self.camera_rotation_gamma = QDoubleSpinBox()
            self.camera_rotation_gamma.setRange(-360, 360)

            camera_location.addWidget(QLabel('Location'))
            camera_location.addWidget(self.camera_location_x)
            camera_location.addWidget(self.camera_location_y)
            camera_location.addWidget(self.camera_location_z)

            camera_rotation.addWidget(QLabel('Rotation'))
            camera_rotation.addWidget(self.camera_rotation_alpha)
            camera_rotation.addWidget(self.camera_rotation_beta)
            camera_rotation.addWidget(self.camera_rotation_gamma)

            Camera_settings.addWidget(self.camera_label)
            Camera_settings.addLayout(camera_location)
            Camera_settings.addLayout(camera_rotation)

            # LIGHTS
            Light_settings = QVBoxLayout()
            self.light_label = QLabel('Light Settings')
            self.light_label.setFont(QFont('Times', 9))

            light_location = QHBoxLayout()
            light_power = QHBoxLayout()

            self.light_location_x = QDoubleSpinBox()
            self.light_location_x.setRange(-1000, 1000)
            self.light_location_y = QDoubleSpinBox()
            self.light_location_y.setRange(-1000, 1000)
            self.light_location_z = QDoubleSpinBox()
            self.light_location_z.setRange(-1000, 1000)

            self.light_power = QSpinBox()
            self.light_power.setMinimum(0)
            self.light_power.setMaximum(10000)

            light_location.addWidget(QLabel('Location'))
            light_location.addWidget(self.light_location_x)
            light_location.addWidget(self.light_location_y)
            light_location.addWidget(self.light_location_z)

            light_power.addWidget(QLabel('Power'))
            light_power.addWidget(self.light_power)
        
            Light_settings.addWidget(self.light_label)
            Light_settings.addLayout(light_location)
            Light_settings.addLayout(light_power)
            
            self.config_layout.addLayout(Video_settings)
            self.config_layout.addLayout(Camera_settings)
            self.config_layout.addLayout(Light_settings)
            self.config_group.setLayout(self.config_layout)

            self.config_group.setEnabled(False)

            self.ok_button = QPushButton('Create Project', self)
            self.ok_button.clicked.connect(self.create_the_project)
            
            self.main_layout.addLayout(box1)
            self.main_layout.addLayout(box2)
            self.main_layout.addWidget(self.config_group)
            self.main_layout.addWidget(self.ok_button)

    def import_scene(self):
        directory, _ = QFileDialog.getOpenFileName(filter='Scene File (*.pkl)')
        
        if directory:
            self.directory_scene = directory
            self.text_editor_scene.setText(self.directory_scene)

        # Make the button glow green
        self.open_button.setStyleSheet('background-color: green')

    def create_scene(self):
        self.window2 = CreateScene()
        self.window2.show()
        self.window2.sceneCreated.connect(self.on_scene_created)

    
    def on_scene_created(self, scene_data):
        self.scene_data = scene_data
        # Make the button glow green
        self.create_button.setStyleSheet('background-color: green')
        
    def process_default_config(self):
        if self.default_config_checkbox.isChecked():

            with open('src/config/config.json', 'r') as file:
                config = json.load(file)

            self.frame_format.setCurrentIndex(0)
            self.resolution_x.setValue(config['VideoRender']['resolution_x'])
            self.resolution_y.setValue(config['VideoRender']['resolution_y'])
            
            self.camera_location_x.setValue(config['Camera']['location'][0])
            self.camera_location_y.setValue(config['Camera']['location'][1])
            self.camera_location_z.setValue(config['Camera']['location'][2])

            self.camera_rotation_alpha.setValue(config['Camera']['rotation_euler'][0])
            self.camera_rotation_beta.setValue(config['Camera']['rotation_euler'][1])
            self.camera_rotation_gamma.setValue(config['Camera']['rotation_euler'][2])

            self.light_location_x.setValue(config['Light']['location'][0])
            self.light_location_y.setValue(config['Light']['location'][1])
            self.light_location_z.setValue(config['Light']['location'][2])

            self.light_power.setValue(config['Light']['energy'])

            self.config_group.setEnabled(True)
        else:
            self.config_group.setEnabled(False)
    
    def create_new_config(self):
        if self.import_config_button.isChecked():

            self.frame_format.setCurrentIndex(0)
            self.resolution_x.setValue(640)
            self.resolution_y.setValue(480)

            self.camera_location_x.setValue(0)
            self.camera_location_y.setValue(0)
            self.camera_location_z.setValue(0)

            self.camera_rotation_alpha.setValue(0)
            self.camera_rotation_beta.setValue(0)
            self.camera_rotation_gamma.setValue(0)

            self.light_location_x.setValue(0)
            self.light_location_y.setValue(0)
            self.light_location_z.setValue(0)

            self.light_power.setValue(0)

            self.config_group.setEnabled(True)
        else:
            self.config_group.setEnabled(False)

    def create_the_project(self):

        # Create the project directory
        os.makedirs(self.project_folder)
        
        # Create data directory
        os.makedirs(self.project_folder + '/data')
        os.makedirs(self.project_folder + '/data/images')
        os.makedirs(self.project_folder + '/data/videos')
        os.makedirs(self.project_folder + '/data/stl')

        # Copy the scene file to the project folder
        if not hasattr(self, 'scene_data'):
            scene_name = os.path.basename(self.directory_scene)
            scene_destination = os.path.join(self.project_folder, 'scene.pkl')
            os.system(f'cp {self.directory_scene} {scene_destination}')
        
        else: # Dump the scene data to the project folder
            scene_destination = os.path.join(self.project_folder, 'scene.pkl')
            pickle.dump(self.scene_data, open(scene_destination, 'wb'))



        # Save the config file
        config = {
            'VideoRender': {
                'OutputPath': 'data/images',
                'STLPath': 'data/stl',
                'FrameFormat': self.frame_format.currentText()  ,
                'resolution_x': self.resolution_x.value(),
                'resolution_y': self.resolution_y.value(),
                'film_transparent': False,
            },
            'Camera': {
                'location': [self.camera_location_x.value(), self.camera_location_y.value(), self.camera_location_z.value()],
                'rotation_euler': [self.camera_rotation_alpha.value(), self.camera_rotation_beta.value(), self.camera_rotation_gamma.value()]
            },
            'Light': {
                'location': [self.light_location_x.value(), self.light_location_y.value(), self.light_location_z.value()],
                'energy': self.light_power.value()
            }
        }

        with open(os.path.join(self.project_folder, 'config.json'), 'w') as file:
            json.dump(config, file)
        
        # Rendering the scene
        self.window2 = ProjectWindow(self.project_folder)
        self.window2.show()
        self.close()
            
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

    ######################################## MENU BAR ########################################
    def about_button_fun(self):
        QMessageBox.about(self, "About FlapKine", '''
        <h1>FlapKine</h1>
        <p>Developed by: Kalbhavi Vadhiraj</p>                  
        <p>Version 0.0.1</p>
        <p>FlapKine provides a visual representation and simulation of the kinematics and aerodynamics of flapping wing micro-aerial vehicles (MAVs). It allows users to analyze and optimize MAV designs with precision and clarity, revealing the intricate mechanics of flapping flight. Whether for research, development, or educational purposes, this tool offers valuable insights into the performance and behavior of MAVs, facilitating advanced design and innovation.</p> 
''')