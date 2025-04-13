import os
import numpy as np
import pandas as pd

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QCursor
from PyQt5.QtWidgets import (
    QCheckBox, QComboBox, QFileDialog, QDesktopWidget, QDoubleSpinBox,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox,
    QPushButton, QSpinBox, QVBoxLayout, QWidget, QFormLayout, QGridLayout,
)

from vtk import (
    vtkSTLReader, vtkPolyDataMapper, vtkActor, vtkAxesActor, vtkRenderer,
    vtkTransform
)
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from stl import mesh
from qtawesome import icon

from src.core.core import Object3D, Sprite
from src.core.transforms.translation import ConstantT, Translation_COM
from src.core.transforms.rotation import ConstantR, Rotation_EulerAngles
from src.core.transforms.flexibility import ConstantF, Flexibility_type1, Flexibility_type2

from app.core.invkinematics import InvKineWindow
from app.widgets.misc.menu_bar import MenuBar


class SpriteCreator(QMainWindow):
    """
    SpriteCreator Class
    ==================

    This class provides the graphical interface for creating and configuring a 3D sprite 
    within the FlapKine application. Users can import STL files, apply transformation types 
    (translation, rotation, flexibility), and optionally use inverse kinematics data for 
    automated rotation specification.

    It also supports setting initial pose parameters and provides a 3D visualization 
    of the configured object using VTK.

    Attributes
    ----------
    SpriteCreated : pyqtSignal
        Signal emitted when the sprite is fully configured and ready.

    menu_bar : MenuBar
        Custom menu bar for handling file-related and application-level actions.

    sprite_name : QLineEdit
        Input field for naming the 3D sprite.

    sprite_stl_path : QLineEdit
        Path input for selecting and displaying the STL file to be imported.

    vtkWidget : QVTKRenderWindowInteractor
        VTK widget used for interactive 3D rendering of the sprite object.

    ren : vtkRenderer
        VTK renderer object responsible for managing the scene display.

    translation_transform : QComboBox
        Dropdown menu for selecting the translation transformation strategy.

    rotation_transform : QComboBox
        Dropdown menu for selecting the rotation transformation strategy.

    flexibility_transform : QComboBox
        Dropdown menu for selecting the flexibility transformation method.

    enable_checkbox : QCheckBox
        Checkbox to enable or disable the use of initial condition settings.

    position_x : QDoubleSpinBox
        Spin box for specifying the initial X-axis position.

    position_y : QDoubleSpinBox
        Spin box for specifying the initial Y-axis position.

    position_z : QDoubleSpinBox
        Spin box for specifying the initial Z-axis position.

    angle_input_alpha : QDoubleSpinBox
        Spin box for specifying the initial alpha (roll) angle in degrees.

    angle_input_beta : QDoubleSpinBox
        Spin box for specifying the initial beta (pitch) angle in degrees.

    angle_input_gamma : QDoubleSpinBox
        Spin box for specifying the initial gamma (yaw) angle in degrees.

    inverse_kinematics : bool
        Boolean flag indicating whether inverse kinematics data is being utilized.

    Methods
    -------
    __init__():
        Initializes the main window, layout, and signal-slot connections.

    init_ui():
        Builds and arranges all UI elements including transformation options and VTK visualization.

    init_menu():
        Sets up the application’s menu bar and connects its functionalities.

    init_sprite_inputs():
        Configures the sprite name and STL file input interface.

    init_transformations():
        Builds the UI for configuring translation, rotation, and flexibility transformations.

    init_initial_conditions():
        Creates the input controls for manually defining initial orientation and position.

    init_finish_controls():
        Adds the "Finish" button used to trigger the final sprite assembly.

    open_file():
        Handles STL file selection and renders the model within the VTK viewport.

    calculate_inverse_kinematics():
        Launches the inverse kinematics window and waits for processed data.

    process_inv_data():
        Receives and stores the angles and order computed from inverse kinematics.

    finish_button_fun():
        Compiles all transformation settings into a Sprite object and emits the creation signal.

    center():
        Repositions the window to the center of the screen.

    about_button_fun():
        Displays a dialog containing information about the FlapKine application.
    """

    SpriteCreated = pyqtSignal(Sprite)

    def __init__(self):
        """
        Initializes the SpriteCreator class.

        Sets up the main window for creating and configuring 3D sprites in the FlapKine environment.
        Defines core window properties including title, size, position, and application icon. 
        Initializes the `inverse_kinematics` flag and sets up the full user interface layout using `init_ui()`.

        Components Initialized:
            - Window title: "Create Sprite"
            - Window icon: Loaded from 'app/assets/flapkine_icon.png'
            - Window geometry: Positioned at (300, 100) with dimensions 800x600
            - Centering: Calls the `center()` method to align window to screen center
            - UI setup: Delegated to `init_ui()` for interface assembly
            - Inverse kinematics flag: Initialized as `False`
        """
        super(SpriteCreator, self).__init__()
        self.inverse_kinematics = False

        self.setWindowTitle("Create Sprite")
        self.setWindowIcon(QIcon(os.path.join('app', 'assets', 'flapkine_icon.png')))
        self.setGeometry(300, 100, 800, 600)
        self.center()

        self.init_ui()

    def init_ui(self):
        """
        Constructs the main UI layout for the SpriteCreator window.

        Initializes and assembles all primary UI sections including menu bar, sprite input fields, 
        transformation configuration, initial conditions, and the finalization button. 
        Also sets the central widget and applies the main layout for the application.

        UI Components Initialized:
            - `primary_color`: Derived from the application's foreground role for consistent theming
            - `menu_bar`: Setup using `init_menu()`
            - `main_layout`: Vertical layout to stack sections
            - `sprite_inputs`: Initialized using `init_sprite_inputs()` for name and STL import
            - `transformations`: Configured using `init_transformations()` (translation, rotation, flexibility)
            - `initial_conditions`: Loaded using `init_initial_conditions()` for position and angle presets
            - `finish_controls`: Finalization controls set via `init_finish_controls()`
            - Central widget: Main QWidget container with layout applied
        """
        self.primary_color = self.palette().color(self.foregroundRole()).name()

        self.init_menu()

        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()

        self.init_sprite_inputs()
        self.init_transformations()
        self.init_initial_conditions()

        self.init_finish_controls()

        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

    def init_menu(self):
        """
        Initializes the custom menu bar for the SpriteCreator window.

        Sets up a `MenuBar` instance and binds it to the main window. Connects core window control 
        actions such as exit, minimize, maximize, restore, and about, ensuring responsive GUI behavior.

        Menu Actions Connected:
            - 'exit': Closes the window
            - 'minimize': Minimizes the window
            - 'maximize': Maximizes the window
            - 'restore': Restores the window to its previous size
            - 'about': Opens the About FlapKine information dialog
        """

        self.menu_bar = MenuBar()
        self.setMenuBar(self.menu_bar)

        self.menu_bar.connect_actions({
            'exit': self.close,
            'minimize': self.showMinimized,
            'maximize': self.showMaximized,
            'restore': self.showNormal,
            'about': self.about_button_fun
        })

    def init_sprite_inputs(self):
        """
        Initializes the sprite input group (`group_1`) for 3D object configuration.

        Creates a `QGroupBox` titled "3DObject Properties" that allows users to input the sprite name 
        and load an STL file. Also sets up a VTK render window for real-time 3D visualization of the imported mesh.

        Components Initialized:
            - `sprite_name` (QLineEdit): Input field for specifying the name of the sprite.
            - `sprite_stl_path` (QLineEdit): Displays the selected STL file path.
            - `sprite_stl_open` (QPushButton): Opens a file dialog to select STL file; uses FontAwesome icon.
            - `vtkWidget` (QVTKRenderWindowInteractor): Embedded VTK viewport for rendering the 3D mesh.
            - `ren` (vtkRenderer): VTK renderer managing scene rendering and background color.
            - Layouts: `QFormLayout` for form-like UI, and `QHBoxLayout` to hold path input and VTK widget.

        Visual Styling:
            - Group box styled with bold text, blue borders, and rounded corners.
            - Labels use "Times" font with consistent size and alignment.

        Connected Actions:
            - `sprite_stl_open.clicked`: Triggers `open_file()` to load and visualize the STL file.
        """

        self.group_1 = QGroupBox("3DObject Properties")
        self.group_1.setFont(QFont('Times', 9))
        group_1_layout = QFormLayout()

        self.group_1.setStyleSheet("""
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

        self.sprite_name = QLineEdit()
        self.sprite_name.setPlaceholderText("Enter Sprite Name")
        sprite_text_label = QLabel("Sprite Name:")
        sprite_text_label.setFont(QFont('Times', 8))
        group_1_layout.addRow(sprite_text_label, self.sprite_name)

        self.sprite_stl_path = QLineEdit()
        self.sprite_stl_path.setPlaceholderText("Select STL file")
        self.sprite_stl_open = QPushButton("Open")
        self.sprite_stl_open.setIcon(icon("fa5.folder-open", color=self.primary_color))
        self.sprite_stl_open.clicked.connect(self.open_file)

        self.stl_path_layout = QHBoxLayout()
        self.stl_path_layout.addWidget(self.sprite_stl_path)
        self.stl_path_layout.addWidget(self.sprite_stl_open)

        self.vtkWidget = QVTKRenderWindowInteractor(self)
        self.stl_path_layout.addWidget(self.vtkWidget)

        self.ren = vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.ren.SetBackground(0.95, 0.95, 0.95)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        self.iren.Initialize()

        stl_path_label = QLabel("STL File Path:")
        stl_path_label.setFont(QFont('Times', 8))
        group_1_layout.addRow(stl_path_label, self.stl_path_layout)

        self.group_1.setLayout(group_1_layout)
        self.main_layout.addWidget(self.group_1)

    def init_transformations(self):
        """
        Initializes the transformation controls for sprite configuration.

        Creates a `QGroupBox` titled "Transformations" containing dropdowns for selecting 
        different transformation modes: Translation, Rotation, and Flexibility. 
        Each dropdown allows the user to choose a transformation strategy for the sprite 
        and triggers an associated update function on change.

        Components Initialized:
            - `translation_transform` (QComboBox): Allows selection of translation type (`Constant`, `COM`).
                - Connected to: `translation_transform_fun()`
            - `rotation_transform` (QComboBox): Allows selection of rotation mode (`Constant`, `Euler_Angles`, `Custom`).
                - Connected to: `rotation_transform_fun()`
            - `flexibility_transform` (QComboBox): Allows selection of flexibility behavior (`Constant`, `FlexibleType1`, `FlexibleType2`, `Custom`).
                - Connected to: `flexibility_transform_fun()`

        Visual Styling:
            - Group box styled with teal-colored bold borders and rounded corners.
            - Labels use "Times" font for consistency.
            - Each control placed using `QFormLayout` for clean, form-like alignment.

        Layout:
            - All transformation controls are embedded within the existing layout of `group_1`.
        """
        transformation_group = QGroupBox("Transformations")
        transformation_group.setFont(QFont('Times', 8))
        transformation_group_layout = QFormLayout()

        transformation_group.setStyleSheet("""
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

        # Translation Transform
        self.translation_transform_layout = QHBoxLayout()
        translation_label = QLabel("Translation Transform:")
        translation_label.setFont(QFont('Times', 7))
        self.translation_transform = QComboBox()
        self.translation_transform.addItems(["Constant", "COM"])
        self.translation_transform.currentIndexChanged.connect(self.translation_transform_fun)
        self.translation_transform_layout.addWidget(self.translation_transform)
        transformation_group_layout.addRow(translation_label, self.translation_transform_layout)

        # Rotation Transform
        self.rotation_transform_layout = QHBoxLayout()
        rotation_label = QLabel("Rotation Transform:")
        rotation_label.setFont(QFont('Times', 7))
        self.rotation_transform = QComboBox()
        self.rotation_transform.addItems(["Constant", "Euler_Angles", "Custom"])
        self.rotation_transform.currentIndexChanged.connect(self.rotation_transform_fun)
        self.rotation_transform_layout.addWidget(self.rotation_transform)
        transformation_group_layout.addRow(rotation_label, self.rotation_transform_layout)

        # Flexibility Transform
        self.flexibility_transform_layout = QHBoxLayout()
        flexibility_label = QLabel("Flexibility Transform:")
        flexibility_label.setFont(QFont('Times', 7))
        self.flexibility_transform = QComboBox()
        self.flexibility_transform.addItems(["Constant", "FlexibleType1", "FlexibleType2", "Custom"])
        self.flexibility_transform.currentIndexChanged.connect(self.flexibility_transform_fun)
        self.flexibility_transform_layout.addWidget(self.flexibility_transform)
        transformation_group_layout.addRow(flexibility_label, self.flexibility_transform_layout)

        transformation_group.setLayout(transformation_group_layout)
        self.group_1.layout().addRow(transformation_group)

    def init_initial_conditions(self):
        """
        Initializes the initial conditions section for sprite setup.

        Creates a `QGroupBox` titled "Initial Conditions" containing UI controls for setting 
        the sprite’s starting position and orientation using position coordinates and Euler angles. 
        These controls are grouped and managed through two sub-initialization functions: 
        `init_position_group()` and `init_angle_group()`.

        By default, the entire group is disabled and can be toggled via a checkbox labeled 
        "Enable Initial Conditions", allowing optional setup of initial state parameters.

        Components Initialized:
            - `group_2` (QGroupBox): Container for position and orientation fields.
            - `enable_checkbox` (QCheckBox): Enables or disables the initial conditions group.
                - Connected to: `enable_checkbox_fun()`
            - Position Inputs: Initialized via `init_position_group()`, includes X, Y, Z spin boxes.
            - Euler Angle Inputs: Initialized via `init_angle_group()`, includes α (alpha), β (beta), γ (gamma).

        Visual Styling:
            - Orange-colored themed group box with bold title and rounded border.
            - Uses `QFormLayout` for neatly aligned form-style UI.

        Layout:
            - Checkbox and group box are added to the main vertical layout (`main_layout`) for integration with the rest of the interface.
        """

        self.group_2 = QGroupBox("Initial Conditions")
        self.group_2.setFont(QFont('Times', 9))
        group_2_layout = QFormLayout()

        self.group_2.setStyleSheet("""
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

        self.init_position_group(group_2_layout)
        self.init_angle_group(group_2_layout)

        self.group_2.setLayout(group_2_layout)
        self.group_2.setEnabled(False)

        self.enable_checkbox = QCheckBox("Enable Initial Conditions")
        self.enable_checkbox.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        self.enable_checkbox.stateChanged.connect(self.enable_checkbox_fun)

        self.main_layout.addWidget(self.enable_checkbox)
        self.main_layout.addWidget(self.group_2)

    def init_position_group(self, parent_layout):
        """
        Initializes the position input group for the sprite's initial body origin.

        Creates a `QGroupBox` titled "Initial Position of Body Origin" that contains 
        spin boxes for specifying the X, Y, and Z coordinates of the sprite's starting location. 
        Each coordinate input is represented using a `QDoubleSpinBox` with a value range from -100 to 100 meters.

        Parameters
        ----------
        parent_layout : QFormLayout
            The layout to which the initialized position group is added.

        Components Initialized:
            - `position_x` (QDoubleSpinBox): Input for X-axis initial position (with "m" suffix).
            - `position_y` (QDoubleSpinBox): Input for Y-axis initial position (with "m" suffix).
            - `position_z` (QDoubleSpinBox): Input for Z-axis initial position (with "m" suffix).

        Signals
        -------
        Each spin box is connected to:
            - `initial_condition_changed`: Slot triggered when any position value changes.

        Visual Styling:
            - Teal-themed group box with bold title and rounded border.
            - Uses `QFormLayout` for compact, readable alignment.

        Layout
        ------
        The `position_group` is appended to the `parent_layout`, which is passed from the calling function.
        """

        position_group = QGroupBox("Initial Position of Body Origin")
        position_group.setStyleSheet("""
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
        layout = QFormLayout()
        self.position_x = QDoubleSpinBox(); self.position_y = QDoubleSpinBox(); self.position_z = QDoubleSpinBox()
        for axis, spinbox in zip(('X', 'Y', 'Z'), (self.position_x, self.position_y, self.position_z)):
            spinbox.setRange(-100, 100)
            spinbox.setSuffix("m")
            spinbox.valueChanged.connect(self.initial_condition_changed)
            label = QLabel(f"{axis}:")
            label.setFont(QFont('Times', 7))
            layout.addRow(label, spinbox)

        position_group.setLayout(layout)
        parent_layout.addRow(position_group)

    def init_angle_group(self, parent_layout):
        """
        Initializes the Euler angle input group for the sprite's initial orientation.

        Constructs a `QGroupBox` titled "Initial Euler Angles" containing spin boxes for 
        defining the initial rotational orientation using three Euler angles: Alpha, Beta, and Gamma.
        Each angle input is provided via a `QDoubleSpinBox`, allowing values in the range of -360° to 360°.

        Parameters
        ----------
        parent_layout : QFormLayout
            The layout into which the angle group is inserted.

        Components Initialized:
            - `angle_input_alpha` (QDoubleSpinBox): Input for the Alpha angle (°).
            - `angle_input_beta` (QDoubleSpinBox): Input for the Beta angle (°).
            - `angle_input_gamma` (QDoubleSpinBox): Input for the Gamma angle (°).

        Signals
        -------
        Each spin box emits:
            - `valueChanged`: Connected to `initial_condition_changed` to propagate changes in orientation.

        Visual Styling:
            - Purple-themed group box with bold headers and rounded styling.
            - Employs `QFormLayout` for structured alignment of angle labels and inputs.

        Layout
        ------
        The `angle_group` is added to the supplied `parent_layout`, typically as part of the initial conditions section.
        """
        angle_group = QGroupBox("Initial Euler Angles")
        angle_group.setStyleSheet("""
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
        layout = QFormLayout()
        self.angle_input_alpha = QDoubleSpinBox(); self.angle_input_beta = QDoubleSpinBox(); self.angle_input_gamma = QDoubleSpinBox()
        for angle, spinbox in zip(("Alpha", "Beta", "Gamma"),
                                (self.angle_input_alpha, self.angle_input_beta, self.angle_input_gamma)):
            spinbox.setRange(-360, 360)
            spinbox.setSuffix("°")
            spinbox.valueChanged.connect(self.initial_condition_changed)
            label = QLabel(f"{angle}:")
            label.setFont(QFont('Times', 7))
            layout.addRow(label, spinbox)

        angle_group.setLayout(layout)
        parent_layout.addRow(angle_group)

    def init_finish_controls(self):
        """
        Initializes the final control elements for sprite creation.

        Adds a "Finish" button to the main layout, enabling the user to complete and confirm
        the sprite configuration process. The button is connected to the `finish_button_fun` 
        slot which handles the finalization logic.

        Components Initialized:
            - `finish_button` (QPushButton): Labeled "Finish", triggers completion of sprite setup.

        Signals
        -------
        - `clicked`: Connected to `finish_button_fun` to process and finalize sprite parameters.

        Layout
        ------
        - Appended directly to `main_layout`, positioned after all configuration groups.
        """
        self.finish_button = QPushButton("Finish")
        self.finish_button.clicked.connect(self.finish_button_fun)
        self.main_layout.addWidget(self.finish_button)

    def open_file(self):
        """
        Opens and loads an STL file for rendering using VTK.

        This method prompts the user to select an STL file through a file dialog.
        Upon selection, it performs the following operations:
            - Sets the STL file path in the corresponding input field.
            - Loads the STL geometry using a VTK reader.
            - Creates a VTK actor from the STL data.
            - Computes bounding box dimensions to determine a suitable axis scale.
            - Creates and adds coordinate axes for both inertial and body frames.
            - Renders the scene in the VTK render window.

        Workflow Steps:
            1. Show `QFileDialog` to select `.stl` file.
            2. Load geometry using `_load_stl_file()`.
            3. Create visual actor via `_create_actor_from_reader()`.
            4. Generate axes using `_create_axes_actor()`.
            5. Final rendering prepared via `_prepare_renderer_with_actors()`.

        Axes:
            - Inertial Axes: X, Y, Z (black)
            - Body Axes: A, B, C (black)

        Notes
        -----
        - Early exit occurs if the user cancels file selection.
        - Actor bounds are used to normalize axis size for consistent visualization.
        """

        file_path, _ = QFileDialog.getOpenFileName(filter='STL File (*.stl)')
        if not file_path:
            return

        self.sprite_stl_path.setText(file_path)

        reader = self._load_stl_file(file_path)
        self.actor = self._create_actor_from_reader(reader)

        bounds = self.actor.GetBounds()
        max_length = max(bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4])

        axes_inertial = self._create_axes_actor("X", "Y", "Z", max_length, color=(0, 0, 0))
        self.axes_body = self._create_axes_actor("A", "B", "C", max_length, color=(0, 0, 0))

        self._prepare_renderer_with_actors(self.actor, axes_inertial, self.axes_body)

    def _load_stl_file(self, file_path):
        """
        Loads an STL file using VTK's STL reader.

        Parameters
        ----------
        file_path : str
            Full path to the `.stl` file to be loaded.

        Returns
        -------
        vtk.vtkSTLReader
            Configured STL reader instance with the file path set.
        
        """
        reader = vtkSTLReader()
        reader.SetFileName(file_path)
        return reader

    def _create_actor_from_reader(self, reader):
        """
        Creates a VTK actor from a given STL reader.

        Configures a `vtkPolyDataMapper` to process the reader's output and assigns it 
        to a `vtkActor`. Sets visual properties such as color and opacity.

        Parameters
        ----------
        reader : vtk.vtkSTLReader
            STL reader instance containing geometry data.

        Returns
        -------
        vtk.vtkActor
            Actor representing the STL model with applied visual properties.
        """
        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        actor = vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.5, 0.7, 1)  # Light blue
        actor.GetProperty().SetOpacity(0.6)
        return actor

    def _create_axes_actor(self, label_x, label_y, label_z, scale, color=(0, 0, 0)):
        """
        Creates a VTK `AxesActor` with custom axis labels, scale, and label color.

        Configures the axis lengths, shaft type, and axis captions for a VTK coordinate 
        system representation. Useful for displaying reference frames in 3D scenes.

        Parameters
        ----------
        label_x : str
            Label for the X-axis (e.g., "X" or "A").
        label_y : str
            Label for the Y-axis (e.g., "Y" or "B").
        label_z : str
            Label for the Z-axis (e.g., "Z" or "C").
        scale : float
            Uniform scaling factor for the length of the axes.
        color : tuple of float, optional
            RGB color for the axis labels (default is black: (0, 0, 0)).

        Returns
        -------
        vtk.vtkAxesActor
            Configured VTK actor representing the 3D coordinate axes.
        """

        axes = vtkAxesActor()
        axes.SetTotalLength(scale * 0.1, scale * 0.1, scale * 0.1)
        axes.SetShaftTypeToCylinder()
        axes.SetAxisLabels(True)

        axes.SetXAxisLabelText(label_x)
        axes.SetYAxisLabelText(label_y)
        axes.SetZAxisLabelText(label_z)

        axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetColor(*color)
        axes.GetYAxisCaptionActor2D().GetCaptionTextProperty().SetColor(*color)
        axes.GetZAxisCaptionActor2D().GetCaptionTextProperty().SetColor(*color)

        return axes

    def _prepare_renderer_with_actors(self, *actors):
        """
        Prepares the VTK renderer by clearing it and adding specified actors.

        This method removes all existing view props from the renderer, adds the provided 
        actors to the scene, resets the camera to frame all visible geometry, and triggers 
        a re-render. It ensures a clean and updated 3D viewport after loading new content.

        Parameters
        ----------
        *actors : vtk.vtkProp
            Variable number of VTK actors (e.g., model, axes) to be added to the renderer.
        """

        self.ren.RemoveAllViewProps()
        for actor in actors:
            self.ren.AddActor(actor)
        self.ren.SetBackground(0.95, 0.95, 0.95)
        self.ren.ResetCamera()
        self.vtkWidget.GetRenderWindow().Render()

    def translation_transform_fun(self):
        """
        Handles UI logic for the translation transform selection.

        Clears any previously added translation UI components and conditionally adds
        a new group of widgets for configuring the translation transform, based on 
        the current selection in the combo box.

        Behavior:
            - If the selected option is 'COM' (index 1), a new translation configuration
            group is created and added to the layout.
            - If 'Constant' (index 0), no additional UI is shown.

        Triggered when:
            - The user changes the selection in the translation transform combo box.
        """

        self._clear_previous_translation_group()

        if self.translation_transform.currentIndex() == 1:
            self.translation_transform_group = self._create_translation_group()
            self.translation_transform_layout.addWidget(self.translation_transform_group)

    def _clear_previous_translation_group(self):
        """
        Removes any existing translation transform UI group from the layout.

        This method checks for the presence of a previously created translation
        transform group (e.g., when switching from one transform type to another),
        and ensures it is properly removed and deleted from memory to prevent
        redundant widgets or memory leaks.

        Effects:
            - Removes the widget from the layout.
            - Deletes the widget instance.
            - Clears the attribute reference.
        """

        if hasattr(self, "translation_transform_group"):
            self.translation_transform_layout.removeWidget(self.translation_transform_group)
            self.translation_transform_group.deleteLater()
            del self.translation_transform_group

    def _create_translation_group(self):
        """
        Creates and returns a UI group box for translation properties.

        This group is dynamically generated when the user selects a specific
        translation transform (e.g., "COM") from the combo box. It displays
        position-related controls that allow configuring translation parameters.

        Group Box Title:
            - "Translation Properties"

        Style:
            - Font: Times, size 8
            - Border: Solid gray with rounded corners

        Returns:
            QGroupBox: A styled container holding translation input widgets.
        """
        group = QGroupBox("Translation Properties")
        group.setFont(QFont('Times', 8))
        group.setStyleSheet("""
            QGroupBox {
                color: #7f8c8d;
                font-weight: bold;
                border: 2px solid #626567;
                border-radius: 6px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px;
            }   
        """)

        layout = QVBoxLayout()
        form_layout = QFormLayout()
        label, hbox = self._create_position_row()
        form_layout.addRow(label, hbox)

        layout.addLayout(form_layout)
        group.setLayout(layout)
        return group

    def _create_position_row(self):
        """
        Creates a labeled input row for specifying the position time series.

        This method constructs a `QLabel` and a horizontal layout containing
        a `QLineEdit` for manual input and a file selection `QPushButton`
        to load the time series data representing the center of mass (COM) position.

        Elements:
            - QLabel: "Position:", styled with Times font
            - QLineEdit: Placeholder "Time series of COM position"
            - QPushButton: "Open", with folder icon and file selection functionality

        Returns:
            tuple: (QLabel, QHBoxLayout) representing the position input row.
        """

        label = QLabel("Position:")
        label.setFont(QFont('Times', 7))

        hbox = QHBoxLayout()
        self.position_input = QLineEdit()
        self.position_input.setPlaceholderText("Time series of COM position")

        self.open_position = QPushButton("Open")
        self.open_position.setFont(QFont('Times', 7))
        color = self.palette().color(self.foregroundRole()).name()
        self.open_position.setIcon(icon("fa5.folder-open", color=color))
        self.open_position.clicked.connect(self.open_position_file)

        hbox.addWidget(self.position_input)
        hbox.addWidget(self.open_position)

        return label, hbox

    def flexibility_transform_fun(self):
        """
        Handles the dynamic creation and display of flexibility transformation UI elements.

        Based on the selected transformation type, this method:
            - Removes any previously displayed flexibility transform group.
            - Checks the current index of the flexibility combo box.
            - Creates and displays the corresponding flexibility group box 
            for "FlexibleType1" or "FlexibleType2".

        Conditions:
            - Index 1: Displays UI for "FlexibleType1"
            - Index 2: Displays UI for "FlexibleType2"
            - Other indices: No UI group is displayed

        UI Elements Managed:
            - Dynamically created group box via `_create_flexibility_group_box`
            - Primary color is derived from the application's current foreground palette
        """

        primary_color = self.palette().color(self.foregroundRole()).name()

        # Remove previous widget if it exists
        if hasattr(self, "flexibility_transform_group"):
            self.flexibility_transform_layout.removeWidget(self.flexibility_transform_group)
            self.flexibility_transform_group.deleteLater()
            del self.flexibility_transform_group

        selected_index = self.flexibility_transform.currentIndex()
        if selected_index not in [1, 2]:
            return

        self.flexibility_transform_group = self._create_flexibility_group_box(selected_index, primary_color)
        self.flexibility_transform_layout.addWidget(self.flexibility_transform_group)

    def _create_flexibility_group_box(self, selected_index, primary_color):
        """
        Create and return a QGroupBox for the selected flexibility transformation type.

        This method builds a group box containing appropriate input rows based on 
        the selected flexibility mode (FlexibleType1 or FlexibleType2). Each row 
        consists of axis toggles and transformation-specific parameters.

        Parameters
        ----------
        selected_index : int
            Index from the flexibility dropdown that determines which input fields to show:
                - 1: FlexibleType1 (shows P-value and Time Period rows)
                - 2: FlexibleType2 (shows M-value and P-value rows)

        primary_color : str
            The current primary color (in hex format) used for styling icons or controls.

        Returns
        -------
        QGroupBox
            A fully configured group box widget containing flexibility-related inputs.
        """

        group = QGroupBox("Flexibility Transform")
        group.setStyleSheet("""
            QGroupBox {
                color: #7f8c8d;
                font-weight: bold;
                border: 2px solid #626567;
                border-radius: 6px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px;
            }
        """)
        layout = QVBoxLayout()

        # Axis toggles
        layout.addLayout(self._create_axis_selector_row())

        if selected_index == 1:
            layout.addLayout(self._create_p_value_row())                        
            layout.addLayout(self._create_time_period_row())

        elif selected_index == 2:
            layout.addLayout(self._create_m_value_row(primary_color))
            layout.addLayout(self._create_p_value_row())

        group.setLayout(layout)
        return group

    def _create_axis_selector_row(self):
        """
        Create and return a horizontal layout with axis selector dropdowns.

        This row provides comboboxes for selecting whether flexibility should be 
        applied along the X, Y, and Z axes. Each dropdown allows the user to 
        choose between 'True' or 'False'.

        Returns
        -------
        QHBoxLayout
            A layout containing axis labels and corresponding boolean selectors 
            for the X, Y, and Z axes.
        """

        layout = QHBoxLayout()

        font7 = QFont('Times', 7)
        font8 = QFont('Times', 8)

        self.temp_combobox_x = QComboBox()
        self.temp_combobox_y = QComboBox()
        self.temp_combobox_z = QComboBox()
        for box in [self.temp_combobox_x, self.temp_combobox_y, self.temp_combobox_z]:
            box.addItems(["True", "False"])
            box.setFont(font8)

        layout.addStretch()
        layout.addWidget(QLabel("X:", font=font7))
        layout.addWidget(self.temp_combobox_x)
        layout.addStretch()
        layout.addWidget(QLabel("Y:", font=font7))
        layout.addWidget(self.temp_combobox_y)
        layout.addStretch()
        layout.addWidget(QLabel("Z:", font=font7))
        layout.addWidget(self.temp_combobox_z)
        layout.addStretch()
        return layout

    def _create_time_period_row(self):
        """
        Create and return a horizontal layout for the time period input.

        This row provides a label and a spin box to configure the time period 
        parameter associated with the flexibility transform.

        Returns
        -------
        QHBoxLayout
            A layout containing a descriptive label and a QSpinBox 
            for specifying the time period.
        """

        layout = QHBoxLayout()
        label = QLabel("Time Period:")
        label.setFont(QFont('Times', 7))
        self.time_period = QSpinBox()
        self.time_period.setRange(0, 100000)
        self.time_period.setFont(QFont('Times', 8))
        layout.addWidget(label)
        layout.addWidget(self.time_period)
        return layout

    def _create_m_value_row(self, primary_color):
        """
        Create and return a horizontal layout for specifying M values.

        This layout includes a label, a QLineEdit for user input, and an 
        "Open" button to load M values from a file. The button icon color is 
        set using the provided primary color.

        Parameters
        ----------
        primary_color : str
            Hex color code used for styling the folder-open icon on the button.

        Returns
        -------
        QHBoxLayout
            A layout containing the M values label, input field, and file open button.
        """

        layout = QHBoxLayout()
        label = QLabel("M values:")
        label.setFont(QFont('Times', 7))

        self.path_m_values = QLineEdit()
        self.path_m_values.setPlaceholderText("Enter M values")
        self.path_m_values.setFont(QFont('Times', 8))

        self.open_m_values = QPushButton("Open")
        self.open_m_values.setIcon(icon("fa5.folder-open", color=primary_color))
        self.open_m_values.clicked.connect(self.open_m_values_fun)

        layout.addWidget(label)
        layout.addWidget(self.path_m_values)
        layout.addWidget(self.open_m_values)
        return layout
    
    def _create_p_value_row(self):
        """
        Create and return a horizontal layout for specifying the value of p.

        The layout consists of a label and a QDoubleSpinBox for entering a 
        floating-point value between 0 and 1, typically used to control flexibility 
        parameters in transformations.

        Returns
        -------
        QHBoxLayout
            A layout containing the label and spinbox for the p value input.
        """

        layout = QHBoxLayout()
        label = QLabel("p:")
        label.setFont(QFont('Times', 7))

        self.p_value = QDoubleSpinBox()
        self.p_value.setRange(0, 1)
        self.p_value.setFont(QFont('Times', 8))

        layout.addWidget(label)
        layout.addWidget(self.p_value)
        return layout

    def rotation_transform_fun(self):
        """
        Handle UI logic based on the selected rotation transform option.

        If 'Euler_Angles' is selected, adds an additional group box for configuring
        Euler angle parameters. If the selection is changed to another mode and a 
        group box exists, it is removed to clean up the layout.
        """

        if self.rotation_transform.currentIndex() == 1:
            group_box = self._create_rotation_group_box()
            self.rotation_transform_layout.addWidget(group_box)
        else:
            if self.rotation_transform_layout.count() > 1:
                item = self.rotation_transform_layout.itemAt(1)
                if item and item.widget():
                    item.widget().deleteLater()

    def _create_rotation_group_box(self):
        """
        Create and return a QGroupBox for configuring rotation transformations.

        This UI group includes:
            - A selector for Euler angle order.
            - Buttons to load time series data for Alpha, Beta, and Gamma angles.
            - An option to invoke inverse kinematics computations.

        The group is styled and embedded within a vertical layout that includes
        labeled fields and appropriate controls.

        Returns:
            QGroupBox: A configured group box widget for rotation transform options.
        """

        group = QGroupBox("Rotation Transform")
        layout = QVBoxLayout()

        layout.addLayout(self._create_order_selector_row())

        euler_layout = QGridLayout()
        euler_layout.addWidget(QLabel("Euler Angles Time Series:"), 0, 0, 1, 3)
        euler_layout.addWidget(self._create_inverse_kinematics_button(), 0, 3)

        euler_layout.addLayout(self._create_angle_input_row("Alpha", "Time series of Alpha", self.open_rotation_alpha), 1, 0, 1, 3)
        euler_layout.addLayout(self._create_angle_input_row("Beta", "Time series of Beta", self.open_rotation_beta), 2, 0, 1, 3)
        euler_layout.addLayout(self._create_angle_input_row("Gamma", "Time series of Gamma", self.open_rotation_gamma), 3, 0, 1, 3)

        layout.addLayout(euler_layout)

        group.setLayout(layout)
        group.setStyleSheet("""
            QGroupBox {
                color: #7f8c8d;
                font-weight: bold;
                border: 2px solid #626567;
                border-radius: 6px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px;
            }
        """)
        return group

    def _create_order_selector_row(self):
        """
        Create and return a horizontal layout for selecting Euler angle rotation order.

        This row includes a label and a combo box populated with standard Euler angle 
        order permutations (both proper and Tait-Bryan sequences), allowing the user 
        to define the desired rotational sequence.

        Returns:
            QHBoxLayout: A layout containing the Euler angle order selection controls.
        """

        layout = QHBoxLayout()
        label = QLabel("Order:")
        label.setFont(QFont('Times', 8))

        self.euler_angles_order = QComboBox()
        self.euler_angles_order.addItems(["ZXZ", "XYX", "YZY", "ZYZ", "XZX", "YXY", "ZXY", "YXZ", "XZY", "YZX", "ZYX", "XYZ"])
        self.euler_angles_order.setFont(QFont('Times', 8))

        layout.addWidget(label)
        layout.addWidget(self.euler_angles_order)
        return layout

    def _create_inverse_kinematics_button(self):
        """
        Create and return a styled QPushButton for importing inverse kinematics data.

        The button allows users to load 3D coordinate data, typically obtained using 
        DLTdv software, for computing inverse kinematics. When clicked, it triggers 
        the `calculate_inverse_kinematics` method.

        The button includes a tooltip, custom icon, font, and cursor, along with
        a stylesheet for consistent appearance and user interaction feedback.

        Returns:
            QPushButton: The configured button for importing inverse kinematics data.
        """

        button = QPushButton("Import Inverse Kinematics")
        button.setIcon(icon("mdi.bird", color=self.palette().color(self.foregroundRole()).name()))
        button.setFont(QFont('Times', 8))
        button.setToolTip("Import 3D coordinates data obtained from DltDv Software")
        button.clicked.connect(self.calculate_inverse_kinematics)
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.setFixedHeight(30)
        button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: none;
                border-radius: 5px;
                padding: 8px 12px;
                cursor: pointer;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }
            QPushButton:focus {
                outline: none;
            }
        """)
        return button

    def _create_angle_input_row(self, label_text, placeholder_text, slot_function):
        """
        Create a horizontal layout row for Euler angle input with a label, QLineEdit, and file open button.

        This helper function generates a reusable UI row used in the rotation transform section
        for entering a time series of Euler angles (Alpha, Beta, Gamma). Each row includes:
        - A QLabel indicating the angle name.
        - A QLineEdit to show or enter the path to the data file.
        - A QPushButton to trigger a file dialog via the provided slot function.

        The QLineEdit and QPushButton are also saved as instance attributes using
        naming format `path_angle_<label_text.lower()>` and `open_angle_<label_text.lower()>`.

        Args:
            label_text (str): The name of the Euler angle (e.g., "Alpha", "Beta", "Gamma").
            placeholder_text (str): The placeholder text for the line edit input.
            slot_function (Callable): The function to be called when the file open button is clicked.

        Returns:
            QHBoxLayout: The fully constructed horizontal layout row.
        """

        layout = QHBoxLayout()

        label = QLabel(f"{label_text}:")
        label.setFont(QFont('Times', 7))

        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder_text)
        line_edit.setFont(QFont('Times', 8))

        open_button = QPushButton("Open")
        open_button.setIcon(icon("fa5.folder-open", color=self.palette().color(self.foregroundRole()).name()))
        open_button.clicked.connect(slot_function)

        # Save references if needed later
        setattr(self, f"path_angle_{label_text.lower()}", line_edit)
        setattr(self, f"open_angle_{label_text.lower()}", open_button)

        layout.addWidget(label)
        layout.addWidget(line_edit)
        layout.addWidget(open_button)

        return layout

    def enable_checkbox_fun(self):
        """
        Enable or disable `group_2` based on the checkbox state.
        """

        if self.enable_checkbox.isChecked():
            self.group_2.setEnabled(True)
        else:
            self.group_2.setEnabled(False)

    def open_rotation_alpha(self):
        """
        Open a CSV file for Alpha angle and update the UI with the selected path.
        """

        directory, _ = QFileDialog.getOpenFileName(filter="CSV Files (*.csv)")

        if directory:
            self.path_angle_alpha.setText(directory)
            self.open_angle_alpha.setStyleSheet("background-color: green")
        
    def open_rotation_beta(self):
        """
        Open a CSV file for Beta angle and update the UI with the selected path.
        """

        directory, _ = QFileDialog.getOpenFileName(filter="CSV Files (*.csv)")

        if directory:
            self.path_angle_beta.setText(directory)
            self.open_angle_beta.setStyleSheet("background-color: green")

    def open_rotation_gamma(self):
        """
        Open a CSV file for Gamma angle and update the UI with the selected path.
        """

        directory, _ = QFileDialog.getOpenFileName(filter="CSV Files (*.csv)")

        if directory:
            self.path_angle_gamma.setText(directory)
            self.open_angle_gamma.setStyleSheet("background-color: green")
    
    def open_position_file(self):
        """
        Open a CSV file for COM position and update the input field and button color.
        """

        directory, _ = QFileDialog.getOpenFileName(filter="CSV Files (*.csv)")

        if directory:
            self.position_input.setText(directory)
            self.open_position.setStyleSheet("background-color: green")
    
    def open_m_values_fun(self):
        """
        Open a CSV file for M values and update the input field and button style.
        """

        directory, _ = QFileDialog.getOpenFileName(filter="CSV Files (*.csv)")

        if directory:
            self.path_m_values.setText(directory)
            self.open_m_values.setStyleSheet("background-color: green")
        
    def finish_button_fun(self):
        """
        Finalizes the creation of a Sprite object using user-specified inputs and transformations.

        This function performs the following:
        
        1. Retrieves the sprite name and STL file path from the UI.
        2. Loads the STL mesh using `numpy-stl`.
        3. Extracts transformation data for:
            - Flexibility
            - Rotation
            - Translation
        4. Optionally applies the inverse transformation to reset the mesh using
        the initial conditions if the `enable_checkbox` is checked.
        5. Validates and prepares the full time series of rotation angles and COM positions.
        6. Creates and emits a `Sprite` object containing the transformed mesh and associated data.

        Emits:
            SpriteCreated (pyqtSignal): Emitted with the finalized `Sprite` object.

        Notes:
            - This method closes the GUI window upon completion.
            - The transformed mesh is reset using `Translation_COM()` and `ConstantF()` 
            when the inverse transformation option is enabled.

        See Also:
            - `_get_flexibility_transform`
            - `_get_rotation_transform`
            - `_get_translation_transform`
            - `_validate_angles_positions`
            - `_get_initial_conditions`

        """
        sprite_name = self.sprite_name.text()
        stl_path = self.sprite_stl_path.text()
        stl_mesh = mesh.Mesh.from_file(stl_path)

        angles_temp = np.array([0, 0, 0])
        positions_temp = np.array([0, 0, 0])

        flexibility_transform = self._get_flexibility_transform(stl_mesh)
        rotation_transform, angles = self._get_rotation_transform()
        translation_transform, positions = self._get_translation_transform()

        temp_object = Object3D(sprite_name, stl_mesh, translation_transform, rotation_transform, flexibility_transform)

        if self.enable_checkbox.isChecked():
            no_transform_temp_object = Object3D(sprite_name, stl_mesh, Translation_COM(), rotation_transform, ConstantF())
            angles_temp, positions_temp = self._get_initial_conditions()
            temp_object.stl_mesh = no_transform_temp_object.transform(positions_temp, angles_temp, 0)

        angles, positions = self._validate_angles_positions(angles, positions)
        sprite = Sprite(temp_object, positions, angles)

        if self.enable_checkbox.isChecked():
            sprite.frame_origin = positions_temp
            sprite.frame_orientation = angles_temp

        self.sprite_data = sprite
        self.SpriteCreated.emit(self.sprite_data)
        self.close()

    def _get_flexibility_transform(self, stl_mesh):
        """
        Constructs and returns the appropriate flexibility transformation based on the user’s selection.

        This method analyzes the geometry of the STL mesh to compute key spatial parameters
        (major and minor axes), and uses UI inputs to return a corresponding flexibility model:
        
        - ConstantF: No flexibility applied.
        - Flexibility_type1: Sinusoidal-based flexibility with defined axes and time period.
        - Flexibility_type2: Custom M-value driven flexibility using external CSV input.

        Parameters
        ----------
        stl_mesh : stl.mesh.Mesh
            The 3D mesh object loaded from the STL file, used to derive geometry bounds.

        Returns
        -------
        Union[ConstantF, Flexibility_type1, Flexibility_type2]
            An instantiated flexibility transformation object depending on the selected mode.

        Notes
        -----
        - `major_axis` and `minor_axis` are extracted from mesh bounds (X and Y directions).
        - Axes of influence (X, Y, Z) are toggled using combo boxes.
        - For Flexibility_type2, M-values are loaded from a user-selected CSV file.

        Raises
        ------
        ValueError
            If required inputs (e.g., M-values path) are missing or invalid.
        """
        temp_vector = np.array(stl_mesh.vectors).reshape(-1, 3)
        min_x, min_y, min_z = np.min(temp_vector, axis=0)
        max_x, max_y, max_z = np.max(temp_vector, axis=0)
        major_axis = (max_x - min_x) / 2
        minor_axis = (max_y - min_y) / 2

        index = self.flexibility_transform.currentIndex()
        if index == 0:
            return ConstantF()

        x, y, z = [combo.currentText() == "True" for combo in self.flexibility_transform_layout.itemAt(1).widget().findChildren(QComboBox)]
        p = self.p_value.value()

        if index == 1:
            time_period = self.time_period.value()
            return Flexibility_type1(x, y, z, major_axis, minor_axis, time_period, p)

        if index == 2:
            m_vals = np.array(pd.read_csv(self.path_m_values.text(), header=None))
            return Flexibility_type2(x, y, z, min_y, major_axis, minor_axis, m_vals, time_period=len(m_vals), p=p)

    def _get_rotation_transform(self):
        """
        Constructs and returns the appropriate rotation transformation object and angle data.

        This method determines the selected rotation mode and builds a corresponding transformation:
        - If rotation is disabled, a constant rotation is returned.
        - If inverse kinematics is enabled, it retrieves angle data from the inverse kinematics window.
        - Otherwise, Euler angles (alpha, beta, gamma) are loaded from user-provided CSV files.

        Returns
        -------
        Tuple[Union[ConstantR, Rotation_EulerAngles], Optional[np.ndarray]]
            A tuple containing:
            - The rotation transformation object.
            - A NumPy array of Euler angles with shape (n, 3) or `None` if not applicable.

        Notes
        -----
        - Rotation mode is selected from a `QComboBox` (`rotation_transform`).
        - Euler angles must be provided as CSV files via line edit fields in the UI.
        - If inverse kinematics is active, precomputed angles and order are retrieved from `self.window.inv_result`.

        Raises
        ------
        ValueError
            If any of the required input files are missing or unreadable.
        """
        if self.rotation_transform.currentIndex() == 0:
            return ConstantR(), None

        if self.inverse_kinematics:
            angles, order = self.window.inv_result
            angles = np.vstack(angles).T
            return Rotation_EulerAngles(order), angles

        widget = self.rotation_transform_layout.itemAt(1).widget()
        order = widget.findChildren(QComboBox)[0].currentText()
        alpha, beta, gamma = [np.array(pd.read_csv(field.text(), header=None)) for field in widget.findChildren(QLineEdit)]
        angles = np.hstack([alpha, beta, gamma])
        return Rotation_EulerAngles(order), angles

    def _get_translation_transform(self):
        """
        Constructs and returns the appropriate translation transformation object and positional data.

        Based on the selected translation mode, this method either returns:
        - A constant translation (no movement),
        - Or a center-of-mass (COM)-based translation using a user-specified CSV file.

        Returns
        -------
        Tuple[Union[ConstantT, Translation_COM], Optional[np.ndarray]]
            A tuple containing:
            - The translation transformation object.
            - A NumPy array of 3D positions with shape (n, 3) if translation is active, else `None`.

        Notes
        -----
        - The translation mode is selected via the `translation_transform` QComboBox.
        - Position data must be supplied in CSV format via a QLineEdit input within the UI.
        - The data is reshaped to match the expected (n, 3) format for COM transformation.

        Raises
        ------
        ValueError
            If the path is empty or the CSV is improperly formatted.
        """
        if self.translation_transform.currentIndex() == 0:
            return ConstantT(), None

        path = self.translation_transform_layout.itemAt(1).widget().findChildren(QLineEdit)[0].text()
        positions = np.array(pd.read_csv(path, header=None)).reshape(-1, 3)
        return Translation_COM(), positions

    def _get_initial_conditions(self):
        """
        Retrieves initial rotation angles and translation positions from the UI inputs.

        This method collects user-defined initial conditions for:
        - Rotation (Euler angles in degrees, converted to radians).
        - Translation (X, Y, Z position components).

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            A tuple containing:
            - `angles` : np.ndarray of shape (3,) — Initial [alpha, beta, gamma] in radians.
            - `positions` : np.ndarray of shape (3,) — Initial [x, y, z] position values.
        
        Notes
        -----
        - Euler angles are converted from degrees to radians using `np.radians`.
        - All values are collected from respective `QDoubleSpinBox` widgets in the UI.
        """

        alpha = np.radians(self.angle_input_alpha.value())
        beta = np.radians(self.angle_input_beta.value())
        gamma = np.radians(self.angle_input_gamma.value())
        angles = np.array([alpha, beta, gamma])

        x = self.position_x.value()
        y = self.position_y.value()
        z = self.position_z.value()
        positions = np.array([x, y, z])

        return angles, positions

    def _validate_angles_positions(self, angles, positions):
        """
        Validates and aligns the shape of rotation angles and translation positions.

        Ensures that both `angles` and `positions` are non-None and shaped correctly
        to support consistent downstream processing. Fills missing values with zeros.

        Parameters
        ----------
        angles : Optional[np.ndarray]
            Rotation angles array of shape (N, 3), or None if not provided.

        positions : Optional[np.ndarray]
            Translation positions array of shape (N, 3), or None if not provided.

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            A tuple containing:
            - `angles` : np.ndarray of shape (N, 3)
            - `positions` : np.ndarray of shape (N, 3)

        Notes
        -----
        - If one of the inputs is None, it's replaced with zeros of matching length.
        - If both are None, both are initialized as a single row of zeros.
        """
        if positions is None and angles is not None:
            positions = np.zeros((angles.shape[0], 3))
        elif angles is None and positions is not None:
            angles = np.zeros((positions.shape[0], 3))
        elif angles is None and positions is None:
            angles = np.zeros((1, 3))
            positions = np.zeros((1, 3))
        return angles, positions

    def initial_condition_changed(self):
        """
        Updates the 3D transform of the actor and body axes based on user-defined initial conditions.

        This method reads the initial Euler angles (in degrees) and position vector from the GUI inputs,
        constructs corresponding VTK rotation and translation transforms, and applies the combined
        transform to the 3D actor and associated body axes.

        Notes
        -----
        - Rotation is performed around X, Y, and Z axes in that order.
        - Transforms are post-multiplied to ensure correct order of translation followed by rotations.
        - The scene is re-rendered to reflect the updated transformation in the VTK widget.
        """
        alpha = self.angle_input_alpha.value()
        beta = self.angle_input_beta.value()
        gamma = self.angle_input_gamma.value()

        x_pos = self.position_x.value()
        y_pos = self.position_y.value()
        z_pos = self.position_z.value()

        alpha = np.radians(alpha)
        beta = np.radians(beta)
        gamma = np.radians(gamma)
        
        angles_temp = np.array([alpha, beta, gamma])
        positions_temp = np.array([x_pos, y_pos, z_pos])

        Rotation_Transform_x = vtkTransform()
        Rotation_Transform_x.RotateX(np.degrees(angles_temp[0]))

        Rotation_Transform_y = vtkTransform()
        Rotation_Transform_y.RotateY(np.degrees(angles_temp[1]))

        Rotation_Transform_z = vtkTransform()
        Rotation_Transform_z.RotateZ(np.degrees(angles_temp[2]))

        final_transform = vtkTransform()
        final_transform.PostMultiply()
        final_transform.Translate(positions_temp)
        final_transform.Concatenate(Rotation_Transform_x)
        final_transform.Concatenate(Rotation_Transform_y)
        final_transform.Concatenate(Rotation_Transform_z)
        
        self.actor.SetUserTransform(final_transform)
        self.axes_body.SetUserTransform(final_transform)
        self.vtkWidget.GetRenderWindow().Render()

    def calculate_inverse_kinematics(self):
        """
        Opens the Inverse Kinematics window and connects its output signal to the data processing slot.

        This method initializes and displays the `InvKineWindow`, which is responsible for loading
        3D coordinate data and computing Euler angles. Once the data is available, it emits the
        `angle_data` signal, which is connected to the `process_inv_data` method for handling.

        Notes
        -----
        - The inverse kinematics data flow is fully asynchronous and signal-driven.
        - The method assumes `process_inv_data` is implemented and compatible with the signal payload.
        """
        self.window = InvKineWindow()
        self.window.show()
        self.window.angle_data.connect(self.process_inv_data)
    
    def process_inv_data(self):
        """
        Processes the Euler angle results from the inverse kinematics window.

        This method retrieves computed angles and their rotation order from the 
        `InvKineWindow`, disables the manual rotation input section to avoid conflict, 
        and updates the rotation order in the UI.

        Notes
        -----
        - Sets `self.inverse_kinematics` to True, indicating automatic angle data is now active.
        - Assumes that `self.window.inv_result` contains a tuple: (angles, order).
        - UI combo box is updated to reflect the computed rotation order.
        """
        angles, order = self.window.inv_result
        alpha_values, beta_values, gamma_values = angles
        self.rotation_transform_layout.itemAt(1).widget().setEnabled(False)
        self.rotation_transform_layout.itemAt(1).widget().findChildren(QComboBox)[0].setCurrentText(order)
        self.inverse_kinematics = True
        
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
    
    def about_button_fun(self):
        """
        Displays an 'About FlapKine' information dialog.

        Shows details about the developer, version, and purpose of the application.
        """
        QMessageBox.about(self, "About FlapKine", '''
        <h1>FlapKine</h1>
        <p>Developed by: Kalbhavi Vadhiraj</p>                  
        <p>Version 0.0.1</p>
        <p>FlapKine provides a visual representation and simulation of the kinematics and aerodynamics of flapping wing micro-aerial vehicles (MAVs). It allows users to analyze and optimize MAV designs with precision and clarity, revealing the intricate mechanics of flapping flight. Whether for research, development, or educational purposes, this tool offers valuable insights into the performance and behavior of MAVs, facilitating advanced design and innovation.</p> 
''')