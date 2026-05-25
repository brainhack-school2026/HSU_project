#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# --- 1. HELP MENU FUNCTION ---
show_help() {
    echo "Usage: ./run_stateMDS.sh [-i input_matrix.tsv] [-o output_directory]"
    echo ""
    echo "Options:"
    echo "  -i  Path to the time x voxels TSV file (Required)"
    echo "  -o  Path to the main output directory (Default: ./output)"
    echo "  -h  Show this help message"
    exit 0
}

# Initialize default variables
INPUT_FILE=""
OUTPUT_DIR="$(pwd)/output"

# --- 2. PARSE COMMAND LINE ARGUMENTS ---
while getopts "i:o:h" opt; do
    case "$opt" in
        i) INPUT_FILE="$OPTARG" ;;
        o) OUTPUT_DIR="$OPTARG" ;;
        h) show_help ;;
        *) show_help ;;
    esac
done

# Check if required input file was provided
if [ -z "$INPUT_FILE" ]; then
    echo "Error: Missing required input file (-i)."
    show_help
fi

echo "========================================================="
echo " Starting stateMDS Pipeline"
echo "========================================================="
echo "Input Matrix:  $INPUT_FILE"
echo "Output Folder: $OUTPUT_DIR"

# --- 3. CREATE OUTPUT DIRECTORIES ---
# This ensures R never crashes due to a missing folder structure
echo "Initializing directory tree..."
mkdir -p "$OUTPUT_DIR/MDSpoint"
mkdir -p "$OUTPUT_DIR/arrowdis"
mkdir -p "$OUTPUT_DIR/plots/2d_trajectories"
mkdir -p "$OUTPUT_DIR/plots/ge_heatmaps"
mkdir -p "$OUTPUT_DIR/plots/LAM_plots"

# --- 4. RUN R SCRIPTS SEQUENTIALLY ---
# We use Rscript to run R directly from the command line.
# We pass the input file and output directory as arguments directly into R.

echo "Step 1: Running Multidimensional Scaling Analysis..."
Rscript R/run_mds_analysis.R --input "$INPUT_FILE" --output "$OUTPUT_DIR"

echo "Step 2: Calculating Advanced Brain Indices (CHA, GE, LAM)..."
Rscript R/run_brain_indices.R --output "$OUTPUT_DIR"

echo "Step 3: Generating Visualizations and Trajectory Plots..."
Rscript R/visualize_trajectories.R --output "$OUTPUT_DIR"

echo "========================================================="
echo " stateMDS Pipeline Completed Successfully!"
echo " All results saved to: $OUTPUT_DIR"
echo "========================================================="