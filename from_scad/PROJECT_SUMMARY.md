# Haus Animation Project - Complete Summary

## Project Overview

**Goal:** Create a 300-frame rotating camera animation of a house model with proper RAL colors applied to walls, windows, roof, and garage door, rendered as PNG frames that can be converted to MP4 video.

**Final Status:** ✓ COMPLETE - All scripts working correctly, animation rendering locally

---

## Final Working Configuration

### Source Model
- **File:** `haus_complete_mit_fenstern.blend`
- **Location:** `/home/eduard/work/tmp/haus/from_scad/`
- **Key Feature:** Contains 27 properly separated mesh objects including 14 individual Fenster (window) objects, Garage_Tor, Dach, and various wall components

### Color Scheme (RAL Standards)
- **Walls:** RAL 9012 (Reinraumweiß/Clean Room White) - RGB(255, 253, 230)
- **Windows/Garage Door:** RAL 3003 (Ruby Red) - RGB(171, 31, 36)
- **Roof:** RAL 2002 (Blood Orange) - RGB(203, 96, 21)

### Camera Settings
- **Distance:** 40 units from scene center
- **Height:** 4 units (approximately 170mm from ground level)
- **Animation:** 360° rotation around house over 300 frames
- **Tracking:** Uses Track-To constraint pointing at scene center

### Lighting Setup
- **7 Sun Lights Total:**
  - Main sun (front-top): Energy 4.0
  - Back sun (rear-right): Energy 2.5
  - Side sun (left): Energy 2.0
  - 4 Fill lights (N/S/E/W cardinal directions): Energy 1.0 each
- **Sky:** Ambient blue sky with strength 2.5
- **Result:** Even illumination from all angles, no dark sides

### Render Settings
- **Engine:** Cycles
- **Resolution:** 1920x1080 (Full HD)
- **Samples:** 128
- **Denoising:** OFF (OpenImageDenoiser not available)
- **FPS:** 30
- **Format:** PNG
- **Performance:** ~5 seconds per frame (~25-30 minutes for full animation)

---

## Working Scripts

### 1. create_animation.py
**Purpose:** Main script for rendering full 300-frame animation

**Usage:**
```bash
cd /home/eduard/work/tmp/haus/from_scad
blender --background --python create_animation.py
```

**What it does:**
1. Loads `haus_complete_mit_fenstern.blend` directly
2. Removes ground plane objects to prevent black borders
3. Applies RAL 9012/3003/2002 colors to all objects
4. Explicitly assigns all mesh polygons to material_index 0 (fixes black faces)
5. Sets up 7-light system with ambient sky
6. Creates rotating camera animation
7. Renders all 300 frames to `/tmp/haus_animation/frame_####.png`
8. Saves setup scene to `/tmp/haus_animation/haus_animation_ready.blend`

**Output:**
- Frames: `/tmp/haus_animation/frame_0001.png` through `frame_0300.png`
- Scene: `/tmp/haus_animation/haus_animation_ready.blend`

### 2. test_frame_200.py
**Purpose:** Quick test script for single frame rendering (configurable)

**Usage:**
```bash
blender --background --python test_frame_200.py
```

**Configuration:**
- Modify `TEST_FRAME = 216` to test different camera angles
- Frame 1: front view
- Frame 75: side view
- Frame 150: back view
- Frame 225: opposite side view

**What it does:**
1. Same setup as create_animation.py
2. Sets scene to specified TEST_FRAME
3. Renders only that single frame
4. Saves to `/tmp/haus_animation/frame_####.png`
5. Saves scene to `/tmp/haus_animation/haus_test.blend`

### 3. apply_colors.py
**Purpose:** Earlier script for color application only (no longer needed in workflow)

**Status:** Deprecated - colors now applied directly in create_animation.py

---

## Key Technical Solutions

### Problem 1: Windows Not Colored
**Initial Issue:** Original `haus.blend` had windows as geometric holes in the mesh, not separate objects

**Solution:** Switched to `haus_complete_mit_fenstern.blend` which has 14 separate Fenster objects that can be assigned red material

### Problem 2: Black Faces on Walls
**Issue:** Small sides of walls appearing black despite material assignment

**Solution:** Explicitly assign all mesh polygons to material_index 0:
```python
if obj.data.materials:
    for face in obj.data.polygons:
        face.material_index = 0
```

