import os
import json

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QDoubleSpinBox, QSpinBox, QLabel, QComboBox,
    QMainWindow, QGroupBox, QCheckBox, QDesktopWidget
)

from qtawesome import icon

class RenderConfig(QMainWindow):
    """
    RenderConfig Class
    ==================

    Main configuration panel for render settings in the FlapKine application.

    This class provides a GUI window that allows users to configure video rendering,
    camera parameters, lighting settings, STL export, and axis reflection for a 3D
    rendering pipeline. The settings are loaded from and saved to a `config.json` file
    within the specified project folder.

    Attributes
    ----------
    project_folder : str
        Path to the folder containing the configuration file.

    frame_format : QComboBox
        Dropdown for selecting the frame image format (e.g., PNG, JPEG, TIFF).

    resolution_x : QSpinBox
        Spin box to specify horizontal resolution.

    resolution_y : QSpinBox
        Spin box to specify vertical resolution.

    camera_location_x, camera_location_y, camera_location_z : QDoubleSpinBox
        Spin boxes to specify camera position in 3D space.

    camera_rotation_alpha, camera_rotation_beta, camera_rotation_gamma : QDoubleSpinBox
        Spin boxes to specify camera rotation in Euler angles.

    light_location_x, light_location_y, light_location_z : QDoubleSpinBox
        Spin boxes to specify light source position in 3D space.

    light_power : QSpinBox
        Spin box to control light energy (intensity).

    stl_enable : QCheckBox
        Checkbox to toggle STL mesh saving.

    reflect_xy, reflect_yz, reflect_xz : QCheckBox
        Checkboxes to select the reflection axis (only one can be active at a time).

    ok_button : QPushButton
        Button to save the current configuration and close the window.

    Methods
    -------
    __init__(project_folder):
        Initializes the main window and constructs the interface.

    initUI():
        Builds and arranges all GUI components and groups.

    _create_video_settings():
        Constructs the video configuration group box.

    _create_camera_settings():
        Constructs the camera configuration group box.

    _create_light_settings():
        Constructs the lighting configuration group box.

    _create_other_settings():
        Constructs the STL and reflection settings panel.

    _assemble_config_group():
        Collects all config panels into a grouped layout.

    _styled_groupbox(title, color, border_color, layout, font_size):
        Returns a styled QGroupBox with custom appearance.

    _labeled_widget(label_text, widget):
        Returns a QWidget with an inline label and the given widget.

    process_default_config():
        Loads the saved configuration from `config.json` and updates the UI.

    save_config():
        Saves the current UI state into `config.json` in the project folder.

    toggle_checkboxes(checked_box):
        Ensures only one reflection checkbox is active at a time.

    center():
        Positions the window at the center of the screen.
    """

    def __init__(self, project_folder):
        """
        Initialize the RenderConfig window.

        Sets up the main render configuration window with appropriate title and icon, using
        a foreground color extracted from the current theme. Stores the provided project
        folder path and initializes the user interface layout and widgets.

        Parameters
        ----------
        project_folder : str
            Absolute path to the folder containing the current project data.

        Attributes
        ----------
        project_folder : str
            Stores the path to the project folder for use in render configuration operations.

        Methods Called
        --------------
        initUI()
            Initializes all UI components and layout for render configuration.
        """
        super(RenderConfig, self).__init__()
        primary_color = self.palette().color(self.foregroundRole()).name()
        self.setWindowTitle("Configure Render")

        self.setWindowIcon(icon("mdi.cog", color=primary_color))

        self.project_folder = project_folder

        self.center()

        self.initUI()

    def initUI(self):
        """
        Initialize and configure the user interface components of the render configuration panel.

        This method sets up the main window layout and populates it with grouped sections for
        configuring video, camera, and lighting settings. It also adds additional controls such as
        STL export toggle and axis reflection options. A confirmation button is included to save
        and apply the chosen configuration settings.

        UI Components Initialized
        -------------------------
        - Video settings group
        - Camera settings group
        - Lighting settings group
        - STL export and reflection axis controls
        - 'Ok' confirmation button with icon
        - Main vertical layout containing all components
        """
        self.center()
        primary_color = self.palette().color(self.foregroundRole()).name()

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        # Configuration sections
        self._create_video_settings()
        self._create_camera_settings()
        self._create_light_settings()
        self._assemble_config_group()

        # Additional options: STL saving and axis reflection
        self._create_other_settings()

        # OK button
        self.ok_button = QPushButton('Ok', self)
        self.ok_button.setIcon(icon("mdi.check-circle", color=primary_color))
        self.ok_button.clicked.connect(self.save_config)

        # Add all components to main layout
        self.main_layout.addWidget(self.config_group)
        self.main_layout.addWidget(self.other_settings_group)
        self.main_layout.addWidget(self.ok_button)

        # Load defaults
        self.process_default_config()

    def _create_video_settings(self):
        """
        Create and configure the video settings group for render configuration.

        This includes UI controls for selecting frame format (e.g., PNG, JPEG, TIFF)
        and specifying output resolution dimensions (X and Y). All widgets are arranged
        in a compact vertical layout and grouped under a styled section titled "Video Settings".

        UI Components
        -------------
        - Frame format dropdown (QComboBox)
        - Resolution input (QSpinBox for X and Y)
        - Labeled horizontal layout for image format
        - Group box titled "Video Settings" with themed styling
        """
        self.frame_format = QComboBox()
        self.frame_format.addItems(['PNG', 'JPEG', 'TIFF'])
        self.frame_format.setCurrentIndex(0)
        self.frame_format.setFont(QFont('Times', 7))

        image_format_layout = QHBoxLayout()
        image_format_label = QLabel("Frame Format")
        image_format_label.setFont(QFont('Times', 7))
        image_format_layout.addWidget(image_format_label)
        image_format_layout.addWidget(self.frame_format)

        self.resolution_x = QSpinBox()
        self.resolution_x.setRange(0, 1920)
        self.resolution_y = QSpinBox()
        self.resolution_y.setRange(0, 1080)

        res_layout = QHBoxLayout()
        res_layout.addWidget(QLabel("Resolution"))
        res_layout.addWidget(self._labeled_widget("  X:", self.resolution_x))
        res_layout.addWidget(self._labeled_widget("  Y:", self.resolution_y))

        layout = QVBoxLayout()
        layout.addLayout(image_format_layout)
        layout.addLayout(res_layout)

        self.video_group = self._styled_groupbox("Video Settings", "#3498db", "#2980b9", layout, font_size=8)

    def _create_camera_settings(self):
        """
        Create and configure the camera settings group for render configuration.

        This section provides spin box controls for specifying the camera’s 3D location
        and orientation in space. Users can input X, Y, Z coordinates for both position
        and Euler angle-based rotations. All elements are organized into a labeled layout
        and enclosed in a themed "Camera Settings" group box.

        UI Components
        -------------
        - Camera location inputs (QDoubleSpinBox for X, Y, Z)
        - Camera rotation inputs (QDoubleSpinBox for α, β, γ)
        - Labeled horizontal layouts for location and rotation
        - Group box titled "Camera Settings" with custom styling
        """
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

        loc_layout = QHBoxLayout()
        loc_layout.addWidget(QLabel("Location"))
        loc_layout.addWidget(self._labeled_widget("X:", self.camera_location_x))
        loc_layout.addWidget(self._labeled_widget("Y:", self.camera_location_y))
        loc_layout.addWidget(self._labeled_widget("Z:", self.camera_location_z))

        rot_layout = QHBoxLayout()
        rot_layout.addWidget(QLabel("Rotation"))
        rot_layout.addWidget(self._labeled_widget("X:", self.camera_rotation_alpha))
        rot_layout.addWidget(self._labeled_widget("Y:", self.camera_rotation_beta))
        rot_layout.addWidget(self._labeled_widget("Z:", self.camera_rotation_gamma))

        layout = QVBoxLayout()
        layout.addLayout(loc_layout)
        layout.addLayout(rot_layout)

        self.camera_group = self._styled_groupbox("Camera Settings", "#16a085", "#13876a", layout, font_size=8)

    def _create_light_settings(self):
        """
        Create and configure the light settings group for render configuration.

        Provides interactive controls to position the scene's light source in 3D space
        and adjust its power intensity. All inputs are grouped into logically labeled
        layouts and wrapped within a stylized "Light Settings" section.

        UI Components
        -------------
        - Light position inputs (QDoubleSpinBox for X, Y, Z)
        - Light intensity input (QSpinBox for power in arbitrary units)
        - Labeled layouts for location and power
        - Group box titled "Light Settings" with custom orange theme
        """
        self.light_location_x = QDoubleSpinBox()
        self.light_location_x.setRange(-1000, 1000)
        self.light_location_y = QDoubleSpinBox()
        self.light_location_y.setRange(-1000, 1000)
        self.light_location_z = QDoubleSpinBox()
        self.light_location_z.setRange(-1000, 1000)
        self.light_power = QSpinBox()
        self.light_power.setRange(0, 10000)

        loc_layout = QHBoxLayout()
        loc_layout.addWidget(QLabel("Location"))
        loc_layout.addWidget(self._labeled_widget("X:", self.light_location_x))
        loc_layout.addWidget(self._labeled_widget("Y:", self.light_location_y))
        loc_layout.addWidget(self._labeled_widget("Z:", self.light_location_z))

        power_layout = QHBoxLayout()
        power_layout.addWidget(QLabel("Power"))
        power_layout.addWidget(self._labeled_widget("Power:", self.light_power))

        layout = QVBoxLayout()
        layout.addLayout(loc_layout)
        layout.addLayout(power_layout)

        self.light_group = self._styled_groupbox("Light Settings", "#e67e22", "#d35400", layout, font_size=8)

    def _assemble_config_group(self):
        """
        Assemble the primary configuration group container.

        Combines individual configuration sections—video, camera, and lighting—
        into a unified vertical layout and embeds them within a stylized QGroupBox
        labeled "Configurations".

        UI Components
        -------------
        - Vertical layout (`QVBoxLayout`) containing:
            - `self.video_group`
            - `self.camera_group`
            - `self.light_group`
        - QGroupBox titled "Configurations" with Times font styling
        """
        self.config_layout = QVBoxLayout()
        self.config_layout.addWidget(self.video_group)
        self.config_layout.addWidget(self.camera_group)
        self.config_layout.addWidget(self.light_group)

        self.config_group = QGroupBox("Configurations")
        self.config_group.setFont(QFont('Times', 9))
        self.config_group.setLayout(self.config_layout)

    def _create_other_settings(self):
        """
        Create additional configuration options including STL export and axis reflections.

        Sets up toggles for saving STL files and applying reflection across the XY, YZ, and XZ planes.
        Groups these controls into a styled section labeled "Other Settings".

        UI Components
        -------------
        - STL Export Toggle (`QCheckBox`): `self.stl_enable`
        - Axis Reflection Checkboxes:
            - `self.reflect_xy`
            - `self.reflect_yz`
            - `self.reflect_xz`
        - Reflect toggles are connected to `self.toggle_checkboxes` for interactive behavior
        - Layout assembled into a custom styled group box
        """
        self.stl_enable = QCheckBox("Save STL")
        self.stl_enable.setFont(QFont('Times', 8))

        self.reflect_xy = QCheckBox("XY")
        self.reflect_yz = QCheckBox("YZ")
        self.reflect_xz = QCheckBox("XZ")
        for checkbox in (self.reflect_xy, self.reflect_yz, self.reflect_xz):
            checkbox.setFont(QFont('Times', 8))
            checkbox.toggled.connect(lambda checked, c=checkbox: self.toggle_checkboxes(c))

        layout = QHBoxLayout()
        stl_layout = QHBoxLayout()
        reflect_layout = QHBoxLayout()

        stl_layout.addWidget(self.stl_enable)
        reflect_layout.addWidget(QLabel("Reflect about Axes:"))
        reflect_layout.addWidget(self.reflect_xy)
        reflect_layout.addWidget(self.reflect_yz)
        reflect_layout.addWidget(self.reflect_xz)

        layout.addLayout(stl_layout)
        layout.addLayout(reflect_layout)

        self.other_settings_group = self._styled_groupbox("Other Settings", "#9b59b6", "#8e44ad", layout, font_size=9)

    def _styled_groupbox(self, title, color, border_color, layout, font_size=9):
        """
        Create a custom-styled QGroupBox with a colored title and border.

        Parameters
        ----------
        title : str
            The title text displayed at the top of the group box.
        color : str
            The font color used for the group box title (hex code or color name).
        border_color : str
            The color of the border surrounding the group box.
        layout : QLayout
            The layout manager containing the widgets to be placed inside the group box.
        font_size : int, optional
            Font size for the title text. Default is 9.

        Returns
        -------
        QGroupBox
            A styled `QGroupBox` widget containing the provided layout and title.
        """
        group = QGroupBox(title)
        group.setFont(QFont('Times', font_size))
        group.setStyleSheet(f"""
            QGroupBox {{
                color: {color};
                font-weight: bold;
                border: 2px solid {border_color};
                border-radius: 6px;
                margin-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px;
            }}
        """)
        group.setLayout(layout)
        return group

    def _labeled_widget(self, label_text, widget):
        """
        Create a widget container with a label and an input/control widget arranged horizontally.

        Parameters
        ----------
        label_text : str
            The text to display as a label for the associated widget.
        widget : QWidget
            The input or control widget (e.g., QSpinBox, QComboBox) to be labeled.

        Returns
        -------
        QWidget
            A container widget with a horizontal layout including the label and the given widget.
        """
        container = QWidget()
        layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setFont(QFont('Times', 7))
        layout.addWidget(label)
        layout.addWidget(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        container.setLayout(layout)
        return container

    def process_default_config(self):
        """
        Load and apply default configuration values from the project directory.

        This method reads a `config.json` file from the project folder and populates
        all render configuration widgets with the corresponding values, including
        video resolution, camera position and orientation, lighting parameters, STL saving,
        and reflection axis toggles.

        Configuration File Structure Expected:
            - VideoRender: { resolution_x, resolution_y }
            - Camera: { location: [x, y, z], rotation_euler: [alpha, beta, gamma] }
            - Light: { location: [x, y, z], energy }
            - STL: bool
            - Reflect: "XY" | "YZ" | "XZ" | None

        Raises
        ------
        FileNotFoundError
            If `config.json` is not found in the project directory.
        KeyError
            If required keys are missing in the config file.
        """
        with open(os.path.join(self.project_folder, 'config.json'), 'r') as file:
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

        self.stl_enable.setChecked(config["STL"])

    def save_config(self):
        """
        Collect and save the current render configuration to `config.json`.

        This method gathers all UI state values (video format, resolution, camera parameters,
        lighting setup, STL export preference, and reflection axis) and serializes them into
        a dictionary. The config is then saved as a JSON file in the project directory under `config.json`.

        Config Structure:
            - VideoRender:
                - OutputPath: str (default 'data/images')
                - STLPath: str (default 'data/stl')
                - FrameFormat: str ('PNG', 'JPEG', 'TIFF')
                - resolution_x: int
                - resolution_y: int
                - film_transparent: bool (always False)
            - Camera:
                - location: list[float, float, float]
                - rotation_euler: list[float, float, float]
            - Light:
                - location: list[float, float, float]
                - energy: int
            - STL: bool
            - Reflect: str | None ("XY", "YZ", "XZ", or None)

        Side Effects
        ------------
        - Overwrites the `config.json` file in the project folder.
        - Closes the configuration window after saving.
        """
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

        self.close()

    def toggle_checkboxes(self, checked_box):
        """
        Enforce mutual exclusivity among axis reflection checkboxes.

        Ensures that only one of the reflection axis checkboxes (XY, YZ, XZ) can be active at a time.
        When a checkbox is toggled on, all others are programmatically toggled off.

        Parameters
        ----------
        checked_box : QCheckBox
            The checkbox that was just toggled to the 'checked' state.

        Behavior
        --------
        - If `checked_box` is checked:
            - Automatically unchecks the other two axis checkboxes.
        - If `checked_box` is unchecked:
            - No action is taken (multiple checkboxes can be off simultaneously).
        """
        if checked_box.isChecked():
            # Uncheck all other checkboxes
            for box in [self.reflect_xy, self.reflect_yz, self.reflect_xz]:
                if box != checked_box:
                    box.setChecked(False)

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
