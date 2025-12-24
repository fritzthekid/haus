#!/usr/bin/env blender --python
"""
Haus-Animation mit Blender
- Lädt haus.blend und dach-neu.stl
- Weist Materialien zu (RAL 085 85 10 + RAL 3003)
- Erstellt Kamera-Animation
- Rendert Film

Verwendung: blender --background --python haus_animation_fixed.py
"""

import bpy
import math
import os
import sys
from mathutils import Vector
import tempfile

# ========== KONFIGURATION ==========
root_dir = os.path.dirname(os.path.abspath(__file__))

HAUS_BLEND = f"{root_dir}/haus.blend"
HAUS_SZENE = f"{root_dir}/haus_szene.blend"
DACH_STL = f"{root_dir}/dach-neu.stl"
os.makedirs("/tmp/haus_animation", exist_ok=True)
OUTPUT_DIR = "/tmp/haus_animation"

# Farben (RAL zu RGB, normalisiert 0-1)
# RAL 085 85 10 (Hellgelb): RGB(250, 230, 160)
COLOR_WAND = (250/255, 230/255, 160/255, 1.0)

# RAL 3003 (Rubinrot): RGB(171, 31, 36)
COLOR_FENSTER = (171/255, 31/255, 36/255, 1.0)

# RAL 2002 (Blutorange): RGB(203, 96, 21)
COLOR_DACH = (203/255, 96/255, 21/255, 1.0)

# Animation
FRAMES = 300
CAMERA_DISTANCE = 150
CAMERA_HEIGHT = 50

# Dach Position (manuelle Anpassung)
DACH_OFFSET_X = 0.0  # Links/Rechts verschieben
DACH_OFFSET_Y = -5.0  # Vorne/Hinten verschieben
DACH_OFFSET_Z = -20.0  # Hoch/Runter verschieben (zusätzlich zur Haus-Höhe)

# ========== SETUP ==========
def clear_scene():
    """Szene komplett leeren - IMPROVED"""
    print("Lösche alte Szene...")
    
    # Alle Objekte löschen
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)
    
    # Meshes löschen
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)
    
    # Materialien löschen
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)
    
    # Kameras und Lichter löschen
    for cam in bpy.data.cameras:
        bpy.data.cameras.remove(cam)
    for light in bpy.data.lights:
        bpy.data.lights.remove(light)
    
    print("  ✓ Szene geleert")
    
def setup_render():
    """Render-Einstellungen"""
    print("Konfiguriere Render-Einstellungen...")
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = 'PNG'
    
    # WICHTIG: Absoluter Pfad mit trailing slash
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    scene.render.filepath = os.path.join(OUTPUT_DIR, "frame_")
    
    scene.frame_start = 1
    scene.frame_end = FRAMES
    scene.render.fps = 30
    
    # Cycles Settings
    scene.cycles.samples = 128
    scene.cycles.use_denoising = False  # Disabled - OpenImageDenoiser not available
    
    print(f"  ✓ Output: {scene.render.filepath}####.png")
    
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

def load_haus(blend = HAUS_BLEND):
    """Haus-Blend laden - KORRIGIERT"""
    print(f"Lade Haus: {blend}")
    
    if not os.path.exists(blend):
        print(f"  ✗ FEHLER: Datei nicht gefunden: {blend}")
        return []
    
    # Append (nicht link!) alle Objekte
    with bpy.data.libraries.load(blend, link=False) as (data_from, data_to):
        data_to.objects = [obj for obj in data_from.objects]
    
    # Objekte zur Szene hinzufügen UND sichtbar machen
    loaded_objects = []
    for obj in data_to.objects:
        if obj is not None:
            # Zur Collection hinzufügen
            bpy.context.collection.objects.link(obj)
            # Sichtbar machen
            obj.hide_viewport = False
            obj.hide_render = False
            loaded_objects.append(obj)
            print(f"  ✓ Objekt geladen: {obj.name}")
    
    if not loaded_objects:
        print(f"  ⚠ WARNUNG: Keine Objekte in {blend} gefunden!")
    
    return loaded_objects

def load_dach():
    """Dach-STL importieren - KORRIGIERT"""
    print(f"Lade Dach: {DACH_STL}")
    
    if not os.path.exists(DACH_STL):
        print(f"  ✗ FEHLER: Datei nicht gefunden: {DACH_STL}")
        return None
    
    # STL importieren
    bpy.ops.wm.stl_import(filepath=DACH_STL)
    
    # Letztes importiertes Objekt ist das Dach
    dach = bpy.context.selected_objects[0]
    dach.name = "Dach"
    print(f"  - Dach geladen: {dach.name}")
    return dach

