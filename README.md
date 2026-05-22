# HSU_project

Bonjour!! I'm Chun-Wei, a postdoc from Taiwan under Joshua's lab at National Taiwan University (NTU). :)

My current research project focuses on functional state transitions in the brain, 
exploring how these dynamic relate to psychological resilience and cognitive agiing. 

Here is our recent paper on functional state transition on Default Mode Network and how it associates with psychological resilience:
[Read the full paper here](https://doi.org/10.1016/j.neuroimage.2025.121508)

<a href="https://github.com/gracehsu">
  <img src="https://avatars.githubusercontent.com/u/7662670?v=4&s=100" width="100px;" alt="Profile Picture"/>
  <br /><sub><b>Chun-Wei</b></sub>
</a>

# 🧠 stateMDS: Automated Functional State Dynamics Pipeline

## 📊 Project Presentation

### 📌 Introduction
This project focuses on transforming an existing neuroimaging analysis framework—`stateMDS`—into a streamlined, open-source tool. 

Currently, stateMDS quantifies and visualizes the dynamic trajectories of brain network states using resting-state fMRI (rsfMRI) data. However, the current workflow requires manual execution across different software environments. This project bridges that gap, making the methodology easily accessible, reproducible, and ready for deployment on local machines or computing clusters.

---

### 🎯 Goal
The goal of this project is to turn my current analyses into a **fully reproducible, automated pipeline**.

#### 📍 Primary Objective
> Build a master shell script (`run_stateMDS.sh`) that takes a pre-extracted matrix of time points × voxels (saved as a `.csv` file) and automatically executes the entire R-based pipeline. 

This includes:
* Performing Multidimensional Scaling (MDS)
* Calculating geometric and dynamic brain indices (Velocity, Convex Hull Area, Grid Entropy, and Laminarity)
* Generating all corresponding results and plots without manual intervention

#### 🚀 Stretch Goals (If time allows)
1. **Upstream Integration:** Incorporate the MATLAB-based voxel extraction script (`catCarryingVoxel.m`) directly into the shell script so the pipeline can accept preprocessed 4D NIfTI volumes.
2. **Open Data Application:** Test the end-to-end pipeline by pulling preprocessed data from open online repositories.
3. **Mask Generation:** Automate the creation of subject-space ROI masks required for the voxel extraction step.

---

### 🔬 Background of this analysis
The core concept of this methodology relies on evaluating brain activity as a dynamic spatial pattern rather than just averaging signals across a region.

* **Functional State:** The spatial pattern of multi-voxel BOLD signal intensities captured at a single time point ($TR$) within a predefined network or ROI.
* **State Transition:** The temporal change in this multi-voxel pattern. By quantifying frame-by-frame changes, we capture the continuous trajectory of a network’s activity.
* **Dimensionality Reduction:** Because voxel-wise patterns are highly dimensional, Multidimensional Scaling (MDS) is used to project these states into a lower-dimensional space (e.g., 2D, 3D or higher).

<p align="center">
  <img src="assets/transition_arrows.png" alt="Example of 2D state space trajectory with transition arrows" width="350">
</p>
<p align="center">
  <em>Example of a 2D state space trajectory. The arrows represent step-by-step transitions (velocity) between functional states over time.</em>
</p>

From these lower-dimensional trajectories, we compute advanced spatial and temporal indices—such as the "arrow distance" (mean velocity) between states, Grid Entropy (GE) for state-space occupancy, and Laminarity (LAM) for state recurrence. This framework is atlas-agnostic and can be applied to any network of interest.

### 📊 Schematic of Functional State Indices

To quantify the dynamic trajectory of brain states in the lower-dimensional MDS space, we calculate several topological and dynamic indices:

<p align="center">
  <img src="assets/indices_schematic.png" alt="Schematic representation of topological and dynamic functional state indices" width="350">
</p>


* **(A) Mean Velocity (MV):** The step-by-step Euclidean distance between consecutive TRs, representing the speed of state transition.
* **(A) Convex Hull Area (CHA):** A topological measure of the total state-space volume explored by the network over the scan duration.
* **(B) Grid Entropy (GE):** A measure of state-space distribution and occupancy. High entropy indicates a diverse, widely varying sequence of states, while low entropy indicates the brain remained in a highly repetitive or constrained state.
* **(C)Laminarity (LAM):** Derived from Recurrence Quantification Analysis (RQA), indicating the tendency of the brain to get "stuck" in a specific state before transitioning.
---

### 📁 Data
Depending on the project phase, the pipeline utilizes:
* **Primary Input:** Voxel-wise fMRI time series data formatted as a `time × voxels` CSV file.
* **Stretch Goal Input:** Preprocessed 4D EPI volumes (`.nii`) and corresponding network/ROI masks (e.g., AAL3, DiFuMo).

---

### 🛠️ Tools
* **Bash / Shell Scripting:** For wrapping the pipeline, handling command-line arguments, and managing file routing.
* **R & RStudio:** The core analytical engine for MDS computation, index calculation (`vegan`, `geometry`, `entropy`), and visualization (`ggplot2`, `plotly`).
* **MATLAB & SPM12:** *(Stretch Goal)* For handling NIfTI volumes and extracting voxel-wise values.
* **Git / GitHub:** For version control, open-source distribution, and project documentation.