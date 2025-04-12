import os
import json

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QProgressBar, QSlider, QSizePolicy, QMessageBox
)

from qtawesome import icon

from app.widgets.misc.render_worker import Worker
from app.widgets.misc.video_player import VideoPlayer

class VideoAnimation(QWidget):
    """
    VideoAnimation Class
    ====================

    A PyQt5-based widget for interactive video playback and 3D frame rendering using precomputed 
    animation data. This class serves as a control center for reviewing and exporting animations 
    produced from dynamic scene transformations within the FlapKine environment.

    The widget includes:
    - A video player for previewing rendered videos.
    - Playback controls (play, pause, repeat).
    - A slider for timeline navigation.
    - A render button to generate video frames using transformation data.
    - A progress bar to monitor rendering status.

    Attributes
    ----------
    project_folder : str
        Path to the project directory containing configuration and output files.

    scene_data : SceneData
        The scene object containing transformation functions (angles, rotation, translation) used 
        to generate frame-wise data.

    angles : List[float]
        List of rotation angles associated with the current scene, used during frame rendering.

    reflect : List[bool]
        Boolean flags indicating which axes (XY, YZ, XZ) are to be reflected during rendering, 
        derived from config settings.

    video_playing : bool
        Internal flag tracking the current playback state.

    primary_color : str
        Primary color extracted from the application palette, used to style UI icons.

    video_widget : VideoPlayer
        Custom widget responsible for loading and displaying the rendered video.

    playButton : QPushButton
        Toggle button to control video playback (play/pause).

    repeatButton : QPushButton
        Toggle button to enable or disable repeat mode after video ends.

    positionSlider : QSlider
        Slider for seeking through video frames.

    render_button : QPushButton
        Button to initiate frame rendering based on scene transformations.

    progress_bar : QProgressBar
        Visual indicator of the frame rendering progress.

    config : dict
        Dictionary holding video configuration (e.g., resolution), loaded from config.json.

    worker : Worker
        Background thread responsible for generating frames during rendering.

    Methods
    -------
    __init__(project_folder, scene_data, parent=None)
        Initializes the video animation widget and sets up the UI, configuration, and media loading.

    _loadConfig()
        Loads video rendering configuration from the project’s config.json file.

    _createWidgets()
        Creates and configures all internal widgets, including video player, buttons, and sliders.

    _createLayout()
        Arranges the UI components using QVBoxLayout and QHBoxLayouts for control and render sections.

    _connectSignals()
        Connects UI signals to their corresponding slot functions for interactive behavior.

    _loadMedia()
        Loads the rendered video from the project directory, if it exists.

    _showError(message)
        Displays or logs an error when video loading or configuration fails.

    playVideo()
        Toggles between play and pause states for the video.

    repeatVideo()
        Enables or disables repeat mode and restarts playback if enabled.

    updateDuration(duration)
        Updates the slider’s maximum range based on the video’s total duration.

    updatePosition(position)
        Updates the slider position based on current playback frame.

    setPosition(position)
        Sets the video’s current position based on slider interaction.

    updateState(state)
        Reacts to the media player’s state change and auto-repeats video if required.

    update_progress(value)
        Updates the progress bar’s value during frame rendering.

    genframes()
        Starts the rendering worker thread to compute and export video frames.

    complete_render()
        Handles cleanup and UI updates after rendering is complete and reloads the new video.
    """

    def __init__(self, project_folder, scene_data, parent=None):
        """
        Initializes the VideoAnimation widget.

        Sets up the video animation interface for playback and rendering of 3D scene transformations 
        within the FlapKine environment. Loads configuration, initializes internal state, and prepares 
        UI components for interaction.

        Initialization Tasks:
            - Stores references to the project folder and scene data.
            - Extracts angle data from the scene's primary object.
            - Loads reflection settings from the `config.json` file.
            - Determines the primary UI color from the active palette.
            - Initializes video playback state as inactive.
            - Calls internal setup methods to build widgets, layouts, signal connections, and media loader.

        Parameters
        ----------
        project_folder : str
            Path to the project directory containing configuration and animation output files.

        scene_data : SceneData
            Object holding transformation parameters (angles, rotation, translation) required for frame rendering.

        parent : QWidget, optional
            Optional parent widget for integration within larger PyQt5 interfaces. Defaults to None.
        """

        super().__init__(parent)
        self.project_folder = project_folder
        self.scene_data = scene_data
        self.angles = self.scene_data.objects[0].angles

        with open(os.path.join(self.project_folder, 'config.json')) as f:
                config = json.load(f)

        reflect = [config['Reflect'] == "XY", config['Reflect'] == "YZ", config['Reflect'] == "XZ"]
        self.reflect = reflect

        self.video_playing = False

        self.primary_color = self.palette().color(self.foregroundRole()).name()
        self._loadConfig()

        self._createWidgets()
        self._createLayout()
        self._connectSignals()
        self._loadMedia()

    def _loadConfig(self):
        """
        Loads video rendering configuration from config.json.

        Attempts to read video rendering parameters from the project's `config.json` file and stores 
        the parsed dictionary in the `self.config` attribute. If the file is not found, a default 
        configuration with 640x480 resolution is used instead.

        File Parsed:
            - config.json located in the project directory

        Attributes Set:
            - self.config : dict containing video resolution and rendering parameters
        """

        config_path = os.path.join(self.project_folder, 'config.json')
        if os.path.exists(config_path):
            with open(config_path) as f:
                self.config = json.load(f)
        else:
            self.config = {"VideoRender": {"resolution_x": 640, "resolution_y": 480}}

    def _createWidgets(self):
        """
        Creates and initializes all internal UI widgets.

        Assembles the core visual components of the video animation interface including the video display, 
        playback controls, timeline slider, rendering button, and progress bar. Styles and sizes are set 
        dynamically based on the rendering configuration.

        Components Initialized:
            - `VideoPlayer`: Displays the rendered animation at configured resolution.
            - `playButton`: Icon-based button to toggle play/pause.
            - `repeatButton`: Checkable button to enable/disable looping.
            - `positionSlider`: Horizontal slider styled with custom CSS for frame navigation.
            - `render_button`: Triggers frame rendering using transformation data.
            - `progress_bar`: Indicates real-time rendering progress.

        Notes
        -----
        - Video widget size is locked based on resolution from `self.config['VideoRender']`.
        - All widgets are styled using QtAwesome icons and custom QSS.
        """

        # Video player
        width = self.config['VideoRender'].get('resolution_x', 640)
        height = self.config['VideoRender'].get('resolution_y', 480)
        self.video_widget = VideoPlayer(width, height)
        self.video_widget.setMinimumSize(width, height)
        self.video_widget.setMaximumSize(width, height)
        self.video_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Buttons
        self.playButton = QPushButton('')
        self.playButton.setIcon(icon("mdi.play", color=self.primary_color))

        self.repeatButton = QPushButton('')
        self.repeatButton.setIcon(icon("mdi.repeat", color=self.primary_color))
        self.repeatButton.setCheckable(True)

        # Slider
        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: none;
                background: #ddd;
                height: 8px;
                border-radius: 4px;
            }

            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00aaff, stop:1 #005a9e);
                border: 2px solid #005a9e;
                width: 18px;
                height: 18px;
                margin: -7px 0;
                border-radius: 9px;
            }

            QSlider::handle:horizontal:hover {
                background: #005a9e;
            }

            QSlider::sub-page:horizontal {
                background: #00aaff;
                border-radius: 4px;
            }

            QSlider::add-page:horizontal {
                background: #ccc;
                border-radius: 4px;
            }
        """)  # Add style here or inject dynamically

        # Render Button + Progress Bar
        self.render_button = QPushButton("Render")
        self.render_button.setFont(QFont('Times', 8))
        self.render_button.setIcon(icon("mdi.printer-3d", color=self.primary_color))

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
    QProgressBar {
        border: 2px solid #005a9e;
        border-radius: 5px;
        text-align: center;
        font-size: 10pt;
        background-color: #ddd;
        padding: 2px;
    }

    QProgressBar::chunk {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00aaff, stop:1 #005a9e);
        border-radius: 5px;
    }
""")  # Add style here

    def _createLayout(self):
        """
        Constructs and applies the layout for the video animation interface.

        Organizes the widget components into a clean vertical layout structure with logical 
        grouping for playback controls and rendering tools. Ensures adaptive spacing and 
        alignment for a responsive UI.

        Layout Structure:
            - `controlLayout` (QHBoxLayout): Holds play, repeat, and slider widgets.
            - `renderLayout` (QHBoxLayout): Holds render button and progress bar.
            - `layout` (QVBoxLayout): Main vertical layout stacking video widget, control layout, 
            and render layout with spacing and stretch for balance.

        Final Layout Assignment:
            - Calls `self.setLayout(layout)` to apply the assembled layout to the widget.
        """
        # Layouts
        controlLayout = QHBoxLayout()
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.repeatButton)
        controlLayout.addWidget(self.positionSlider)

        renderLayout = QHBoxLayout()
        renderLayout.addWidget(self.render_button)
        renderLayout.addWidget(self.progress_bar)

        layout = QVBoxLayout()
        layout.addWidget(self.video_widget)

        layout.addSpacing(10)  # Optional visual buffer
        layout.addLayout(controlLayout)
        layout.addLayout(renderLayout)
        layout.addStretch()  # Push everything above if extra space

        self.setLayout(layout)

    def _connectSignals(self):
        """
        Connects UI signals to their corresponding slot functions.

        Establishes all internal signal-slot connections required for interactive behavior, 
        including video playback, repeat toggling, slider movement, rendering initiation, 
        and real-time media updates.

        Signal Connections:
            - `playButton.clicked` → `playVideo()`
            - `repeatButton.clicked` → `repeatVideo()`
            - `positionSlider.sliderMoved` → `setPosition()`
            - `render_button.clicked` → `genframes()`
            - `media_player.durationChanged` → `updateDuration()`
            - `media_player.positionChanged` → `updatePosition()`
            - `media_player.stateChanged` → `updateState()`

        Purpose:
            Ensures responsive video control and rendering feedback through Qt's event-driven architecture.
        """
        self.playButton.clicked.connect(self.playVideo)
        self.repeatButton.clicked.connect(self.repeatVideo)
        self.positionSlider.sliderMoved.connect(self.setPosition)
        self.render_button.clicked.connect(self.genframes)

        self.video_widget.media_player.durationChanged.connect(self.updateDuration)
        self.video_widget.media_player.positionChanged.connect(self.updatePosition)
        self.video_widget.media_player.stateChanged.connect(self.updateState)

    def _loadMedia(self):
        project_name = os.path.basename(self.project_folder)
        video_path = os.path.join(self.project_folder, f'data/videos/{project_name}.mp4')

        if os.path.exists(video_path):
            self.video_widget.setMedia(video_path)
        else:
            self.showAlertDialog('Error', f"Render files not found at: {video_path}")

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

    def playVideo(self):
        """
        Toggles video playback state between play and pause.

        Handles the core play/pause logic based on the internal `video_playing` flag. Updates both the 
        media player's state and the icon displayed on the play button to reflect the current action.

        Behavior:
            - If video is playing: pauses playback and updates button to 'play' icon.
            - If video is paused: starts playback and updates button to 'pause' icon.

        Updates:
            - `video_playing` flag
            - `playButton` icon using QtAwesome with primary UI color
        """
        if self.video_playing:
            self.video_widget.media_player.pause()
            self.playButton.setIcon(icon("mdi.play", color=self.primary_color))
            self.video_playing = False
        else:
            self.video_widget.media_player.play()
            self.playButton.setIcon(icon("mdi.pause", color=self.primary_color))
            self.video_playing = True

    def repeatVideo(self):
        """
        Toggles repeat mode for the video playback.

        Checks the state of the `repeatButton` and updates the repeat icon accordingly. If repeat mode 
        is enabled, the video restarts from the beginning and begins playback immediately. If disabled, 
        it simply reverts the icon to the repeat state.

        Behavior:
            - If checked: sets icon to `repeat-off`, resets position to start, and plays the video.
            - If unchecked: sets icon back to `repeat`.

        UI Updates:
            - `repeatButton` icon
            - `playButton` icon (set to 'pause' if playback is restarted)
        """
        if self.repeatButton.isChecked():
            self.repeatButton.setIcon(icon("mdi.repeat-off", color=self.primary_color))
            self.video_widget.media_player.setPosition(0)
            self.video_widget.media_player.play()
            self.playButton.setIcon(icon("mdi.pause", color=self.primary_color))
        else:
            self.repeatButton.setIcon(icon("mdi.repeat", color=self.primary_color))

    def updateDuration(self, duration):
        """
        Updates the slider range based on video duration.

        Parameters
        ----------
        duration : int
            Total duration of the video in milliseconds.
        """
        self.positionSlider.setRange(0, duration)

    def updatePosition(self, position):
        """
        Updates the slider's value to match the current playback position.

        Parameters
        ----------
        position : int
            Current position of the video in milliseconds.
        """
        self.positionSlider.setValue(position)

    def setPosition(self, position):
        """
        Sets the media player to the given position.

        Parameters
        ----------
        position : int
            New playback position in milliseconds.
        """
        self.video_widget.media_player.setPosition(position)

    def updateState(self, state):
        """
        Handles media state changes and auto-repeats video if in repeat mode.

        Parameters
        ----------
        state : QMediaPlayer.State
            Current state of the media player.
        """
        if state == QMediaPlayer.StoppedState and self.repeatButton.isChecked():
            self.video_widget.media_player.setPosition(0)
            self.video_widget.media_player.play()
    
    def update_progress(self, value):
        """
        Updates the progress bar with the given value.

        Parameters
        ----------
        value : int or float
            Current progress percentage (0–100).
        """
        self.progress_bar.setValue(int(value))

    def genframes(self):
        """
        Starts the frame rendering process using a background worker thread.

        Initializes a `Worker` instance with the current scene parameters and begins the rendering task 
        asynchronously. Disables the render button during processing and connects progress and completion 
        signals for real-time UI feedback.

        Workflow:
            - Disables `render_button` to prevent multiple triggers.
            - Instantiates `Worker` with `project_folder`, `angles`, `scene_data`, and `reflect`.
            - Connects `progress_signal` to `update_progress()` for live updates.
            - Starts the worker thread to render frames.
            - Connects `finished` signal to `complete_render()` for post-processing and cleanup.
        """
        self.render_button.setEnabled(False)
        self.worker = Worker(self.project_folder, self.angles, self.scene_data, self.reflect)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.start()
        self.worker.finished.connect(self.complete_render)

    def complete_render(self):
        """
        Finalizes the rendering process and updates the UI.

        Re-enables the render button, displays a confirmation dialog with the output video path, 
        and reloads the rendered video into the video player for immediate preview.

        Post-Render Actions:
            - Enables `render_button` for future rendering.
            - Displays alert with the final video path.
            - Loads the new video into `video_widget` using `setMedia()`.
        """
        self.render_button.setEnabled(True)
        project_name = os.path.basename(self.project_folder)
        video_path = os.path.join(self.project_folder, f'data/videos/{project_name}.mp4')
        self.showAlertDialog('Alert', f"Video rendered successfully at: {video_path}")
        self.video_widget.setMedia(video_path)

