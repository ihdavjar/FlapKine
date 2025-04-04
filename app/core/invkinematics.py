import numpy as np
import pandas as pd
import qtawesome as qta
import vtk
from scipy.signal import savgol_filter
from sklearn.ensemble import RandomForestRegressor
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.vtkRenderingContext2D import vtkTextProperty

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (
    QComboBox, QFileDialog, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QPushButton, QSplitter, QVBoxLayout, QWidget
)

from app.widgets.menu_bar import MenuBar
from src.core.inverse_kinematics.analytical_methods import model_analytical


class InvKineWindow(QMainWindow):
    """
    InvKineWindow Class
    ===================

    This class defines the main GUI window for the FlapKine Inverse Kinematics application.

    It enables importing 3D coordinate data, visualizing it, and computing inverse kinematics angles
    (Roll, Pitch, Yaw) based on selected Euler angle sequences.

    Attributes
    ----------
    angle_data : pyqtSignal
        Signal emitted when inverse kinematics results are calculated.

    menu_bar : MenuBar
        Custom menu bar for handling file and application actions.

    data_path : QLineEdit
        Input field to specify or display the path of the imported data file.

    euler_angles_order : QComboBox
        Dropdown for selecting Euler angle sequences (e.g., XYZ, ZYX, etc.).

    finish_button : QPushButton
        Button to finalize processing and emit the results.

    left_group : QGroupBox
        Contains the 3D scatter plot visualization components.

    right_group : QGroupBox
        Contains the line plots for Roll (α), Pitch (β), and Yaw (γ) angles.

    data : np.ndarray
        The cleaned and filtered 3D point data imported from CSV.

    inv_result : tuple
        Tuple of calculated angles and selected Euler sequence.

    Methods
    -------
    __init__():
        Constructor that initializes all UI elements, signals, and layout.

    initUI() -> QVBoxLayout:
        Constructs the main layout of the application including widgets and plots.

    createImportWidget() -> QWidget:
        Builds the "Import Data" section including file path and Euler angle selection.

    createEulerAngleSelection() -> QWidget:
        Returns a widget with a dropdown for choosing the Euler angle convention.

    createGraphGroup() -> QGroupBox:
        Assembles the left and right graph groups into one visualization section.

    process_data(data: pd.DataFrame) -> pd.DataFrame:
        Applies filtering (e.g., Savitzky-Golay) and machine learning corrections
        (e.g., Random Forest) to raw input data.

    import_data():
        Handles CSV file selection and invokes data processing.

    calCulate_InverseKinematics() -> tuple[list, list, list]:
        Computes the Roll (α), Pitch (β), and Yaw (γ) angles from 3D data and Euler sequence.

    createLeftGroup() -> QGroupBox:
        Initializes the left-side UI group for selecting points and rendering 3D plots using VTK.

    createRightGroup() -> QGroupBox:
        Initializes the right-side UI group with line plots for the inverse kinematics angles.

    plot_data_left():
        Renders a 3D scatter plot of the current data selection in the left VTK widget.

    plot_data_right():
        Plots α, β, γ angle variations using line charts in the right VTK widgets.

    finish_button_fun():
        Emits `angle_data` signal with results and closes the window.
    """

    angle_data = pyqtSignal(tuple)

    def __init__(self):
        """
        Initializes the InvKineWindow class.

        Sets up the main window properties, including title, size, and icon. 
        Initializes the custom menu bar and connects its actions (exit, minimize, maximize, restore).
        Also sets up the central widget and layout for the application's main interface.

        Components Initialized:
            - Window title: "Inverse Kinematics"
            - Window size: 1200x800
            - Window icon: Robot icon using QtAwesome
            - Menu bar: Custom `MenuBar` instance with connected actions
            - Main layout: Set from `initUI()` method

        """
        super(InvKineWindow, self).__init__()

        self.setWindowTitle("Inverse Kinematics")

        self.resize(1200, 800)

        self.setWindowIcon(QIcon(qta.icon("mdi.robot", color="black")))

        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)

        self.menu_bar.connect_actions({
            'exit': self.close,
            'minimize': self.showMinimized,
            'maximize': self.showMaximized,
            'restore': self.showNormal,
        })
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = self.initUI()
        main_widget.setLayout(main_layout)
    
    def initUI(self)-> QVBoxLayout:
        """
        Sets up the main UI layout for the inverse kinematics window.

        Constructs and arranges the primary user interface elements vertically:
            - Import Widget: Includes file path input and import button.
            - Graph Visualization Group: Contains 3D scatter plot and angle plot visualizations.
            - Finish Button: Triggers finalization of data processing and emits results.

        The finish button is initially disabled and is activated after valid data is imported.

        Returns:
            QVBoxLayout: The main vertical layout containing all primary UI components.
        """
        main_layout = QVBoxLayout(self)

        # Import Widget
        import_widget = self.createImportWidget()
        main_layout.addWidget(import_widget)

        # Graph Visualization
        graph_group = self.createGraphGroup()
        main_layout.addWidget(graph_group)

        # Finish Button
        self.finish_button = QPushButton("Finish")
        self.finish_button.setFont(QFont('Times', 8))
        self.finish_button.clicked.connect(self.finish_button_fun)
        self.finish_button.setEnabled(False)
        main_layout.addWidget(self.finish_button)

        return main_layout

    def createImportWidget(self)->QWidget:
        """
        Creates the 'Import Data' UI section.

        This widget provides functionality for importing external CSV data files.
        It includes:
            - A label indicating the section purpose.
            - A text input field for specifying the path to the data file.
            - An 'Import Data' button to load and process the file.
            - A dropdown for selecting the Euler angle rotation order.

        When the import button is clicked, it triggers the data import and processing pipeline.

        Returns:
            QWidget: A horizontal layout widget containing file import controls and Euler angle selection.
        """
        import_widget = QWidget()
        import_layout = QHBoxLayout(import_widget)
        import_layout.setContentsMargins(0, 0, 0, 0)
        import_layout.setSpacing(0)

        import_label = QLabel("Import Data")
        import_label.setFont(QFont('Times', 8))
        import_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        import_label.setStyleSheet("color: #333;")

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
        import_layout.addWidget(self.createEulerAngleSelection())

        import_widget.setLayout(import_layout)
        return import_widget

    def createEulerAngleSelection(self)->QWidget:
        """
        Creates the Euler Angle Sequence selection widget.

        This dropdown allows the user to select a specific Euler rotation sequence
        to be used in inverse kinematics calculations. Common intrinsic and extrinsic
        sequences are provided in the options.

        Upon changing the selection, the corresponding angle plots are updated 
        to reflect the new rotation order.

        Returns:
            QWidget: A widget containing a label and a QComboBox for Euler angle sequence selection.
        """
        order_widget = QWidget()
        order_layout = QHBoxLayout()

        order_label = QLabel("Euler Angle Sequence:")
        order_label.setFont(QFont('Times', 8))

        self.euler_angles_order = QComboBox()
        self.euler_angles_order.addItems(
            ["ZXZ", "XYX", "YZY", "ZYZ", "XZX", "YXY", "ZXY", "YXZ", "XZY", "YZX", "ZYX", "XYZ"]
        )
        self.euler_angles_order.setFont(QFont('Times', 8))
        self.euler_angles_order.currentIndexChanged.connect(self.plot_data_right)
        self.euler_angles_order.setEnabled(False)

        order_layout.addWidget(order_label)
        order_layout.addWidget(self.euler_angles_order)
        order_widget.setLayout(order_layout)
        return order_widget

    def createGraphGroup(self)->QGroupBox:
        """
        Creates the main visualization group for the application.

        This method sets up the grouped section of the GUI that displays both:
        - The 3D scatter plot (left group) for visualizing imported data points.
        - The angle plots (right group) for displaying Roll, Pitch, and Yaw over time.

        The layout is organized using a horizontal splitter to allow dynamic resizing
        of both visual areas side-by-side.

        Returns:
            QGroupBox: A group box containing the combined visualization components.
        """

        graph_group = QGroupBox("Visualisation")
        graph_group.setFont(QFont('Times', 9))
        graph_layout = QHBoxLayout()

        main_splitter = QSplitter(Qt.Horizontal)
        self.createLeftGroup()
        self.createRightGroup()

        main_splitter.addWidget(self.left_group)
        main_splitter.addWidget(self.right_group)
        main_splitter.setSizes([400, 400])

        graph_layout.addWidget(main_splitter)
        graph_group.setLayout(graph_layout)
        return graph_group
    
    @staticmethod
    def process_data(data: pd.DataFrame) -> pd.DataFrame:
        """
        Applies filtering and correction to raw 3D point data using Savitzky-Golay filter
        and Random Forest regression.

        For each of the four tracked points (pt1 to pt4), this method:
            - Smooths the X, Y, Z coordinates using Savitzky-Golay filtering.
            - Subsamples the smoothed data for training.
            - Trains individual Random Forest models to predict each coordinate over time.
            - Applies the trained models to generate corrected X, Y, Z trajectories.

        Args:
            data (pd.DataFrame): Raw input data with point coordinates labeled as 'pt{n}_X', 'pt{n}_Y', 'pt{n}_Z'.

        Returns:
            pd.DataFrame: A copy of the input data with corrected X, Y, and Z values for each point.
        """
        data_copy = data.copy()

        for i in range(1, 5):
            x_data_temp = data['pt{}_X'.format(i)]
            y_data_temp = data['pt{}_Y'.format(i)]
            z_data_temp = data['pt{}_Z'.format(i)]

            x_data_temp = np.array(x_data_temp)
            y_data_temp = np.array(y_data_temp)
            z_data_temp = np.array(z_data_temp)
            x_data_temp_filter = savgol_filter(x_data_temp, 51, 3)
            y_data_temp_filter = savgol_filter(y_data_temp, 51, 3)
            z_data_temp_filter = savgol_filter(z_data_temp, 51, 3)
            temp_data = pd.DataFrame({
                'time': np.arange(0, len(x_data_temp), 1),
                'x': x_data_temp_filter,
                'y': y_data_temp_filter,
                'z': z_data_temp_filter,
            })
            temp_data.dropna(inplace=True)
            times_ = np.array(temp_data['time']).reshape(-1, 1)[::5]
            x_data_temp_filter = np.array(temp_data['x']).reshape(-1)[::5]
            y_data_temp_filter = np.array(temp_data['y']).reshape(-1)[::5]
            z_data_temp_filter = np.array(temp_data['z']).reshape(-1)[::5]
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

    def import_data(self)-> None:
        """
        Handles the process of importing and preparing CSV data for inverse kinematics analysis.

        This method:
            - Opens a file dialog for the user to select a CSV file.
            - Updates the data path in the input field.
            - Processes the imported data using filtering and correction.
            - Converts the cleaned data into a NumPy array.
            - Enables UI components related to angle selection and visualization.
            - Triggers updates for both 3D point and angle visualization.
            - Activates the "Finish" button to allow finalizing the process.
        """
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

    def calCulate_InverseKinematics(self)-> tuple[list, list, list]:
        """
        Calculates the inverse kinematics angles: α (alpha), β (beta), and γ (gamma).

        This method:
            - Iterates through each time frame of the imported 3D point data.
            - Extracts the 3D coordinates of 4 points for each frame.
            - Computes two directional vectors based on those points.
            - Calculates the normal vector to the plane formed by these vectors.
            - Uses the selected Euler angle sequence to analytically compute the angles.

        Returns:
            tuple: A tuple containing three lists of calculated angles in radians:
                - alpha_values (list): α angles.
                - beta_values (list): β angles.
                - gamma_values (list): γ angles.
        """

        alpha_values = []
        beta_values = []
        gamma_values = []

        rotation_angle = self.euler_angles_order.currentText()

        for i in range(len(self.data)):
            points_3d = []

            for j in range(4):
                cordinate_point = [
                    self.data[i][j * 3],
                    self.data[i][j * 3 + 1],
                    self.data[i][j * 3 + 2],
                ]
                points_3d.append(cordinate_point)

            points_3d = np.array(points_3d)

            # Get the plane from three points
            vector_A = points_3d[3] - points_3d[2]
            vector_B = points_3d[1] - points_3d[0]

            vector_A = vector_A / np.linalg.norm(vector_A)
            vector_B = vector_B / np.linalg.norm(vector_B)
            normal_to_plane = np.cross(vector_A, vector_B)

            alpha_rad, beta_rad, gamma_rad = model_analytical(
                rotation_angle, [vector_A, vector_B, normal_to_plane]
            )

            alpha_values.append(alpha_rad)
            beta_values.append(beta_rad)
            gamma_values.append(gamma_rad)

        return (alpha_values, beta_values, gamma_values)

    def createLeftGroup(self)-> None:
        """
        Creates the left group for 3D point visualization.

        This section of the UI:
            - Provides a dropdown (QComboBox) to select between 4 tracked 3D points.
            - Initializes a VTK rendering widget (QVTKRenderWindowInteractor) to display
            the trajectory of the selected point in 3D space.

        Note:
            This visualization helps in analyzing the spatial motion of each point
            before calculating α (alpha), β (beta), and γ (gamma) angles.

        Sets:
            self.left_group (QGroupBox): Group box containing the dropdown and VTK widget.
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

    def createRightGroup(self)-> None:
        """
        Creates the right group for visualizing the inverse kinematics angles.

        This UI section sets up three vertically stacked VTK context views to display:
            - α (alpha) angle over time
            - β (beta) angle over time
            - γ (gamma) angle over time

        Each subplot is rendered using vtkChartXY within a QVTKRenderWindowInteractor.
        These charts provide real-time feedback of angle calculations derived from the
        selected Euler sequence and 3D point data.

        Sets:
            self.right_group (QGroupBox): Group box containing the three VTK angle plots.
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

    def plot_data_left(self)-> None:
        """
        Plots the 3D trajectory of the selected point in the left VTK view.

        This method:
            - Extracts the x, y, z coordinates of the selected point across all time steps.
            - Renders a scatter plot using spherical glyphs in a VTK renderer.
            - Dynamically adjusts camera position and axis bounds to mimic the cubic aspect
            of Plotly-style 3D plots for visual consistency and better spatial perception.

        The plotted data provides a temporal spatial reference for one of the tracked points
        used in inverse kinematics analysis.

        Side Effects:
            - Updates `self.scatter_actor_left` with new point data.
            - Adjusts camera and clipping ranges.
            - Triggers a re-render of the left VTK widget.
        """

        # Remove previous scatter actor if it exists
        if hasattr(self, 'scatter_actor_left') and self.scatter_actor_left:
            self.ren_l.RemoveActor(self.scatter_actor_left)

        # Extract data points based on selected point index
        num_point = int(self.point_num.currentIndex())
        x_data = np.array(self.data[:, num_point * 3])
        y_data = np.array(self.data[:, num_point * 3 + 1])
        z_data = np.array(self.data[:, num_point * 3 + 2])

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

        max_range = (
            max(x_max - x_min, y_max - y_min, z_max - z_min) / 2.0
        )  # Half of the largest dimension

        # Set up cubic bounds for better aspect ratio
        self.ren_l.GetActiveCamera().SetFocalPoint(center_x, center_y, center_z)
        self.ren_l.GetActiveCamera().SetPosition(
            center_x + max_range, center_y + max_range, center_z + max_range
        )
        self.ren_l.GetActiveCamera().SetViewUp(0, 0, 1)  # Keep Z-axis upward
        self.ren_l.ResetCameraClippingRange()

        # --- Keep white background ---
        self.ren_l.SetBackground(1.0, 1.0, 1.0)  # White background

        # Adjust Camera & Render
        self.ren_l.ResetCamera()
        self.vtkWidget_l.GetRenderWindow().Render()

    def plot_data_right(self):
        """
        Plots the inverse kinematics angles (α, β, γ) on three VTK line charts.

        This method:
            - Computes the Euler angles (alpha, beta, gamma) using the selected sequence.
            - Updates three vertically stacked VTK charts for visualizing these angles over time.
            - Each chart is color-coded:
                - α (alpha) in red
                - β (beta) in green
                - γ (gamma) in blue
            - Applies styling for axes and titles to ensure clarity and visual consistency.

        These plots help visualize the orientation evolution of the tracked plane using the selected Euler angle convention.
        
        Side Effects:
            - Updates `chart_r_1`, `chart_r_2`, `chart_r_3` with fresh plot data.
            - Triggers a re-render of all three right-side VTK widgets.
        """

        # Retrieve calculated inverse kinematics values
        alpha_values, beta_values, gamma_values = self.calCulate_InverseKinematics()

        def update_chart(chart, data, title, color)-> None:
            """
            Updates a VTK chart with new data.
            :param chart: vtkChartXY object
            :param data: List or numpy array of values
            :param title: Title of the plot
            :param color: (R, G, B) tuple in float range [0,1]
            """
            table = vtk.vtkTable()

            arr_x = vtk.vtkFloatArray()
            arr_x.SetName("Index")
            arr_y = vtk.vtkFloatArray()
            arr_y.SetName("Value")

            # Ensure data is a 1D array
            data = np.array(data).flatten()

            # 🚨 Clear existing plots before adding new data
            chart.ClearPlots()

            # Create linspace for X values
            x_values = np.linspace(0, len(data) - 1, len(data))

            for x, value in zip(x_values, data):
                arr_x.InsertNextValue(float(x))
                arr_y.InsertNextValue(float(value))

            table.AddColumn(arr_x)
            table.AddColumn(arr_y)

            line_plot = chart.AddPlot(vtk.vtkChart.LINE)
            line_plot.SetInputData(table, 0, 1)
            line_plot.SetColorF(color[0], color[1], color[2])
            line_plot.SetWidth(2.0)

            chart.GetAxis(vtk.vtkAxis.BOTTOM).SetTitle("Time")
            chart.GetAxis(vtk.vtkAxis.LEFT).SetTitle("Angle (deg)")

            text_prop = vtkTextProperty()
            text_prop.SetFontFamilyToArial()
            text_prop.BoldOn()
            text_prop.SetFontSize(16)
            text_prop.SetColor(color[0], color[1], color[2])

            chart.SetTitle(title)
            chart.GetTitleProperties().ShallowCopy(text_prop)

        # Update each chart with new data
        update_chart(self.chart_r_1, alpha_values, "alpha", (1, 0, 0))  # Red
        update_chart(self.chart_r_2, beta_values, "beta", (0, 1, 0))  # Green
        update_chart(self.chart_r_3, gamma_values, "gamma", (0, 0, 1))  # Blue

        # Render updated charts
        self.vtkWidget_r_1.GetRenderWindow().Render()
        self.vtkWidget_r_2.GetRenderWindow().Render()
        self.vtkWidget_r_3.GetRenderWindow().Render()

    def finish_button_fun(self):
        """
        Finalizes the inverse kinematics computation and emits the results.

        This method:
            - Calculates the Euler angles (α, β, γ) using the selected rotation sequence.
            - Packages the result along with the selected Euler angle convention.
            - Emits the data via the `angle_data` signal for downstream processing or visualization.
            - Closes the current window upon completion.

        Side Effects:
            - Updates `self.inv_result` with computed angles and selected sequence.
            - Emits `angle_data` signal carrying the result tuple.
            - Closes the active dialog/UI window.
        """
        self.inv_result = (
            self.calCulate_InverseKinematics(),
            self.euler_angles_order.currentText(),
        )

        self.angle_data.emit(self.inv_result)
        self.close()