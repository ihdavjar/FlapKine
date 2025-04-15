import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QDesktopWidget, QMainWindow, QMessageBox,
    QVBoxLayout, QWidget, QLabel, QPushButton, QFileDialog
)

from qtawesome import icon

from version import __version__
from app.widgets.misc.menu_bar import MenuBar
from app.ui.creators.project_creator import ProjectCreator
from app.ui.editor.project_editor import ProjectWindow


class MainWindow(QMainWindow):
    """
    MainWindow Class
    ================

    The main window of the FlapKine application, providing the interface to create and open projects, 
    access menu items, and navigate the application.

    Attributes
    ----------
    menu_bar : MenuBar
        Custom menu bar widget containing the application's menu actions.
        
    b_new : QPushButton
        Button for creating a new project.
        
    b_open : QPushButton
        Button for opening an existing project.

    Methods
    -------
    __init__():
        Initializes the main window, sets the window title, icon, and connects menu actions.

    initUI():
        Initializes the user interface layout, including the title, buttons, and central widget.

    center():
        Centers the window on the screen.

    create_new_project():
        Opens a dialog to select a directory to create a new project and launches the ProjectCreator window.

    open_existing_project():
        Opens a dialog to select an existing project directory and launches the ProjectWindow.

    maximize_button_fun():
        Maximizes the window and re-centers it on the screen.

    minimize_button_fun():
        Minimizes the window.

    restore_button_fun():
        Restores the window to its normal size.

    exit_button_fun():
        Closes the main window.

    show_about():
        Displays an "About" dialog containing information about the FlapKine application.
    """
    def __init__(self):
        """
        Initializes the main window of the FlapKine application.

        Sets up the window properties including title, icon, and menu bar. Configures actions in the menu 
        bar such as creating a new project, opening an existing project, minimizing, maximizing, restoring, 
        and showing an about dialog. The UI components are initialized through the `initUI()` method.

        Components Initialized:
            - Window title: "FlapKine"
            - Window icon: FlapKine icon from assets
            - Menu bar: Custom `MenuBar` instance with connected actions:
                - New Project
                - Open Project
                - Minimize
                - Maximize
                - Restore
                - About (application info dialog)
            - Central layout and buttons: Buttons to create a new project or open an existing one, set up in `initUI()`
        """
        super(MainWindow, self).__init__()
        # Place the window in the center of the screen
        self.setWindowTitle("FlapKine")

        # Set the icon
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS 
        else:
            base_path = os.path.dirname(__file__)
        icon_path = os.path.join(base_path, 'app', 'assets', 'flapkine_icon.png')
        self.setWindowIcon(QIcon(icon_path))
        
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)
        self.menu_bar.connect_actions({
            'new': self.create_new_project,
            'open': self.open_existing_project,
            'minimize': self.showMinimized,
            'maximize': self.showMaximized,
            'restore': self.showNormal,
            'about': self.about_button_fun
        })

        self.initUI()

    def initUI(self):
        """
        Initializes the user interface for the FlapKine main window.

        Sets up the geometry, central widget, and layout for the main window. Configures the primary color 
        based on the foreground role, and adds UI components including a title label and buttons for creating 
        a new project or opening an existing project. The layout and buttons are arranged in a vertical box 
        layout (`QVBoxLayout`), with central alignment.

        Components Initialized:
            - Window geometry: Position set to (200, 200), size (400, 250)
            - Central widget: Contains the title label and buttons
            - Title label: "Welcome to FlapKine", styled with font size 18px and bold weight
            - Buttons:
                - New Project: Triggered via `create_new_project()` method
                - Open Project: Triggered via `open_existing_project()` method
            - Layout: Vertical box layout (`QVBoxLayout`) with central alignment for the components
        """
        self.setGeometry(200, 200, 400, 250)
        self.center()

        primary_color = self.palette().color(self.foregroundRole()).name()

        central_widget = QWidget(self)

        center_layout = QVBoxLayout()

        # Add a title label
        title = QLabel("Welcome to FlapKine")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignCenter)
        

        # Adding Buttons
        self.b_new = QPushButton(self)
        self.b_new.setText("  New Project")
        self.b_new.setIcon(icon("fa5.file", color=primary_color))
        self.b_new.clicked.connect(self.create_new_project)
        

        self.b_open = QPushButton(self)
        self.b_open.setText("  Open Project")
        self.b_open.setIcon(icon("fa5.folder-open", color=primary_color))
        self.b_open.clicked.connect(self.open_existing_project)


        center_layout.addWidget(title)
        center_layout.addWidget(self.b_new)
        center_layout.addWidget(self.b_open)
        
        center_layout.setAlignment(Qt.AlignCenter)
        central_widget.setLayout(center_layout)
        self.setCentralWidget(central_widget)


    def center(self):
        """
        Centers the main window on the screen.

        This method calculates the center position of the screen based on the screen resolution and window size, 
        and moves the main window to that position. It ensures that the window is always positioned centrally when 
        opened or restored.

        Components Used:
            - Screen resolution: Obtained using `QDesktopWidget().screenGeometry()`
            - Window size: Retrieved using the `geometry()` method of the main window
            - Window move: The `move()` method is used to set the calculated central position
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
    
    def create_new_project(self):
        """
        Opens the ProjectCreator window for creating a new project.

        This method prompts the user to select a directory where the new project will be saved. Once a directory 
        is selected, it initializes the `ProjectCreator` window with the chosen directory and shows it. The main 
        window is then closed.

        Components Involved:
            - `QFileDialog.getSaveFileName()`: Used to prompt the user to select a save location for the new project.
            - `ProjectCreator`: A separate window responsible for the project creation interface.
            - `show()`: Displays the new `ProjectCreator` window.
            - `close()`: Closes the current main window after initiating the new project creation.
        """
        directory, _ = QFileDialog.getSaveFileName(self, 'Select Directory')

        self.window2 = ProjectCreator(directory)
        self.window2.show()
        self.close()

    def open_existing_project(self):
        """
        Opens an existing project by selecting a directory.

        This method allows the user to select an existing project directory using a file dialog. Once a directory 
        is selected, it displays the path in a message box. It then opens the `ProjectWindow` for the selected directory 
        and displays it. The main window is closed to focus on the project editor.

        Components Involved:
            - `QFileDialog.getExistingDirectory()`: Prompts the user to select an existing project directory.
            - `ProjectWindow`: A separate window responsible for managing and editing the selected project.
            - `show()`: Displays the `ProjectWindow` window.
            - `close()`: Closes the current main window after opening the existing project.
        """
        directory = QFileDialog.getExistingDirectory(self, 'Select Directory')

        self.window2 = ProjectWindow(directory)
        self.window2.show()
        self.close()

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