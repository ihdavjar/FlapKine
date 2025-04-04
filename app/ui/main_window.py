import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import qtawesome as qta

from app.widgets.menu_bar import MenuBar
from app.ui.editor.project_editor import ProjectWindow
from app.ui.creators.project_creator import ProjectCreator


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # Place the window in the center of the screen
        self.setWindowTitle("FlapKine")

        # Set the icon
        self.setWindowIcon(QIcon(os.path.join('app', 'assets', 'flapkine_icon.png')))
        
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)
        self.menu_bar.connect_actions({
            'new': self.create_new_project,
            'open': self.open_existing_project,
            'minimize': self.showMinimized,
            'maximize': self.showMaximized,
            'restore': self.showNormal,
            'about': self.show_about
        })

        self.initUI()

    def initUI(self):
        
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
        self.b_new.setIcon(qta.icon("fa5.file", color=primary_color))
        self.b_new.clicked.connect(self.create_new_project)
        

        self.b_open = QPushButton(self)
        self.b_open.setText("  Open Project")
        self.b_open.setIcon(qta.icon("fa5.folder-open", color=primary_color))
        self.b_open.clicked.connect(self.open_existing_project)


        center_layout.addWidget(title)
        center_layout.addWidget(self.b_new)
        center_layout.addWidget(self.b_open)
        
        center_layout.setAlignment(Qt.AlignCenter)
        central_widget.setLayout(center_layout)
        self.setCentralWidget(central_widget)


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

    ######################################## MENU BAR ########################################
    def maximize_button_fun(self):
        self.showMaximized()
        self.center()

    def minimize_button_fun(self):
        self.showMinimized()
    
    def restore_button_fun(self):
        self.showNormal()

    def exit_button_fun(self):
        self.close()

    def show_about(self):
        QMessageBox.about(self, "About FlapKine", '''
        <h1>FlapKine</h1>
        <p>Developed by: Kalbhavi Vadhiraj</p>                  
        <p>Version 0.0.1</p>
        <p>FlapKine provides a visual representation and simulation of the kinematics and aerodynamics of flapping wing micro-aerial vehicles (MAVs). It allows users to analyze and optimize MAV designs with precision and clarity, revealing the intricate mechanics of flapping flight. Whether for research, development, or educational purposes, this tool offers valuable insights into the performance and behavior of MAVs, facilitating advanced design and innovation.</p> 
''')