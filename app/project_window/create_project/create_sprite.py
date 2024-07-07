import numpy as np
import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from stl import mesh
from plotly import graph_objects as go
import plotly.io as pio

from src.core.core import Object3D, Sprite
from src.core.transforms.flexibility import ConstantF, Flexibility_type1
from src.core.transforms.rotation import ConstantR, Rotation_EulerAngles

class CreateSprite(QMainWindow):

    SpriteCreated = pyqtSignal(Sprite)

    def __init__(self):
        super(CreateSprite, self).__init__()

        self.center()
        self.setWindowTitle("Create Sprite")

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


        main_layout = QVBoxLayout()
        self.main_widget = QWidget()


        group_1 = QGroupBox("3DObject Properties")
        group_1_layout = QVBoxLayout()

        ########## Sprite Name ##########
        sprite_name_layout = QHBoxLayout()
        self.sprite_name = QLineEdit()
        self.sprite_name.setPlaceholderText("Enter Sprite Name")
        sprite_name_layout.addWidget(QLabel("Sprite Name"))
        sprite_name_layout.addWidget(self.sprite_name)

        ########## STL File Path ##########
        self.sprite_stl_path_layout = QHBoxLayout()
        self.sprite_stl_path = QLineEdit()
        self.sprite_stl_open = QPushButton("Open")
        self.sprite_stl_open.clicked.connect(self.open_file)

        self.sprite_stl_path_layout.addWidget(QLabel("STL File Path"))
        self.sprite_stl_path_layout.addWidget(self.sprite_stl_path)
        self.sprite_stl_path_layout.addWidget(self.sprite_stl_open)


        ########## Flexibility Transform ##########
        self.flexibility_transform_layout = QHBoxLayout()
        self.flexibility_transform = QComboBox()
        self.flexibility_transform.addItem("Constant")
        self.flexibility_transform.addItem("FlexibleType1")
        self.flexibility_transform.addItem("Custom")
        self.flexibility_transform.currentIndexChanged.connect(self.flexibility_transform_fun)

        self.flexibility_transform_layout.addWidget(QLabel("Flexibility Transform"))
        self.flexibility_transform_layout.addWidget(self.flexibility_transform)


        ########## Rotation Transform ##########
        self.rotation_transform_layout = QHBoxLayout()
        self.rotation_transform = QComboBox()
        self.rotation_transform.addItem("Constant")
        self.rotation_transform.addItem("Euler_Angles")
        self.rotation_transform.addItem("Custom")
        self.rotation_transform.currentIndexChanged.connect(self.rotation_transform_fun)

        self.rotation_transform_layout.addWidget(QLabel("Rotation Transform"))
        self.rotation_transform_layout.addWidget(self.rotation_transform)


        group_1_layout.addLayout(sprite_name_layout)
        group_1_layout.addLayout(self.sprite_stl_path_layout)
        group_1_layout.addLayout(self.flexibility_transform_layout)
        group_1_layout.addLayout(self.rotation_transform_layout)

        ########## GROUP 2 ##########
        self.group_2 = QGroupBox("Initial Conditions")
        group_2_layout = QVBoxLayout()

        # Flexibility Transform
        time_layout = QHBoxLayout()
        self.time_input = QSpinBox()
        self.time_input.setRange(0, 10000)

        time_layout.addWidget(QLabel("Time"))
        time_layout.addWidget(self.time_input)

        # Rotation Transform
        angle_layout = QVBoxLayout()   
        angle_label = QLabel("Initial Euler Angles")
        self.angle_input_alpha = QDoubleSpinBox()
        self.angle_input_alpha.setRange(-360, 360)
        self.angle_input_alpha.setSuffix("°")

        self.angle_input_beta = QDoubleSpinBox()
        self.angle_input_beta.setRange(-360, 360)
        self.angle_input_beta.setSuffix("°")

        self.angle_input_gamma = QDoubleSpinBox()
        self.angle_input_gamma.setRange(-360, 360)
        self.angle_input_gamma.setSuffix("°")

        angle_layout.addWidget(angle_label)
        angle_layout.addWidget(QLabel("Alpha"))
        angle_layout.addWidget(self.angle_input_alpha)
        angle_layout.addWidget(QLabel("Beta"))
        angle_layout.addWidget(self.angle_input_beta)
        angle_layout.addWidget(QLabel("Gamma"))
        angle_layout.addWidget(self.angle_input_gamma)

        group_2_layout.addLayout(time_layout)
        group_2_layout.addLayout(angle_layout)
        
        group_1.setLayout(group_1_layout)
        self.group_2.setLayout(group_2_layout)

        self.group_2.setEnabled(False)

        main_layout.addWidget(group_1)
        self.enable_checkbox = QCheckBox("Enable Initial Conditions")
        self.enable_checkbox.stateChanged.connect(self.enable_checkbox_fun)
        main_layout.addWidget(self.enable_checkbox)
        main_layout.addWidget(self.group_2)
        self.finish_button = QPushButton("Finish")
        main_layout.addWidget(self.finish_button)
        self.finish_button.clicked.connect(self.finish_button_fun)

        self.main_widget.setLayout(main_layout)
        self.setCentralWidget(self.main_widget)

    def open_file(self):
        directory, _ = QFileDialog.getOpenFileName(filter='STL File (*.stl)')

        if directory:

            plotly_chart_view = QWebEngineView()

            self.sprite_stl_path.setText(directory)

            # Load the stl mesh 
            your_mesh = mesh.Mesh.from_file(directory)

            # Extract the vertices and faces
            vertices = your_mesh.vectors.reshape(-1, 3)
            x, y, z = vertices[:, 0], vertices[:, 1], vertices[:, 2]

            # Create a unique set of vertices and a list of faces
            unique_vertices, unique_indices = np.unique(vertices, axis=0, return_inverse=True)
            i, j, k = unique_indices.reshape(-1, 3).T

            # Create a 3D mesh plot
            fig = go.Figure(data=[go.Mesh3d(
                x=unique_vertices[:, 0],
                y=unique_vertices[:, 1],
                z=unique_vertices[:, 2],
                i=i,
                j=j,
                k=k,
                opacity=1,
                color='lightblue'
            )])

            # Set plot layout
            fig.update_layout(
                title='STL Mesh Plot',
                scene=dict(
                    xaxis=dict(title='X'),
                    yaxis=dict(title='Y'),
                    zaxis=dict(title='Z')
                )
            )
            # Freeze the axis so that they don't auto-scale
            fig.update_scenes(aspectmode='cube')

            # Set x, y, z axis limits
            fig.update_layout(scene=dict(xaxis=dict(range=[-10, 10]), yaxis=dict(range=[-10, 10]), zaxis=dict(range=[-10, 10])))

            # Set the camera on the x axis at 1,0,0
            fig.update_layout(scene_camera=dict(eye=dict(x=1, y=0, z=0)))

            # Switch of the grid
            fig.update_layout(
            scene=dict(
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False),
            zaxis=dict(showgrid=False, zeroline=False),
        )
    )   # Customize layout for dark theme
            fig.update_layout(
                scene=dict(
                    xaxis=dict(
                        backgroundcolor='rgba(0,0,0,0)',  # Background color of the scene
                        gridcolor='white',  # Color of gridlines
                        showbackground=False,  # Hide the background
                        showgrid=False,  # Hide gridlines
                        zeroline=False,  # Hide the zero line
                        linecolor='white',  # Color of axis lines
                        tickfont=dict(color='white'),  # Color of tick labels
                    ),
                    yaxis=dict(
                        backgroundcolor='rgba(0,0,0,0)',  # Background color of the scene
                        gridcolor='white',  # Color of gridlines
                        showbackground=False,  # Hide the background
                        showgrid=False,  # Hide gridlines
                        zeroline=False,  # Hide the zero line
                        linecolor='white',  # Color of axis lines
                        tickfont=dict(color='white'),  # Color of tick labels
                    ),
                    zaxis=dict(
                        backgroundcolor='rgba(0,0,0,0)',  # Background color of the scene
                        gridcolor='white',  # Color of gridlines
                        showbackground=False,  # Hide the background
                        showgrid=False,  # Hide gridlines
                        zeroline=False,  # Hide the zero line
                        linecolor='white',  # Color of axis lines
                        tickfont=dict(color='white'),  # Color of tick labels
                    ),
                ),
                plot_bgcolor='rgba(0,0,0,0)',  # Background color of the plot
            )
    
            html = pio.to_html(fig, full_html=False, include_plotlyjs='cdn')

            plotly_chart_view.setHtml(html)

            self.sprite_stl_path_layout.addWidget(plotly_chart_view, 2)




    def flexibility_transform_fun(self):
        if self.flexibility_transform.currentIndex() == 1:

            flexibility_transform_group = QGroupBox("Flexibility Transform")
            flexibitity_transform_layout = QVBoxLayout()

            temp_QHBoxLayout_1 = QHBoxLayout()
            temp_QHBoxLayout_1.addWidget(QLabel("x"))
            temp_combobox_x = QComboBox()
            temp_combobox_x.addItems(["True", "False"])
            temp_QHBoxLayout_1.addWidget(temp_combobox_x)
            
            temp_QHBoxLayout_1.addWidget(QLabel("y"))
            temp_combobox_y = QComboBox()
            temp_combobox_y.addItems(["True", "False"])
            temp_QHBoxLayout_1.addWidget(temp_combobox_y)

            temp_QHBoxLayout_1.addWidget(QLabel("z"))
            temp_combobox_z = QComboBox()
            temp_combobox_z.addItems(["True", "False"])
            temp_QHBoxLayout_1.addWidget(temp_combobox_z)

            flexibitity_transform_layout.addLayout(temp_QHBoxLayout_1)
            

            temp_QHBoxLayout_2 = QHBoxLayout()
            temp_QHBoxLayout_2.addWidget(QLabel("Major Axis"))
            temp_combobox_major = QDoubleSpinBox()
            temp_combobox_major.setRange(0, 100)
            temp_QHBoxLayout_2.addWidget(temp_combobox_major)

            temp_QHBoxLayout_2.addWidget(QLabel("Minor Axis"))
            temp_combobox_minor = QDoubleSpinBox()
            temp_combobox_minor.setRange(0, 100)
            temp_QHBoxLayout_2.addWidget(temp_combobox_minor)

            flexibitity_transform_layout.addLayout(temp_QHBoxLayout_2)

            flexibility_transform_group.setLayout(flexibitity_transform_layout)

            self.flexibility_transform_layout.addWidget(flexibility_transform_group)

        else:
            # Remove the widget
            if (self.flexibility_transform_layout.itemAt(2) != None):
                self.flexibility_transform_layout.itemAt(2).widget().deleteLater()

    def rotation_transform_fun(self):
        if self.rotation_transform.currentIndex() == 1:

            rotation_transform_group = QGroupBox("Rotation Transform")
            rotation_transform_layout = QVBoxLayout()

            temp_QHBoxLayout_1 = QHBoxLayout()
            temp_QHBoxLayout_1.addWidget(QLabel("Order"))
            euler_angles_order = QComboBox()
            euler_angles_order.addItems(["ZXZ", "XYX", "YZY", "ZYZ", "XZX", "YXY", "ZXY", "YXZ", "XZY", "YZX", "ZYX", "XYZ"])
            temp_QHBoxLayout_1.addWidget(euler_angles_order)
            rotation_transform_layout.addLayout(temp_QHBoxLayout_1)

            temp_QVBoxLayout_2 = QVBoxLayout()
            temp_QVBoxLayout_2.addWidget(QLabel("Euler Angles"))

            temp_QHBoxLayout_2_1 = QHBoxLayout()
            temp_QHBoxLayout_2_1.addWidget(QLabel("Alpha"))
            self.path_angle_alpha = QLineEdit()
            temp_QHBoxLayout_2_1.addWidget(self.path_angle_alpha)
            self.open_angle_alpha = QPushButton("Open")
            self.open_angle_alpha.clicked.connect(self.open_rotation_alpha)
            temp_QHBoxLayout_2_1.addWidget(self.open_angle_alpha)
            temp_QVBoxLayout_2.addLayout(temp_QHBoxLayout_2_1)

            temp_QHBoxLayout_2_2 = QHBoxLayout()
            temp_QHBoxLayout_2_2.addWidget(QLabel("Beta"))
            self.path_angle_beta = QLineEdit()
            temp_QHBoxLayout_2_2.addWidget(self.path_angle_beta)
            self.open_angle_beta = QPushButton("Open")
            self.open_angle_beta.clicked.connect(self.open_rotation_beta)
            temp_QHBoxLayout_2_2.addWidget(self.open_angle_beta)
            temp_QVBoxLayout_2.addLayout(temp_QHBoxLayout_2_2)

            temp_QHBoxLayout_2_3 = QHBoxLayout()
            temp_QHBoxLayout_2_3.addWidget(QLabel("Gamma"))
            self.path_angle_gamma = QLineEdit()
            temp_QHBoxLayout_2_3.addWidget(self.path_angle_gamma)
            self.open_angle_gamma = QPushButton("Open")
            self.open_angle_gamma.clicked.connect(self.open_rotation_gamma)
            temp_QHBoxLayout_2_3.addWidget(self.open_angle_gamma)
            temp_QVBoxLayout_2.addLayout(temp_QHBoxLayout_2_3)

            rotation_transform_layout.addLayout(temp_QVBoxLayout_2)
            rotation_transform_group.setLayout(rotation_transform_layout)

            self.rotation_transform_layout.addWidget(rotation_transform_group) 

        else:
            # Remove the widget
            if (self.rotation_transform_layout.itemAt(2) != None):
                self.rotation_transform_layout.itemAt(2).widget().deleteLater()
            
    def enable_checkbox_fun(self):
        if self.enable_checkbox.isChecked():
            self.group_2.setEnabled(True)
        else:
            self.group_2.setEnabled(False)

    def open_rotation_alpha(self):
        directory, _ = QFileDialog.getOpenFileName(filter="CSV Files (*.csv)")

        if directory:
            self.path_angle_alpha.setText(directory)
            self.open_angle_alpha.setStyleSheet("background-color: green")
        
    def open_rotation_beta(self):
        directory, _ = QFileDialog.getOpenFileName(filter="CSV Files (*.csv)")

        if directory:
            self.path_angle_beta.setText(directory)
            self.open_angle_beta.setStyleSheet("background-color: green")

    def open_rotation_gamma(self):
        directory, _ = QFileDialog.getOpenFileName(filter="CSV Files (*.csv)")

        if directory:
            self.path_angle_gamma.setText(directory)
            self.open_angle_gamma.setStyleSheet("background-color: green")
        
    def finish_button_fun(self):
        # Create the 3DObject
        sprite_name = self.sprite_name.text()
        # Import the STL mesh
        stl_path = self.sprite_stl_path.text()
        # Flexibility Transform
        if self.flexibility_transform.currentIndex() == 0:
            flexibility_transform = ConstantF()

        elif self.flexibility_transform.currentIndex() == 1:
            # Load the other values
            x = self.flexibility_transform_layout.itemAt(2).widget().findChildren(QComboBox)[0].currentText()
            y = self.flexibility_transform_layout.itemAt(2).widget().findChildren(QComboBox)[1].currentText()
            z = self.flexibility_transform_layout.itemAt(2).widget().findChildren(QComboBox)[2].currentText()

            major_axis = self.flexibility_transform_layout.itemAt(2).widget().findChildren(QDoubleSpinBox)[0].value()
            minor_axis = self.flexibility_transform_layout.itemAt(2).widget().findChildren(QDoubleSpinBox)[1].value()

            flexibility_transform = Flexibility_type1(x, y, z, major_axis, minor_axis)

        # Rotation Transform
        if self.rotation_transform.currentIndex() == 0:
            rotation_transform = ConstantR()

        elif self.rotation_transform.currentIndex() == 1:
            order = self.rotation_transform_layout.itemAt(2).widget().findChildren(QComboBox)[0].currentText()
            
            alpha = self.rotation_transform_layout.itemAt(2).widget().findChildren(QLineEdit)[0].text()
            beta = self.rotation_transform_layout.itemAt(2).widget().findChildren(QLineEdit)[1].text()
            gamma = self.rotation_transform_layout.itemAt(2).widget().findChildren(QLineEdit)[2].text()

            alpha_values = np.array(pd.read_csv(alpha, header=None))
            beta_values = np.array(pd.read_csv(beta, header=None))
            gamma_values = np.array(pd.read_csv(gamma, header=None))

            rotation_transform = Rotation_EulerAngles(order)

        # Loading the stl mesh
        stl_mesh = mesh.Mesh.from_file(stl_path)

        temp_object = Object3D(sprite_name, stl_mesh, flexibility_transform, rotation_transform)
        # Load the initial conditions
        if self.enable_checkbox.isChecked():
            time = self.time_input.value()
            alpha = self.angle_input_alpha.value()
            beta = self.angle_input_beta.value()
            gamma = self.angle_input_gamma.value()

            angles = np.array([alpha, beta, gamma])
            temp_object.stl_mesh = temp_object.transform(0, [alpha, beta, gamma])

        angles = np.hstack([alpha_values, beta_values, gamma_values])
        sprite = Sprite(temp_object, angles)
        self.sprite_data = sprite
        self.SpriteCreated.emit(self.sprite_data)
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
