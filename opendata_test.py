import numpy as np
import subprocess
from nilearn import datasets, image
from nilearn.maskers import NiftiMasker

# ---------------------------------------------------------
# STEP 1: Fetch fMRIPrep Data (MNI Space)
# ---------------------------------------------------------
print("Fetching fMRI data...")
dataset = datasets.fetch_development_fmri(n_subjects=1)
fmri_img = dataset.func[0]        
confounds_file = dataset.confounds[0] 

# ---------------------------------------------------------
# STEP 2: Fetch Schaefer Atlas and Isolate the DMN
# ---------------------------------------------------------
print("Fetching Schaefer 2018 Atlas...")
# Grabbing the 100-parcel, 7-network version (2mm resolution to match typical EPI)
atlas = datasets.fetch_atlas_schaefer_2018(n_rois=100, yeo_networks=7, resolution_mm=2)
atlas_img = atlas.maps
labels = atlas.labels

print("Building DMN Mask...")
# Find all region indices that belong to the Default Mode Network
# (Adding 1 because atlas background is 0, regions start at 1)
dmn_indices = [i + 1 for i, label in enumerate(labels) if b'Default' in label]

# Create a binary mask where voxels are 1 if they belong to DMN, 0 otherwise
dmn_mask = image.math_img(f"np.isin(img, {dmn_indices})", img=atlas_img)

# ---------------------------------------------------------
# STEP 3: Denoise, Bandpass, and Extract Voxel Values
# ---------------------------------------------------------
print("Extracting and cleaning DMN voxel time series...")
masker = NiftiMasker(
    mask_img=dmn_mask,         # Apply our custom DMN mask
    standardize=True,          # Z-scores the time series
    detrend=True,              # Removes linear drift
    high_pass=0.01,            # Bandpass filters
    low_pass=0.08,             
    t_r=2.0,                   # Repetition Time
    memory='nilearn_cache',    
    verbose=1
)

# Output matrix: Shape = (n_volumes, n_voxels_in_DMN)
time_series = masker.fit_transform(fmri_img, confounds=confounds_file)
print(f"Extraction complete! Shape: {time_series.shape[0]} TRs by {time_series.shape[1]} DMN voxels.")

# ---------------------------------------------------------
# STEP 4: Export to stateMDS
# ---------------------------------------------------------
output_file = "sub-001_DMN_timeseries.csv"
print(f"Saving extracted matrix to {output_file}...")

# Save the matrix as a CSV so your R/Matlab backend can read it easily
np.savetxt(output_file, time_series, delimiter=",")

# Execute your GitHub bash script
print("Firing stateMDS pipeline...")
try:
    # Point this to wherever your run_stateMDS.sh is located
    bash_command = f"./run_stateMDS.sh --input {output_file}"
    
    # This runs the bash script and pipes the terminal output right here
    result = subprocess.run(bash_command, shell=True, check=True, text=True, capture_output=True)
    print(result.stdout)
    
except subprocess.CalledProcessError as e:
    print("stateMDS script hit an error:")
    print(e.stderr)