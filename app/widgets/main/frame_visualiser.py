import os
import json
import numpy as np
import vtk
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel, QPushButton, QGroupBox
)
from PyQt5.QtGui import QFont
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import qtawesome as qta
from src.core.transforms.vtk_transform import *


class Visualizer3DWidget(QWidget):
    def __init__(self, scene_data, project_folder, angles, parent=None):
        super().__init__(parent)

        self.scene_data = scene_data
        self.project_folder = project_folder
        self.angles = angles
        self.playing = False

        self.init_ui()

    def init_ui(self):
        primary_color = self.palette().color(self.foregroundRole()).name()


        layout = QVBoxLayout(self)
        control_layout = QHBoxLayout()

        self.slider_label = QLabel("Frame: 0")
        self.slider_label.setFont(QFont('Arial', 8, QFont.Weight.Bold))
        self.slider_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slider_label.setStyleSheet("color: #333;")

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(self.angles) - 1)
        self.slider.setValue(0)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(max(1, len(self.angles) // 10))
        self.slider.valueChanged.connect(self.on_slider_value_changed)
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: none;
                background: #ddd;
                height: 8px;
                border-radius: 4px;
            }

            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00aaff, stop:1 #005a9e);
                border: 2px solid #005a9e;
                width: 18px;
                height: 18px;
                margin: -7px 0;
                border-radius: 9px;
            }

            QSlider::handle:horizontal:hover {
                background: #005a9e;
            }

            QSlider::sub-page:horizontal {
                background: #00aaff;
                border-radius: 4px;
            }

            QSlider::add-page:horizontal {
                background: #ccc;
                border-radius: 4px;
            }
        """)

        self.play_button = QPushButton()
        self.play_button.setIcon(qta.icon("mdi.play", color=primary_color))
        self.play_button.clicked.connect(self.toggle_play)

        self.next_button = QPushButton()
        self.next_button.setIcon(qta.icon("mdi.skip-next", color=primary_color))
        self.next_button.clicked.connect(lambda: self.slider.setValue(self.slider.value() + 1))

        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.next_button)
        control_layout.addWidget(self.slider)
        control_layout.addWidget(self.slider_label)

        self.vtkWidget = QVTKRenderWindowInteractor(self)
        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.vtkWidget.setStyleSheet("background-color: #fafafa; border: 1px solid #bbb; border-radius: 10px;")
        
        layout.addLayout(control_layout)
        layout.addWidget(self.vtkWidget)

        self.setLayout(layout)

        self.setup_visualization()

    def setup_visualization(self):
        with open(os.path.join(self.project_folder, 'config.json')) as f:
            config = json.load(f)

        reflect = [config['Reflect'] == "XY", config['Reflect'] == "YZ", config['Reflect'] == "XZ"]
        self.reflect = reflect

        mesh = self.scene_data.save_stl(-1, reflect_xy=reflect[0], reflect_yz=reflect[1], reflect_xz=reflect[2])
        poly_data = self.stl_mesh_to_vtk(mesh)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(poly_data)

        self.actor = vtk.vtkActor()
        self.actor.SetMapper(mapper)
        self.actor.GetProperty().SetColor(0.5, 0.7, 1)
        self.actor.GetProperty().SetOpacity(0.7)

        self.ren.SetBackground(0.95, 0.95, 0.95)
        self.ren.AddActor(self.actor)
        self.ren.AddActor(self.create_axes_actor(poly_data))

        self.body_axes = []
        for sprite in self.scene_data.objects:
            self.body_axes.append(self.create_body_axes(sprite))

        for axes in self.body_axes:
            self.ren.AddActor(axes)

        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        self.iren.Initialize()
        self.ren.ResetCamera()

    def create_axes_actor(self, poly_data):
        bounds = poly_data.GetBounds()
        max_length = max(bounds[1]-bounds[0], bounds[3]-bounds[2], bounds[5]-bounds[4])
        axes = vtk.vtkAxesActor()
        axes.SetTotalLength(max_length * 0.1, max_length * 0.1, max_length * 0.1)
        axes.SetShaftType(0)
        axes.SetAxisLabels(1)
        axes.SetXAxisLabelText("X")
        axes.SetYAxisLabelText("Y")
        axes.SetZAxisLabelText("Z")
        for caption in [axes.GetXAxisCaptionActor2D(), axes.GetYAxisCaptionActor2D(), axes.GetZAxisCaptionActor2D()]:
            caption.GetCaptionTextProperty().SetColor(0, 0, 0)
        return axes

    def create_body_axes(self, sprite):
        max_length = max(self.actor.GetBounds()[1::2]) * 0.05
        axes = vtk.vtkAxesActor()
        axes.SetTotalLength(max_length, max_length, max_length)
        axes.SetShaftType(0)
        axes.SetAxisLabels(1)
        axes.SetXAxisLabelText("A")
        axes.SetYAxisLabelText("B")
        axes.SetZAxisLabelText("C")
        for caption in [axes.GetXAxisCaptionActor2D(), axes.GetYAxisCaptionActor2D(), axes.GetZAxisCaptionActor2D()]:
            caption.GetCaptionTextProperty().SetColor(0, 0, 0)

        angles = sprite.frame_orientation
        position = sprite.frame_origin

        transform = vtk.vtkTransform()
        transform.Translate(position)
        transform.RotateX(np.degrees(angles[0]))
        transform.RotateY(np.degrees(angles[1]))
        transform.RotateZ(np.degrees(angles[2]))
        axes.SetUserTransform(transform)

        return axes

    def toggle_play(self):
        primary_color = self.palette().color(self.foregroundRole()).name()
        self.playing = not self.playing
        self.play_button.setIcon(qta.icon("mdi.pause" if self.playing else "mdi.play", color=primary_color))
        if self.playing:
            self.play_frames()

    def play_frames(self):
        if self.playing:
            next_frame = (self.slider.value() + 1) % len(self.angles)
            self.slider.setValue(next_frame)
            self.on_slider_value_changed()
            QTimer.singleShot(50, self.play_frames)

    def on_slider_value_changed(self):
        index = self.slider.value()
        self.slider_label.setText(f"Frame: {index}")

        for i, sprite in enumerate(self.scene_data.objects):
            angle = sprite.angles[index]
            position = sprite.positions[index]
            axes_pos = sprite.frame_origin

            actor_trans = vtk.vtkTransform()
            actor_trans.PostMultiply()
            actor_trans.Translate(position)

            axes_trans = vtk.vtkTransform()
            axes_trans.PostMultiply()
            axes_trans.Translate(position + axes_pos)

            if hasattr(sprite.object_.rotation_transform, 'type'):
                rot_trans = vtk_rotation(sprite.object_.rotation_transform.type, angle)
                actor_trans.Concatenate(rot_trans)
                axes_trans.Concatenate(rot_trans)

            self.body_axes[i].SetUserTransform(axes_trans)

        self.actor.SetUserTransform(actor_trans)
        self.vtkWidget.GetRenderWindow().Render()

    def stl_mesh_to_vtk(self, stl_mesh):
        """
        Convert an stl.mesh.Mesh (numpy-stl) object to vtkPolyData.
        """
        poly_data = vtk.vtkPolyData()
        points = vtk.vtkPoints()
        cells = vtk.vtkCellArray()

        # Extract unique vertices and create a mapping
        unique_vertices, indices = np.unique(stl_mesh.vectors.reshape(-1, 3), axis=0, return_inverse=True)

        # Insert vertices into vtkPoints
        for vertex in unique_vertices:
            points.InsertNextPoint(vertex[0], vertex[1], vertex[2])

        # Insert faces into vtkCellArray
        for i in range(0, len(indices), 3):
            triangle = vtk.vtkTriangle()
            for j in range(3):
                triangle.GetPointIds().SetId(j, indices[i + j])
            cells.InsertNextCell(triangle)

        # Assign points and cells to polydata
        poly_data.SetPoints(points)
        poly_data.SetPolys(cells)
        return poly_data
