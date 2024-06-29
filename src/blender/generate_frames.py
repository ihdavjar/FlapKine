import os
import bpy
from src.config.config import config

# Set the output directory where rendered images will be saved
output_dir = os.path.join(os.getcwd(), config['VideoRender']['OutputPath'])  # Output directory

# List of STL file paths
stl_files_dir = os.path.join(os.getcwd(), config['VideoRender']['STLPath'])  # STL files directory


# Set rendering parameters
bpy.context.scene.render.image_settings.file_format = config['VideoRender']['FrameFormat']  # Output image format
bpy.context.scene.render.resolution_x = config['VideoRender']['resolution_x']  # Output resolution X
bpy.context.scene.render.resolution_y = config['VideoRender']['resolution_y']  # Output resolution Y
bpy.context.scene.render.film_transparent = config['VideoRender']['film_transparent']  # Enable transparent background

# Set the camera parameters
bpy.context.scene.camera.location = (30, 0, 0)  # Camera location
bpy.context.scene.camera.rotation_euler = (1.572, 0, 1.57)  # Camera rotation

# Set the light parameters
bpy.data.objects['Light'].location = (4, 0, 4)  # Light location
bpy.data.objects['Light'].data.energy = 1000  # Light energy

## Add a cube
bpy.ops.mesh.primitive_cube_add(size=0.5)  # Add a cube


# by.data.objects['Cube'].scale = (0.1, 0.1, 0.1)  # Scale the default cube


# Remove the default cube
bpy.data.objects.remove(bpy.data.objects['Cube'], do_unlink=True)


# Set the scene frame rate
bpy.context.scene.render.fps = 24


# Ensure output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

stl_files = sorted([f for f in os.listdir(stl_files_dir) if f.endswith('.stl')])

# Loop through each STL file
for i in range(len(stl_files)-1):

    stl_file_name = f"ellipse_{i}.stl"
    
    # Set file names
    stl_file_path = os.path.join(stl_files_dir, stl_file_name)

    # Import STL file as a new object
    bpy.ops.import_mesh.stl(filepath=stl_file_path)
    
    # Select the imported object
    imported_object = bpy.context.selected_objects[0]

    # Define the output image filename based on the STL file name
    output_filename = f'frame_{i + 1}.png'
    output_path = os.path.join(output_dir, output_filename)


    # Render the image
    bpy.context.scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)
    
    # Delete the imported object to clear the scene for the next iteration
    bpy.ops.object.select_all(action='DESELECT')
    imported_object.select_set(True)
    bpy.ops.object.delete()

print("Rendering complete")