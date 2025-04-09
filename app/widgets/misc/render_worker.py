import os
import json

import bpy
import bmesh
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QThread, pyqtSignal, QMetaObject, Qt, pyqtSlot

from src.utils.utils import create_video_from_frames
from src.core.transforms.vtk_transform import *
        
        
class Worker(QThread):
    """
    Worker Class
    ============

    This class handles background STL processing and frame rendering in Blender for the
    FlapKine application. Executed in a separate thread, it applies camera and lighting
    configurations, processes STL meshes, renders 3D frames, and optionally generates STL files
    and a final video output.

    The class communicates progress updates through a PyQt signal and ensures synchronization
    with the GUI by invoking Blender rendering operations via the main thread.

    Attributes
    ----------
    progress_signal : pyqtSignal
        Signal emitting the rendering progress as a float percentage.

    project_folder : str
        Absolute path to the user's project directory containing config and output folders.

    angles : list
        List of angles (e.g., for animation or keyframes) used for generating frames.

    scene_data_ : SceneData
        Custom scene object that contains geometry and logic for saving STL representations.

    reflect : tuple(bool, bool, bool)
        Tuple of booleans indicating which axes (XY, YZ, XZ) to reflect the STL geometry on.

    stl_files : list
        Internal list of STL files generated or processed during the rendering loop.

    Methods
    -------
    __init__(project_folder, angles, scene_data, reflect, parent=None):
        Initializes the rendering worker with configuration, scene data, and transformation options.

    run():
        Loads the Blender project, configures the scene, loops through STL frames, renders them,
        saves optional STL outputs, and compiles the final video.

    import_and_render(stl_mesh, output_dir, frame_index):
        Imports a single STL mesh into Blender, applies materials, renders a frame,
        and cleans up the object from the scene afterward.
    """
    progress_signal = pyqtSignal(float)

    def __init__(self, project_folder, angles, scene_data, reflect, parent=None):
        """
        Initializes the Worker thread responsible for 3D frame rendering and video compilation.

        This thread handles the automated import of STL frames, applies camera and lighting 
        settings from the project configuration, renders each frame using Blender, 
        optionally saves STL files, and compiles a final video from the rendered images.

        Parameters
        ----------
        project_folder : str
            Absolute path to the project directory, expected to contain the configuration 
            file (`config.json`) and asset subfolders (`data/stl`, `data/images`, etc.).
        
        angles : list of float
            List of joint angles or frame parameters used to generate each STL model.
        
        scene_data : object
            A scene manager or handler object responsible for generating and returning STL 
            meshes from the given angles and reflection flags.
        
        reflect : tuple of bool
            A 3-tuple indicating whether to apply geometric reflection across the 
            XY, YZ, and XZ planes, respectively. Used for symmetrical scene variations.
        
        parent : QObject, optional
            Optional parent object for integration with the Qt object tree.
        """
        super(Worker, self).__init__(parent)
        self.project_folder = project_folder    
        self.angles = angles
        self.scene_data_ = scene_data
        self.reflect = reflect
        self.stl_files = []

    def run(self):
        """
        Executes the rendering workflow asynchronously in a separate thread.

        This method orchestrates the complete rendering pipeline using Blender’s Python API:
        - Loads project configuration from `config.json`, including render format, resolution, 
          camera pose, and lighting parameters.
        - Prepares the Blender scene with specified render and environment settings.
        - Iterates through a sequence of frames generated from input angles:
            - Requests an STL mesh from the scene manager, applying reflection flags.
            - Renders each frame with a defined material (e.g., blue surface).
            - Optionally exports STL files if enabled in the config.
        - Emits real-time progress updates through `progress_signal` for GUI feedback.
        - After rendering all frames, compiles the image sequence into a video using 
          `create_video_from_frames`.

        This method is designed to run in the background to prevent UI freezing during
        long rendering operations.
        """

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
        """
        Imports a single STL mesh into Blender, renders it, and exports the result as an image.

        This method is invoked on the main thread via `QMetaObject.invokeMethod` to comply with 
        Blender’s threading constraints, ensuring that all scene operations are thread-safe.

        Parameters
        ----------
        stl_mesh : numpy-stl STL mesh
            A triangle mesh object representing the 3D geometry of the current frame, 
            typically produced using NumPy-STL or equivalent STL generation logic.
        output_dir : str
            Absolute path to the directory where the rendered image should be saved.
        frame_index : int
            Index of the current frame in the animation sequence; determines output filename 
            (e.g., `frame_1.png`, `frame_2.png`, ...).

        Notes
        -----
        - Creates a temporary Blender object from the STL geometry using `bmesh`.
        - Applies a blue material to the mesh.
        - Renders a still image using Blender's internal renderer and saves it to disk.
        - Cleans up the mesh object post-render to free memory and keep the scene clean.
        """
         
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