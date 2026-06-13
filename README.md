# Mesh to STEP Converter

Convert mesh files (STL, 3MF, OBJ, PLY, OFF) to solid body STEP files using FreeCAD’s CLI.

## Usage

1. Place your mesh files in the `input/` directory
2. Run the converter:
   ```bash
   ./run_converter.sh
   ```
3. Find your converted `.step` files in the `output/` directory

**Note:** Source mesh files are automatically deleted after a fully successful conversion (a file is kept if any object in it fails).

## Supported Formats

`.stl`, `.3mf`, `.obj`, `.ply`, `.off` — any mesh format FreeCAD’s `Mesh` module can import.

A single file may contain more than one body (common with 3MF). FreeCAD merges all parts into one mesh on import, so the converter splits that mesh into its disconnected components and writes each as a **separate STEP file**:

- Single-body file → `name.step`
- Multi-body file → `name_01.step`, `name_02.step`, … (one per body)

## Requirements

- **FreeCAD** must be installed on your system
  - Download from: https://www.freecad.org/downloads.php
  - macOS: Install to `/Applications/FreeCAD.app`
  - Linux: Install via package manager or Flatpak

## Directory Structure

```
mesh2solid/
├── input/                   # Input: Place mesh files here
├── output/                  # Output: Converted STEP files
├── convert_mesh_to_step.py  # Main conversion script
├── run_converter.sh         # Runner script
└── README.md
```

## Technical Notes
- **Relative paths**: All paths are relative to the script location for portability.
- **FreeCAD modules used**: `FreeCAD`, `Mesh`, `Part`

## How It Works

The script uses FreeCAD's bundled Python interpreter to:
1. Load each mesh file
2. Split the imported mesh into its disconnected bodies
3. Convert each body's mesh geometry to a solid shape
4. Export each solid as its own STEP file
5. Delete the original mesh file once every body converts successfully

## Conversion Process

1. Load mesh with `Mesh.insert()`
2. Split into bodies with `mesh.getSeparateComponents()`
3. For each body:
   1. Convert to shape with `shape.makeShapeFromMesh()`
   2. Clean geometry with `shape.removeSplitter()`
   3. Create solid with `Part.Solid()`
   4. Export with `solid.exportStep()`

## Troubleshooting

### FreeCAD not found
If you get a "FreeCAD not found" error:
- Ensure FreeCAD is installed to a standard location
- macOS: `/Applications/FreeCAD.app`
- Linux: `/usr/lib/freecad`, `/opt/freecad`, or via Snap

## Common FreeCAD Paths
- macOS: `/Applications/FreeCAD.app/Contents/Resources/bin/python` (with lib in PYTHONPATH)
- Linux: `/usr/lib/freecad/bin/python`, `/opt/freecad/bin/python`

### Conversion fails for a file
Some complex or malformed mesh files may fail to convert. The script will:
- Report the error
- Continue processing other files
- Keep the original mesh file (only deleted on full success)