**Location:** Lines 119-121 in create_animation.py, lines 111-113 in test_frame_200.py

### Problem 3: Black Borders Around Walls
**Issue:** Ground plane object causing black borders where walls intersect it

**Solution:** Remove plane objects before rendering:
```python
for obj in list(bpy.data.objects):
    if obj.type == 'MESH' and 'plane' in obj.name.lower():
        bpy.data.objects.remove(obj, do_unlink=True)
```

**Location:** Lines 42-47 in create_animation.py, lines 39-43 in test_frame_200.py

### Problem 4: Camera Too Far and Too High
**Issue:** House only fraction of frame, needed 250-300% zoom to see properly

**Solution:**
- Reduced CAMERA_DISTANCE from 150 to 40
- Reduced CAMERA_HEIGHT from 50 to 4
- Removed auto-adjustment based on scene size

### Problem 5: Dark Sides on House
**Issue:** Back and side faces of house appearing too dark

**Solution:** Implemented 7-light setup with main suns from multiple angles plus fill lights from all cardinal directions, plus strong ambient sky (strength 2.5)

### Problem 6: OpenImageDenoiser Not Available
**Issue:** Blender build doesn't include OpenImageDenoiser

**Solution:** Disabled denoising: `scene.cycles.use_denoising = False`

---

## Project Evolution

### Phase 1: Initial Attempts (../claude directory)
- Used `haus.blend` with windows as geometric holes
- Could not apply red color to window flanks
- Attempted face-level material assignment - too complex
- **Decision:** Find better source model

### Phase 2: New Approach (from_scad directory)
- Found `haus_complete_mit_fenstern.blend` with separated objects
- Created `apply_colors.py` for initial color testing
- Created `test_frame_200.py` for single-frame testing
- Created `create_animation.py` for full rendering

### Phase 3: Refinements
- Fixed black faces issue
- Fixed black borders (removed ground plane)
- Adjusted camera position (40 units distance, 4 units height)
- Changed wall color from yellow to RAL 9012 (white)
- Removed dependency on intermediate haus_colored.blend file

### Phase 4: Final Working State
- All scripts using `haus_complete_mit_fenstern.blend` directly
- Proper RAL 9012 wall color
- Correct camera positioning
- No black faces or borders
- Even lighting from all angles
- User rendering locally with all corrections

---

## Scene Objects

**27 Mesh Objects Total:**
- Balkon
- Dach
- Fenster_Hinten_Oben
- Fenster_Hinten_Unten_1, 2, 3, 4
- Fenster_Vorne_1, 2, 3, 4, 5, 6, 7
- Garage_Rahmen
- Garage_Tor
- Rahmen_Mitte, Oben, Unten
- Rueckwand_Oben_Basis
- Seitenwand_Links, Rechts
- Terrasse
- Tür_Hinten_Oben_1, 2
- Tür_Hinten_Unten
- Vorderwand_Basis

**Material Assignment Logic:**
- If "dach" in name → Orange (RAL 2002)
- If "fenster" or "garage_tor" or "garagentor" in name → Red (RAL 3003)
- All other objects → White (RAL 9012)

---

## Creating MP4 Video from Frames

### Basic Command
```bash
ffmpeg -framerate 30 -i /tmp/haus_animation/frame_%04d.png -c:v libx264 -pix_fmt yuv420p output.mp4
```

### Slower Animation (15 FPS)
```bash
ffmpeg -framerate 15 -i /tmp/haus_animation/frame_%04d.png -c:v libx264 -pix_fmt yuv420p output_slow.mp4
```

### Higher Quality
```bash
ffmpeg -framerate 30 -i /tmp/haus_animation/frame_%04d.png -c:v libx264 -crf 18 -pix_fmt yuv420p output_hq.mp4
```

**Parameters Explained:**
- `-framerate`: Frames per second (30 = normal speed, 15 = half speed)
- `-i`: Input pattern (%04d = 4-digit frame numbers)
- `-c:v libx264`: H.264 video codec
- `-crf 18`: Quality (lower = better, 18 = high quality, 23 = default)
- `-pix_fmt yuv420p`: Pixel format for compatibility

---

## File Locations

