import os
import json
import pickle
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import qtawesome as qta

from app.ui.editor.project_editor import ProjectWindow
from app.ui.creators.scene_creator import CreateScene
from app.widgets.menu_bar import MenuBar

class ProjectCreator(QMainWindow): 

    def __init__(self, project_folder):
        super(ProjectCreator, self).__init__()
        # Place the window in the center of the screen
        self.setWindowTitle("Import Scene")

        # Set the icon
        self.setWindowIcon(QIcon(os.path.join('app', 'assets', 'flapkine_icon.png')))

        self.project_folder = project_folder
        
        # Add the menu bar
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)
    
        self.menu_bar.connect_actions({
            'exit': self.close,
            'minimize': self.showMinimized,
            'maximize': self.showMaximized,
            'restore': self.showNormal,
            'about': self.about_button_fun,
        })

        self.initUI()

    def initUI(self):
        self.center()

        primary_color = self.palette().color(self.foregroundRole()).name()

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create the main layout
        self.main_layout = QVBoxLayout(central_widget)

        box1 = QHBoxLayout()
        box2 = QHBoxLayout()

        # SCENE
        scene_import = QWidget()
        label = QLabel('Import Scene', self)
        label.setFont(QFont('Times', 9))
        # Add the two buttons side by side
        self.open_button = QPushButton('Open', self)
        self.open_button.setFont(QFont('Times', 8))
        self.open_button.setIcon(qta.icon("fa5.folder-open", color=primary_color))
        self.open_button.clicked.connect(self.import_scene)

        self.text_editor_scene = QLineEdit()
        
        self.create_button = QPushButton('Create', self)
        self.create_button.setFont(QFont('Times', 8))
        self.create_button.setIcon(qta.icon("mdi.folder-plus-outline", color=primary_color))
        self.create_button.clicked.connect(self.create_scene)

        # CONFIG
        config_options = QWidget()
        self.default_config_checkbox = QCheckBox('Use Default Config', self)
        self.default_config_checkbox.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        self.default_config_checkbox.setChecked(False)
        self.default_config_checkbox.stateChanged.connect(self.process_default_config)

        self.import_config_button = QPushButton('New Config', self)
        self.import_config_button.setFont(QFont('Times', 8))
        self.import_config_button.setCheckable(True)
        self.import_config_button.setChecked(False)
        self.import_config_button.toggled.connect(self.create_new_config)

        box1.addWidget(label)
        box1.addWidget(self.text_editor_scene)
        box1.addWidget(self.open_button)
        box1.addWidget(self.create_button)
        scene_import.setLayout(box1)

        box2.addWidget(self.default_config_checkbox)
        box2.addWidget(self.import_config_button)
        config_options.setLayout(box2)


        ############################ CONFIG WINDOW ############################
        self.config_group = QGroupBox("Configurations")
        self.config_group.setFont(QFont('Times', 9))

        self.config_layout = QVBoxLayout()

        # VIDEORENDER
        video_group = QGroupBox("Video Settings")
        video_group.setFont(QFont('Times', 8))
        video_group.setStyleSheet("""
QGroupBox {
    color: #3498db;  /* Title text color (blue) */
    font-weight: bold;
    border: 2px solid #2980b9; /* Border color */
    border-radius: 5px;
    margin-top: 10px; /* Space between border and title */
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left; /* Positioning title */
    padding: 5px; /* Space around title */
}
""")

        
        video_settings = QVBoxLayout()

        # Image Format Settings
        image_settings = QHBoxLayout()
        image_settings_label = QLabel("Frame Format")
        image_settings_label.setFont(QFont('Times', 7))

        self.frame_format = QComboBox()
        self.frame_format.addItems(['PNG', 'JPEG', 'TIFF'])
        self.frame_format.setFont(QFont('Times', 7))
        self.frame_format.setCurrentIndex(0)
        image_settings.addWidget(image_settings_label)
        image_settings.addWidget(self.frame_format)
        
        # Image/ Video Resolution Settings
        self.resolution_settings = QHBoxLayout()  

        res_x = QHBoxLayout() 
        res_x_wid = QWidget()
        res_x_label = QLabel("  X:")
        res_x_label.setFont(QFont('Times', 7))
        self.resolution_x = QSpinBox()
        self.resolution_x.setMinimum(0)
        self.resolution_x.setMaximum(1920)
        res_x.addWidget(res_x_label)
        res_x.addWidget(self.resolution_x)
        res_x_wid.setLayout(res_x)

        res_y = QHBoxLayout()
        res_y_wid = QWidget()
        res_y_label = QLabel("  Y:")
        res_y_label.setFont(QFont('Times', 7))
        self.resolution_y = QSpinBox()
        self.resolution_y.setMinimum(0)
        self.resolution_y.setMaximum(1080)
        res_y.addWidget(res_y_label)
        res_y.addWidget(self.resolution_y)
        res_y_wid.setLayout(res_y)
        
        res_title = QLabel("Resolution")
        res_title.setFont(QFont('Times', 7))
        self.resolution_settings.addWidget(res_title)
        self.resolution_settings.addWidget(res_x_wid)
        self.resolution_settings.addWidget(res_y_wid)
        
        
        video_settings.addLayout(image_settings)
        video_settings.addLayout(self.resolution_settings)
        video_group.setLayout(video_settings)

        # CAMERA
        camera_setting_grp = QGroupBox("Camera Settings")
        camera_setting_grp.setFont(QFont('Times', 8))

        camera_setting_grp.setStyleSheet("""
QGroupBox {
    color: #16a085;  /* Teal - Title text */
    font-weight: bold;
    border: 2px solid #13876a; /* Darker Teal - Border */
    border-radius: 6px;
    margin-top: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 5px;
}
""")

        Camera_settings = QVBoxLayout()

        camera_location = QHBoxLayout()
        camera_rotation = QHBoxLayout()

        cam_x_wid = QWidget()
        cam_x = QHBoxLayout()
        cam_x_label = QLabel("X:")
        cam_x_label.setFont(QFont('Times', 7))
        self.camera_location_x = QDoubleSpinBox()
        self.camera_location_x.setRange(-1000, 1000)
        cam_x.addWidget(cam_x_label)
        cam_x.addWidget(self.camera_location_x)
        cam_x_wid.setLayout(cam_x)

        cam_y_wid = QWidget()
        cam_y = QHBoxLayout()
        cam_y_label = QLabel("Y:")
        cam_y_label.setFont(QFont('Times', 7))
        self.camera_location_y = QDoubleSpinBox()
        self.camera_location_y.setRange(-1000, 1000)
        cam_y.addWidget(cam_y_label)
        cam_y.addWidget(self.camera_location_y)
        cam_y_wid.setLayout(cam_y)

        cam_z_wid = QWidget()
        cam_z = QHBoxLayout()
        cam_z_label = QLabel("Z:")
        cam_z_label.setFont(QFont('Times', 7))
        self.camera_location_z = QDoubleSpinBox()
        self.camera_location_z.setRange(-1000, 1000)
        cam_z.addWidget(cam_z_label)
        cam_z.addWidget(self.camera_location_z)
        cam_z_wid.setLayout(cam_z)
    

        cam_alpha_wid = QWidget()
        cam_alpha = QHBoxLayout()
        cam_alpha_label = QLabel("X:")
        self.camera_rotation_alpha = QDoubleSpinBox()
        self.camera_rotation_alpha.setRange(-360, 360)
        cam_alpha.addWidget(cam_alpha_label)
        cam_alpha.addWidget(self.camera_rotation_alpha)
        cam_alpha_wid.setLayout(cam_alpha)

        cam_beta_wid = QWidget()
        cam_beta = QHBoxLayout()
        cam_beta_label = QLabel("Y:")
        self.camera_rotation_beta = QDoubleSpinBox()
        self.camera_rotation_beta.setRange(-360, 360)
        cam_beta.addWidget(cam_beta_label)
        cam_beta.addWidget(self.camera_rotation_beta)
        cam_beta_wid.setLayout(cam_beta)

        cam_gamma_wid = QWidget()
        cam_gamma = QHBoxLayout()
        cam_gamma_label = QLabel("Z:")
        self.camera_rotation_gamma = QDoubleSpinBox()
        self.camera_rotation_gamma.setRange(-360, 360)
        cam_gamma.addWidget(cam_gamma_label)
        cam_gamma.addWidget(self.camera_rotation_gamma)
        cam_gamma_wid.setLayout(cam_gamma)

        camera_location.addWidget(QLabel('Location'))
        camera_location.addWidget(cam_x_wid)
        camera_location.addWidget(cam_y_wid)
        camera_location.addWidget(cam_z_wid)

        camera_rotation.addWidget(QLabel('Rotation'))
        camera_rotation.addWidget(cam_alpha_wid)
        camera_rotation.addWidget(cam_beta_wid)
        camera_rotation.addWidget(cam_gamma_wid)

        Camera_settings.addLayout(camera_location)
        Camera_settings.addLayout(camera_rotation)
        camera_setting_grp.setLayout(Camera_settings)

        # LIGHT SETTINGS
        light_setting_grp = QGroupBox("Light Settings")
        light_setting_grp.setFont(QFont('Times', 8))
        light_setting_grp.setStyleSheet("""
QGroupBox {
    color: #e67e22;  /* Orange - Title text */
    font-weight: bold;
    border: 2px solid #d35400; /* Darker Orange - Border */
    border-radius: 6px;
    margin-top: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 5px;
}
""")

        Light_settings = QVBoxLayout()

        light_location = QHBoxLayout()
        light_power = QHBoxLayout()

        # X Coordinate
        light_x_wid = QWidget()
        light_x = QHBoxLayout()
        light_x_label = QLabel("X:")
        light_x_label.setFont(QFont('Times', 7))
        self.light_location_x = QDoubleSpinBox()
        self.light_location_x.setRange(-1000, 1000)
        light_x.addWidget(light_x_label)
        light_x.addWidget(self.light_location_x)
        light_x_wid.setLayout(light_x)

        # Y Coordinate
        light_y_wid = QWidget()
        light_y = QHBoxLayout()
        light_y_label = QLabel("Y:")
        light_y_label.setFont(QFont('Times', 7))
        self.light_location_y = QDoubleSpinBox()
        self.light_location_y.setRange(-1000, 1000)
        light_y.addWidget(light_y_label)
        light_y.addWidget(self.light_location_y)
        light_y_wid.setLayout(light_y)

        # Z Coordinate
        light_z_wid = QWidget()
        light_z = QHBoxLayout()
        light_z_label = QLabel("Z:")
        light_z_label.setFont(QFont('Times', 7))
        self.light_location_z = QDoubleSpinBox()
        self.light_location_z.setRange(-1000, 1000)
        light_z.addWidget(light_z_label)
        light_z.addWidget(self.light_location_z)
        light_z_wid.setLayout(light_z)

        # Power Setting
        light_power_wid = QWidget()
        light_power_layout = QHBoxLayout()
        light_power_label = QLabel("Power:")
        light_power_label.setFont(QFont('Times', 7))
        self.light_power = QSpinBox()
        self.light_power.setMinimum(0)
        self.light_power.setMaximum(10000)
        light_power_layout.addWidget(light_power_label)
        light_power_layout.addWidget(self.light_power)
        light_power_wid.setLayout(light_power_layout)

        # Add widgets to layouts
        light_location.addWidget(QLabel("Location"))
        light_location.addWidget(light_x_wid)
        light_location.addWidget(light_y_wid)
        light_location.addWidget(light_z_wid)

        light_power.addWidget(QLabel("Power"))
        light_power.addWidget(light_power_wid)

        Light_settings.addLayout(light_location)
        Light_settings.addLayout(light_power)
        light_setting_grp.setLayout(Light_settings)
        
        self.config_layout.addWidget(video_group)
        self.config_layout.addWidget(camera_setting_grp)
        self.config_layout.addWidget(light_setting_grp)
        self.config_group.setLayout(self.config_layout)
        self.config_group.setEnabled(False)

        ############################ OTHER SETTINGS ############################
        other_settings_group = QGroupBox("Other Settings")
        other_settings_group.setFont(QFont('Times', 9))

        other_settings_group.setStyleSheet("""
QGroupBox {
    color: #9b59b6;  /* Purple - Title text */
    font-weight: bold;
    border: 2px solid #8e44ad; /* Darker Purple - Border */
    border-radius: 6px;
    margin-top: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 5px;
}   
""")
        other_settings = QHBoxLayout()

        ############################ STL CONFIG ############################
        self.stl_enable = QCheckBox("Save STL")
        self.stl_enable.setFont(QFont('Times', 8))
        
        stl_layout = QHBoxLayout()
        stl_layout.addWidget(self.stl_enable)
        
        ############################ REFLECT CONFIG ########################

        reflect_label = QLabel("Reflect about Axes: ")
        reflect_label.setFont(QFont('Times', 8))
        self.reflect_xy = QCheckBox('XY')
        self.reflect_yz = QCheckBox('YZ')
        self.reflect_xz = QCheckBox('XZ')

        # Connect each checkbox to the toggle function
        self.reflect_xy.toggled.connect(lambda: self.toggle_checkboxes(self.reflect_xy))
        self.reflect_yz.toggled.connect(lambda: self.toggle_checkboxes(self.reflect_yz))
        self.reflect_xz.toggled.connect(lambda: self.toggle_checkboxes(self.reflect_xz))

        reflect_layout = QHBoxLayout()
        reflect_layout.addWidget(reflect_label)
        reflect_layout.addWidget(self.reflect_xy)
        reflect_layout.addWidget(self.reflect_yz)
        reflect_layout.addWidget(self.reflect_xz)

    
        other_settings.addLayout(stl_layout)
        other_settings.addLayout(reflect_layout)
        other_settings_group.setLayout(other_settings)

        ############################ OK BUTTON ############################
        self.ok_button = QPushButton('Create Project', self)
        self.ok_button.clicked.connect(self.create_the_project)
        
        self.main_layout.addWidget(scene_import)
        self.main_layout.addWidget(config_options)
        self.main_layout.addWidget(self.config_group)
        self.main_layout.addWidget(other_settings_group)
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

            with open('src/config/default_config.json', 'r') as file:
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

            if config['Reflect'] == 'XY':
                self.reflect_xy.setChecked(True)
            elif config['Reflect'] == 'YZ':
                self.reflect_yz.setChecked(True)
            elif config['Reflect'] == 'XZ':
                self.reflect_xz.setChecked(True)
            else:
                self.reflect_xy.setChecked(False)
                self.reflect_yz.setChecked(False)
                self.reflect_xz.setChecked(False)

            self.config_group.setEnabled(True)
            self.stl_enable.setChecked(config['STL'])

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

            self.reflect_xy.setChecked(False)
            self.reflect_yz.setChecked(False)
            self.reflect_xz.setChecked(False)
            self.stl_enable.setChecked(False)

        else:
            self.config_group.setEnabled(False)

    def create_the_project(self):

        # Create the project directory
        os.makedirs(self.project_folder)
        
        # Create data directory
        os.makedirs(self.project_folder + '/data')
        os.makedirs(self.project_folder + '/data/images')
        os.makedirs(self.project_folder + '/data/videos')

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
            },
            'STL': True if self.stl_enable.isChecked() else False,
            
            'Reflect': 'XY' if self.reflect_xy.isChecked() else 'YZ' if self.reflect_yz.isChecked() else 'XZ' if self.reflect_xz.isChecked() else None
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

    def toggle_checkboxes(self, checked_box):
        """Ensures only one checkbox is checked at a time."""
        if checked_box.isChecked():
            # Uncheck all other checkboxes
            for box in [self.reflect_xy, self.reflect_yz, self.reflect_xz]:
                if box != checked_box:
                    box.setChecked(False)
    
    def about_button_fun(self):
        QMessageBox.about(self, "About FlapKine", '''
        <h1>FlapKine</h1>
        <p>Developed by: Kalbhavi Vadhiraj</p>                  
        <p>Version 0.0.1</p>
        <p>FlapKine provides a visual representation and simulation of the kinematics and aerodynamics of flapping wing micro-aerial vehicles (MAVs). It allows users to analyze and optimize MAV designs with precision and clarity, revealing the intricate mechanics of flapping flight. Whether for research, development, or educational purposes, this tool offers valuable insights into the performance and behavior of MAVs, facilitating advanced design and innovation.</p> 
''')