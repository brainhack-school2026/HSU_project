import os
import numpy as np
import pandas as pd
import subprocess
from nilearn import datasets, image
from nilearn.maskers import NiftiMasker

# ==========================================
# CONFIGURATION BLOCK
# ==========================================
# 1. Atlas Selection ("schaefer" or "aal")
ATLAS = "schaefer" 

# Set your target ROI keyword. 
# For Schaefer, 'Default' grabs the DMN. For AAL, you might use 'Cingulum' or 'Precuneus'.
TARGET_ROI = "Default" 

# Directories for your bash script
INPUT_DIR = "data/voxels"
OUTPUT_DIR = "output_stateMDS"

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==========================================
# STEP 1: Fetch and Filter ADHD Cohort
# ==========================================
print("Fetching ADHD-200 Dataset pool...")
# Fetch 40 subjects to ensure we have enough to pull 10 of each type
dataset = datasets.fetch_adhd(n_subjects=40)

# Convert phenotypic data to a clean DataFrame
pheno = pd.DataFrame(dataset.phenotypic)

# In the ADHD dataset, 'adhd' column: 0 = Control, 1 = ADHD
controls = pheno[pheno['adhd'] == 0].head(10)
patients = pheno[pheno['adhd'] == 1].head(10)

# Combine them and get their original indices so we can grab their brain files
selected_cohort = pd.concat([controls, patients])
cohort_indices = selected_cohort.index.tolist()

print(f"Successfully selected 10 Controls and 10 ADHD subjects.")

# ==========================================
# STEP 2: Fetch Atlas and Build Mask
# ==========================================
print(f"Loading the {ATLAS.upper()} atlas...")

if ATLAS == "schaefer":
    atlas = datasets.fetch_atlas_schaefer_2018(n_rois=100, yeo_networks=7, resolution_mm=2)
    atlas_img, labels = atlas.maps, atlas.labels
    # Schaefer labels are byte-strings (e.g., b'7Networks_Default_PFC_1')
    target_indices = [i + 1 for i, label in enumerate(labels) if TARGET_ROI.encode() in label]

elif ATLAS == "aal":
    atlas = datasets.fetch_atlas_aal()
    atlas_img, labels = atlas.maps, atlas.labels
    # AAL uses standard strings, and uses a specific string-integer index mapping
    target_indices = [int(atlas.indices[i]) for i, label in enumerate(labels) if TARGET_ROI in label]

else:
    raise ValueError("Atlas not supported in this script. Choose 'schaefer' or 'aal'.")

# Create the binary mask
print(f"Building mask for ROI: {TARGET_ROI}...")
roi_mask = image.math_img(f"np.isin(img, {target_indices})", img=atlas_img)

# ==========================================
# STEP 3: Loop Through Cohort & Process
# ==========================================
n_trs_detected = 0 # We will save this to pass to the bash script

for idx in cohort_indices:
    subject_id = dataset.phenotypic[idx]['Subject'] # Usually looks like b'0010042'
    diagnosis = "ADHD" if dataset.phenotypic[idx]['adhd'] == 1 else "CTRL"
    
    # Decode the subject ID to a normal string
    sub_str = subject_id.decode('utf-8') if isinstance(subject_id, bytes) else str(subject_id)
    file_prefix = f"sub-{sub_str}_{diagnosis}"
    
    print(f"\nProcessing {file_prefix}...")
    
    fmri_img = dataset.func[idx]        
    confounds_file = dataset.confounds[idx] 
    
    masker = NiftiMasker(
        mask_img=roi_mask,
        standardize=True,
        detrend=True,
        high_pass=0.01,
        low_pass=0.08,
        t_r=2.0, 
        memory='nilearn_cache',
        verbose=0 # Turning off verbose so it doesn't spam your terminal 20 times
    )

    # Extract the matrix
    time_series = masker.fit_transform(fmri_img, confounds=confounds_file)
    n_trs_detected = time_series.shape[0] # Grab the dynamic TR count
    
    print(f" -> Extracted Shape: {n_trs_detected} TRs x {time_series.shape[1]} Voxels")

    # Save to the input directory for stateMDS
    output_csv = os.path.join(INPUT_DIR, f"{file_prefix}_timeseries.csv")
    np.savetxt(output_csv, time_series, delimiter=",")

print(f"\nAll 20 subjects successfully processed and saved to {INPUT_DIR}/")

# ==========================================
# STEP 4: Trigger stateMDS Bash Script
# ==========================================
print("\nFiring stateMDS pipeline on the cohort...")
try:
    # Notice we dynamically pass {n_trs_detected} to your -t flag!
    bash_command = f"./run_stateMDS.sh -d {INPUT_DIR} -o {OUTPUT_DIR} -t {n_trs_detected}"
    
    result = subprocess.run(bash_command, shell=True, check=True, text=True, capture_output=True)
    print(result.stdout)
    
except subprocess.CalledProcessError as e:
    print("\n❌ stateMDS script hit an error:")
    print(e.stderr)
    if e.stdout:
        print(e.stdout)