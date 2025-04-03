import numpy as np
import pandas as pd

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sklearn.ensemble import RandomForestRegressor
from scipy.signal import savgol_filter
from src.core.transforms.vtk_transform import *
from src.core.inverse_kinematics.analytical_methods import model_analytical
import vtk
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import qtawesome as qta


from PyQt5.QtCore import pyqtSignal, Qt
        
class InvKineWindow(QMainWindow):
    
    angle_data = pyqtSignal(tuple)

    def __init__(self):
        super(InvKineWindow, self).__init__()

        # Place the window in the center of the screen
        self.setWindowTitle("Inverse Kinematics")

        # Set the window geometry
        self.resize(1200, 800)

        # Set the icon
        self.setWindowIcon(QIcon(qta.icon("mdi.robot", color="black")))
        
        ############################ Menu Bar ################################
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
        self.new_window_action = self.window_menu.addAction('New Window')
        self.new_window_action.setEnabled(False)
        
        ############################ Main Layout ################################
        # Create the main widget and set it as the central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create the main layout
        main_layout = QVBoxLayout(central_widget)

        import_widget = QWidget()
        import_layout = QHBoxLayout(import_widget)
        import_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        import_layout.setSpacing(0)  # Remove spacing between widgets


        import_label = QLabel("Import Data")
        import_label.setFont(QFont('Times', 8))
        import_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        import_label.setStyleSheet("color: #333;")  # Darker color for better visibility

        self.data_path = QLineEdit()
        self.data_path.setPlaceholderText("Path to the data file")
        self.data_path.setFont(QFont('Times', 8))
        self.data_path.setStyleSheet("background-color: #f0f0f0; color: #333;")
        self.data_path.setFixedHeight(30)

        import_button = QPushButton("Import Data")
        import_button.setFont(QFont('Times', 8))
        import_button.setStyleSheet("background-color: #005a9e; color: white;")
        import_button.setIcon(qta.icon("mdi.file-import", color="white"))
        import_button.clicked.connect(self.import_data)

        import_layout.addWidget(import_label)
        import_layout.addWidget(self.data_path)
        import_layout.addWidget(import_button)

        order_widget = QWidget()
        order_layout = QHBoxLayout()
        order_label = QLabel("Euler Angle Sequence:")
        order_label.setFont(QFont('Times', 8))

        self.euler_angles_order = QComboBox()
        self.euler_angles_order.addItems(["ZXZ", "XYX", "YZY", "ZYZ", "XZX", "YXY", "ZXY", "YXZ", "XZY", "YZX", "ZYX", "XYZ"])
        self.euler_angles_order.setFont(QFont('Times', 8))
        self.euler_angles_order.currentIndexChanged.connect(self.plot_data_right)
        self.euler_angles_order.setEnabled(False)

        order_layout.addWidget(order_label)
        order_layout.addWidget(self.euler_angles_order)
        order_widget.setLayout(order_layout)
        import_layout.addWidget(order_widget)
        import_widget.setLayout(import_layout)

        graph_group = QGroupBox("Visualisation")
        graph_group.setFont(QFont('Times', 9))
        graph_layout = QHBoxLayout() 

        main_splitter = QSplitter(Qt.Horizontal)

        self.createLeftGroup()
        self.createRightGroup()

        # Add both rows to main vertical splitter
        main_splitter.addWidget(self.left_group)
        main_splitter.addWidget(self.right_group)


        main_splitter.setSizes([400, 400])   # Each half is 400px tall
        
        # Add the main splitter to the layout
        graph_layout.addWidget(main_splitter)
        graph_group.setLayout(graph_layout)
        main_layout.addWidget(import_widget)
        main_layout.addWidget(graph_group)

        self.finish_button = QPushButton("Finish")
        self.finish_button.setFont(QFont('Times', 8))
        self.finish_button.clicked.connect(self.finish_button_fun)
        self.finish_button.setEnabled(False)

        main_layout.addWidget(self.finish_button)
        
    ############################ Project Functions ################################
    def process_data(self, data):

        # Make a copy of the data
        data_copy = data.copy()

        for i in range(1, 5):
            x_data_temp = data['pt{}_X'.format(i)]
            y_data_temp = data['pt{}_Y'.format(i)]
            z_data_temp = data['pt{}_Z'.format(i)]

            x_data_temp = np.array(x_data_temp)
            y_data_temp = np.array(y_data_temp)
            z_data_temp = np.array(z_data_temp)

            # Filter the data
            x_data_temp_filter = savgol_filter(x_data_temp, 51, 3)
            y_data_temp_filter = savgol_filter(y_data_temp, 51, 3)
            z_data_temp_filter = savgol_filter(z_data_temp, 51, 3)

            temp_data = pd.DataFrame({'time':np.arange(0, len(x_data_temp), 1), 'x':x_data_temp_filter, 'y':y_data_temp_filter, 'z':z_data_temp_filter})
            temp_data.dropna(inplace=True)
            times_ = np.array(temp_data['time']).reshape(-1, 1)[::5]
            x_data_temp_filter = np.array(temp_data['x']).reshape(-1, )[::5]
            y_data_temp_filter = np.array(temp_data['y']).reshape(-1, )[::5]
            z_data_temp_filter = np.array(temp_data['z']).reshape(-1, )[::5]

            # Correct the data
            model = RandomForestRegressor()
            model.fit(times_, x_data_temp_filter)
            x_data_temp_corrected = model.predict(np.arange(0, len(x_data_temp), 1).reshape(-1, 1))

            model = RandomForestRegressor()
            model.fit(times_, y_data_temp_filter)
            y_data_temp_corrected = model.predict(np.arange(0, len(x_data_temp), 1).reshape(-1, 1))

            model = RandomForestRegressor()
            model.fit(times_, z_data_temp_filter)
            z_data_temp_corrected = model.predict(np.arange(0, len(x_data_temp), 1).reshape(-1, 1))

            data_copy['pt{}_X'.format(i)] = x_data_temp_corrected
            data_copy['pt{}_Y'.format(i)] = y_data_temp_corrected
            data_copy['pt{}_Z'.format(i)] = z_data_temp_corrected

        return data_copy

    def import_data(self):
        directory, _ = QFileDialog.getOpenFileName(filter="CSV Files (*.csv)")

        if directory:
            self.data_path.setText(directory)
            self.data = self.process_data(pd.read_csv(directory))
            self.data.dropna(inplace=True)
            self.data = self.data.to_numpy()

            self.euler_angles_order.setEnabled(True)
            self.left_group.setEnabled(True)
            self.plot_data_left()

            self.right_group.setEnabled(True)
            self.plot_data_right()

            self.finish_button.setEnabled(True)
    
    def calCulate_InverseKinematics(self):
        alpha_values = []
        beta_values = []
        gamma_values = []

        rotation_angle = self.euler_angles_order.currentText()

        for i in range(len(self.data)):
            points_3d = []

            for j in range(4):
                cordinate_point = [self.data[i][j*3], self.data[i][j*3+1], self.data[i][j*3+2]]
                points_3d.append(cordinate_point)
        
            points_3d = np.array(points_3d)
        
            # Get the plane from three points
            vector_A = points_3d[3] - points_3d[2]
            vector_B = points_3d[1] - points_3d[0]

            vector_A = vector_A/np.linalg.norm(vector_A)
            vector_B = vector_B/np.linalg.norm(vector_B)
            normal_to_plane = np.cross(vector_A, vector_B)

            alpha_rad, beta_rad, gamma_rad = model_analytical(rotation_angle, [vector_A, vector_B, normal_to_plane])

            alpha_values.append(alpha_rad)
            beta_values.append(beta_rad)
            gamma_values.append(gamma_rad)

        return (alpha_values, beta_values, gamma_values)
        
    def createLeftGroup(self):
        """
        Creates the left group with a combo box and a VTK rendering widget.
        """
        self.left_group = QGroupBox("A")
        self.left_group.setFont(QFont('Times', 8))

        layout = QVBoxLayout()

        self.point_num = QComboBox()
        self.point_num.addItems(["Point 1", "Point 2", "Point 3", "Point 4"])
        self.point_num.setFont(QFont('Times', 7))
        self.point_num.currentIndexChanged.connect(self.plot_data_left)
        layout.addWidget(self.point_num)

        # Initialize VTK Widget
        self.vtkWidget_l = QVTKRenderWindowInteractor(self)
        self.ren_l = vtk.vtkRenderer()
        self.vtkWidget_l.GetRenderWindow().AddRenderer(self.ren_l)
        self.ren_l.ResetCamera()
        layout.addWidget(self.vtkWidget_l)

        self.left_group.setEnabled(False)
        self.left_group.setLayout(layout)
    
    def createRightGroup(self):
        """
        Creates the right group with three VTK rendering widgets for the Roll, Pitch, and Yaw angle plots.
        """
        self.right_group = QGroupBox("B")
        self.right_group.setFont(QFont('Times', 8))

        layout = QVBoxLayout()
        splitter = QSplitter(Qt.Vertical)

        # Create context views for each plot
        self.vtkWidget_r_1 = QVTKRenderWindowInteractor(self)
        self.vtkWidget_r_1.Initialize()
        self.context_view_1 = vtk.vtkContextView()
        self.context_view_1.SetRenderWindow(self.vtkWidget_r_1.GetRenderWindow())
        self.chart_r_1 = vtk.vtkChartXY()
        self.context_view_1.GetScene().AddItem(self.chart_r_1)
        splitter.addWidget(self.vtkWidget_r_1)

        self.vtkWidget_r_2 = QVTKRenderWindowInteractor(self)
        self.vtkWidget_r_2.Initialize()
        self.context_view_2 = vtk.vtkContextView()
        self.context_view_2.SetRenderWindow(self.vtkWidget_r_2.GetRenderWindow())
        self.chart_r_2 = vtk.vtkChartXY()
        self.context_view_2.GetScene().AddItem(self.chart_r_2)
        splitter.addWidget(self.vtkWidget_r_2)

        self.vtkWidget_r_3 = QVTKRenderWindowInteractor(self)
        self.vtkWidget_r_3.Initialize()
        self.context_view_3 = vtk.vtkContextView()
        self.context_view_3.SetRenderWindow(self.vtkWidget_r_3.GetRenderWindow())
        self.chart_r_3 = vtk.vtkChartXY()
        self.context_view_3.GetScene().AddItem(self.chart_r_3)
        splitter.addWidget(self.vtkWidget_r_3)

        layout.addWidget(splitter)
        self.right_group.setLayout(layout)
        self.right_group.setEnabled(False)

    def plot_data_left(self):
        """
        Updates the left VTK widget with a scatter plot of the selected data point.
        Ensures the view is auto-scaled to resemble a Plotly 3D scatter plot.
        """

        # Remove previous scatter actor if it exists
        if hasattr(self, 'scatter_actor_left') and self.scatter_actor_left:
            self.ren_l.RemoveActor(self.scatter_actor_left)

        # Extract data points based on selected point index
        num_point = int(self.point_num.currentIndex())
        x_data = np.array(self.data[:, num_point*3])
        y_data = np.array(self.data[:, num_point*3 + 1])
        z_data = np.array(self.data[:, num_point*3 + 2])

        # Convert points to VTK format
        vtk_points = vtk.vtkPoints()
        for x, y, z in zip(x_data, y_data, z_data):
            vtk_points.InsertNextPoint(x, y, z)

        # Create polydata object
        polydata = vtk.vtkPolyData()
        polydata.SetPoints(vtk_points)

        # Create a sphere glyph for scatter plot points
        sphere_source = vtk.vtkSphereSource()
        sphere_source.SetRadius(0.15)  # Marker size
        sphere_source.SetPhiResolution(20)
        sphere_source.SetThetaResolution(20)

        glyph = vtk.vtkGlyph3D()
        glyph.SetInputData(polydata)
        glyph.SetSourceConnection(sphere_source.GetOutputPort())
        glyph.SetScaleModeToDataScalingOff()  # Keep uniform size

        # Mapper and Actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(glyph.GetOutputPort())

        self.scatter_actor_left = vtk.vtkActor()
        self.scatter_actor_left.SetMapper(mapper)
        self.scatter_actor_left.GetProperty().SetColor(0.2, 0.6, 1.0)  # Light blue color

        # Add new scatter plot
        self.ren_l.AddActor(self.scatter_actor_left)

        # --- Normalize Axis Scaling to Mimic Plotly ---
        bounds = vtk_points.GetBounds()
        x_min, x_max = bounds[0], bounds[1]
        y_min, y_max = bounds[2], bounds[3]
        z_min, z_max = bounds[4], bounds[5]

        # Compute the center and maximum range
        center_x = (x_min + x_max) / 2.0
        center_y = (y_min + y_max) / 2.0
        center_z = (z_min + z_max) / 2.0

        max_range = max(x_max - x_min, y_max - y_min, z_max - z_min) / 2.0  # Half of the largest dimension

        # Set up cubic bounds for better aspect ratio
        self.ren_l.GetActiveCamera().SetFocalPoint(center_x, center_y, center_z)
        self.ren_l.GetActiveCamera().SetPosition(center_x + max_range, center_y + max_range, center_z + max_range)
        self.ren_l.GetActiveCamera().SetViewUp(0, 0, 1)  # Keep Z-axis upward
        self.ren_l.ResetCameraClippingRange()

        # --- Keep white background ---
        self.ren_l.SetBackground(1.0, 1.0, 1.0)  # White background

        # Adjust Camera & Render
        self.ren_l.ResetCamera()
        self.vtkWidget_l.GetRenderWindow().Render()

    def plot_data_right(self):
        """
        Updates the right VTK widgets with line plots for Roll (α), Pitch (β), and Yaw (γ) angles.
        """
        # Retrieve calculated inverse kinematics values
        alpha_values, beta_values, gamma_values = self.calCulate_InverseKinematics()

        def update_chart(chart, data, title, color):
            """
            Updates a VTK chart with new data.
            :param chart: vtkChartXY object
            :param data: List or numpy array of values
            :param title: Title of the plot
            :param color: (R, G, B) tuple in float range [0,1]
            """
            table = vtk.vtkTable()

            arrX = vtk.vtkFloatArray()
            arrX.SetName("Index")
            arrY = vtk.vtkFloatArray()
            arrY.SetName("Value")

            # Ensure data is a 1D array
            data = np.array(data).flatten()

            # 🚨 Clear existing plots before adding new data
            chart.ClearPlots()

            # Create linspace for X values
            x_values = np.linspace(0, len(data) - 1, len(data))

            for x, value in zip(x_values, data):
                arrX.InsertNextValue(float(x))
                arrY.InsertNextValue(float(value))

            table.AddColumn(arrX)
            table.AddColumn(arrY)

            line_plot = chart.AddPlot(vtk.vtkChart.LINE)
            line_plot.SetInputData(table, 0, 1)
            line_plot.SetColorF(color[0], color[1], color[2])
            line_plot.SetWidth(2.0)

            chart.SetTitle(title)

        # Update each chart with new data
        update_chart(self.chart_r_1, alpha_values, "Pitching Angle", (1, 0, 0))  # Red
        update_chart(self.chart_r_2, beta_values, "Pitch Angle", (0, 1, 0))  # Green
        update_chart(self.chart_r_3, gamma_values, "Flapping Angle", (0, 0, 1))  # Blue

        # Render updated charts
        self.vtkWidget_r_1.GetRenderWindow().Render()
        self.vtkWidget_r_2.GetRenderWindow().Render()
        self.vtkWidget_r_3.GetRenderWindow().Render()
    
    def finish_button_fun(self):
        self.inv_result = (self.calCulate_InverseKinematics(), self.euler_angles_order.currentText())

        self.angle_data.emit(self.inv_result)
        self.close()