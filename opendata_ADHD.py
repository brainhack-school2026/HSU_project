import os
import numpy as np
import pandas as pd
import subprocess
import nibabel as nib
from nilearn import datasets, image
from nilearn.maskers import NiftiMasker

# ==========================================
# CONFIGURATION BLOCK
# ==========================================
ATLAS = "schaefer" 
TARGET_ROI = "Default" 
INPUT_DIR = "data/voxels"
OUTPUT_DIR = "output_stateMDS"
TARGET_TR = 2.0  

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==========================================
# STEP 1: Fetch and Filter ADHD Cohort by TR
# ==========================================
print(f"Fetching ADHD-200 Dataset pool...")
dataset = datasets.fetch_adhd(n_subjects=40)

valid_controls = []
valid_patients = []

print(f"Scanning NIfTI headers for subjects with TR = {TARGET_TR}s...")

for idx, func_file in enumerate(dataset.func):
    img_header = nib.load(func_file).header
    actual_tr = img_header.get_zooms()[3]
    
    if round(actual_tr, 2) == TARGET_TR:
        # THE FIX: Use .iloc[idx] because phenotypic is a Pandas DataFrame
        pheno = dataset.phenotypic.iloc[idx]
        diagnosis = pheno['adhd']
        
        if diagnosis == 0 and len(valid_controls) < 10:
            valid_controls.append(idx)
        elif diagnosis == 1 and len(valid_patients) < 10:
            valid_patients.append(idx)
            
    if len(valid_controls) == 10 and len(valid_patients) == 10:
        break

cohort_indices = valid_controls + valid_patients
print(f"Successfully selected {len(valid_controls)} Controls and {len(valid_patients)} ADHD subjects with TR = {TARGET_TR}.")

# ==========================================
# STEP 2: Fetch Atlas and Build Mask
# ==========================================
print(f"Loading the {ATLAS.upper()} atlas...")

if ATLAS == "schaefer":
    atlas = datasets.fetch_atlas_schaefer_2018(n_rois=100, yeo_networks=7, resolution_mm=2)
    atlas_img, labels = atlas.maps, atlas.labels
    
    target_indices = [
        i + 1 for i, label in enumerate(labels) 
        if TARGET_ROI in (label.decode('utf-8') if isinstance(label, bytes) else str(label))
    ]

elif ATLAS == "aal":
    atlas = datasets.fetch_atlas_aal()
    atlas_img, labels = atlas.maps, atlas.labels
    target_indices = [
        int(atlas.indices[i]) for i, label in enumerate(labels) 
        if TARGET_ROI in (label.decode('utf-8') if isinstance(label, bytes) else str(label))
    ]
else:
    raise ValueError("Atlas not supported. Choose 'schaefer' or 'aal'.")

print(f"Building mask for ROI: {TARGET_ROI}...")
roi_mask = image.math_img(f"np.isin(img, {target_indices})", img=atlas_img)

# ==========================================
# STEP 3: Loop Through Cohort & Process
# ==========================================
n_trs_detected = 0 

for idx in cohort_indices:
    # THE FIX: Use .iloc[idx] here as well
    pheno = dataset.phenotypic.iloc[idx]
    subject_id = pheno['Subject']
    diagnosis = "ADHD" if pheno['adhd'] == 1 else "CTRL"
    
    # Robust string conversion to prevent Pandas from dropping leading zeros
    if isinstance(subject_id, bytes):
        sub_str = subject_id.decode('utf-8')
    else:
        sub_str = str(subject_id)
        
    if sub_str.isdigit():
        sub_str = sub_str.zfill(7) # Forces it back to 7 digits (e.g., 0010042)
        
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
        t_r=TARGET_TR,
        memory='nilearn_cache',
        verbose=0 
    )

    time_series = masker.fit_transform(fmri_img, confounds=confounds_file)
    n_trs_detected = time_series.shape[0] 
    
    print(f" -> Extracted Shape: {n_trs_detected} TRs x {time_series.shape[1]} Voxels")

    output_csv = os.path.join(INPUT_DIR, f"{file_prefix}_timeseries.csv")
    np.savetxt(output_csv, time_series, delimiter=",")

print(f"\nAll subjects successfully processed and saved to {INPUT_DIR}/")

# ==========================================
# STEP 4: Trigger stateMDS Bash Script
# ==========================================
print("\nFiring stateMDS pipeline on the cohort...")
try:
    bash_command = f"./run_stateMDS.sh -d {INPUT_DIR} -o {OUTPUT_DIR} -t {n_trs_detected}"
    result = subprocess.run(bash_command, shell=True, check=True, text=True, capture_output=True)
    print(result.stdout)
    
except subprocess.CalledProcessError as e:
    print("\n❌ stateMDS script hit an error:")
    print(e.stderr)
    if e.stdout:
        print(e.stdout)