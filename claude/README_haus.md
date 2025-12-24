# Haus-Animation mit Blender

## Dateien
- `haus_animation.py` - Blender Python-Script (Setup)
- `render_haus.sh` - Komplettes Render-Script
- `haus.blend` - Dein Haus-Modell
- `dach-neu.stl` - Dein Dach-Modell

## Schnellstart

```bash
# Alles in einem Schritt (dauert 30-60 Minuten)
bash render_haus.sh
```

Das Script:
1. Lädt Haus + Dach
2. Weist Materialien zu (Gelb + Rot)
3. Erstellt Kamera-Animation (Umkreisung)
4. Rendert 300 Frames (10 Sekunden)
5. Erstellt MP4 + WebM Video

## Schritt für Schritt

### 1. Szene erstellen (ohne Rendern)
```bash
blender --background --python haus_animation.py
```

Ergebnis: `haus_szene.blend` in `/mnt/user-data/outputs/haus_render/`

### 2. Szene in Blender GUI öffnen (zum Anpassen)
```bash
blender /mnt/user-data/outputs/haus_render/haus_szene.blend
```

### 3. Manuell rendern
```bash
blender --background /mnt/user-data/outputs/haus_render/haus_szene.blend --render-anim
```

### 4. Video erstellen (falls Frames vorhanden)
```bash
cd /mnt/user-data/outputs/haus_render
ffmpeg -framerate 30 -i frame_%04d.png -c:v libx264 -crf 18 haus_animation.mp4
```

## Farben

**Aktuell eingestellt:**
- **Wände:** RAL 085 85 10 (Hellgelb) - RGB(250, 230, 160)
- **Fenster/Rahmen:** RAL 3003 (Rubinrot) - RGB(171, 31, 36)
- **Dach:** Grau - RGB(76, 76, 76)

**Farben ändern** im Script `haus_animation.py`:

```python
# Zeile 14-18
COLOR_WAND = (250/255, 230/255, 160/255, 1.0)    # RAL 085 85 10
COLOR_FENSTER = (171/255, 31/255, 36/255, 1.0)   # RAL 3003
```

## Anpassungen

### Animation ändern

**Dauer:**
```python
# Zeile 20
FRAMES = 300  # 10 Sekunden @ 30fps
# 600 = 20 Sekunden
# 150 = 5 Sekunden
```

**Kamera-Bewegung:**
```python
# Zeile 21-22
CAMERA_DISTANCE = 150  # Abstand zum Haus
CAMERA_HEIGHT = 50     # Höhe der Kamera

# Größere Werte = weiter weg / höher
```

**Andere Kamera-Bewegung** (Zeile 151-166 ändern):

```python
# Statt Umkreisung: Kamera fährt zu
for frame in range(1, FRAMES + 1):
    progress = frame / FRAMES
    distance = CAMERA_DISTANCE * (1 - progress * 0.7)  # 70% näher
    camera.location = (center[0] + distance, center[1], CAMERA_HEIGHT)
    camera.keyframe_insert(data_path="location", frame=frame)
```

### Render-Qualität

**Im Script Zeile 36:**
```python
scene.cycles.samples = 128  # Standard
# 64 = schneller, weniger Qualität
# 256 = langsamer, bessere Qualität
# 512 = sehr langsam, beste Qualität
```

**Auflösung ändern (Zeile 31-32):**
```python
scene.render.resolution_x = 1920  # Breite
scene.render.resolution_y = 1080  # Höhe

# 1280x720 = HD (schneller)
# 3840x2160 = 4K (viel langsamer!)
```

### Beleuchtung

**Sonnenintensität (Zeile 144):**
```python
sun.data.energy = 3.0  # Standard
# 5.0 = heller
# 1.0 = dunkler
```

**Sonnenwinkel (Zeile 145):**
```python
sun.rotation_euler = (math.radians(45), 0, math.radians(-45))
# Erste Zahl = Höhe (0-90°)
# Letzte Zahl = Rotation (-180 bis 180°)
```

## Material-Zuweisung

Das Script weist Materialien basierend auf Objektnamen zu:

- `'dach'` im Namen → Grau
- `'fenster'`, `'rahmen'`, `'flank'` im Namen → Rot
- Alles andere → Gelb

**Falls falsch zugewiesen:**

1. Szene in Blender öffnen
2. Objekt auswählen
3. Material-Tab → Material wechseln

**Oder im Script ändern (Zeile 97-115):**

```python
# Beispiel: Tür auch rot
elif any(x in obj_name_lower for x in ['fenster', 'rahmen', 'flank', 'tür']):
    obj.data.materials.append(mat_fenster)
```

## Fehlersuche

**"Blender nicht gefunden":**
```bash
sudo apt install blender
```

**"Objekte werden nicht geladen":**
- Prüfe ob `haus.blend` und `dach-neu.stl` korrekt sind
- Öffne `haus.blend` manuell in Blender GUI

**"Materialien falsch zugewiesen":**
- Öffne `haus_szene.blend` in Blender GUI
- Prüfe Objektnamen
- Passe Material-Zuweisung im Script an

**"Rendern dauert ewig":**
- Reduziere Samples: `scene.cycles.samples = 64`
- Reduziere Auflösung: `1280x720`
- Weniger Frames: `FRAMES = 150`

**"Kamera zeigt falschen Bereich":**
- Passe `CAMERA_DISTANCE` und `CAMERA_HEIGHT` an
- Öffne Szene in Blender GUI und teste Kamera-Position

## Render-Zeiten (grob)

**Bei 1920x1080, 128 Samples, 300 Frames:**
- Schneller PC (8 Cores): ~30 Minuten
- Mittel (4 Cores): ~60 Minuten
- Langsam (2 Cores): ~2 Stunden

**Pro Frame:** ca. 5-15 Sekunden

## Output

Nach Render:
```
/mnt/user-data/outputs/haus_render/
├── frame_0001.png
├── frame_0002.png
├── ...
├── frame_0300.png
├── haus_animation.mp4
├── haus_animation.webm
└── haus_szene.blend
```

## Tipps

1. **Erst testen:** Rendere nur 10 Frames zum Testen
   ```bash
   # Im Script: FRAMES = 10
   ```

2. **GPU nutzen:** Falls CUDA/OptiX verfügbar (viel schneller!)
   ```python
   # Zeile 30 ändern:
   scene.cycles.device = 'GPU'
   ```

3. **Einzelframe testen:**
   ```bash
   blender -b haus_szene.blend -f 1  # Nur Frame 1
   ```

4. **Hintergrund ändern:**
   ```python
   # Zeile 150: Himmelfarbe
   bg.inputs['Color'].default_value = (0.5, 0.7, 1.0, 1.0)
   # (R, G, B, Alpha) - Werte 0-1
   ```
