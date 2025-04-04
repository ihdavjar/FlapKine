import os
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from stl import mesh
import qtawesome as qta
import vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from src.core.core import Object3D, Sprite
from src.core.transforms.translation import *
from src.core.transforms.rotation import *
from src.core.transforms.flexibility import *
from app.core.invkinematics import *


class CreateSprite(QMainWindow):

    SpriteCreated = pyqtSignal(Sprite)

    def __init__(self):
        super(CreateSprite, self).__init__()

        self.inverse_kinematics = False

        self.setWindowTitle("Create Sprite")

        # Set the icon
        self.setWindowIcon(QIcon(os.path.join('app', 'assets', 'flap_kine_icon.png')))
        self.setGeometry(300, 100, 800, 600)  # Set a better window size
        self.center()

        primary_color = self.palette().color(self.foregroundRole()).name()

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
        self.undo_action.setEnabled(False)
        self.redo_action = self.edit_menu.addAction('Redo')
        self.redo_action.setEnabled(False)

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


        main_layout = QVBoxLayout()
        self.main_widget = QWidget()


        group_1 = QGroupBox("3DObject Properties")
        group_1.setFont(QFont('Times', 9))
        group_1_layout = QFormLayout()
        group_1.setStyleSheet("""
    QGroupBox {
        color: #3498db;  /* Title text color (blue) */
        font-weight: bold;
        border: 2px solid #2980b9; /* Border color */
        border-radius: 5px;
        margin-top: 10px; /* Space between border and title */
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left; /* Positioning title */
        padding: 5px; /* Space around title */
    }
""")

        ########## Sprite Name ##########
        self.sprite_name = QLineEdit()
        self.sprite_name.setPlaceholderText("Enter Sprite Name")
        sprite_text_label = QLabel("Sprite Name:")
        sprite_text_label.setFont(QFont('Times', 8))
        group_1_layout.addRow(sprite_text_label, self.sprite_name)


        ########## STL File Path ##########
        self.sprite_stl_path = QLineEdit()
        self.sprite_stl_path.setPlaceholderText("Select STL file")
        self.sprite_stl_open = QPushButton("Open")
        self.sprite_stl_open.setIcon(qta.icon("fa5.folder-open", color=primary_color))
        self.sprite_stl_open.clicked.connect(self.open_file)
        self.stl_path_layout = QHBoxLayout()
        self.stl_path_layout.addWidget(self.sprite_stl_path)
        self.stl_path_layout.addWidget(self.sprite_stl_open)

        # Adding Plotting Features
        self.vtkWidget = QVTKRenderWindowInteractor(self)
        self.stl_path_layout.addWidget(self.vtkWidget)

        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)

        self.ren.SetBackground(0.95, 0.95, 0.95)  # Light gray


        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        self.iren.Initialize()

        stl_path_label = QLabel("STL File Path:")
        stl_path_label.setFont(QFont('Times', 8))
        group_1_layout.addRow(stl_path_label, self.stl_path_layout)


        ########### Transformations ##############
        transformation_group = QGroupBox("Transformations")
        transformation_group.setFont(QFont('Times', 8))
        transformation_group_layout = QFormLayout()
        transformation_group.setStyleSheet("""
    QGroupBox {
        color: #16a085;  /* Teal - Title text */
        font-weight: bold;
        border: 2px solid #13876a; /* Darker Teal - Border */
        border-radius: 6px;
        margin-top: 10px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 5px;
    }
""")

        ########## Translation Transform ##########
        self.translation_transform_layout = QHBoxLayout()
        transformation_label = QLabel("Translation Transform:")
        transformation_label.setFont(QFont('Times', 7))
        self.translation_transform = QComboBox()
        self.translation_transform.addItem("Constant")
        self.translation_transform.addItem("COM")
        self.translation_transform.currentIndexChanged.connect(self.translation_transform_fun)

        self.translation_transform_layout.addWidget(self.translation_transform)
        transformation_group_layout.addRow(transformation_label, self.translation_transform_layout)


        ########## Rotation Transform ##########
        self.rotation_transform_layout = QHBoxLayout()
        rotation_label = QLabel("Rotation Transform:")
        rotation_label.setFont(QFont('Times', 7))
        self.rotation_transform = QComboBox()
        self.rotation_transform.addItem("Constant")
        self.rotation_transform.addItem("Euler_Angles")
        self.rotation_transform.addItem("Custom")
        self.rotation_transform.currentIndexChanged.connect(self.rotation_transform_fun)
        
        self.rotation_transform_layout.addWidget(self.rotation_transform)
        transformation_group_layout.addRow(rotation_label, self.rotation_transform_layout)

        ########## Flexibility Transform ##########
        self.flexibility_transform_layout = QHBoxLayout()
        flexibility_label = QLabel("Flexibility Transform:")
        flexibility_label.setFont(QFont('Times', 7))
        self.flexibility_transform = QComboBox()
        self.flexibility_transform.addItem("Constant")
        self.flexibility_transform.addItem("FlexibleType1")
        self.flexibility_transform.addItem("FlexibleType2")
        self.flexibility_transform.addItem("Custom")
        self.flexibility_transform.currentIndexChanged.connect(self.flexibility_transform_fun)

        self.flexibility_transform_layout.addWidget(self.flexibility_transform)
        transformation_group_layout.addRow(flexibility_label, self.flexibility_transform_layout)

        transformation_group.setLayout(transformation_group_layout)
        group_1_layout.addRow(transformation_group)
        

        ########## GROUP 2 ##########
        self.group_2 = QGroupBox("Initial Conditions")
        self.group_2.setFont(QFont('Times', 9))
        group_2_layout = QFormLayout()
        self.group_2.setStyleSheet("""
    QGroupBox {
        color: #e67e22;  /* Orange - Title text */
        font-weight: bold;
        border: 2px solid #d35400; /* Darker Orange - Border */
        border-radius: 6px;
        margin-top: 10px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 5px;
    }
""")

        # Flexibility Transform
        time_label = QLabel("Time instant:")
        time_label.setFont(QFont('Times', 7))

        # Translation Transform
        position_group = QGroupBox("Initial Position of Body Origin")
        position_group.setStyleSheet("""
    QGroupBox {
        color: #16a085;  /* Teal - Title text */
        font-weight: bold;
        border: 2px solid #13876a; /* Darker Teal - Border */
        border-radius: 6px;
        margin-top: 10px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 5px;
    }
""")
        position_layout = QFormLayout()
        
        self.position_x = QDoubleSpinBox()
        self.position_x.setRange(-100, 100)
        self.position_x.setSuffix("m")
        self.position_x.valueChanged.connect(self.initial_condition_changed)

        self.position_y = QDoubleSpinBox()
        self.position_y.setRange(-100, 100)
        self.position_y.setSuffix("m")
        self.position_y.valueChanged.connect(self.initial_condition_changed)

        self.position_z = QDoubleSpinBox()
        self.position_z.setRange(-100, 100)
        self.position_z.setSuffix("m")
        self.position_z.valueChanged.connect(self.initial_condition_changed)

        x_pos_label = QLabel("X:")
        x_pos_label.setFont(QFont('Times', 7))

        y_pos_label = QLabel("Y:")
        y_pos_label.setFont(QFont('Times', 7))

        z_pos_label = QLabel("Z:")
        z_pos_label.setFont(QFont('Times', 7))

        position_layout.addRow(x_pos_label, self.position_x)
        position_layout.addRow(y_pos_label, self.position_y)
        position_layout.addRow(z_pos_label, self.position_z)

        position_group.setLayout(position_layout)   

        # Rotation Transform
        angle_group = QGroupBox("Initial Euler Angles")
        angle_layout = QFormLayout()   
        angle_group.setStyleSheet("""
    QGroupBox {
        color: #9b59b6;  /* Purple - Title text */
        font-weight: bold;
        border: 2px solid #8e44ad; /* Darker Purple - Border */
        border-radius: 6px;
        margin-top: 10px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 5px;
    }   
""")
        self.angle_input_alpha = QDoubleSpinBox()
        self.angle_input_alpha.setRange(-360, 360)
        self.angle_input_alpha.setSuffix("°")
        self.angle_input_alpha.valueChanged.connect(self.initial_condition_changed)

        alpha_label = QLabel("Alpha:")
        alpha_label.setFont(QFont('Times', 7))

        self.angle_input_beta = QDoubleSpinBox()
        self.angle_input_beta.setRange(-360, 360)
        self.angle_input_beta.setSuffix("°")
        self.angle_input_beta.valueChanged.connect(self.initial_condition_changed)

        beta_label = QLabel("Beta:")
        beta_label.setFont(QFont('Times', 7))

        self.angle_input_gamma = QDoubleSpinBox()
        self.angle_input_gamma.setRange(-360, 360)
        self.angle_input_gamma.setSuffix("°")
        self.angle_input_gamma.valueChanged.connect(self.initial_condition_changed)

        gamma_label = QLabel("Gamma:")
        gamma_label.setFont(QFont('Times', 7))

        angle_layout.addRow(alpha_label, self.angle_input_alpha)
        angle_layout.addRow(beta_label, self.angle_input_beta)
        angle_layout.addRow(gamma_label, self.angle_input_gamma)


        angle_group.setLayout(angle_layout)

        group_2_layout.addRow(position_group)
        group_2_layout.addRow(angle_group)
        
        
        group_1.setLayout(group_1_layout)
        self.group_2.setLayout(group_2_layout)

        self.group_2.setEnabled(False)

        main_layout.addWidget(group_1)
        self.enable_checkbox = QCheckBox("Enable Initial Conditions")
        self.enable_checkbox.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
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

            self.sprite_stl_path.setText(directory)

            # Load STL file
            reader = vtk.vtkSTLReader()
            reader.SetFileName(directory)

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(reader.GetOutputPort())

            self.actor = vtk.vtkActor()
            self.actor.SetMapper(mapper)
            self.actor.GetProperty().SetColor(0.5, 0.7, 1)  # Light blue
            # Reduce opacity
            self.actor.GetProperty().SetOpacity(0.6)
            self.ren.SetBackground(0.95, 0.95, 0.95)  # Light gray

            # Calculate the bounding box of the STL model
            bounds = self.actor.GetBounds()  # Get the bounds of the actor (xmin, xmax, ymin, ymax, zmin, zmax)
            x_length = bounds[1] - bounds[0]  # xmax - xmin
            y_length = bounds[3] - bounds[2]  # ymax - ymin
            z_length = bounds[5] - bounds[4]  # zmax - zmin

            # Determine the largest dimension to scale the axes proportionally
            max_length = max(x_length, y_length, z_length)

            axes_inertial = vtk.vtkAxesActor()
            axes_inertial.SetTotalLength(max_length * 0.1, max_length * 0.1, max_length * 0.1)  # Scale axes to 20% of the largest dimension
            axes_inertial.SetShaftType(0)  # Use a cylinder for the shaft
            axes_inertial.SetAxisLabels(1)  # Enable axis labels

            # Set the axis labels with subscript E
            axes_inertial.SetXAxisLabelText("X")  # Unicode subscript '1'
            axes_inertial.SetYAxisLabelText("Y")  # Unicode subscript '2'
            axes_inertial.SetZAxisLabelText("Z")  # Unicode subscript '3'

            axes_inertial.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetColor(0, 0, 0)
            axes_inertial.GetYAxisCaptionActor2D().GetCaptionTextProperty().SetColor(0, 0, 0)
            axes_inertial.GetZAxisCaptionActor2D().GetCaptionTextProperty().SetColor(0, 0, 0)


            # Body Axes
            self.axes_body = vtk.vtkAxesActor()
            self.axes_body.SetTotalLength(max_length * 0.1, max_length * 0.1, max_length * 0.1)  # Scale axes to 20% of the largest dimension
            self.axes_body.SetShaftType(0)  # Use a cylinder for the shaft
            self.axes_body.SetAxisLabels(1)  # Enable axis labels

            self.axes_body.SetXAxisLabelText("A") 
            self.axes_body.SetYAxisLabelText("B")
            self.axes_body.SetZAxisLabelText("C")

            self.axes_body.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetColor(0, 0, 0)
            self.axes_body.GetYAxisCaptionActor2D().GetCaptionTextProperty().SetColor(0, 0, 0)
            self.axes_body.GetZAxisCaptionActor2D().GetCaptionTextProperty().SetColor(0, 0, 0)

            # Clear previous actors and add new one
            self.ren.RemoveAllViewProps()
            self.ren.AddActor(self.actor)
            self.ren.AddActor(axes_inertial)
            self.ren.AddActor(self.axes_body)
            self.ren.ResetCamera()

            # Render the scene
            self.vtkWidget.GetRenderWindow().Render()

    def translation_transform_fun(self):
        primary_color = self.palette().color(self.foregroundRole()).name()

        # Remove the previous widget if it exists
        if hasattr(self, "translation_transform_group"):
            self.translation_transform_layout.removeWidget(self.translation_transform_group)
            self.translation_transform_group.deleteLater()
            del self.translation_transform_group  # Remove reference

        # Check if the selected index is 1
        if self.translation_transform.currentIndex() == 1:
            self.translation_transform_group = QGroupBox("Translation Properties")
            self.translation_transform_group.setFont(QFont('Times', 8))
            translation_transform_layout = QVBoxLayout()
            self.translation_transform_group.setStyleSheet("""
                QGroupBox {
                    color: #7f8c8d;  /* Gray - Title text */
                    font-weight: bold;
                    border: 2px solid #626567; /* Darker Gray - Border */
                    border-radius: 6px;
                    margin-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 5px;
                }   
            """)

            temp_Layout = QFormLayout()
            pos_label = QLabel("Position:")
            pos_label.setFont(QFont('Times', 7))

            temp_QHBoxLayout = QHBoxLayout()
            self.position_input = QLineEdit()
            self.position_input.setPlaceholderText("Time series of COM position")

            self.open_position = QPushButton("Open")
            self.open_position.setFont(QFont('Times', 7))
            self.open_position.setIcon(qta.icon("fa5.folder-open", color=primary_color))
            self.open_position.clicked.connect(self.open_position_file)

            temp_QHBoxLayout.addWidget(self.position_input)
            temp_QHBoxLayout.addWidget(self.open_position)
            temp_Layout.addRow(pos_label, temp_QHBoxLayout)

            translation_transform_layout.addLayout(temp_Layout)
            self.translation_transform_group.setLayout(translation_transform_layout)

            # Add the new layout to the main translation layout
            self.translation_transform_layout.addWidget(self.translation_transform_group)

    def flexibility_transform_fun(self):
        primary_color = self.palette().color(self.foregroundRole()).name()

        # Remove the previous widget if it exists
        if hasattr(self, "flexibility_transform_group"):
            self.flexibility_transform_layout.removeWidget(self.flexibility_transform_group)
            self.flexibility_transform_group.deleteLater()
            del self.flexibility_transform_group  # Remove reference

        selected_index = self.flexibility_transform.currentIndex()

        if selected_index in [1, 2]:  
            self.flexibility_transform_group = QGroupBox("Flexibility Transform")
            flexibility_transform_layout = QVBoxLayout()

            # Apply consistent style
            self.flexibility_transform_group.setStyleSheet("""
                QGroupBox {
                    color: #7f8c8d;  
                    font-weight: bold;
                    border: 2px solid #626567;
                    border-radius: 6px;
                    margin-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 5px;
                }   
            """)

            form_layout = QGridLayout()

            # Axis Selection (X, Y, Z) with Equal Spacing
            axis_layout = QHBoxLayout()

            x_label = QLabel("X:")
            x_label.setFont(QFont('Times', 7))
            self.temp_combobox_x = QComboBox()
            self.temp_combobox_x.addItems(["True", "False"])
            self.temp_combobox_x.setFont(QFont('Times', 8))

            y_label = QLabel("Y:")
            y_label.setFont(QFont('Times', 7))
            self.temp_combobox_y = QComboBox()
            self.temp_combobox_y.addItems(["True", "False"])
            self.temp_combobox_y.setFont(QFont('Times', 8))

            z_label = QLabel("Z:")
            z_label.setFont(QFont('Times', 7))
            self.temp_combobox_z = QComboBox()
            self.temp_combobox_z.addItems(["True", "False"])
            self.temp_combobox_z.setFont(QFont('Times', 8))

            axis_layout.addStretch()
            axis_layout.addWidget(x_label)
            axis_layout.addWidget(self.temp_combobox_x)
            axis_layout.addStretch()
            axis_layout.addWidget(y_label)
            axis_layout.addWidget(self.temp_combobox_y)
            axis_layout.addStretch()
            axis_layout.addWidget(z_label)
            axis_layout.addWidget(self.temp_combobox_z)
            axis_layout.addStretch()

            flexibility_transform_layout.addLayout(axis_layout)

            if selected_index == 1:
                # Time Period Setting
                time_label = QLabel("Time Period:")
                time_label.setFont(QFont('Times', 7))
                self.time_period = QSpinBox()
                self.time_period.setRange(0, 100000)
                self.time_period.setFont(QFont('Times', 8))

                time_layout = QHBoxLayout()
                time_layout.addWidget(time_label)
                time_layout.addWidget(self.time_period)
                flexibility_transform_layout.addLayout(time_layout)

            elif selected_index == 2:
                # M-values Input Row
                m_values_label = QLabel("M values:")
                m_values_label.setFont(QFont('Times', 7))
                self.path_m_values = QLineEdit()
                self.path_m_values.setPlaceholderText("Enter M values")  # Add placeholder
                self.path_m_values.setFont(QFont('Times', 8))
                self.open_m_values = QPushButton("Open")
                self.open_m_values.setIcon(qta.icon("fa5.folder-open", color=primary_color))
                self.open_m_values.clicked.connect(self.open_m_values_fun)

                p_label = QLabel("p:")
                p_label.setFont(QFont('Times', 7))
                self.p_value = QDoubleSpinBox()
                self.p_value.setRange(0, 1)
                self.p_value.setFont(QFont('Times', 8))

                m_values_layout = QHBoxLayout()
                m_values_layout.addWidget(m_values_label)
                m_values_layout.addWidget(self.path_m_values)
                m_values_layout.addWidget(self.open_m_values)
                flexibility_transform_layout.addLayout(m_values_layout)

                p_layout = QHBoxLayout()
                p_layout.addWidget(p_label)
                p_layout.addWidget(self.p_value)
                flexibility_transform_layout.addLayout(p_layout)

            self.flexibility_transform_group.setLayout(flexibility_transform_layout)
            self.flexibility_transform_layout.addWidget(self.flexibility_transform_group)

        else:
            # Remove widget if another option is selected
            if self.flexibility_transform_layout.count() > 1:
                item = self.flexibility_transform_layout.itemAt(1)
                if item and item.widget():
                    item.widget().deleteLater()

    def rotation_transform_fun(self):
    
        if self.rotation_transform.currentIndex() == 1:

            # Create the main group box
            rotation_transform_group = QGroupBox("Rotation Transform")
            rotation_transform_layout = QVBoxLayout()

            # Order selection row
            order_layout = QHBoxLayout()
            order_label = QLabel("Order:")
            order_label.setFont(QFont('Times', 8))

            euler_angles_order = QComboBox()
            euler_angles_order.addItems(["ZXZ", "XYX", "YZY", "ZYZ", "XZX", "YXY", "ZXY", "YXZ", "XZY", "YZX", "ZYX", "XYZ"])
            euler_angles_order.setFont(QFont('Times', 8))

            order_layout.addWidget(order_label)
            order_layout.addWidget(euler_angles_order)

            # Euler Angles Inputs (Grid Layout)
            euler_angles_layout = QGridLayout()
            euler_angles_layout.addWidget(QLabel("Euler Angles Time Series:"), 0, 0, 1, 3)  # Title spanning 3 columns

            # Add button to add inverse kinematics
            inverse_kinematics_button = QPushButton("Import Inverse Kinematics")
            inverse_kinematics_button.setIcon(qta.icon("mdi.bird", color=self.palette().color(self.foregroundRole()).name()))
            inverse_kinematics_button.setFont(QFont('Times', 8))
            inverse_kinematics_button.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
            inverse_kinematics_button.setFixedHeight(30)  # Set a fixed height for the button
            inverse_kinematics_button.clicked.connect(self.calculate_inverse_kinematics)  # Connect to the function

            # Add hover message
            inverse_kinematics_button.setToolTip("Import 3D cordinates data obtained from DltDv Software")
            inverse_kinematics_button.setStyleSheet("""
    QPushButton {
        background-color: #3498db;  /* Blue button color */
        color: white;  /* White text color */
        font-weight: bold;  /* Bold text */
        font-size: 14px;  /* Adjusted font size */
        border: none;  /* No border */
        border-radius: 5px;  /* Rounded corners */
        padding: 8px 12px;  /* Better padding for appearance */
        cursor: pointer;  /* Pointer cursor on hover */
    }
    
    QPushButton:hover {
        background-color: #2980b9;  /* Darker blue on hover */
    }

    QPushButton:pressed {
        background-color: #1f618d;  /* Even darker blue when pressed */
    }

    QPushButton:focus {
        outline: none;  /* Removes default focus outline */
    }
""")

            inverse_kinematics_button.setCursor(QCursor(Qt.PointingHandCursor))  # Change cursor to pointer

            euler_angles_layout.addWidget(inverse_kinematics_button, 0, 3)  # Add button to the first row

            # Alpha Row
            alpha_label = QLabel("Alpha:")
            alpha_label.setFont(QFont('Times', 7))
            self.path_angle_alpha = QLineEdit()
            self.path_angle_alpha.setPlaceholderText("Time series of Alpha")
            self.open_angle_alpha = QPushButton("Open")
            self.open_angle_alpha.setIcon(qta.icon("fa5.folder-open", color=self.palette().color(self.foregroundRole()).name()))
            self.open_angle_alpha.clicked.connect(self.open_rotation_alpha)

            euler_angles_layout.addWidget(alpha_label, 1, 0)
            euler_angles_layout.addWidget(self.path_angle_alpha, 1, 1)
            euler_angles_layout.addWidget(self.open_angle_alpha, 1, 2)

            # Beta Row
            beta_label = QLabel("Beta:")
            beta_label.setFont(QFont('Times', 7))
            self.path_angle_beta = QLineEdit()
            self.path_angle_beta.setPlaceholderText("Time series of Beta")
            self.open_angle_beta = QPushButton("Open")
            self.open_angle_beta.setIcon(qta.icon("fa5.folder-open", color=self.palette().color(self.foregroundRole()).name()))
            self.open_angle_beta.clicked.connect(self.open_rotation_beta)

            euler_angles_layout.addWidget(beta_label, 2, 0)
            euler_angles_layout.addWidget(self.path_angle_beta, 2, 1)
            euler_angles_layout.addWidget(self.open_angle_beta, 2, 2)

            # Gamma Row
            gamma_label = QLabel("Gamma:")
            gamma_label.setFont(QFont('Times', 7))
            self.path_angle_gamma = QLineEdit()
            self.path_angle_gamma.setPlaceholderText("Time series of Gamma")
            self.open_angle_gamma = QPushButton("Open")
            self.open_angle_gamma.setIcon(qta.icon("fa5.folder-open", color=self.palette().color(self.foregroundRole()).name()))
            self.open_angle_gamma.clicked.connect(self.open_rotation_gamma)

            euler_angles_layout.addWidget(gamma_label, 3, 0)
            euler_angles_layout.addWidget(self.path_angle_gamma, 3, 1)
            euler_angles_layout.addWidget(self.open_angle_gamma, 3, 2)

            # Add layouts to the main layout
            rotation_transform_layout.addLayout(order_layout)
            rotation_transform_layout.addLayout(euler_angles_layout)

            # Apply improved styling
            rotation_transform_group.setStyleSheet("""
                QGroupBox {
                    color: #7f8c8d;  /* Gray - Title text */
                    font-weight: bold;
                    border: 2px solid #626567; /* Darker Gray - Border */
                    border-radius: 6px;
                    margin-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 5px;
                }
            """)

            rotation_transform_group.setLayout(rotation_transform_layout)
            self.rotation_transform_layout.addWidget(rotation_transform_group)

        else:
            # Remove the widget safely
            if self.rotation_transform_layout.count() > 1:
                item = self.rotation_transform_layout.itemAt(1)
                if item and item.widget():
                    item.widget().deleteLater()

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
    
    def open_position_file(self):
        directory, _ = QFileDialog.getOpenFileName(filter="CSV Files (*.csv)")

        if directory:
            self.position_input.setText(directory)
            self.open_position.setStyleSheet("background-color: green")
    
    def open_m_values_fun(self):
        directory, _ = QFileDialog.getOpenFileName(filter="CSV Files (*.csv)")

        if directory:
            self.path_m_values.setText(directory)
            self.open_m_values.setStyleSheet("background-color: green")
        
    def finish_button_fun(self):

        # Create the 3DObject
        sprite_name = self.sprite_name.text()
        
        # Import the STL mesh
        stl_path = self.sprite_stl_path.text()
        
        # Loading the stl mesh
        stl_mesh = mesh.Mesh.from_file(stl_path)

        temp_vector = np.array(stl_mesh.vectors)
        temp_vector = temp_vector.reshape(-1, 3)
        min_x, min_y, min_z = np.min(temp_vector, axis=0)
        max_x, max_y, max_z = np.max(temp_vector, axis=0)
        angles_temp = np.array([0, 0, 0])
        positions_temp = np.array([0, 0, 0])

        # Flexibility Transform
        if self.flexibility_transform.currentIndex() == 0:
            flexibility_transform = ConstantF()

        elif self.flexibility_transform.currentIndex() == 1:
            # Load the other values
            x = self.flexibility_transform_layout.itemAt(1).widget().findChildren(QComboBox)[0].currentText() == "True"
            y = self.flexibility_transform_layout.itemAt(1).widget().findChildren(QComboBox)[1].currentText() == "True"
            z = self.flexibility_transform_layout.itemAt(1).widget().findChildren(QComboBox)[2].currentText() == "True"

            major_axis = (max_x - min_x)/2
            minor_axis = (max_y - min_y)/2

            p = self.p_value.value()

            flexibility_transform = Flexibility_type1(x, y, z, major_axis, minor_axis, p=p)

        elif self.flexibility_transform.currentIndex() == 2:

            # Load the other values
            x = self.flexibility_transform_layout.itemAt(1).widget().findChildren(QComboBox)[0].currentText() == "True"
            y = self.flexibility_transform_layout.itemAt(1).widget().findChildren(QComboBox)[1].currentText() == "True"
            z = self.flexibility_transform_layout.itemAt(1).widget().findChildren(QComboBox)[2].currentText() == "True"

            m_vals = np.array(pd.read_csv(self.path_m_values.text(), header=None))

            major_axis = (max_x - min_x)/2
            minor_axis = (max_y - min_y)/2

            p = self.p_value.value()

            flexibility_transform = Flexibility_type2(x, y, z, min_y, major_axis, minor_axis, m_vals, time_period=len(m_vals), p=p)

        # Rotation Transform
        if self.rotation_transform.currentIndex() == 0:
            rotation_transform = ConstantR()

            angles = None

        elif self.rotation_transform.currentIndex() == 1:

            if self.inverse_kinematics:
                angles, order = self.window.inv_result
                alpha_values, beta_values, gamma_values = angles
                
                angles = np.vstack([alpha_values, beta_values, gamma_values]).T
            
            else:

                order = self.rotation_transform_layout.itemAt(1).widget().findChildren(QComboBox)[0].currentText()
                
                alpha = self.rotation_transform_layout.itemAt(1).widget().findChildren(QLineEdit)[0].text()
                beta = self.rotation_transform_layout.itemAt(1).widget().findChildren(QLineEdit)[1].text()
                gamma = self.rotation_transform_layout.itemAt(1).widget().findChildren(QLineEdit)[2].text()

                alpha_values = np.array(pd.read_csv(alpha, header=None))
                beta_values = np.array(pd.read_csv(beta, header=None))
                gamma_values = np.array(pd.read_csv(gamma, header=None))

                angles = np.hstack([alpha_values, beta_values, gamma_values])

            rotation_transform = Rotation_EulerAngles(order)
            
        # Translation Transform
        if self.translation_transform.currentIndex() == 0:
            translation_transform = ConstantT()

            positions = None

        elif self.translation_transform.currentIndex() == 1:
            positions = self.translation_transform_layout.itemAt(1).widget().findChildren(QLineEdit)[0].text()
            translation_transform = Translation_COM()
        
            positions = np.array(pd.read_csv(positions, header=None))

            positions = positions.reshape(-1, 3)
            
        
        temp_object = Object3D(sprite_name, stl_mesh, translation_transform, rotation_transform, flexibility_transform)

        # Load the initial conditions
        if self.enable_checkbox.isChecked():

            no_transform_temp_object = Object3D(sprite_name, stl_mesh, Translation_COM(), rotation_transform, ConstantF())
            
            
            alpha = self.angle_input_alpha.value()
            beta = self.angle_input_beta.value()
            gamma = self.angle_input_gamma.value()

            x_pos = self.position_x.value()
            y_pos = self.position_y.value()
            z_pos = self.position_z.value()

            alpha = np.radians(alpha)
            beta = np.radians(beta)
            gamma = np.radians(gamma)
            
            angles_temp = np.array([alpha, beta, gamma])
            positions_temp = np.array([x_pos, y_pos, z_pos])

            temp_object.stl_mesh = no_transform_temp_object.transform(positions_temp, angles_temp, 0)

        if positions is None and angles is not None:
            positions = np.zeros((angles.shape[0], 3))
        
        if angles is None and positions is not None:
            angles = np.zeros((positions.shape[0], 3))

        if angles is None and positions is None:
            positions = np.zeros((1, 3))
            angles = np.zeros((1, 3))
                  
        sprite = Sprite(temp_object, positions, angles)

        if self.enable_checkbox.isChecked():
            sprite.frame_origin = positions_temp
            sprite.frame_orientation = angles_temp

        self.sprite_data = sprite
        self.SpriteCreated.emit(self.sprite_data)
        self.close()
    
    def initial_condition_changed(self):

        alpha = self.angle_input_alpha.value()
        beta = self.angle_input_beta.value()
        gamma = self.angle_input_gamma.value()

        x_pos = self.position_x.value()
        y_pos = self.position_y.value()
        z_pos = self.position_z.value()

        alpha = np.radians(alpha)
        beta = np.radians(beta)
        gamma = np.radians(gamma)
        
        angles_temp = np.array([alpha, beta, gamma])
        positions_temp = np.array([x_pos, y_pos, z_pos])

        Rotation_Transform_x = vtk.vtkTransform()
        Rotation_Transform_x.RotateX(np.degrees(angles_temp[0]))

        Rotation_Transform_y = vtk.vtkTransform()
        Rotation_Transform_y.RotateY(np.degrees(angles_temp[1]))

        Rotation_Transform_z = vtk.vtkTransform()
        Rotation_Transform_z.RotateZ(np.degrees(angles_temp[2]))

        final_transform = vtk.vtkTransform()
        final_transform.PostMultiply()
        final_transform.Translate(positions_temp)
        final_transform.Concatenate(Rotation_Transform_x)
        final_transform.Concatenate(Rotation_Transform_y)
        final_transform.Concatenate(Rotation_Transform_z)
        
        self.actor.SetUserTransform(final_transform)
        self.axes_body.SetUserTransform(final_transform)
        self.vtkWidget.GetRenderWindow().Render()

    def calculate_inverse_kinematics(self):
        self.window = InvKineWindow()
        self.window.show()
        self.window.angle_data.connect(self.process_inv_data)
    
    def process_inv_data(self):
        angles, order = self.window.inv_result
        alpha_values, beta_values, gamma_values = angles
        self.rotation_transform_layout.itemAt(1).widget().setEnabled(False)
        self.rotation_transform_layout.itemAt(1).widget().findChildren(QComboBox)[0].setCurrentText(order)
        self.inverse_kinematics = True
        
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

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = CreateSprite()
    window.show()
    sys.exit(app.exec_())