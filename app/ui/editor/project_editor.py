import os
import pickle

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QDesktopWidget, QGroupBox, QHBoxLayout, QMainWindow, QMessageBox,
    QVBoxLayout, QWidget, QSplitter,
)

from app.widgets.misc.menu_bar import MenuBar
from app.widgets.misc.render_config_edit import RenderConfig
from app.widgets.main.video_animation import VideoAnimation
from app.widgets.main.frame_visualiser import Visualizer3DWidget
from app.widgets.main.point_visualiser import PointScatterWidget
    

    
class ProjectWindow(QMainWindow):
    """
    ProjectWindow Class
    ===================

    This class represents the main operational GUI window for managing and visualizing a completed FlapKine project.

    It provides a split interface integrating video animation playback, 3D visual scene visualization, and 
    interactive point manipulation tools. It also includes a custom menu bar for global actions and supports 
    dynamic reconfiguration of render settings. Scene data is automatically loaded from the project folder and 
    used to initialize the application modules.

    Attributes
    ----------
    project_folder : str
        Path to the FlapKine project directory containing scene data and assets.

    menu_bar : MenuBar
        Custom top menu bar allowing control over application-level features like exit, minimize, 
        restore, about info, and render configuration.

    right_group : PointScatterWidget
        Right panel widget displaying the interactive point scatter tool for the imported scene.

    topleftgroup : VideoAnimation
        Top-left panel widget used for rendering and controlling video animations of the project.

    bottomleftgroup : Visualizer3DWidget
        Bottom-left panel widget used for rendering and interacting with the 3D scene visualization.

    scene_data : SceneData
        Deserialized scene data loaded from the project folder (extracted from `scene.pkl`).

    angles : list
        List of orientation angles (usually Roll, Pitch, Yaw) for the primary object in the scene.

    Methods
    -------
    __init__(project_folder: str)
        Initializes the main window, loads project data, composes the layout, and sets up the UI modules.

    process_project()
        Loads the serialized scene file from the project folder and extracts associated parameters.

    center()
        Moves the application window to the center of the user's screen for better UX.

    showErrorDialog(title: str, message: str)
        Displays a critical error dialog with the given title and message.

    showAlertDialog(title: str, message: str)
        Displays an informational alert dialog with the given title and message.

    change_render_config()
        Opens the secondary RenderConfig window for customizing rendering parameters.

    about_button_fun()
        Displays information about the application and its authorship in a modal dialog.
    """

    def __init__(self, project_folder):
        """
        Initializes the ProjectWindow class.

        Sets up the main window for visualizing and interacting with an existing FlapKine project.
        This includes configuring the window's properties, loading the project data, initializing
        the custom menu bar with predefined actions, and constructing the main layout containing
        video animation, 3D visualization, and point interaction panels.

        Parameters
        ----------
        project_folder : str
            Path to the directory where the FlapKine project and its scene data are stored.

        Components Initialized
        ----------------------
        - Window title: "FlapKine"
        - Window size: 1280x800 pixels
        - Window icon: FlapKine icon from `app/assets/flapkine_icon.png`
        - Menu bar: Custom `MenuBar` instance with connected actions:
            - Exit
            - Minimize
            - Maximize
            - Restore
            - About (application info)
            - Configure Render (opens render configuration window)
        - Scene data: Loaded from `scene.pkl` in the project folder
        - Right pane: `PointScatterWidget` for interactive point-based scene control
        - Top-left pane: `VideoAnimation` player for reviewing motion sequences
        - Bottom-left pane: `Visualizer3DWidget` for real-time 3D rendering
        """

        super(ProjectWindow, self).__init__()
        
        self.project_folder = project_folder
        self.setWindowTitle("FlapKine")
        self.resize(1280, 800)
        self.center()
        self.setWindowIcon(QIcon(os.path.join('app', 'assets', 'flapkine_icon.png')))

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

        self.process_project()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        main_splitter = QSplitter(Qt.Horizontal)

        # ------------------------ RIGHT PANE ------------------------
        self.right_group = PointScatterWidget(self.scene_data)
        main_splitter.addWidget(self.right_group)
        self.right_group.setMinimumSize(640, 800)
        self.right_group.setMaximumSize(640, 800)

        # ------------------------ LEFT PANE ------------------------
        left_splitter = QSplitter(Qt.Vertical)

        # --- Top Left Group: Video Animation ---
        self.topleftgroup = VideoAnimation(self.project_folder, self.scene_data)
        topleft_groupbox = QGroupBox("Video Animation")
        topleft_layout = QVBoxLayout()
        topleft_layout.addWidget(self.topleftgroup)
        topleft_groupbox.setLayout(topleft_layout)
        topleft_groupbox.setMinimumSize(640, 400)
        topleft_groupbox.setMaximumSize(640, 400)

        # --- Bottom Left Group: 3D Visualizer ---
        self.bottomleftgroup = Visualizer3DWidget(self.scene_data, self.project_folder, self.angles)
        bottomleft_groupbox = QGroupBox("3D Visualizer")
        bottomleft_layout = QVBoxLayout()
        bottomleft_layout.addWidget(self.bottomleftgroup)
        bottomleft_groupbox.setLayout(bottomleft_layout)
        bottomleft_groupbox.setMinimumSize(640, 400)
        bottomleft_groupbox.setMaximumSize(640, 400)

        # Add to vertical splitter (left side)
        left_splitter.addWidget(topleft_groupbox)
        left_splitter.addWidget(bottomleft_groupbox)
        left_splitter.setSizes([400, 400])
        left_splitter.setMinimumSize(640, 800)
        left_splitter.setMaximumSize(640, 800)

        # Insert left into main splitter
        main_splitter.insertWidget(0, left_splitter)
        main_splitter.setSizes([640, 640])

        main_layout.addWidget(main_splitter)

    def process_project(self):
        """
        Loads the project scene data from the specified folder.

        Attempts to locate and deserialize the `scene.pkl` file from the given project directory. 
        If successful, initializes `scene_data` and extracts orientation `angles` from the first 
        object in the scene. Displays a critical error dialog if the scene file is missing.

        Behavior
        --------
        - Loads: `scene_data` : Deserialized scene object containing project metadata
        - Extracts: `angles` : Orientation data from the first scene object

        Error Handling
        --------------
        - Displays a critical error dialog if `scene.pkl` is not found in the `project_folder`.
        """

        scene_path = os.path.join(self.project_folder, 'scene.pkl')
        
        if not os.path.exists(scene_path):
            self.showErrorDialog('Error', f"No project found at: {self.project_folder}")
            
        else:
            with open(scene_path, 'rb') as scene_file:
                self.scene_data = pickle.load(scene_file)
                self.angles = self.scene_data.objects[0].angles

    def center(self):
        """
        Centers the application window on the user's screen.

        Calculates the screen resolution and window size to determine the optimal top-left
        coordinates that position the window in the center of the screen. Adjusts the window
        position accordingly.
        
        Notes
        -----
        This method ensures consistent window placement regardless of screen resolution.
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

    def showErrorDialog(self, title, message):
        """
        Displays a critical error dialog with the specified title and message.

        Creates and shows a modal `QMessageBox` configured to indicate an error condition.
        Typically used to alert users when essential files or configurations are missing.

        Parameters
        ----------
        title : str
            The title text displayed on the error dialog window.

        message : str
            The detailed error message shown within the dialog content.
        """
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle(title)
        error_dialog.setText(message)
        error_dialog.exec_()

    def showAlertDialog(self, title, message):
        """
        Displays an informational alert dialog with the given title and message.

        Presents a modal `QMessageBox` configured to convey general information to the user.
        Commonly used for confirmations, status updates, or non-critical notices.

        Parameters
        ----------
        title : str
            The title text displayed on the alert dialog window.

        message : str
            The information content shown inside the dialog.
        """
        alert_dialog = QMessageBox()
        alert_dialog.setIcon(QMessageBox.Information)
        alert_dialog.setWindowTitle(title)
        alert_dialog.setText(message)
        alert_dialog.exec_()
    
    def change_render_config(self):
        """
        Launches the render configuration interface.

        Instantiates a `RenderConfig` window using the current project folder and displays it.
        This allows users to modify rendering parameters such as resolution, lighting, and output format.

        Notes
        -----
        The `RenderConfig` window is shown non-modally, allowing interaction with the main window simultaneously.
        """
        self.window2 = RenderConfig(self.project_folder)
        self.window2.show()

    def about_button_fun(self):
        """
        Displays the About dialog for the FlapKine application.

        Opens a modal `QMessageBox` containing application metadata, author information,
        and a brief description of the project's purpose and capabilities.
        """
        QMessageBox.about(self, "About FlapKine", '''
        <h1>FlapKine</h1>
        <p>Developed by: Kalbhavi Vadhiraj</p>                  
        <p>Version 0.0.1</p>
        <p>FlapKine provides a visual representation and simulation of the kinematics and aerodynamics of flapping wing micro-aerial vehicles (MAVs). It allows users to analyze and optimize MAV designs with precision and clarity, revealing the intricate mechanics of flapping flight. Whether for research, development, or educational purposes, this tool offers valuable insights into the performance and behavior of MAVs, facilitating advanced design and innovation.</p> 
''')