def position_dach_on_haus():
    """Positioniert das Dach auf dem Haus"""
    print("Positioniere Dach auf Haus...")

    # Haus-Objekt finden
    haus = bpy.data.objects.get("Haus")
    dach = bpy.data.objects.get("Dach")

    if not haus:
        print("  ⚠ WARNUNG: Haus-Objekt nicht gefunden!")
        return

    if not dach:
        print("  ⚠ WARNUNG: Dach-Objekt nicht gefunden!")
        return

    # Aktuelle Positionen anzeigen
    print(f"  - Haus Position: X={haus.location.x:.2f}, Y={haus.location.y:.2f}, Z={haus.location.z:.2f}")
    print(f"  - Dach Position (vorher): X={dach.location.x:.2f}, Y={dach.location.y:.2f}, Z={dach.location.z:.2f}")

    # Berechne die Höhe des Hauses (Bounding Box)
    bbox_corners = [haus.matrix_world @ Vector(corner) for corner in haus.bound_box]
    max_z = max(corner[2] for corner in bbox_corners)
    min_z = min(corner[2] for corner in bbox_corners)
    haus_height = max_z - min_z

    print(f"  - Haus-Höhe (berechnet): {haus_height:.2f}")

    # Verschiebe das Dach
    dach.location.x += DACH_OFFSET_X
    dach.location.y += DACH_OFFSET_Y
    dach.location.z += haus_height + DACH_OFFSET_Z

    print(f"  - Offset angewendet: X={DACH_OFFSET_X:.2f}, Y={DACH_OFFSET_Y:.2f}, Z={haus_height:.2f}+{DACH_OFFSET_Z:.2f}")
    print(f"  ✓ Dach Position (nachher): X={dach.location.x:.2f}, Y={dach.location.y:.2f}, Z={dach.location.z:.2f}")

def assign_materials():
    """Materialien zuweisen - VEREINFACHT"""
    print("Weise Materialien zu...")

    # Materialien erstellen
    mat_wand = create_material("Wand_Gelb", COLOR_WAND, roughness=0.7)
    mat_dach = create_material("Dach_Blutorange", COLOR_DACH, roughness=0.8)

    # Alle Mesh-Objekte durchgehen
    mesh_count = 0
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            mesh_count += 1
            obj_name_lower = obj.name.lower()

            # Material zuweisen
            obj.data.materials.clear()

            if 'dach' in obj_name_lower:
                obj.data.materials.append(mat_dach)
                print(f"  - {obj.name}: Dach (Blutorange RAL 2002)")
            elif 'haus' in obj_name_lower:
                obj.data.materials.append(mat_wand)
                print(f"  - {obj.name}: Haus Wände (Gelb) - Fenster erscheinen als Öffnungen")
            elif 'plane' in obj_name_lower:
                # Ground plane - use a different color or skip
                mat_ground = create_material("Boden", (0.6, 0.6, 0.6, 1.0), roughness=0.9)
                obj.data.materials.append(mat_ground)
                print(f"  - {obj.name}: Boden (Grau)")
            else:
                obj.data.materials.append(mat_wand)
                print(f"  - {obj.name}: Standard (Gelb)")

    print(f"  ✓ {mesh_count} Objekte mit Material versehen")

def setup_lighting():
    """Beleuchtung erstellen - MIT RUNDUM-AUSLEUCHTUNG"""
    print("Erstelle Beleuchtung...")

    # Hauptsonne (von oben-vorne)
    bpy.ops.object.light_add(type='SUN', location=(100, -100, 200))
    sun1 = bpy.context.object
    sun1.name = "Sun_Main"
    sun1.data.energy = 4.0
    sun1.rotation_euler = (math.radians(45), 0, math.radians(-45))
    print("  ✓ Hauptsonne erstellt")

    # Zweite Sonne (von hinten-rechts für Rückseite)
    bpy.ops.object.light_add(type='SUN', location=(-100, 100, 150))
    sun2 = bpy.context.object
    sun2.name = "Sun_Back"
    sun2.data.energy = 2.5
    sun2.rotation_euler = (math.radians(60), 0, math.radians(135))
    print("  ✓ Rücklicht erstellt")

    # Dritte Sonne (von links für Schattenseite)
    bpy.ops.object.light_add(type='SUN', location=(100, 100, 150))
    sun3 = bpy.context.object
    sun3.name = "Sun_Side"
    sun3.data.energy = 2.0
    sun3.rotation_euler = (math.radians(50), 0, math.radians(45))
    print("  ✓ Seitenlicht erstellt")

    # Schwache Fülllichter von allen Seiten (verhindert dunkle Bereiche)
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
        # Richte Licht zum Zentrum
        direction = (-x, -y, -z/2)
        fill.rotation_euler = (math.radians(60), 0, math.atan2(direction[1], direction[0]))

    print("  ✓ 4 Fülllichter erstellt (rundherum)")

    # Himmel (noch heller für mehr Umgebungslicht)
    world = bpy.context.scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = (0.5, 0.7, 1.0, 1.0)
    bg.inputs['Strength'].default_value = 2.5  # Erhöht auf 2.5 für noch mehr Umgebungslicht
    print("  ✓ Himmel konfiguriert (stark erhöht)")

