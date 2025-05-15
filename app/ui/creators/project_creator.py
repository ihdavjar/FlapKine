import os
import sys
import json
import pickle

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QFont, QIcon, QDesktopServices
from PyQt5.QtWidgets import (
    QCheckBox, QComboBox, QFileDialog, QDesktopWidget, QDoubleSpinBox,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox,
    QPushButton, QSpinBox, QVBoxLayout, QWidget
)

from qtawesome import icon

from version import __version__
from app.ui.creators.scene_creator import SceneCreator
from app.ui.editor.project_editor import ProjectWindow
from app.widgets.misc.menu_bar import MenuBar

class ProjectCreator(QMainWindow):
    """
    ProjectCreator Class
    ====================

    This class defines the main GUI window for the FlapKine project creation module.

    It enables importing or generating scene data, configuring essential parameters such as
    video resolution, camera and lighting setup, STL output, and reflection properties,
    and finalizing the project setup with or without default configuration profiles.

    Attributes
    ----------
    project_folder : str
        Path to the directory where the new project will be initialized.

    menu_bar : MenuBar
        Custom top menu bar that handles application-level actions like exit or minimize.

    text_editor_scene : QLineEdit
        Input field for the path of the scene file to import.

    open_button : QPushButton
        Opens a file dialog to import a scene.

    create_button : QPushButton
        Launches the CreateScene window to generate a new scene.

    default_config_checkbox : QCheckBox
        Enables or disables using default configuration settings.

    import_config_button : QPushButton
        Button to initiate creation of a custom configuration profile.

    config_group : QGroupBox
        Group box containing all video, camera, and light configuration controls.

    frame_format : QComboBox
        Dropdown menu for selecting video frame format (e.g., PNG, JPEG).

    resolution_x : QSpinBox
        Sets the horizontal resolution of the output video.

    resolution_y : QSpinBox
        Sets the vertical resolution of the output video.

    camera_location_x : QDoubleSpinBox
    camera_location_y : QDoubleSpinBox
    camera_location_z : QDoubleSpinBox
        Spin boxes for defining camera position in 3D space.

    camera_focal_x : QDoubleSpinBox
    camera_focal_y : QDoubleSpinBox
    camera_focal_z : QDoubleSpinBox
        Spin boxes for defining camera focal point in 3D space.

    light_location_x : QDoubleSpinBox
    light_location_y : QDoubleSpinBox
    light_location_z : QDoubleSpinBox
        Spin boxes for defining light position in 3D space.

    light_power : QSpinBox
        Sets the power level of the scene lighting.

    stl_enable : QCheckBox
        Enables STL file generation for the final output.

    reflect_xy : QCheckBox
    reflect_yz : QCheckBox
    reflect_xz : QCheckBox
        Checkboxes to enable reflection across the XY, YZ, or XZ planes respectively.

    ok_button : QPushButton
        Finalizes the creation of the project with all selected settings.

    Methods
    -------
    __init__(project_folder: str):
        Initializes the window and sets up the user interface and interactions.

    initUI():
        Composes and organizes the complete interface layout.

    setup_central_widget():
        Defines the central widget and primary layout structure.

    setup_scene_import(primary_color: str):
        Initializes the section for importing or creating scenes.

    setup_config_options():
        Adds toggle options for using default or custom configurations.

    setup_config_group(primary_color: str):
        Builds the configuration container for video, camera, and light settings.

    setup_video_settings():
        Adds UI elements related to video format and resolution.

    setup_resolution_inputs():
        Assembles spin boxes for video resolution input.

    setup_camera_settings():
        Adds input fields for configuring camera position and orientation.

    add_camera_controls(location_layout: QHBoxLayout, rotation_layout: QHBoxLayout):
        Populates the camera control section with coordinate and rotation controls.

    setup_light_settings():
        Adds input fields for configuring light source position and power.

    setup_other_settings():
        Adds extra controls for STL export and axis-based reflection.

    import_scene():
        Opens a file dialog to allow users to select and import a scene file.

    create_scene():
        Opens the CreateScene interface for building new scenes.

    on_scene_created(scene_data: dict):
        Callback function that processes newly created scene data.

    process_default_config():
        Loads and applies default configuration presets.

    create_new_config():
        Opens the interface for defining a new custom configuration.

    create_the_project():
        Consolidates all inputs and generates the project directory and metadata.

    center():
        Moves the window to the center of the user's screen.

    toggle_checkboxes(checked_box: QCheckBox):
        Ensures only one axis reflection checkbox can be active at a time.

    about_button_fun():
        Displays application and author information in an About dialog.
    """

    def __init__(self, project_folder):
        """
        Initializes the ProjectCreator class.

        Sets up the main window for the FlapKine project creation interface. Configures window properties
        such as title and icon, assigns the target project folder, initializes the custom menu bar with
        connected actions, and builds the main UI using `initUI()`.

        Components Initialized:
            - Window title: "Import Scene"
            - Window icon: FlapKine icon from assets
            - Project folder: User-defined destination for saving project data
            - Menu bar: Custom `MenuBar` instance with connected actions:
                - Exit
                - Minimize
                - Maximize
                - Restore
                - About (application info dialog)
            - Main layout and widgets: Triggered through the `initUI()` method
        """
        super(ProjectCreator, self).__init__()
        # Place the window in the center of the screen
        self.setWindowTitle("Import Scene")

        # Set the icon
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)
        icon_path = os.path.join(base_path, 'app', 'assets', 'flapkine_icon.png')
        self.setWindowIcon(QIcon(icon_path))

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
            'doc': self.show_doc,
        })

        self.initUI()

    def initUI(self):
        """
        Sets up the main UI layout for the Project Creator window.

        Constructs and arranges the primary user interface elements required for setting up a FlapKine project:
            - Scene Import Section: For importing or creating a scene file.
            - Configuration Options: Enables toggling between default and custom configuration.
            - Configuration Group: Contains settings for video format, camera, and lighting.
            - Other Settings: Includes STL export toggle and reflection axis checkboxes.
            - Final Action Button: "Create Project" button to confirm and finalize project setup.

        The method also centers the window on screen and dynamically uses the current palette's primary color
        to style relevant UI sections.

        Components Added to Main Layout:
            - Scene import widgets
            - Config options and grouped settings
            - STL and reflection options
            - "Create Project" QPushButton (connected to `create_the_project`)
        """
        self.center()
        primary_color = self.palette().color(self.foregroundRole()).name()
        self.setup_central_widget()
        self.setup_scene_import(primary_color)
        self.setup_config_options()
        self.setup_config_group(primary_color)
        self.setup_other_settings()
        self.ok_button = QPushButton('Create Project', self)
        self.ok_button.clicked.connect(self.create_the_project)
        self.main_layout.addWidget(self.ok_button)

    def setup_central_widget(self):
        """
        Configures the central widget and main layout of the Project Creator window.

        Initializes the main UI container by setting a `QWidget` as the central widget of the main window.
        A vertical box layout (`QVBoxLayout`) is then assigned to this widget, serving as the base layout
        for all subsequent UI components in the application.

        Components Initialized:
            - `central_widget`: Main container widget for all UI elements.
            - `main_layout`: Vertical layout used to stack UI sections top-to-bottom.
        """
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

    def setup_scene_import(self, primary_color):
        """
        Creates the scene import section of the Project Creator window.

        Adds UI components for importing an existing scene file or creating a new one. This section includes:
            - A label indicating the purpose of the section.
            - A line edit to show or input the path to the scene file.
            - An "Open" button with folder icon to trigger a file dialog for scene selection.
            - A "Create" button with a plus-folder icon to open a scene creation interface.

        Button click events are connected to respective handler methods (`import_scene`, `create_scene`).

        Components Added:
            - QLabel: "Import Scene"
            - QLineEdit: `text_editor_scene` for displaying scene path
            - QPushButton: `open_button` to import a file
            - QPushButton: `create_button` to create a new scene
            - HBox Layout: Wraps the above components horizontally and adds to the main layout

        Parameters:
            primary_color (str): The primary UI color used for icons in this section.
        """

        box1 = QHBoxLayout()
        scene_import = QWidget()
        label = QLabel('Import Scene', self)
        label.setFont(QFont('Times', 9))
        self.open_button = QPushButton('Open', self)
        self.open_button.setFont(QFont('Times', 8))
        self.open_button.setIcon(icon("fa5.folder-open", color=primary_color))
        self.open_button.clicked.connect(self.import_scene)
        self.text_editor_scene = QLineEdit()
        self.create_button = QPushButton('Create', self)
        self.create_button.setFont(QFont('Times', 8))
        self.create_button.setIcon(icon("mdi.folder-plus-outline", color=primary_color))
        self.create_button.clicked.connect(self.create_scene)
        box1.addWidget(label)
        box1.addWidget(self.text_editor_scene)
        box1.addWidget(self.open_button)
        box1.addWidget(self.create_button)
        scene_import.setLayout(box1)
        self.main_layout.addWidget(scene_import)

    def setup_config_options(self):
        """
        Sets up configuration option widgets.

        Initializes the interface section that allows the user to choose between using default
        configuration settings or creating a new custom configuration.

        Components Initialized:
            - `default_config_checkbox`: A checkbox to enable or disable usage of default config.
            - `import_config_button`: A toggle button to create a new custom configuration.

        Connections:
            - `default_config_checkbox.stateChanged` → `process_default_config()`
            - `import_config_button.toggled` → `create_new_config()`
        """
        box2 = QHBoxLayout()
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
        box2.addWidget(self.default_config_checkbox)
        box2.addWidget(self.import_config_button)
        config_options.setLayout(box2)
        self.main_layout.addWidget(config_options)

    def setup_config_group(self, primary_color):
        """
        Sets up the configuration group section.

        Initializes the grouped container for all configuration settings including video, camera,
        and lighting controls. This section is disabled by default and is enabled upon creating
        a new custom configuration.

        Components Initialized:
            - `config_group`: QGroupBox titled "Configurations"
            - `config_layout`: Vertical layout containing:
                - Video settings (via `setup_video_settings()`)
                - Camera settings (via `setup_camera_settings()`)
                - Light settings (via `setup_light_settings()`)
        """

        self.config_group = QGroupBox("Configurations")
        self.config_group.setFont(QFont('Times', 9))
        self.config_layout = QVBoxLayout()
        self.setup_video_settings()
        self.setup_camera_settings()
        self.setup_light_settings()
        self.config_group.setLayout(self.config_layout)
        self.config_group.setEnabled(False)
        self.main_layout.addWidget(self.config_group)

    def setup_video_settings(self):
        video_group = QGroupBox("Video Settings")
        video_group.setFont(QFont('Times', 8))
        video_group.setStyleSheet("""
    QGroupBox {
        color: #3498db;
        font-weight: bold;
        border: 2px solid #2980b9;
        border-radius: 5px;
        margin-top: 10px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 5px;
    }
    """)
        video_settings = QVBoxLayout()
        image_settings = QHBoxLayout()
        image_settings_label = QLabel("Frame Format")
        image_settings_label.setFont(QFont('Times', 7))
        self.frame_format = QComboBox()
        self.frame_format.addItems(['PNG', 'JPEG', 'TIFF'])
        self.frame_format.setFont(QFont('Times', 7))
        self.frame_format.setCurrentIndex(0)
        image_settings.addWidget(image_settings_label)
        image_settings.addWidget(self.frame_format)
        self.resolution_settings = QHBoxLayout()
        self.setup_resolution_inputs()
        video_settings.addLayout(image_settings)
        video_settings.addLayout(self.resolution_settings)
        video_group.setLayout(video_settings)
        self.config_layout.addWidget(video_group)

    def setup_resolution_inputs(self):
        """
        Adds input controls for setting video resolution.

        Initializes two spin boxes for specifying horizontal (X) and vertical (Y) resolution values,
        and appends them to the resolution settings layout with appropriate labels.

        Components Initialized:
            - `resolution_x`: Spin box for horizontal resolution (0 to 1920)
            - `resolution_y`: Spin box for vertical resolution (0 to 1080)
            - Title label: "Resolution" (Times, size 7)
        """
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

    def setup_camera_settings(self):
        """
        Sets up the camera configuration section within the config group.

        Creates a stylized group box labeled "Camera Settings" containing controls for:
            - Camera Position
            - Camera Focal Point
            - Camera View Up Vector

        Layout Structure:
            - Three horizontal QHBoxLayouts for each subcomponent
            - Each axis (X, Y, Z) has its own labeled QDoubleSpinBox

        Subcomponents Added:
            - Camera Location Controls: via `add_camera_controls`
            - Camera Focal Controls: via `add_camera_controls`
            - Camera View-Up Controls: via `add_camera_controls`

        The assembled group is added to the main configuration layout.
        """
        camera_setting_grp = QGroupBox("Camera Settings")
        camera_setting_grp.setFont(QFont('Times', 8))
        camera_setting_grp.setStyleSheet("""
        QGroupBox {
            color: #16a085;
            font-weight: bold;
            border: 2px solid #13876a;
            border-radius: 6px;
            margin-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 5px;
        }
        """)

        camera_settings = QVBoxLayout()
        camera_location = QHBoxLayout()
        camera_focal = QHBoxLayout()
        camera_up = QHBoxLayout()

        self.add_camera_controls(camera_location, camera_focal, camera_up)

        camera_settings.addLayout(camera_location)
        camera_settings.addLayout(camera_focal)
        camera_settings.addLayout(camera_up)

        camera_setting_grp.setLayout(camera_settings)
        self.config_layout.addWidget(camera_setting_grp)

    def add_camera_controls(self, location_layout, focal_layout, up_layout):
        """
        Adds camera position, focal point, and view-up vector controls to the given layouts.

        Each control group is populated with labeled `QDoubleSpinBox` widgets for X, Y, and Z axes.

        Parameters
        ----------
        location_layout : QHBoxLayout
            Layout to which camera position (location) spinboxes are added.

        focal_layout : QHBoxLayout
            Layout to which camera focal point spinboxes are added.

        up_layout : QHBoxLayout
            Layout to which camera view-up vector spinboxes are added.

        Attributes Set
        --------------
        camera_location_x, camera_location_y, camera_location_z : QDoubleSpinBox
            Spinboxes for camera position in world coordinates.

        camera_focal_x, camera_focal_y, camera_focal_z : QDoubleSpinBox
            Spinboxes for focal target point of the camera.

        camera_up_x, camera_up_y, camera_up_z : QDoubleSpinBox
            Spinboxes for defining the view-up direction of the camera.
        """

        def add_control(label_text, min_val, max_val):
            """Creates a QWidget containing a label and a spinbox."""
            wid = QWidget()
            layout = QHBoxLayout()
            label = QLabel(label_text)
            label.setFont(QFont('Times', 7))
            spinbox = QDoubleSpinBox()
            spinbox.setRange(min_val, max_val)
            layout.addWidget(label)
            layout.addWidget(spinbox)
            layout.setContentsMargins(0, 0, 0, 0)
            wid.setLayout(layout)
            return wid, spinbox

        # Camera Location Controls
        location_layout.addWidget(QLabel('Location'))
        for axis in ['x', 'y', 'z']:
            wid, spinbox = add_control(axis.upper() + ':', -1000, 1000)
            setattr(self, f'camera_location_{axis}', spinbox)
            location_layout.addWidget(wid)

        # Camera Focal Controls
        focal_layout.addWidget(QLabel('Focal Point'))
        for axis in ['x', 'y', 'z']:
            wid, spinbox = add_control(axis.upper() + ':', -1000, 1000)
            setattr(self, f'camera_focal_{axis}', spinbox)
            focal_layout.addWidget(wid)

        # Camera View-Up Controls
        up_layout.addWidget(QLabel('View Up'))
        for axis in ['x', 'y', 'z']:
            wid, spinbox = add_control(axis.upper() + ':', -1.0, 1.0)
            spinbox.setSingleStep(0.1)
            setattr(self, f'camera_up_{axis}', spinbox)
            up_layout.addWidget(wid)

    def setup_light_settings(self):
        """
        Sets up the light configuration panel within the configuration layout.

        Creates a styled `QGroupBox` labeled "Light Settings", including controls
        for adjusting light location (X, Y, Z) and power level. Each axis input
        is represented by a `QDoubleSpinBox`, and power is controlled by a `QSpinBox`.

        UI Elements Initialized:
            - Location:
                - X, Y, Z SpinBoxes (`light_location_x`, `light_location_y`, `light_location_z`)
                - Range: -1000 to 1000
            - Power:
                - SpinBox `light_power`
                - Range: 0 to 10000

        Visual Styling:
            - Group title and border styled with orange tones for visual grouping.
        """

        light_setting_grp = QGroupBox("Light Settings")
        light_setting_grp.setFont(QFont('Times', 8))
        light_setting_grp.setStyleSheet("""
    QGroupBox {
        color: #e67e22;
        font-weight: bold;
        border: 2px solid #d35400;
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
        light_location.addWidget(QLabel("Location"))
        for axis in ['x', 'y', 'z']:
            wid = QWidget()
            layout = QHBoxLayout()
            label = QLabel(axis.upper() + ':')
            label.setFont(QFont('Times', 7))
            spinbox = QDoubleSpinBox()
            spinbox.setRange(-1000, 1000)
            layout.addWidget(label)
            layout.addWidget(spinbox)
            wid.setLayout(layout)
            setattr(self, f'light_location_{axis}', spinbox)
            light_location.addWidget(wid)
        power_wid = QWidget()
        power_layout = QHBoxLayout()
        power_label = QLabel("Power:")
        power_label.setFont(QFont('Times', 7))
        self.light_power = QSpinBox()
        self.light_power.setMinimum(0)
        self.light_power.setMaximum(10000)
        power_layout.addWidget(power_label)
        power_layout.addWidget(self.light_power)
        power_wid.setLayout(power_layout)
        light_power.addWidget(QLabel("Power"))
        light_power.addWidget(power_wid)
        Light_settings.addLayout(light_location)
        Light_settings.addLayout(light_power)
        light_setting_grp.setLayout(Light_settings)
        self.config_layout.addWidget(light_setting_grp)

    def setup_other_settings(self):
        """
        Sets up additional configuration options under the "Other Settings" group.

        Adds controls for STL file saving and axis reflection toggles.
        Includes checkboxes for reflecting the scene geometry about XY, YZ, and XZ planes,
        as well as a toggle for enabling STL export.

        UI Elements:
            - Save STL: Checkbox (`stl_enable`)
            - Axis Reflection: Checkboxes (`reflect_xy`, `reflect_yz`, `reflect_xz`)
                - Each connected to `toggle_checkboxes()` for handling exclusive selection.

        Styling:
            - Group box styled in purple tones for clear visual separation.
        """
        other_settings_group = QGroupBox("Other Settings")
        other_settings_group.setFont(QFont('Times', 9))
        other_settings_group.setStyleSheet("""
    QGroupBox {
        color: #9b59b6;
        font-weight: bold;
        border: 2px solid #8e44ad;
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
        self.stl_enable = QCheckBox("Save STL")
        self.stl_enable.setFont(QFont('Times', 8))
        stl_layout = QHBoxLayout()
        stl_layout.addWidget(self.stl_enable)
        reflect_label = QLabel("Reflect about Axes: ")
        reflect_label.setFont(QFont('Times', 8))
        self.reflect_xy = QCheckBox('XY')
        self.reflect_yz = QCheckBox('YZ')
        self.reflect_xz = QCheckBox('XZ')
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
        self.main_layout.addWidget(other_settings_group)

    def import_scene(self):
        """
        Opens a file dialog to import a scene `.pkl` file.

        Sets the selected file path in the scene input field and updates the open button's appearance.
        """
        directory, _ = QFileDialog.getOpenFileName(filter='Scene File (*.pkl)')

        if directory:
            self.directory_scene = directory
            self.text_editor_scene.setText(self.directory_scene)

        # Make the button glow green
        self.open_button.setStyleSheet('background-color: green')

    def create_scene(self):
        """
        Opens the scene creation window.

        Launches a `CreateScene` dialog and connects its `sceneCreated` signal
        to the `on_scene_created` handler.
        """
        self.window2 = SceneCreator()
        self.window2.show()
        self.window2.sceneCreated.connect(self.on_scene_created)

    def on_scene_created(self, scene_data):
        """
        Handles the scene data returned from the scene creation window.

        Stores the scene data and updates the 'Create' button's appearance to indicate success.
        """
        self.scene_data = scene_data
        # Make the button glow green
        self.create_button.setStyleSheet('background-color: green')

    def process_default_config(self):
        """
        Applies default configuration settings from a JSON file.

        If the 'Use Default Config' checkbox is checked, this method loads predefined
        configuration values from `default_config.json` and applies them to the respective
        input fields for video resolution, camera parameters, lighting, reflection axes,
        and STL export. If the checkbox is unchecked, the configuration section is disabled.

        Behavior:
            - Loads JSON from `src/config/default_config.json`.
            - Sets resolution (X, Y), camera location (X, Y, Z), and camera rotation (α, β, γ).
            - Sets light position (X, Y, Z) and light power.
            - Configures reflection plane (XY, YZ, XZ) and STL checkbox state.
            - Enables or disables the configuration group box accordingly.

        UI Elements Updated:
            - frame_format
            - resolution_x, resolution_y
            - camera_location_x/y/z
            - camera_focal_x/y/z
            - light_location_x/y/z
            - light_power
            - reflect_xy, reflect_yz, reflect_xz
            - stl_enable
            - config_group (enabled/disabled)
        """

        if self.default_config_checkbox.isChecked():

            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(__file__)
            config_path = os.path.join(base_path, 'src', 'config', 'default_config.json')

            with open(config_path, 'r') as file:
                config = json.load(file)

            self.frame_format.setCurrentIndex(0)
            self.resolution_x.setValue(config['VideoRender']['resolution_x'])
            self.resolution_y.setValue(config['VideoRender']['resolution_y'])

            self.camera_location_x.setValue(config['Camera']['location'][0])
            self.camera_location_y.setValue(config['Camera']['location'][1])
            self.camera_location_z.setValue(config['Camera']['location'][2])

            self.camera_focal_x.setValue(config['Camera']['focal'][0])
            self.camera_focal_y.setValue(config['Camera']['focal'][1])
            self.camera_focal_z.setValue(config['Camera']['focal'][2])

            self.camera_up_x.setValue(config['Camera']['up'][0])
            self.camera_up_y.setValue(config['Camera']['up'][1])
            self.camera_up_z.setValue(config['Camera']['up'][2])

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
        """
        Initializes a blank configuration setup for a new project.

        When the 'New Config' toggle button is enabled, this method populates all relevant
        input fields with baseline default values, effectively clearing any previous data
        and preparing the UI for a new configuration. If the toggle is disabled, the
        configuration group is disabled.

        Behavior:
            - Resets video resolution to 640x480.
            - Sets all camera position and rotation spinboxes to 0.
            - Resets light position and power to 0.
            - Disables all reflection checkboxes and STL saving option.
            - Enables or disables the configuration group box accordingly.

        UI Elements Updated:
            - frame_format
            - resolution_x, resolution_y
            - camera_location_x/y/z
            - camera_focal_x/y/z
            - light_location_x/y/z
            - light_power
            - reflect_xy, reflect_yz, reflect_xz
            - stl_enable
            - config_group (enabled/disabled)
        """

        if self.import_config_button.isChecked():

            self.frame_format.setCurrentIndex(0)
            self.resolution_x.setValue(640)
            self.resolution_y.setValue(480)

            self.camera_location_x.setValue(0)
            self.camera_location_y.setValue(0)
            self.camera_location_z.setValue(0)

            self.camera_focal_x.setValue(0)
            self.camera_focal_y.setValue(0)
            self.camera_focal_z.setValue(0)

            self.camera_up_x.setValue(0)
            self.camera_up_y.setValue(0)
            self.camera_up_z.setValue(1)

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
        """
        Finalizes and creates the project with the configured scene and settings.

        This method performs the full setup of the project directory, including:
        - Directory structure creation for images, videos, and data.
        - Copying or serializing the scene file into the project folder.
        - Saving a configuration JSON file based on current UI state.
        - Launching the project rendering window.

        Project Structure Created:
            - <project_folder>/
                ├── scene.pkl
                ├── config.json
                └── data/
                    ├── images/
                    └── videos/

        Configuration Saved (`config.json`):
            - VideoRender:
                - OutputPath: 'data/images'
                - STLPath: 'data/stl'
                - FrameFormat: selected from dropdown
                - resolution_x/y: selected resolution values
                - film_transparent: fixed as False
            - Camera:
                - location: (x, y, z) position
                - focal: (x, y, z) focal point
                - up: (x, y, z) view-up vector
            - Light:
                - location: (x, y, z) position
                - energy: integer power value
            - STL: Boolean, from checkbox
            - Reflect: 'XY', 'YZ', 'XZ' or None based on user selection

        Behavior:
            - If `scene_data` exists, it is pickled and saved.
            - Otherwise, the provided `.pkl` scene file is copied to the project folder.
            - After setup, a new `ProjectWindow` instance is launched and the current window is closed.
        """

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
                'focal': [self.camera_focal_x.value(), self.camera_focal_y.value(), self.camera_focal_z.value()],
                'up': [self.camera_up_x.value(), self.camera_up_y.value(), self.camera_up_z.value()]
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
        """
        Centers the application window on the screen.

        Calculates screen and window dimensions, then moves the window to the center position.
        """
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
        """
        Enforces mutual exclusivity among axis reflection checkboxes.

        When one checkbox is selected, all others are unchecked.
        """
        if checked_box.isChecked():
            # Uncheck all other checkboxes
            for box in [self.reflect_xy, self.reflect_yz, self.reflect_xz]:
                if box != checked_box:
                    box.setChecked(False)

    def about_button_fun(self):
        """
        Displays an 'About FlapKine' information dialog.

        Shows details about the developer, version, and purpose of the application.
        """
        QMessageBox.about(self, "About FlapKine", f'''
        <h1>FlapKine</h1>
        <p>Developed by: Kalbhavi Vadhiraj</p>
        <p>Version {__version__}</p>
        <p>FlapKine provides a visual representation and simulation of the kinematics and aerodynamics of flapping wing micro-aerial vehicles (MAVs). It allows users to analyze and optimize MAV designs with precision and clarity, revealing the intricate mechanics of flapping flight. Whether for research, development, or educational purposes, this tool offers valuable insights into the performance and behavior of MAVs, facilitating advanced design and innovation.</p>
''')

    def about_button_fun(self):
        """
        Displays an 'About FlapKine' information dialog.

        Shows details about the developer, version, and purpose of the application.
        """
        QMessageBox.about(self, "About FlapKine", f'''
        <h1>FlapKine</h1>
        <p>Developed by: Kalbhavi Vadhiraj</p>
        <p>Version {__version__}</p>
        <p>FlapKine provides a visual representation and simulation of the kinematics and aerodynamics of flapping wing micro-aerial vehicles (MAVs). It allows users to analyze and optimize MAV designs with precision and clarity, revealing the intricate mechanics of flapping flight. Whether for research, development, or educational purposes, this tool offers valuable insights into the performance and behavior of MAVs, facilitating advanced design and innovation.</p>
''')

    def show_doc(self):
        """
        Displays the documentation for the FlapKine application.

        This method opens the documentation file in the default web browser.
        """
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)
        doc_path = "https://ihdavjar.github.io/FlapKine/"
        QDesktopServices.openUrl(QUrl.fromLocalFile(doc_path))