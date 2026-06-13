#!/usr/bin/env python3
"""
Mesh to STEP Converter using FreeCAD

This script converts mesh files (STL, 3MF, OBJ, PLY, OFF) to solid body STEP
files using FreeCAD's headless mode. It processes all supported mesh files in
the input directory and outputs STEP files to the output directory.

A single mesh file may contain more than one body (3MF in particular, where
FreeCAD merges all parts into one mesh on import). The merged mesh is split
into its disconnected components and each component is converted to its own
solid and written as a separate STEP file.

Usage:
    Run via FreeCAD's Python interpreter:
    freecadcmd convert_mesh_to_step.py

    Or on macOS:
    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd convert_mesh_to_step.py
"""

import sys
import os

# Get the directory where this script is located (for relative paths)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(SCRIPT_DIR, "input")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")

# Mesh formats FreeCAD's Mesh module can import.
SUPPORTED_EXTENSIONS = (".stl", ".3mf", ".obj", ".ply", ".off")

# Tolerance for mesh -> shape conversion.
# Lower values = higher quality but slower processing.
SHAPE_TOLERANCE = 0.1

def setup_directories():
    """Ensure input and output directories exist."""
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_mesh_files():
    """Get list of supported mesh files in the input directory."""
    if not os.path.exists(INPUT_DIR):
        return []

    mesh_files = [
        f for f in os.listdir(INPUT_DIR)
        if f.lower().endswith(SUPPORTED_EXTENSIONS)
    ]
    return sorted(mesh_files)

def mesh_to_solid(mesh_data):
    """Convert FreeCAD mesh data to a solid Part shape."""
    import Part

    shape = Part.Shape()
    shape.makeShapeFromMesh(mesh_data.Topology, SHAPE_TOLERANCE)

    # Refine the shape to clean up the geometry.
    shape = shape.removeSplitter()

    # Create a solid from the shape.
    if shape.isValid():
        return Part.Solid(shape)
    # Try to make a solid anyway.
    return Part.makeSolid(shape)

def get_bodies(doc):
    """
    Return every disconnected body in the imported document as a list of
    mesh objects.

    FreeCAD merges all parts of a multi-object file (e.g. 3MF) into a single
    mesh on import, so we split each imported mesh into its separate connected
    components to recover the individual bodies.
    """
    bodies = []
    for obj in doc.Objects:
        if hasattr(obj, "Mesh"):
            bodies.extend(obj.Mesh.getSeparateComponents())
    return bodies

def convert_mesh_file(filename):
    """
    Convert a single mesh file to one or more STEP files.

    Each disconnected body in the file is exported as its own STEP file. For a
    single-body file the output is named "<base>.step"; for a multi-body file
    each output is named "<base>_NN.step" (one per body).

    Args:
        filename: Name of the mesh file (not full path)

    Returns:
        True if every body converted successfully, False otherwise.
    """
    import FreeCAD
    import Mesh

    in_path = os.path.join(INPUT_DIR, filename)
    base_name = os.path.splitext(filename)[0]

    print(f"Converting: {filename}")

    doc = FreeCAD.newDocument("Conversion")
    try:
        # Import the mesh, then split into individual bodies.
        Mesh.insert(in_path, doc.Name)
        bodies = get_bodies(doc)

        if not bodies:
            print("  ERROR: no mesh bodies found in file")
            return False

        total = len(bodies)
        if total > 1:
            print(f"  Found {total} bodies")
        width = max(2, len(str(total)))

        succeeded = 0
        failed = 0

        for index, body in enumerate(bodies, start=1):
            if total == 1:
                out_name = base_name
            else:
                out_name = f"{base_name}_{index:0{width}d}"

            step_path = os.path.join(OUTPUT_DIR, f"{out_name}.step")

            try:
                solid = mesh_to_solid(body)
                solid.exportStep(step_path)
                print(f"  -> Created: {out_name}.step")
                succeeded += 1
            except Exception as e:
                print(f"  ERROR converting body {index}: {str(e)}")
                failed += 1

        return failed == 0 and succeeded > 0

    except Exception as e:
        print(f"  ERROR reading {filename}: {str(e)}")
        return False

    finally:
        FreeCAD.closeDocument(doc.Name)

def main():
    """Main function to process all mesh files."""
    print("=" * 60)
    print("Mesh to STEP Converter")
    print("=" * 60)

    # Ensure directories exist
    setup_directories()

    # Get list of mesh files
    mesh_files = get_mesh_files()

    if not mesh_files:
        print(f"\nNo mesh files found in: {INPUT_DIR}")
        print("Supported formats: " + ", ".join(SUPPORTED_EXTENSIONS))
        print("Please place your mesh files in the 'input' directory.")
        print("=" * 60)
        return

    print(f"\nFound {len(mesh_files)} mesh file(s) to process:")
    for f in mesh_files:
        print(f"  - {f}")
    print()

    # Process each file
    successful = 0
    failed = 0
    files_to_remove = []

    for mesh_file in mesh_files:
        if convert_mesh_file(mesh_file):
            successful += 1
            files_to_remove.append(mesh_file)
        else:
            failed += 1

    # Remove successfully converted source files
    print()
    for mesh_file in files_to_remove:
        mesh_path = os.path.join(INPUT_DIR, mesh_file)
        try:
            os.remove(mesh_path)
            print(f"Removed: {mesh_file}")
        except Exception as e:
            print(f"Warning: Could not remove {mesh_file}: {e}")

    # Summary
    print()
    print("=" * 60)
    print(f"Conversion complete!")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Output directory: {OUTPUT_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
