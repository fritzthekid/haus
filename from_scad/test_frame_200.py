#!/usr/bin/env blender --python
"""
Setup animation and render only frame some for testing
"""

import bpy
import math
import os
from mathutils import Vector

# ========== KONFIGURATION ==========
root_dir = os.path.dirname(os.path.abspath(__file__))
HAUS_COMPLETE = f"{root_dir}/haus_complete_mit_fenstern.blend"
os.makedirs("/tmp/haus_animation", exist_ok=True)
OUTPUT_DIR = "/tmp/haus_animation"

# Farben (RAL zu RGB, normalisiert 0-1)
RAL_9012 = (255/255, 253/255, 230/255, 1.0) # RAL 9012 — Reinraumweiß
COLOR_WAND = RAL_9012 
RAL_3003 = (134/255, 26/255, 34/255, 1.0) # rubin rot
COLOR_FENSTER = RAL_3003 
# Heller Tonziegel (mediterran)
RAL_2001 = (180/255, 90/255, 60/255, 1.0)
COLOR_DACH = RAL_2001 

TEST_FRAME = 216

# Animation
FRAMES = 300
CAMERA_DISTANCE = 40  # Reduced from 150 to make house larger (closer camera)
CAMERA_HEIGHT = 4    # Lowered from 50 to ~170 units from ground

print("="*60)
print(f"TESTING HAUS ANIMATION - FRAME {TEST_FRAME}")
print("="*60)

# Load the complete haus scene
print(f"\nLoading: {HAUS_COMPLETE}")
bpy.ops.wm.open_mainfile(filepath=HAUS_COMPLETE)

# Remove problematic objects (ground plane that might cause black borders)
print("\nCleaning scene...")
for obj in bpy.data.objects:
    if obj.type == 'MESH' and 'plane' in obj.name.lower():
        bpy.data.objects.remove(obj, do_unlink=True)
        print(f"  - Removed: {obj.name}")

# Setup render settings
def setup_render():
    """Render-Einstellungen"""
    print("\nConfiguring render settings...")
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = 'PNG'

    scene.frame_start = 1
    scene.frame_end = FRAMES
    scene.render.fps = 30

    # Cycles Settings
    scene.cycles.samples = 128
    scene.cycles.use_denoising = False

    print(f"  ✓ Render settings configured")

