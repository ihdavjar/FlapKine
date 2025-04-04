import os
import sys
import pickle
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from src.core.core import Scene
import qtawesome as qta

from app.ui.creators.sprite_creator import SpriteCreator
from app.widgets.menu_bar import MenuBar

class SceneCreator(QMainWindow):
    """
    SceneCreator Class
    ==================

    This class defines the GUI window for creating and importing a scene in the FlapKine application.

    It allows users to add multiple sprites by either importing pre-saved `.pkl` scene files or creating new ones 
    via a custom sprite builder. The final scene data is constructed from these sprites and emitted as a `Scene` object.

    Attributes
    ----------
    sceneCreated : pyqtSignal
        Custom signal emitted with a `Scene` object after the scene is finalized.

    menu_bar : MenuBar
        Top-level custom menu bar providing actions like minimize, maximize, restore, exit, and about.

    main_widget : QWidget
        Central widget containing the entire GUI layout.

    sprites_list_layout : QVBoxLayout
        Layout to which all sprite group widgets (representing individual sprite entries) are added.

    sprite_list : list
        Holds sprite data objects that are either loaded from file or generated via UI.

    text_editor_scene : QLineEdit
        Input field for specifying or displaying the path of a sprite/scene file to import.

    open_button : QPushButton
        Opens a file dialog to import an existing `.pkl` scene file.

    create_button : QPushButton
        Launches the sprite creation interface to build a new sprite and attach it to the scene.

    window : SpriteCreator
        Instance of the SpriteCreator dialog window for generating new sprite data.

    Methods
    -------
    __init__():
        Initializes the GUI, sets up the menu bar, central layout, and connects signals to handlers.

    initUI() -> QVBoxLayout:
        Builds the core layout including sprite controls and an import button, and returns the root layout.

    add_sprite():
        Dynamically creates a new sprite entry group with input fields and buttons for import or creation.

    import_sprite(sprite_group: QGroupBox):
        Opens a file dialog to import a `.pkl` sprite file and sets the path in the associated input field.

    create_sprite(sprite_group: QGroupBox):
        Opens a sprite creation window and connects its result to the current sprite group.

    save_sprite(sprite_group: QGroupBox):
        Retrieves created sprite data from the sprite creation dialog and stores it for final scene building.

    drop_sprite():
        Removes the last sprite group entry from the list, simulating a stack-based deletion of sprites.

    okay_button_fun():
        Gathers all sprite data (from created or imported sources), builds a `Scene` object, emits it, and closes the window.

    center():
        Centers the main window on the user's screen using screen and window geometry.

    about_button_fun():
        Displays an informational dialog with app version, developer info, and a description of FlapKine's purpose.
    """

    sceneCreated = pyqtSignal(Scene)

    def __init__(self):
        """
        Initializes the SceneCreator class.

        Sets up the main window for the FlapKine scene creation interface. This includes configuring
        core window properties such as the title and icon, initializing the sprite storage list, 
        integrating a custom menu bar, and building the full user interface layout through `initUI()`.

        Components Initialized:
            - Window title: "Create Scene"
            - Window icon: FlapKine logo loaded from assets
            - Sprite list: An empty list used to store imported or created sprite data
            - Menu bar: A custom `MenuBar` instance with the following connected actions:
                - Exit (closes the window)
                - Minimize (minimizes the window)
                - Maximize (maximizes the window)
                - Restore (restores to normal size)
                - About (shows application info dialog)
            - Main layout: Assembled using `initUI()` and set to the central widget
            - Centered window: Positioned to the center of the screen via `center()`
        """
        super(SceneCreator, self).__init__()

        self.center()
        self.setWindowTitle("Create Scene")
        self.setWindowIcon(QIcon(os.path.join('app', 'assets', 'flapkine_icon.png')))

        # Add the menu bar
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)

        self.menu_bar.connect_actions({
            'exit': self.close,
            'minimize': self.showMinimized,
            'maximize': self.showMaximized,
            'restore': self.showNormal,
            'about': self.about_button_fun
        })

        self.sprite_list = []

        self.main_widget = QWidget()
        main_layout = self.initUI()
        
        self.main_widget.setLayout(main_layout)
        self.setCentralWidget(self.main_widget)        
    
    def initUI(self)-> QVBoxLayout:
        """
        Builds the user interface layout for the SceneCreator window.

        Assembles the core layout for sprite management and scene import. This includes interactive
        controls for adding or removing sprite blocks, configuring scene entries, and finalizing 
        the import process. All components are organized using vertical and horizontal layouts
        to ensure a structured and intuitive interface.

        UI Components:
            - Sprite Controls GroupBox:
                - Title: "Sprite Controls"
                - Font: Times, size 9
                - Contains:
                    - Horizontal layout with:
                        - QLabel: "Manage Sprites:"
                        - QPushButton: Add (connected to `add_sprite`)
                        - QPushButton: Drop (connected to `drop_sprite`)
                    - Vertical layout container for dynamically added sprite groups

            - Import Scene Button:
                - Label: "Import Scene"
                - Font: Times, size 9
                - Style: Increased font size and padding
                - Connected to `okay_button_fun` to finalize and emit the scene

        Returns
        -------
        QVBoxLayout
            The main vertical layout containing all scene creation controls.
        """

        main_layout = QVBoxLayout()
        
        # Main widget and layout
        sprite_settings_grp = QGroupBox("Sprite Controls")
        sprite_settings_grp.setFont(QFont('Times', 9))
        sprite_layout = QVBoxLayout()
        
        # Add and Drop buttons
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add")
        add_button.setIcon(qta.icon("mdi.plus-box-multiple-outline"))
        add_button.clicked.connect(self.add_sprite)
        
        drop_button = QPushButton("Drop")
        drop_button.setIcon(qta.icon("mdi.minus-box-multiple-outline"))
        drop_button.clicked.connect(self.drop_sprite)

        button_layout_label = QLabel("Manage Sprites:")
        button_layout_label.setFont(QFont('Times', 8))

        button_layout.addWidget(button_layout_label)
        button_layout.addWidget(add_button)
        button_layout.addWidget(drop_button)
        sprite_layout.addLayout(button_layout)

        # List of Sprites
        self.sprites_list_layout = QVBoxLayout()
        sprite_layout.addLayout(self.sprites_list_layout)

        sprite_settings_grp.setLayout(sprite_layout)
        
        # Okay button
        okay_button = QPushButton("Import Scene")
        okay_button.setFont(QFont('Times', 9))
        okay_button.setStyleSheet("font-size: 14px; padding: 8px;")
        okay_button.clicked.connect(self.okay_button_fun)

        main_layout.addWidget(sprite_settings_grp)
        main_layout.addWidget(okay_button)

        return main_layout

    def add_sprite(self):
        """
        Dynamically adds a new sprite input group to the scene creator layout.

        Creates a labeled group box for each sprite, allowing the user to either import or create 
        a new sprite scene. Each group includes a text field for naming the scene, along with 
        'Open' and 'Create' buttons connected to their respective handler functions.

        Components Added:
            - QGroupBox: Labeled as "Sprite <n>", where n is the current sprite count
                - Font: Times, size 8
                - Layout: QHBoxLayout containing:
                    - QLineEdit: For entering the scene name
                        - Placeholder: "Enter Scene Name"
                        - Font: Times, size 7
                        - Expands horizontally
                    - QPushButton: "Open"
                        - Icon: Folder open icon (color matched to palette foreground)
                        - Connected to `import_sprite` with sprite group context
                    - QPushButton: "Create"
                        - Icon: Folder plus icon (color matched to palette foreground)
                        - Connected to `create_sprite` with sprite group context

        Updates
        -------
        self.sprites_list_layout : QVBoxLayout
            Appends the newly created sprite group to the vertical sprite list layout.
        """

        primary_color = self.palette().color(self.foregroundRole()).name()

        # Create a groupd
        sprite_group = QGroupBox()
        sprite_group.setTitle(f"Sprite {self.sprites_list_layout.count() + 1}")
        sprite_group.setFont(QFont('Times', 8))

        # Create a layout for the group
        sprite_import = QHBoxLayout()
    
        self.text_editor_scene = QLineEdit()
        self.text_editor_scene.setPlaceholderText('Enter Scene Name')
        self.text_editor_scene.setFont(QFont('Times', 7))
        self.text_editor_scene.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.open_button = QPushButton('Open', self)
        self.open_button.setIcon(qta.icon("fa5.folder-open", color=primary_color))
        self.open_button.setFont(QFont('Times', 7))
        self.open_button.clicked.connect(lambda: self.import_sprite(sprite_group))

        self.create_button = QPushButton('Create', self)
        self.create_button.setIcon(qta.icon("mdi.folder-plus-outline", color=primary_color))
        self.create_button.setFont(QFont('Times', 7))
        self.create_button.clicked.connect(lambda: self.create_sprite(sprite_group))

        sprite_import.addWidget(self.text_editor_scene)
        sprite_import.addWidget(self.open_button)
        sprite_import.addWidget(self.create_button)
        sprite_group.setLayout(sprite_import)

        self.sprites_list_layout.addWidget(sprite_group) 
    
    def import_sprite(self, sprite_group):
        """
        Handles the import of a sprite scene from a `.pkl` file into the given sprite group.

        Opens a file dialog for the user to select a pickle file representing a pre-saved sprite 
        scene. Upon selection, the file path is displayed in the group's `QLineEdit`, and the 
        corresponding 'Open' button is visually updated to indicate success.

        Parameters
        ----------
        sprite_group : QGroupBox
            The container widget representing a single sprite input group whose child widgets
            (text field and open button) are updated.

        Behavior
        --------
        - Launches a file dialog restricted to `.pkl` files.
        - If a valid file is selected:
            - Sets the file path in the `QLineEdit` of the group.
            - Changes the background color of the first `QPushButton` (assumed to be 'Open') to green.
        """
        directory, _ = QFileDialog.getOpenFileName(filter='Scene File (*.pkl)')

        if directory:
            sprite_group.findChild(QLineEdit).setText(directory)
            sprite_group.findChild(QPushButton).setStyleSheet('background-color: green')
    
    def create_sprite(self, sprite_group):
        """
        Launches the sprite creation interface and connects the result to the given sprite group.

        Opens a new `SpriteCreator` window that allows the user to build a custom sprite. Upon
        successful sprite creation (signaled via the `SpriteCreated` signal), the sprite data
        is passed to the `save_sprite()` method which updates the associated `sprite_group`.

        Parameters
        ----------
        sprite_group : QGroupBox
            The sprite group container that will be updated with the created sprite information.

        Behavior
        --------
        - Initializes and displays a `SpriteCreator` dialog.
        - Connects the `SpriteCreated` signal to a lambda function that:
            - Triggers `save_sprite(sprite_group)` on sprite creation.
        """

        self.window = SpriteCreator()
        self.window.show()
        self.window.SpriteCreated.connect(lambda : self.save_sprite(sprite_group))

    def save_sprite(self, sprite_group):
        """
        Saves the newly created sprite and updates the corresponding UI group.

        Retrieves the sprite data from the `SpriteCreator` window and appends it to the internal
        sprite list. Additionally, visually confirms sprite creation by updating the style of
        the 'Create' button in the provided `sprite_group`.

        Parameters
        ----------
        sprite_group : QGroupBox
            The UI container representing the sprite entry to be updated with visual feedback.

        Behavior
        --------
        - Changes the second QPushButton's background color to green within `sprite_group`.
        - Appends the newly created sprite data (`self.window.sprite_data`) to `self.sprite_list`.
        """
        sprite_group.findChildren(QPushButton)[1].setStyleSheet('background-color: green')
        self.sprite_list.append(self.window.sprite_data)
        
    def drop_sprite(self):
        """
        Removes the most recently added sprite input group from the UI.

        This method checks if any sprite input groups exist within the `sprites_list_layout`.
        If present, it removes the last added `QGroupBox` widget and schedules it for deletion,
        effectively updating the scene creator interface.

        Behavior
        --------
        - Identifies and removes the last widget in `self.sprites_list_layout`.
        - Ensures proper memory cleanup by calling `deleteLater()` on the removed widget.
        """
        if self.sprites_list_layout.count() > 0:
            widget_to_remove = self.sprites_list_layout.itemAt(self.sprites_list_layout.count() - 1).widget()
            self.sprites_list_layout.removeWidget(widget_to_remove)
            widget_to_remove.deleteLater()

    def okay_button_fun(self):
        """
        Finalizes the scene creation and emits the constructed scene data.

        This method processes all sprite input groups in the UI, loads their corresponding
        `.pkl` files (if not already loaded), and compiles them into a `Scene` object. Once
        constructed, the `sceneCreated` signal is emitted with the new scene, and the window
        is closed.

        Behavior
        --------
        - Checks if `self.sprite_list` is empty:
            - If so, iterates through all sprite input widgets.
            - Extracts file paths from `QLineEdit` entries and loads corresponding `.pkl` data.
            - Appends loaded sprite data to `self.sprite_list`.
        - Instantiates a `Scene` object using the loaded sprite data.
        - Emits `sceneCreated` signal with the new `Scene` instance.
        - Closes the `SceneCreator` window.
        """
        if self.sprite_list == []:
            for i in range(self.sprites_list_layout.count()):
                sprite_group = self.sprites_list_layout.itemAt(i).widget()
                sprite_name = sprite_group.findChild(QLineEdit).text()
                sprite_data = pickle.load(open(sprite_name, 'rb'))
                self.sprite_list.append(sprite_data)
        
        scene_data = Scene(self.sprite_list)
        self.sceneCreated.emit(scene_data)
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