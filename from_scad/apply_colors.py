#!/usr/bin/env blender --python
"""
Apply colors to haus_complete_mit_fenstern.blend
"""

import bpy
import os

# ========== KONFIGURATION ==========
root_dir = os.path.dirname(os.path.abspath(__file__))
HAUS_BLEND = f"{root_dir}/haus_complete_mit_fenstern.blend"
OUTPUT_DIR = "/tmp/haus_animation"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Farben (RAL zu RGB, normalisiert 0-1)
# RAL 085 85 10 (Hellgelb): RGB(250, 230, 160)
COLOR_WAND = (250/255, 230/255, 160/255, 1.0)

# RAL 3003 (Rubinrot): RGB(171, 31, 36)
COLOR_FENSTER = (171/255, 31/255, 36/255, 1.0)

# RAL 2002 (Blutorange): RGB(203, 96, 21)
COLOR_DACH = (203/255, 96/255, 21/255, 1.0)

print("="*60)
print("APPLYING COLORS TO HAUS MODEL")
print("="*60)

# Load the blend file
print(f"\nLoading: {HAUS_BLEND}")
bpy.ops.wm.open_mainfile(filepath=HAUS_BLEND)

def create_material(name, color, roughness=0.5, metallic=0.0):
    """Material erstellen"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    # Shader Setup
    output = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic

    mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat

# Create materials
print("\nCreating materials...")
mat_wand = create_material("Wand_Gelb", COLOR_WAND, roughness=0.7)
mat_fenster = create_material("Fenster_Rot", COLOR_FENSTER, roughness=0.3)
mat_dach = create_material("Dach_Blutorange", COLOR_DACH, roughness=0.8)
print("  ✓ Materials created")

# Diagnose: Show all objects
print("\n" + "="*60)
print("OBJECTS IN SCENE:")
print("="*60)
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        print(f"  • {obj.name}")

# Apply materials
print("\n" + "="*60)
print("APPLYING MATERIALS:")
print("="*60)

for obj in bpy.data.objects:
    if obj.type == 'MESH':
        obj_name_lower = obj.name.lower()

        # Clear existing materials
        obj.data.materials.clear()

        # Assign based on name
        if 'dach' in obj_name_lower:
            obj.data.materials.append(mat_dach)
            print(f"  - {obj.name}: Dach (Blutorange RAL 2002)")
        elif 'fenster' in obj_name_lower or 'garage_tor' in obj_name_lower or 'garagentor' in obj_name_lower:
            obj.data.materials.append(mat_fenster)
            print(f"  - {obj.name}: Fenster/Tor (Rot RAL 3003)")
        else:
            # Everything else is walls
            obj.data.materials.append(mat_wand)
            print(f"  - {obj.name}: Wand (Gelb RAL 085 85 10)")

# Save the scene
output_blend = os.path.join(OUTPUT_DIR, "haus_colored.blend")
bpy.ops.wm.save_as_mainfile(filepath=output_blend)

print("\n" + "="*60)
print("DONE!")
print("="*60)
print(f"Saved to: {output_blend}")
print("="*60)
