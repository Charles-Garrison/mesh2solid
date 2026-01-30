#!/usr/bin/env python3
"""
STL to STEP Converter using FreeCAD

This script converts mesh STL files to solid body STEP files using FreeCAD's
headless mode. It processes all STL files in the stl_files directory and
outputs STEP files to the step_files directory.

Usage:
    Run via FreeCAD's Python interpreter:
    freecadcmd convert_stl_to_step.py

    Or on macOS:
    /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd convert_stl_to_step.py
"""

import sys
import os

# Get the directory where this script is located (for relative paths)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STL_DIR = os.path.join(SCRIPT_DIR, "stl_files")
STEP_DIR = os.path.join(SCRIPT_DIR, "step_files")

def setup_directories():
    """Ensure input and output directories exist."""
    os.makedirs(STL_DIR, exist_ok=True)
    os.makedirs(STEP_DIR, exist_ok=True)

def get_stl_files():
    """Get list of STL files in the input directory."""
    if not os.path.exists(STL_DIR):
        return []

    stl_files = [
        f for f in os.listdir(STL_DIR)
        if f.lower().endswith('.stl')
    ]
    return sorted(stl_files)

def convert_stl_to_step(stl_filename):
    """
    Convert a single STL file to STEP format.

    Args:
        stl_filename: Name of the STL file (not full path)

    Returns:
        True if conversion successful, False otherwise
    """
    try:
        import FreeCAD
        import Mesh
        import Part

        stl_path = os.path.join(STL_DIR, stl_filename)
        base_name = os.path.splitext(stl_filename)[0]
        step_path = os.path.join(STEP_DIR, f"{base_name}.step")

        print(f"Converting: {stl_filename}")

        # Create a new FreeCAD document
        doc = FreeCAD.newDocument("Conversion")

        # Import the STL mesh
        Mesh.insert(stl_path, doc.Name)

        # Get the mesh object
        mesh_obj = doc.Objects[0]
        mesh_data = mesh_obj.Mesh

        # Convert mesh to shape
        # The tolerance value affects the quality of the conversion
        # Lower values = higher quality but slower processing
        shape = Part.Shape()
        shape.makeShapeFromMesh(mesh_data.Topology, 0.1)

        # Refine the shape to clean up the geometry
        shape = shape.removeSplitter()

        # Create a solid from the shape
        if shape.isValid():
            solid = Part.Solid(shape)
        else:
            # Try to make a solid anyway
            solid = Part.makeSolid(shape)

        # Export to STEP
        solid.exportStep(step_path)

        # Close the document
        FreeCAD.closeDocument(doc.Name)

        print(f"  -> Created: {base_name}.step")
        return True

    except Exception as e:
        print(f"  ERROR converting {stl_filename}: {str(e)}")
        return False

def main():
    """Main function to process all STL files."""
    print("=" * 60)
    print("STL to STEP Converter")
    print("=" * 60)

    # Ensure directories exist
    setup_directories()

    # Get list of STL files
    stl_files = get_stl_files()

    if not stl_files:
        print(f"\nNo STL files found in: {STL_DIR}")
        print("Please place your .stl files in the 'stl_files' directory.")
        print("=" * 60)
        return

    print(f"\nFound {len(stl_files)} STL file(s) to process:")
    for f in stl_files:
        print(f"  - {f}")
    print()

    # Process each file
    successful = 0
    failed = 0
    files_to_remove = []

    for stl_file in stl_files:
        if convert_stl_to_step(stl_file):
            successful += 1
            files_to_remove.append(stl_file)
        else:
            failed += 1

    # Remove successfully converted STL files
    print()
    for stl_file in files_to_remove:
        stl_path = os.path.join(STL_DIR, stl_file)
        try:
            os.remove(stl_path)
            print(f"Removed: {stl_file}")
        except Exception as e:
            print(f"Warning: Could not remove {stl_file}: {e}")

    # Summary
    print()
    print("=" * 60)
    print(f"Conversion complete!")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Output directory: {STEP_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
