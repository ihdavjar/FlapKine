import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QSlider
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl

class VideoPlayer(QWidget):
    
    def __init__(self, width=640, height=480):  # Default size
        
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create video widget
        self.video_widget = QVideoWidget(self)
        self.video_widget.setSizePolicy(QWidget.sizePolicy(self).Expanding, QWidget.sizePolicy(self).Expanding)
        self.video_widget.setMinimumSize(400, 225)  # Ensuring a minimum size

        layout.addWidget(self.video_widget)

        # Setup media player
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)

        # Set initial size
        self.setMinimumSize(width, height)

    def setMedia(self, video_path):
        media = QMediaContent(QUrl.fromLocalFile(video_path))
        self.media_player.setMedia(media)
        self.media_player.pause()

    def resizeEvent(self, event):
        """Ensure the video widget resizes properly and maintains aspect ratio."""
        self.video_widget.setGeometry(self.rect())  # Stretch to fit full screen
        super().resizeEvent(event)