import os
import json
from PyQt5.QtWidgets import (
    QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton,
    QProgressBar, QSlider, QLabel, QSizePolicy
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtMultimedia import QMediaPlayer
import qtawesome as qta

from app.widgets.misc.video_player import VideoPlayer 
from app.widgets.misc.render_worker import Worker  

class VideoAnimation(QWidget):
    def __init__(self, project_folder, scene_data, parent=None):
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
        config_path = os.path.join(self.project_folder, 'config.json')
        if os.path.exists(config_path):
            with open(config_path) as f:
                self.config = json.load(f)
        else:
            self.config = {"VideoRender": {"resolution_x": 640, "resolution_y": 480}}

    def _createWidgets(self):
        # Video player
        width = self.config['VideoRender'].get('resolution_x', 640)
        height = self.config['VideoRender'].get('resolution_y', 480)
        self.video_widget = VideoPlayer(width, height)

        # Buttons
        self.playButton = QPushButton('')
        self.playButton.setIcon(qta.icon("mdi.play", color=self.primary_color))

        self.repeatButton = QPushButton('')
        self.repeatButton.setIcon(qta.icon("mdi.repeat", color=self.primary_color))
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
        self.render_button.setIcon(qta.icon("mdi.printer-3d", color=self.primary_color))

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
        # Layouts
        controlLayout = QHBoxLayout()
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.repeatButton)
        controlLayout.addWidget(self.positionSlider)

        renderLayout = QHBoxLayout()
        renderLayout.addWidget(self.render_button)
        renderLayout.addWidget(self.progress_bar)

        groupLayout = QVBoxLayout()
        groupLayout.addWidget(self.video_widget)
        groupLayout.addLayout(controlLayout)
        groupLayout.addLayout(renderLayout)

        self.groupBox = QGroupBox("Animation Window")
        self.groupBox.setFont(QFont('Times', 9))
        self.groupBox.setLayout(groupLayout)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.groupBox)
        self.setLayout(mainLayout)

    def _connectSignals(self):
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
            self._showError("No render found at: " + self.project_folder)

    def _showError(self, message):
        # You can hook this to a QMessageBox or propagate the error
        print(f"[Error] {message}")

    # ---------- Logic Handlers ----------
    def playVideo(self):
        if self.video_playing:
            self.video_widget.media_player.pause()
            self.playButton.setIcon(qta.icon("mdi.play", color=self.primary_color))
            self.video_playing = False
        else:
            self.video_widget.media_player.play()
            self.playButton.setIcon(qta.icon("mdi.pause", color=self.primary_color))
            self.video_playing = True

    def repeatVideo(self):
        if self.repeatButton.isChecked():
            self.repeatButton.setIcon(qta.icon("mdi.repeat-off", color=self.primary_color))
            self.video_widget.media_player.setPosition(0)
            self.video_widget.media_player.play()
            self.playButton.setIcon(qta.icon("mdi.pause", color=self.primary_color))
        else:
            self.repeatButton.setIcon(qta.icon("mdi.repeat", color=self.primary_color))

    def updateDuration(self, duration):
        self.positionSlider.setRange(0, duration)

    def updatePosition(self, position):
        self.positionSlider.setValue(position)

    def setPosition(self, position):
        self.video_widget.media_player.setPosition(position)

    def updateState(self, state):
        if state == QMediaPlayer.StoppedState and self.repeatButton.isChecked():
            self.video_widget.media_player.setPosition(0)
            self.video_widget.media_player.play()
    
    def update_progress(self, value):
        self.progress_bar.setValue(int(value))

    def genframes(self):

        self.render_button.setEnabled(False)

        self.worker = Worker(self.project_folder, self.angles, self.scene_data, self.reflect)

        self.worker.progress_signal.connect(self.update_progress)

        self.worker.start()

        self.worker.finished.connect(self.complete_render)

    def complete_render(self):
        self.render_button.setEnabled(True)
        project_name = os.path.basename(self.project_folder)
        video_path = os.path.join(self.project_folder, f'data/videos/{project_name}.mp4')
        self.showAlertDialog('Alert', f"Video rendered successfully at: {video_path}")
        self.video_widget.setMedia(video_path)

