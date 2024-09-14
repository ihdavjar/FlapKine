import os
import sys
import pickle
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from src.core.core import Scene
from app.project_window.create_project.create_sprite import CreateSprite

class CreateScene(QMainWindow):

    sceneCreated = pyqtSignal(Scene)

    def __init__(self):
        super(CreateScene, self).__init__()

        self.center()
        
        self.setWindowTitle("Create Scene")

        # Set the icon
        self.setWindowIcon(QIcon(os.path.join('app', 'assets', 'flap_kine_icon.png')))

        # Add the menu bar
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu('File')
        self.new_action = self.file_menu.addAction('New')
        self.new_action.setEnabled(False)
        self.open_action = self.file_menu.addAction('Open')
        self.open_action.setEnabled(False)
        self.exit_action = self.file_menu.addAction('Exit')
        self.exit_action.triggered.connect(self.close)

        self.edit_menu = self.menu.addMenu('Edit')
        self.undo_action = self.edit_menu.addAction('Undo')
        self.redo_action = self.edit_menu.addAction('Redo')

        self.window_menu = self.menu.addMenu('Window')
        self.minimize_action = self.window_menu.addAction('Minimize')
        self.minimize_action.triggered.connect(self.showMinimized)
        self.maximize_action = self.window_menu.addAction('Maximize')
        self.maximize_action.triggered.connect(self.showMaximized)
        self.restore_action = self.window_menu.addAction('Restore')
        self.restore_action.triggered.connect(self.showNormal)

        self.render_menu = self.menu.addMenu('Render')
        self.render_option = self.render_menu.addAction('Configure Render')
        self.render_option.setEnabled(False)

        self.help_menu = self.menu.addMenu('Help')
        self.about_action = self.help_menu.addAction('About') 
        self.about_action.triggered.connect(self.about_button_fun)

        self.sprite_list = []

        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)

        
        # Main widget and layout
        self.add_drop_widget = QWidget()
        self.add_drop_layout = QVBoxLayout(self.add_drop_widget)
        
        # Add and Drop buttons
        self.button_layout = QHBoxLayout()
        self.add_button = QPushButton("ADD")
        self.add_button.clicked.connect(self.add_sprite)
        
        self.drop_button = QPushButton("DROP")
        self.drop_button.clicked.connect(self.drop_sprite)

        self.button_layout.addWidget(QLabel("ADD/DROP Sprite"))
        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.drop_button)
        
        self.add_drop_layout.addLayout(self.button_layout)
        
        # Layout for dropdowns
        self.sprites_layout = QVBoxLayout()
        self.add_drop_layout.addLayout(self.sprites_layout)

        # Okay button
        self.okay_button = QPushButton("import")
        self.okay_button.clicked.connect(self.import_button)

        self.main_layout.addWidget(self.add_drop_widget)
        self.main_layout.addWidget(self.okay_button)
        self.setCentralWidget(self.main_widget)
        
        
    def add_sprite(self):

        # Create a groupd
        sprite_group = QGroupBox()
        sprite_group.setTitle(f"Sprite {self.sprites_layout.count() + 1}")

        # Create a layout for the group
        sprite_import = QHBoxLayout()
    
        self.text_editor_scene = QLineEdit()
        self.text_editor_scene.setText('Enter Scene Name')
        self.open_button = QPushButton('Open', self)
        self.open_button.clicked.connect(lambda: self.import_sprite(sprite_group))

        self.create_button = QPushButton('Create', self)
        self.create_button.clicked.connect(lambda: self.create_sprite(sprite_group))

        sprite_import.addWidget(self.text_editor_scene)
        sprite_import.addWidget(self.open_button)
        sprite_import.addWidget(self.create_button)
        sprite_group.setLayout(sprite_import)

        self.sprites_layout.addWidget(sprite_group) 
    
    def import_sprite(self, sprite_group):
        
        directory, _ = QFileDialog.getOpenFileName(filter='Scene File (*.pkl)')

        if directory:
            sprite_group.findChild(QLineEdit).setText(directory)
            sprite_group.findChild(QPushButton).setStyleSheet('background-color: green')
    
    def create_sprite(self, sprite_group):
        self.window = CreateSprite()
        self.window.show()
        self.window.SpriteCreated.connect(lambda : self.save_sprite(sprite_group))

    def save_sprite(self, sprite_group):
        sprite_group.findChildren(QPushButton)[1].setStyleSheet('background-color: green')
        self.sprite_list.append(self.window.sprite_data)
        
    def drop_sprite(self):
        # Remove the last dropdown menu if exists
        if self.sprites_layout.count() > 0:
            widget_to_remove = self.sprites_layout.itemAt(self.sprites_layout.count() - 1).widget()
            self.sprites_layout.removeWidget(widget_to_remove)
            widget_to_remove.deleteLater()

    def import_button(self):
        if self.sprite_list == []:
            for i in range(self.sprites_layout.count()):
                sprite_group = self.sprites_layout.itemAt(i).widget()
                sprite_name = sprite_group.findChild(QLineEdit).text()
                sprite_data = pickle.load(open(sprite_name, 'rb'))
                self.sprite_list.append(sprite_data)
        
        scene_data = Scene(self.sprite_list)
        self.sceneCreated.emit(scene_data)
        self.close()

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
    
    ######################################## MENU BAR ########################################
    def about_button_fun(self):
        QMessageBox.about(self, "About FlapKine", '''
        <h1>FlapKine</h1>
        <p>Developed by: Kalbhavi Vadhiraj</p>                  
        <p>Version 0.0.1</p>
        <p>FlapKine provides a visual representation and simulation of the kinematics and aerodynamics of flapping wing micro-aerial vehicles (MAVs). It allows users to analyze and optimize MAV designs with precision and clarity, revealing the intricate mechanics of flapping flight. Whether for research, development, or educational purposes, this tool offers valuable insights into the performance and behavior of MAVs, facilitating advanced design and innovation.</p> 
''')