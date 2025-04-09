import os
import bpy
import bmesh
import json

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from src.utils.utils import create_video_from_frames
from src.core.transforms.vtk_transform import *


import os
import json
from PyQt5.QtCore import QThread, pyqtSignal, QMetaObject, Qt
import bpy
        
        
class Worker(QThread):
    progress_signal = pyqtSignal(float)

    def __init__(self, project_folder, angles, scene_data, reflect, parent=None):
        super(Worker, self).__init__(parent)
        self.project_folder = project_folder    
        self.angles = angles
        self.scene_data_ = scene_data
        self.reflect = reflect
        self.stl_files = []

    def run(self):
        
        # Load the Blender project
        with open(os.path.join(self.project_folder, 'config.json')) as f:
            config = json.load(f)

        
        # Set rendering parameters
        bpy.context.scene.render.image_settings.file_format = config['VideoRender']['FrameFormat']  # Output image format
        bpy.context.scene.render.resolution_x = config['VideoRender']['resolution_x']  # Output resolution X
        bpy.context.scene.render.resolution_y = config['VideoRender']['resolution_y']  # Output resolution Y
        bpy.context.scene.render.film_transparent = config['VideoRender']['film_transparent']  # Enable transparent background

        # Set the camera parameters
        bpy.context.scene.camera.location = tuple(config['Camera']['location'])  # Camera location
        bpy.context.scene.camera.rotation_euler = tuple(config['Camera']['rotation_euler'])  # Camera rotation

        bpy.context.scene.camera.data.type = 'PERSP'
        bpy.context.scene.camera.data.lens = 140

        # Set the light parameters
        bpy.data.objects['Light'].location = tuple(config['Light']['location'])  # Light location
        bpy.data.objects['Light'].data.energy = config['Light']['energy']  # Light energy

        # Remove the default cube
        if 'Cube' in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects['Cube'], do_unlink=True)

        # Set the scene frame rate
        bpy.context.scene.render.fps = 24  # Frame rate

         # Set the world background color to white
        bpy.context.scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.95, 0.95, 0.95, 1)
        # Create a blue material
        blue_material = bpy.data.materials.new(name="BlueMaterial")
        blue_material.use_nodes = True
        bsdf = blue_material.node_tree.nodes.get('Principled BSDF')
        bsdf.inputs['Base Color'].default_value = (0, 0, 1, 1)  # Blue color
        
        # stl_files_dir = os.path.join(self.project_folder, 'data/stl')
        output_dir = os.path.join(self.project_folder, 'data/images')
        stl_dir = os.path.join(self.project_folder, 'data/stl')

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        if config["STL"]:
            if not os.path.exists(stl_dir):
                os.makedirs(stl_dir)

        # Loop through each STL file
        for i in range(len(self.angles)):
            stl_file = self.scene_data_.save_stl(i, reflect_xy=self.reflect[0], reflect_yz=self.reflect[1], reflect_xz=self.reflect[2])
            
            if config["STL"]:
                stl_file.save(os.path.join(stl_dir, f"stl_mesh_{i}.stl"))
            
            # Import STL file and render in the main thread
            QMetaObject.invokeMethod(self, "import_and_render", Qt.BlockingQueuedConnection,
                                     Q_ARG(object, stl_file), Q_ARG(str, output_dir), Q_ARG(int, i+1))

            self.progress_signal.emit((i + 1)/len(self.angles) * 100)
            
        frames_path = os.path.join(self.project_folder, 'data/images')
        project_name = os.path.basename(self.project_folder)
        video_path = os.path.join(self.project_folder, f"data/videos/{project_name}.mp4")

        create_video_from_frames(frames_path, video_path, frame_rate=20,
                                 width=config['VideoRender']['resolution_x'], height=config['VideoRender']['resolution_y'], libx264=False)

    @pyqtSlot(object, str, int)
    def import_and_render(self, stl_mesh, output_dir, frame_index):
        """ Handle numpy-stl mesh directly instead of file path """
        
        # Create a new Blender mesh and object
        new_mesh = bpy.data.meshes.new("imported_mesh")
        new_object = bpy.data.objects.new("ImportedObject", new_mesh)
        bpy.context.collection.objects.link(new_object)
        
        # Create BMesh to build geometry from numpy-stl mesh
        bm = bmesh.new()
        for face in stl_mesh.vectors:
            verts = [bm.verts.new(v) for v in face]
            bm.faces.new(verts)
        
        bm.to_mesh(new_mesh)
        bm.free()

        # Add material to the object
        blue_material_name = "BlueMaterial"
        if not any(mat.name == blue_material_name for mat in new_mesh.materials):
            # Create the blue material if it doesn't exist
            if blue_material_name not in bpy.data.materials:
                blue_material = bpy.data.materials.new(name=blue_material_name)
                blue_material.use_nodes = True
                bsdf = blue_material.node_tree.nodes.get('Principled BSDF')
                bsdf.inputs['Base Color'].default_value = (0, 0, 1, 1)  # Blue color
            else:
                blue_material = bpy.data.materials.get(blue_material_name)
            
            # Assign the material to the object
            new_mesh.materials.append(blue_material)

        # Set the render output file path and render
        output_filename = f'frame_{frame_index}.png'
        output_path = os.path.join(output_dir, output_filename)
        
        bpy.context.scene.render.filepath = output_path
        bpy.ops.render.render(write_still=True)

        # Clean up the object after rendering
        bpy.ops.object.select_all(action='DESELECT')
        new_object.select_set(True)
        bpy.ops.object.delete()