def create_material(name, color, roughness=0.5, metallic=0.0):
    """Material erstellen"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    output = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic

    mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat

def apply_materials():
    """Materialien zuweisen"""
    print("\nApplying materials...")

    mat_wand = create_material("Wand_Gelb", COLOR_WAND, roughness=0.7)
    mat_fenster = create_material("Fenster_Rot", COLOR_FENSTER, roughness=0.3)
    mat_dach = create_material("Dach_Blutorange", COLOR_DACH, roughness=0.8)

    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            obj_name_lower = obj.name.lower()

            # Clear existing materials
            obj.data.materials.clear()

            # Assign material based on object name
            if 'dach' in obj_name_lower:
                obj.data.materials.append(mat_dach)
                print(f"  - {obj.name}: Dach (Orange)")
            elif 'fenster' in obj_name_lower or 'garage_tor' in obj_name_lower or 'garagentor' in obj_name_lower:
                obj.data.materials.append(mat_fenster)
                print(f"  - {obj.name}: Fenster/Tor (Red)")
            else:
                # Everything else gets yellow (walls, frames, balcony, terrace, etc.)
                obj.data.materials.append(mat_wand)
                print(f"  - {obj.name}: Wand (Yellow)")

            # Ensure all faces use the material (assign material to all faces)
            if obj.data.materials:
                for face in obj.data.polygons:
                    face.material_index = 0

    print("  ✓ Materials applied to all objects and faces")

# Setup lighting
def setup_lighting():
    """Beleuchtung erstellen - MIT RUNDUM-AUSLEUCHTUNG"""
    print("\nCreating lighting...")

    # Delete existing lights
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)

    # Hauptsonne (von oben-vorne)
    bpy.ops.object.light_add(type='SUN', location=(100, -100, 200))
    sun1 = bpy.context.object
    sun1.name = "Sun_Main"
    sun1.data.energy = 4.0
    sun1.rotation_euler = (math.radians(45), 0, math.radians(-45))

    # Zweite Sonne (von hinten-rechts für Rückseite)
    bpy.ops.object.light_add(type='SUN', location=(-100, 100, 150))
    sun2 = bpy.context.object
    sun2.name = "Sun_Back"
    sun2.data.energy = 2.5
    sun2.rotation_euler = (math.radians(60), 0, math.radians(135))

    # Dritte Sonne (von links für Schattenseite)
    bpy.ops.object.light_add(type='SUN', location=(100, 100, 150))
    sun3 = bpy.context.object
    sun3.name = "Sun_Side"
    sun3.data.energy = 2.0
    sun3.rotation_euler = (math.radians(50), 0, math.radians(45))

    # Schwache Fülllichter von allen Seiten
    fill_positions = [
        ("Fill_North", 0, -150, 100, 1.0),
        ("Fill_South", 0, 150, 100, 1.0),
        ("Fill_East", 150, 0, 100, 1.0),
        ("Fill_West", -150, 0, 100, 1.0),
    ]

    for name, x, y, z, energy in fill_positions:
        bpy.ops.object.light_add(type='SUN', location=(x, y, z))
        fill = bpy.context.object
        fill.name = name
        fill.data.energy = energy
        direction = (-x, -y, -z/2)
        fill.rotation_euler = (math.radians(60), 0, math.atan2(direction[1], direction[0]))

    # Himmel
    world = bpy.context.scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = (0.5, 0.7, 1.0, 1.0)
    bg.inputs['Strength'].default_value = 2.5
    print("  ✓ 7 lights + sky configured")

# Get scene bounds
def get_scene_bounds():
    """Bounding Box aller Objekte berechnen"""
    mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
    if not mesh_objects:
        return (0, 0, 0), 100

    min_x = min_y = min_z = float('inf')
    max_x = max_y = max_z = float('-inf')

    for obj in mesh_objects:
        bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

        for corner in bbox_corners:
            min_x = min(min_x, corner[0])
            max_x = max(max_x, corner[0])
            min_y = min(min_y, corner[1])
            max_y = max(max_y, corner[1])
            min_z = min(min_z, corner[2])
            max_z = max(max_z, corner[2])

    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    center_z = (min_z + max_z) / 2

    size = max(max_x - min_x, max_y - min_y, max_z - min_z)

    return (center_x, center_y, center_z), size

# Setup camera
def setup_camera():
    """Kamera erstellen und animieren"""
    print("\nCreating camera animation...")

    # Delete existing cameras
    for obj in bpy.data.objects:
        if obj.type == 'CAMERA':
            bpy.data.objects.remove(obj, do_unlink=True)

    # Get scene center
    center, size = get_scene_bounds()

    # Use configured distance (don't auto-adjust)
    camera_dist = CAMERA_DISTANCE

    print(f"  - Scene center: ({center[0]:.1f}, {center[1]:.1f}, {center[2]:.1f})")
    print(f"  - Scene size: {size:.1f}")
    print(f"  - Camera distance: {camera_dist:.1f}")

    # Empty für Tracking
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=center)
    target = bpy.context.object
    target.name = "Camera_Target"

    # Kamera erstellen
    bpy.ops.object.camera_add(location=(center[0] + camera_dist, center[1], CAMERA_HEIGHT))
    camera = bpy.context.object
    camera.name = "Camera"
    bpy.context.scene.camera = camera

    # Track-To Constraint
    constraint = camera.constraints.new('TRACK_TO')
    constraint.target = target
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'

    # Kamera-Animation: Umkreist das Haus
    for frame in range(1, FRAMES + 1):
        angle = (frame / FRAMES) * 2 * math.pi
        x = center[0] + camera_dist * math.cos(angle)
        y = center[1] + camera_dist * math.sin(angle)
        z = CAMERA_HEIGHT

        camera.location = (x, y, z)
        camera.keyframe_insert(data_path="location", frame=frame)

    print(f"  ✓ Camera animation created ({FRAMES} frames)")

# Execute setup
setup_render()
apply_materials()
setup_lighting()
setup_camera()

# Set to frame TEST_FRAME
bpy.context.scene.frame_set(TEST_FRAME)
print(f"\nSet to frame {TEST_FRAME}")

# Save scene
output_blend = os.path.join(OUTPUT_DIR, "haus_test.blend")
bpy.ops.wm.save_as_mainfile(filepath=output_blend)
print(f"Scene saved: {output_blend}")

# Render frame TEST_FRAME
output_file = os.path.join(OUTPUT_DIR, f"frame_{TEST_FRAME:04d}.png")
bpy.context.scene.render.filepath = output_file

print(f"\n" + "="*60)
print(f"RENDERING FRAME {TEST_FRAME}...")
print("="*60)

bpy.ops.render.render(write_still=True)

print("\n" + "="*60)
print("DONE!")
print("="*60)
print(f"Test frame saved: {output_file}")
print("="*60)