def get_scene_bounds():
    """Bounding Box aller Objekte berechnen"""
    if not bpy.data.objects:
        return (0, 0, 0), 100
    
    # Nur Mesh-Objekte
    mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
    if not mesh_objects:
        return (0, 0, 0), 100
    
    # Bounding Box berechnen
    min_x = min_y = min_z = float('inf')
    max_x = max_y = max_z = float('-inf')
    
    for obj in mesh_objects:
        # Weltkoordinaten der Bounding Box
        bbox_corners = [obj.matrix_world @ Vector(corner)
                        for corner in obj.bound_box]

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
    
    # Größte Ausdehnung
    size = max(max_x - min_x, max_y - min_y, max_z - min_z)
    
    return (center_x, center_y, center_z), size

def setup_camera():
    """Kamera erstellen und animieren"""
    print("Erstelle Kamera-Animation...")
    
    # Szenen-Zentrum finden
    center, size = get_scene_bounds()
    
    # Kamera-Abstand basierend auf Größe
    camera_dist = max(CAMERA_DISTANCE, size * 2)
    
    print(f"  - Szenen-Zentrum: ({center[0]:.1f}, {center[1]:.1f}, {center[2]:.1f})")
    print(f"  - Szenen-Größe: {size:.1f}")
    print(f"  - Kamera-Abstand: {camera_dist:.1f}")
    
    # Empty für Tracking erstellen
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
        
        # Kamera zeigt immer auf Zentrum
        direction = bpy.data.objects.new("temp", None)
        direction.location = center
        
        # Track-To Constraint für automatische Ausrichtung
        if frame == 1:
            constraint = camera.constraints.new('TRACK_TO')
            constraint.target = direction
            constraint.track_axis = 'TRACK_NEGATIVE_Z'
            constraint.up_axis = 'UP_Y'
        
        camera.keyframe_insert(data_path="location", frame=frame)
    
    print(f"  ✓ Kamera-Animation erstellt ({FRAMES} Frames)")

def main():
    """Hauptfunktion"""
    print("=" * 60)
    print("HAUS-ANIMATION SETUP")
    print("=" * 60)
    
    # Test: bpy verfügbar?
    try:
        print(f"Blender Version: {bpy.app.version_string}")
        print(f"Python Version: {sys.version.split()[0]}")
    except Exception as e:
        print(f"FEHLER beim Laden von bpy: {e}")
        sys.exit(1)
    
    print("")
    
    # Output-Verzeichnis erstellen
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Szene vorbereiten
    clear_scene()
    setup_render()
    
    print("")
    
    # Modelle laden
    # haus_objects = load_haus()
    # dach = load_dach()

    haus_szene = load_haus(HAUS_SZENE)

    # Prüfen ob was geladen wurde
    mesh_count = len([o for o in bpy.data.objects if o.type == 'MESH'])
    print(f"\n→ Gesamt {mesh_count} Mesh-Objekte in der Szene")

    if mesh_count == 0:
        print("\n✗ FEHLER: Keine Objekte geladen!")
        print("  Prüfe:")
        print(f"  1. Existiert {HAUS_BLEND}?")
        print(f"  2. Existiert {DACH_STL}?")
        print("  3. Enthält haus.blend Objekte?")
        sys.exit(1)

    print("")

    # Dach auf Haus positionieren
#    position_dach_on_haus()

    print("")

    # Materialien zuweisen
    assign_materials()
    
    print("")
    
    # Beleuchtung
#    setup_lighting()
    
    print("")
    
    # Kamera
    setup_camera()
    
    # Szene speichern
    output_blend = os.path.join(OUTPUT_DIR, "haus_szene.blend")
    bpy.ops.wm.save_as_mainfile(filepath=output_blend)
    print(f"\nSzene gespeichert: {output_blend}")

    print("\n" + "=" * 60)
    print("SETUP ABGESCHLOSSEN - STARTE RENDERING")
    print("=" * 60)
    print(f"Frames: {FRAMES}")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Szene: {output_blend}")

    # Animation rendern
    print("\nRendere Animation...")
    bpy.ops.render.render(animation=True)

    print("\n" + "=" * 60)
    print("RENDERING ABGESCHLOSSEN")
    print("=" * 60)
    print(f"Frames gespeichert in: {OUTPUT_DIR}/frame_####.png")
    print("=" * 60)

if __name__ == "__main__":
    main()
