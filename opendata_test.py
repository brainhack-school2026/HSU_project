import os
import numpy as np
import subprocess
from nilearn import datasets, image
from nilearn.maskers import NiftiMasker

# ==========================================
# STEP 1: Fetch fMRIPrep Data (MNI Space)
# ==========================================
print("Fetching fMRI data...")
dataset = datasets.fetch_development_fmri(n_subjects=1)
fmri_img = dataset.func[0]        
confounds_file = dataset.confounds[0] 

# ==========================================
# STEP 2: Fetch Schaefer Atlas and Isolate DMN
# ==========================================
print("Fetching Schaefer 2018 Atlas...")
atlas = datasets.fetch_atlas_schaefer_2018(n_rois=100, yeo_networks=7, resolution_mm=2)
atlas_img = atlas.maps
labels = atlas.labels

print("Building DMN Mask...")
dmn_indices = [i + 1 for i, label in enumerate(labels) if b'Default' in label]
dmn_mask = image.math_img(f"np.isin(img, {dmn_indices})", img=atlas_img)

# ==========================================
# STEP 3: Extract Voxel Values
# ==========================================
print("Extracting and cleaning DMN voxel time series...")
masker = NiftiMasker(
    mask_img=dmn_mask,
    standardize=True,
    detrend=True,
    high_pass=0.01,
    low_pass=0.08,
    t_r=2.0,
    memory='nilearn_cache',
    verbose=1
)

time_series = masker.fit_transform(fmri_img, confounds=confounds_file)
print(f"Extraction complete! Shape: {time_series.shape[0]} TRs by {time_series.shape[1]} DMN voxels.")

# ==========================================
# STEP 4: Format Directories & Export
# ==========================================
# Define the directories exactly as your Bash script expects them
INPUT_DIR = "data/voxels"
OUTPUT_DIR = "output_stateMDS" # Named specifically so it doesn't accidentally overwrite unrelated 'output' folders

# Create the directories if they don't exist
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Save the matrix into the specific input directory
output_csv = os.path.join(INPUT_DIR, "sub-001_DMN_timeseries.csv")
print(f"Saving extracted matrix to {output_csv}...")
np.savetxt(output_csv, time_series, delimiter=",")

# ==========================================
# STEP 5: Trigger stateMDS Bash Script
# ==========================================
print("\nFiring stateMDS pipeline...")
try:
    # We use the exact flags your run_stateMDS.sh script expects: -d and -o
    bash_command = f"./run_stateMDS.sh -d {INPUT_DIR} -o {OUTPUT_DIR}"
    
    # Execute the command and stream the output
    result = subprocess.run(bash_command, shell=True, check=True, text=True, capture_output=True)
    
    # Print the beautiful echo statements from your Bash script
    print(result.stdout)
    
except subprocess.CalledProcessError as e:
    print("\n❌ stateMDS script hit an error:")
    print(e.stderr)
    # If the R script crashes, it will print the exact R error message here
    if e.stdout:
        print(e.stdout)