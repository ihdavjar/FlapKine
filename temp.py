import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl, pyqtSignal

class VideoPlayer(QWidget):
    def __init__(self, video_path):
        super().__init__()
        self.setWindowTitle("Video Player")

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.video_widget = QVideoWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.video_widget)
        self.setLayout(layout)

        self.mediaPlayer.setVideoOutput(self.video_widget)
        video_url = QUrl.fromLocalFile(video_path)
        self.mediaPlayer.setMedia(QMediaContent(video_url))

        # Connect media player signals for looping
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)

        self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.StoppedState:
            self.mediaPlayer.play()

    def positionChanged(self, position):
        duration = self.mediaPlayer.duration()
        if position >= duration - 1000:  # within 1 second of end
            self.mediaPlayer.setPosition(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Provide the path to your .mp4 file here
    video_path = "project1/data/videos/stl_animation_temp_compressed.mp4"

    player = VideoPlayer(video_path)
    player.show()

    sys.exit(app.exec_())