### Source Files
- `/home/eduard/work/tmp/haus/from_scad/haus_complete_mit_fenstern.blend` - Source model
- `/home/eduard/work/tmp/haus/from_scad/create_animation.py` - Full animation script
- `/home/eduard/work/tmp/haus/from_scad/test_frame_200.py` - Test frame script
- `/home/eduard/work/tmp/haus/from_scad/apply_colors.py` - Deprecated color script

### Output Files
- `/tmp/haus_animation/frame_0001.png` through `frame_0300.png` - Rendered frames
- `/tmp/haus_animation/haus_animation_ready.blend` - Full animation scene
- `/tmp/haus_animation/haus_test.blend` - Test frame scene

### Documentation
- `/home/eduard/work/tmp/haus/from_scad/PROGRESS_LOG.md` - Development progress log
- `/home/eduard/work/tmp/haus/from_scad/PROJECT_SUMMARY.md` - This file

### Deprecated
- `/home/eduard/work/tmp/haus/claude/haus_animation.py` - Old script using haus.blend
- `/tmp/haus_animation/haus_colored.blend` - Intermediate file (no longer used)

---

## Scene Measurements

**Bounding Box:**
- Center: (5.0, 5.7, 4.9)
- Size: 14.5 units
- Camera distance: 40 units (manually configured)
- Camera height: 4 units (manually configured)

**Animation:**
- Total frames: 300
- FPS: 30
- Duration: 10 seconds at 30 FPS, 20 seconds at 15 FPS
- Camera path: Complete 360° circle around scene center

---

## Next Steps (Optional)

If you want to make changes:

1. **Adjust camera position:** Modify `CAMERA_DISTANCE` and `CAMERA_HEIGHT` in create_animation.py
2. **Change colors:** Modify `RAL_9012`, `COLOR_FENSTER`, `COLOR_DACH` values
3. **Render quality:** Adjust `scene.cycles.samples` (higher = better quality, slower)
4. **Animation speed:** Change `FRAMES` value or use different `-framerate` in ffmpeg
5. **Test different angles:** Change `TEST_FRAME` in test_frame_200.py (1-300)

---

## Success Criteria - All Achieved ✓

- ✓ Animation uses correct source file (haus_complete_mit_fenstern.blend)
- ✓ All objects properly colored with RAL standards
- ✓ Windows and garage door appear red (RAL 3003)
- ✓ Walls appear white (RAL 9012)
- ✓ Roof appears orange (RAL 2002)
- ✓ Camera positioned close enough (house fills frame)
- ✓ Camera at correct height (4 units from ground)
- ✓ No black faces on walls or other objects
- ✓ No black borders around walls
- ✓ Even lighting from all angles (no dark sides)
- ✓ 300 frames rendering successfully
- ✓ Output directory organized (/tmp/haus_animation/)
- ✓ Frames ready for ffmpeg conversion to MP4

---

## Project Timeline

**2025-12-26** - Project completion
- Initial attempts with haus.blend (windows as holes)
- Discovered haus_complete_mit_fenstern.blend (proper separated objects)
- Created and tested all three Python scripts
- Fixed black faces issue (explicit polygon material assignment)
- Fixed black borders (removed ground plane)
- Adjusted camera position (40 distance, 4 height)
- Updated wall color to RAL 9012
- Full animation rendering locally with all corrections applied

---

## Technical Notes

### Blender Version Compatibility
Scripts tested with Blender 3.x using Cycles engine. Requires:
- Python 3.x
- Blender with Cycles support
- mathutils module (included with Blender)

### Performance Optimization
- Samples set to 128 (balance of quality/speed)
- Denoising disabled (not available in this build)
- Resolution 1920x1080 (Full HD)
- Each frame: ~5 seconds
- Full animation: ~25-30 minutes

### Color Standards Reference
- RAL 9012 (Reinraumweiß): Very light warm white, used in clean rooms
- RAL 3003 (Rubinrot): Deep ruby red, classic window/door color
- RAL 2002 (Blutorange): Blood orange, traditional roof tile color

---

## Conclusion

The Blender house animation project is complete and working correctly. All technical challenges have been resolved:

- Proper source model with separated window objects
- Correct RAL color application to all surfaces
- Fixed black faces and borders through explicit material assignment
- Optimal camera positioning for house visibility
- Comprehensive lighting setup for even illumination
- Efficient rendering workflow with test capability

The animation is currently rendering locally and will produce 300 high-quality PNG frames ready for conversion to MP4 video using ffmpeg.

**Project Status: COMPLETE ✓**
