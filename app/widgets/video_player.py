import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QSlider
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize media player and video widget objects
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoWidget = QVideoWidget()

        # Set video display widget
        self.mediaPlayer.setVideoOutput(self.videoWidget)

        # Create UI elements
        self.initUI()

    def initUI(self):
        # Create play button
        self.playButton = QPushButton('Play')
        self.playButton.clicked.connect(self.playVideo)

        # Create pause button
        self.pauseButton = QPushButton('Pause')
        self.pauseButton.clicked.connect(self.pauseVideo)

        # Create repeat button
        self.repeatButton = QPushButton('Repeat')
        self.repeatButton.setCheckable(True)
        self.repeatButton.clicked.connect(self.repeatVideo)

        # Create slider for video position
        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        # Create label for displaying status
        self.statusLabel = QLabel('')

        # Layout for buttons
        controlLayout = QHBoxLayout()
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.pauseButton)
        controlLayout.addWidget(self.repeatButton)

        # Main layout
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.videoWidget)  # Add video widget to main layout
        mainLayout.addLayout(controlLayout)
        mainLayout.addWidget(self.positionSlider)
        mainLayout.addWidget(self.statusLabel)

        self.setLayout(mainLayout)

        # Connect media player signals
        self.mediaPlayer.durationChanged.connect(self.updateDuration)
        self.mediaPlayer.positionChanged.connect(self.updatePosition)
        self.mediaPlayer.stateChanged.connect(self.updateState)

        # Import video file
        video_path = '/mnt1/Research/Kinematics_App/FlapKine/data/videos/stl_animation_temp.mp4'  # Replace with your video file path
        self.setMedia(video_path)

    def playVideo(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            return
        self.mediaPlayer.play()

    def pauseVideo(self):
        if self.mediaPlayer.state() == QMediaPlayer.PausedState:
            return
        self.mediaPlayer.pause()
    
    def repeatVideo(self):
        if self.repeatButton.isChecked():
            self.mediaPlayer.setPosition(0)
            self.mediaPlayer.play()

    def updateDuration(self, duration):
        self.positionSlider.setRange(0, duration)

    def updatePosition(self, position):
        self.positionSlider.setValue(position)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def updateState(self, state):
        if state == QMediaPlayer.PlayingState:
            self.statusLabel.setText('Playing')
        elif state == QMediaPlayer.PausedState:
            self.statusLabel.setText('Paused')
        elif state == QMediaPlayer.StoppedState:
            self.statusLabel.setText('Stopped')
            if self.repeatButton.isChecked():
                self.mediaPlayer.setPosition(0)
                self.mediaPlayer.play()


    def setMedia(self, url):
        media = QMediaContent(QUrl.fromLocalFile(url))
        self.mediaPlayer.setMedia(media)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())