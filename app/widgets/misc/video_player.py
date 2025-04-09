from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QWidget, QVBoxLayout

class VideoPlayer(QWidget):
    """
    VideoPlayer Class
    =================

    A lightweight QWidget-based video player for embedding video playback within PyQt5 GUIs.

    This player uses `QMediaPlayer` and `QVideoWidget` to load and display local video files 
    with support for resizing and basic control operations like pause/play.

    Attributes
    ----------
    video_widget : QVideoWidget
        Widget used to render video content within the layout.

    media_player : QMediaPlayer
        Media player responsible for managing video playback and rendering to `video_widget`.

    Methods
    -------
    __init__(width=640, height=480):
        Initializes the video player layout, media pipeline, and default video dimensions.

    setMedia(video_path):
        Loads a local video file from the specified path and prepares it for playback.

    resizeEvent(event):
        Handles resizing of the widget to ensure the video maintains full screen coverage.
    """

    def __init__(self, width=640, height=480):
        """
        Initializes the video player UI and media components.

        Parameters
        ----------
        width : int, optional
            The minimum width of the video player window (default is 640).
        height : int, optional
            The minimum height of the video player window (default is 480).
        """
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create video widget
        self.video_widget = QVideoWidget(self)
        self.video_widget.setSizePolicy(QWidget.sizePolicy(self).Expanding, QWidget.sizePolicy(self).Expanding)
        self.video_widget.setMinimumSize(400, 225)

        layout.addWidget(self.video_widget)

        # Setup media player
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)

        # Set initial size
        self.setMinimumSize(width, height)

    def setMedia(self, video_path):
        """
        Loads and prepares a video file for playback.

        Parameters
        ----------
        video_path : str
            Absolute or relative path to the local video file to be loaded.
        
        Notes
        -----
        - Video is automatically paused after loading. Use `media_player.play()` to begin playback.
        """
        media = QMediaContent(QUrl.fromLocalFile(video_path))
        self.media_player.setMedia(media)
        self.media_player.pause()

    def resizeEvent(self, event):
        """
        Resizes the video widget to fit the available window space.

        Ensures that the embedded video stretches appropriately while maintaining layout behavior.

        Parameters
        ----------
        event : QResizeEvent
            Resize event triggered when the widget is resized by the user or layout system.
        """
        self.video_widget.setGeometry(self.rect())
        super().resizeEvent(event)
