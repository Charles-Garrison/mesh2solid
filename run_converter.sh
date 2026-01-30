#!/bin/bash
#
# STL to STEP Converter Runner Script
# This script finds FreeCAD's Python and runs the conversion script with it.
#

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONVERTER_SCRIPT="$SCRIPT_DIR/convert_stl_to_step.py"

# macOS FreeCAD paths
FREECAD_APP="/Applications/FreeCAD.app"
FREECAD_APP_ALT="$HOME/Applications/FreeCAD.app"

# Function to setup and run with FreeCAD on macOS
run_macos() {
    local APP_PATH="$1"
    local RESOURCES="$APP_PATH/Contents/Resources"
    local BIN="$RESOURCES/bin"
    local LIB="$RESOURCES/lib"

    if [ ! -d "$APP_PATH" ]; then
        return 1
    fi

    echo "Using FreeCAD: $APP_PATH"
    echo ""

    # Set up environment for FreeCAD's Python
    export PYTHONPATH="$LIB:$PYTHONPATH"
    export DYLD_LIBRARY_PATH="$LIB:$DYLD_LIBRARY_PATH"
    export DYLD_FRAMEWORK_PATH="$RESOURCES/Frameworks:$DYLD_FRAMEWORK_PATH"

    # Run the converter
    "$BIN/python" "$CONVERTER_SCRIPT"
    return 0
}

# Function to run on Linux
run_linux() {
    # Try common Linux FreeCAD locations
    local FREECAD_PATHS=(
        "/usr/lib/freecad"
        "/usr/lib/freecad-python3"
        "/opt/freecad"
        "/snap/freecad/current/usr"
    )

    for base in "${FREECAD_PATHS[@]}"; do
        if [ -x "$base/bin/python" ] && [ -d "$base/lib" ]; then
            echo "Using FreeCAD: $base"
            echo ""
            export PYTHONPATH="$base/lib:$PYTHONPATH"
            export LD_LIBRARY_PATH="$base/lib:$LD_LIBRARY_PATH"
            "$base/bin/python" "$CONVERTER_SCRIPT"
            return 0
        fi
    done

    return 1
}

# Main execution
echo "Looking for FreeCAD..."

# Detect OS and run appropriate function
case "$(uname -s)" in
    Darwin)
        if run_macos "$FREECAD_APP"; then
            exit 0
        elif run_macos "$FREECAD_APP_ALT"; then
            exit 0
        fi
        ;;
    Linux)
        if run_linux; then
            exit 0
        fi
        ;;
esac

# If we get here, FreeCAD was not found
echo "ERROR: FreeCAD not found!"
echo ""
echo "Please install FreeCAD from:"
echo "  - https://www.freecad.org/downloads.php"
echo ""
echo "macOS: Install to /Applications/FreeCAD.app"
echo "Linux: Install via package manager, Snap, or Flatpak"
exit 1
