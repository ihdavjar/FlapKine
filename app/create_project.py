import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


from app.project_window import ProjectWindow

class CreateProjectWin(QMainWindow):
    def __init__(self, project_folder):
        super(CreateProjectWin, self).__init__()
        # Place the window in the center of the screen
        self.setWindowTitle("Import Scene")

        self.project_folder = project_folder
        
        # Add the menu bar
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu('File')
        self.open_action = self.file_menu.addAction('Open')
        self.save_action = self.file_menu.addAction('Save')
        self.exit_action = self.file_menu.addAction('Exit')

        self.edit_menu = self.menu.addMenu('Edit')
        self.undo_action = self.edit_menu.addAction('Undo')
        self.redo_action = self.edit_menu.addAction('Redo')

        self.window_menu = self.menu.addMenu('Window')
        self.minimize_action = self.window_menu.addAction('Minimize')
        self.maximize_action = self.window_menu.addAction('Maximize')
        self.restore_action = self.window_menu.addAction('Restore')

        self.render_menu = self.menu.addMenu('Render')
        self.render_option = self.render_menu.addAction('Configure Render')

        self.help_menu = self.menu.addMenu('Help')
        self.about_action = self.help_menu.addAction('About')  
        self.initUI()

    def initUI(self):
        
            
            self.resize(150, 150)
            self.center()

            # Central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            # Create the main layout
            main_layout = QHBoxLayout(central_widget)

            # Add the two buttons side by side
            self.open_button = QPushButton('Open', self)
            self.open_button.clicked.connect(self.import_scene)
            
            self.create_button = QPushButton('Create', self)
            
            main_layout.addWidget(self.open_button)
            main_layout.addWidget(self.create_button)

    def import_scene(self):
        directory, _ = QFileDialog.getOpenFileName(filter='Scene File (*.pkl)')
        
        if directory:
            # Copy to the project directory
            os.system(f'cp {directory} {self.project_folder}')

    def create_scene(self):
        pass
            
    def center(self):
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


