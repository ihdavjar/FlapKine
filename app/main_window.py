import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from app.project_window import ProjectWindow
from app.create_project import CreateProjectWin


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # Place the window in the center of the screen
        self.setWindowTitle("FlapKine")
        
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
            
            self.resize(300, 150)
            self.center()
    
            # Adding Buttons
            self.b_new = QPushButton(self)
            self.b_new.setText("New")
            self.b_new.setFont(QFont('Times', 9))
            self.b_new.clicked.connect(self.create_new_project)
            self.b_new.move(100, 50)
    
            self.b_open = QPushButton(self)
            self.b_open.setText("Open")
            self.b_open.setFont(QFont('Times', 9))
            self.b_open.clicked.connect(self.open_existing_project)
            self.b_open.move(100, 100)
       

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
    
    def create_new_project(self):
        directory, _ = QFileDialog.getSaveFileName(self, 'Select Directory')

        self.window2 = CreateProjectWin(directory)
        self.window2.show()
        self.close()

    def open_existing_project(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Directory')
        
        if directory:
            QMessageBox.information(self, 'Directory Selected', f'Selected Directory: {directory}')

        self.window2 = ProjectWindow(directory)
        self.window2.show()
        self.close()

