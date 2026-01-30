# STL to STEP Converter

Convert mesh STL files to solid body STEP files using FreeCAD’s CLI.

## Usage

1. Place your `.stl` files in the `stl_files/` directory
2. Run the converter:
   ```bash
   ./run_converter.sh
   ```
3. Find your converted `.step` files in the `step_files/` directory

**Note:** Successfully converted STL files are automatically deleted after conversion.

## Requirements

- **FreeCAD** must be installed on your system
  - Download from: https://www.freecad.org/downloads.php
  - macOS: Install to `/Applications/FreeCAD.app`
  - Linux: Install via package manager or Flatpak

## Directory Structure

```
mesh2solid/
├── stl_files/              # Input: Place STL files here
├── step_files/             # Output: Converted STEP files
├── convert_stl_to_step.py  # Main conversion script
├── run_converter.sh        # Runner script
└── README.md
```

## Technical Notes
- **Relative paths**: All paths are relative to the script location for portability.
- **FreeCAD modules used**: `FreeCAD`, `Mesh`, `Part`

## How It Works

The script uses FreeCAD's bundled Python interpreter to:
1. Load each STL mesh file
2. Convert the mesh geometry to a solid shape
3. Export the solid as a STEP file
4. Delete the original STL file upon successful conversion

## Conversion Process

1. Load STL with `Mesh.insert()`
2. Convert to shape with `shape.makeShapeFromMesh()`
3. Clean geometry with `shape.removeSplitter()`
4. Create solid with `Part.Solid()`
5. Export with `solid.exportStep()`

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
Some complex or malformed STL files may fail to convert. The script will:
- Report the error
- Continue processing other files
- Keep the original STL file (only deleted on success)