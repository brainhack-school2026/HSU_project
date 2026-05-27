# HSU_project

Bonjour!! I'm Chun-Wei, a postdoc from Taiwan under Joshua's lab at National Taiwan University (NTU). :)

My current research project focuses on functional state transitions in the brain, exploring how these dynamics relate to psychological resilience and cognitive aging. 

Here is our recent paper on functional state transitions in the Default Mode Network and how it associates with psychological resilience:
[Read the full paper here](https://doi.org/10.1016/j.neuroimage.2025.121508)

<a href="https://github.com/gracehsu">
  <img src="https://avatars.githubusercontent.com/u/7662670?v=4&s=100" width="100px;" alt="Profile Picture"/>
  <br /><sub><b>Chun-Wei</b></sub>
</a>

---

# 🧠 stateMDS: Automated Functional State Dynamics Pipeline

## 📊 Project Presentation

### 📌 Introduction
This project focuses on transforming an existing neuroimaging analysis framework—`stateMDS`—into a streamlined, open-source tool. 

Currently, `stateMDS` quantifies and visualizes the dynamic trajectories of brain network states using resting-state fMRI (rsfMRI) data. However, the current workflow requires manual execution across different software environments. This project bridges that gap, making the methodology easily accessible, reproducible, and ready for deployment on local machines or computing clusters.

---

### 🎯 Goal
The goal of this project is to turn my current analyses into a **fully reproducible, automated pipeline**.

#### 📍 Primary Objective
> Build a master shell script (`run_stateMDS.sh`) that takes a pre-extracted matrix of time points × voxels (saved as a `.csv` or `.tsv` file) and automatically executes the entire R-based pipeline. 

This includes:
* Performing Non-metric Multidimensional Scaling (NMDS)
* Calculating geometric and dynamic brain indices (Mean Velocity, Convex Hull Area, Grid Entropy, and Laminarity)
* Generating all corresponding results and plots without manual intervention

#### 🚀 Stretch Goals (If time allows)
* **Upstream Integration:** Incorporate the MATLAB-based voxel extraction script (`catCarryingVoxel.m`) directly into the shell script so the pipeline can accept preprocessed 4D NIfTI volumes.
* **Open Data Application:** Test the end-to-end pipeline by pulling preprocessed data from open online repositories.
* **Mask Generation:** Automate the creation of subject-space ROI masks required for the voxel extraction step.

---

### 🔬 Background of this Analysis
The core concept of this methodology relies on evaluating brain activity as a dynamic spatial pattern rather than just averaging signals across a region.

* **Functional State:** The spatial pattern of multi-voxel BOLD signal intensities captured at a single time point (TR) within a predefined network or ROI.
* **State Transition:** The temporal change in this multi-voxel pattern. By quantifying frame-by-frame changes, we capture the continuous trajectory of a network’s activity.
* **Dimensionality Reduction:** Because voxel-wise patterns are highly dimensional, Non-metric Multidimensional Scaling (NMDS) is used to project these states into a lower-dimensional space.

<p align="center">
  <img src="assets/transition_arrows.png" alt="Example of 2D state space trajectory with transition arrows" width="350">
</p>
<p align="center">
  <em>Example of a 2D state space trajectory. The arrows represent step-by-step transitions (velocity) between functional states over time.</em>
</p>

From these topological trajectories, we compute advanced spatial and temporal indices. This framework is atlas-agnostic and can be applied to any network of interest.

### 📊 Schematic of Functional State Indices

To quantify the dynamic trajectory of brain states, we calculate several topological and dynamic indices:

<p align="center">
  <img src="assets/indices_schematic.png" alt="Schematic representation of topological and dynamic functional state indices" width="350">
</p>

* **(A) Mean Velocity (MV):** The step-by-step Euclidean distance between consecutive TRs, representing the speed of state transition.
* **(A) Convex Hull Area (CHA):** A topological measure of the total state-space volume explored by the network over the scan duration.
* **(B) Grid Entropy (GE):** A measure of state-space distribution and occupancy. High entropy indicates a diverse, widely varying sequence of states, while low entropy indicates the brain remained in a highly repetitive or constrained state.
* **(C) Laminarity (LAM):** Derived from Recurrence Quantification Analysis (RQA), indicating the tendency of the brain to get "stuck" in a specific state before transitioning.

---

## 💻 How to Use the Pipeline

### 📦 Prerequisites
Ensure you have **R** installed on your system. Install the required libraries by running this in your R console:
```R
install.packages(c("optparse", "vegan", "readr", "fs", "dplyr", "geometry", "entropy", "fields", "ggplot2"))
```

### 📂 Project Structure
Ensure your input data (`.csv` or `.tsv` files representing Time points × Voxels) is placed in the correct directory before running:

```text
stateMDS/
├── run_stateMDS.sh               # Master Bash script
├── R/
│   ├── run_mds_analysis.R        # Step 1: NMDS & Velocity
│   ├── run_brain_indices.R       # Step 2: CHA, GE, LAM
│   └── visualize_trajectories.R  # Step 3: Plotting
└── data/
    └── voxels/                   # Place your input matrices here
        ├── sub-01_voxels.csv
        └── ...
```

### 🚀 Quick Start (Default Run)
The default pipeline dynamically searches for the mathematically optimal dimension (up to k=10) for every subject where the NMDS stress falls below 0.15. 

Open your terminal and navigate to the `stateMDS` root folder. Make the script executable (only needed once):

```bash
chmod +x run_stateMDS.sh
```

Run the pipeline:

```bash
./run_stateMDS.sh
```

All multi-dimensional calculations and 2D projection plots will be saved to the `output/` folder.

### ⚙️ Advanced Usage & Customization
You can fully customize the pipeline's behavior using terminal flags:

* `-d` : Input directory containing TSV/CSV files (Default: `data/voxels`)
* `-o` : Main output directory (Default: `output`)
* `-t` : Maximum TRs to analyze per subject (Default: `180`)
* `-s` : Maximum acceptable stress value (Default: `0.15`)
* `-k` : Maximum dimension to test (Default: `10`)

**Example: The Dual-Folder Approach**
It is recommended to run the pipeline twice to separate rigorous math from intuitive visuals.

Run 1 (Optimal Math - Finds true dimension for statistical analysis):
```bash
./run_stateMDS.sh -o output_optimal
```

Run 2 (Forced 2D Visuals - Forces k=2 for clean supplementary figures):
```bash
./run_stateMDS.sh -o output_2D -k 2 -s 1.0
```

### 📁 Data
Depending on the project phase, the pipeline utilizes:
* **Primary Input:** Voxel-wise fMRI time series data formatted as a `time × voxels` CSV file.
* **Stretch Goal Input:** Preprocessed 4D EPI volumes (`.nii`) and corresponding network/ROI masks (e.g., AAL3, DiFuMo).

---

### 🔮 Future Architecture: Python & Nilearn Integration

While the current pipeline relies on MATLAB for initial voxel extraction, the ultimate vision for **stateMDS** is to become a 100% open-source application using Python. 

By shifting upstream processing to `nilearn`, the pipeline will eliminate proprietary software dependencies and smoothly bridge the gap between BIDS-compliant preprocessing and our dynamic state analysis.

#### The Unified Open-Source Workflow

* **Stage 1: Preprocessing (fMRIPrep)** - Outputs cleaned, standardized 4D NIfTI volumes.
* **Stage 2: Voxel-wise Time Series Extraction (Python/Nilearn)** - Uses `nilearn.maskers.NiftiMasker` to apply network/grey matter masks, detrend the signal, and output a clean `time × voxels` CSV file.
* **Stage 3: Dynamic State Analysis (stateMDS)** - The `run_stateMDS.sh` script ingests the CSV files. R executes NMDS, computes dynamic indices (Velocity, CHA, GE, LAM), and generates automated trajectory plots.

#### Proposed Shell Implementation
Future iterations of `run_stateMDS.sh` will act as a wrapper to execute both tools sequentially on a computing cluster:

```bash
# 1. Extract standardized voxel-wise time series using Nilearn
python extract_voxels.py \
  --input /data/fmriprep/sub-01/func/sub-01_task-rest_space-MNI152_desc-preproc_bold.nii.gz \
  --mask /data/masks/dmn_mask.nii.gz \
  --output /data/nilearn_output/sub-01_voxels.csv

# 2. Run stateMDS on the extracted CSV
EXTRACTED_CSV="/data/nilearn_output/sub-01_voxels.csv"
./run_stateMDS.sh -d $(dirname "$EXTRACTED_CSV") -o output_optimal
```

### 🛠️ Tools
* **Bash / Shell Scripting:** For wrapping the pipeline, handling command-line arguments, and managing file routing.
* **R & RStudio:** The core analytical engine for NMDS computation, index calculation (`vegan`, `geometry`, `entropy`), and visualization (`ggplot2`, `fields`).
* **MATLAB & SPM12:** *(Current Upstream)* For handling NIfTI volumes and extracting voxel-wise values via `catCarryingVoxel.m`.
* **Python & Nilearn:** *(Future Architecture)* For applying grey matter masks, detrending, and voxel-level signal extraction (`NiftiMasker`), which will eventually replace the MATLAB dependencies.
* **Git / GitHub:** For version control, open-source distribution, and project documentation.