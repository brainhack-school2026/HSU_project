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
# STEP 1: Fetch and Clean Phenotypic Data
# ==========================================
print("Fetching ADHD-200 Dataset pool...")
dataset = datasets.fetch_adhd(n_subjects=40)

# Make it bulletproof: Handle Nilearn returning paths, lists, or arrays
if isinstance(dataset.phenotypic, list) and len(dataset.phenotypic) > 0 and isinstance(dataset.phenotypic[0], str):
    pheno_df = pd.read_csv(dataset.phenotypic[0])
elif isinstance(dataset.phenotypic, str):
    pheno_df = pd.read_csv(dataset.phenotypic)
else:
    pheno_df = pd.DataFrame(dataset.phenotypic)

# Standardize column names (lowercase) to avoid 'Subject' vs 'subject' errors
pheno_df.columns = [str(c).lower() for c in pheno_df.columns]

# Decode byte-strings to normal text
for col in pheno_df.columns:
    if pheno_df[col].dtype == object:
        pheno_df[col] = pheno_df[col].apply(lambda x: x.decode('utf-8') if isinstance(x, bytes) else str(x))

# Ensure subject column is formatted strictly as a 7-digit string (e.g., 0010042)
if 'subject' in pheno_df.columns:
    pheno_df['subject'] = pheno_df['subject'].astype(str).str.zfill(7)

# ==========================================
# STEP 2: Filter ADHD Cohort by TR
# ==========================================
valid_controls = []
valid_patients = []

print(f"Scanning NIfTI headers to find 10 Controls and 10 ADHD (TR = {TARGET_TR}s)...")

for idx, func_file in enumerate(dataset.func):
    # 1. Check the TR
    img_header = nib.load(func_file).header
    actual_tr = img_header.get_zooms()[3]
    
    if round(actual_tr, 2) == TARGET_TR:
        # 2. Extract Subject ID directly from the NIfTI file path
        sub_id = os.path.basename(func_file).split('_')[0]
        
        # 3. Look up this subject in our cleaned dataframe
        if 'subject' in pheno_df.columns:
            subject_row = pheno_df[pheno_df['subject'] == sub_id]
            if subject_row.empty:
                continue # Skip if metadata is missing for this file
            diagnosis_code = int(subject_row.iloc[0]['adhd'])
        else:
            diagnosis_code = int(pheno_df.iloc[idx].get('adhd', 0))
        
        # 4. Sort into the correct cohort
        if diagnosis_code == 0 and len(valid_controls) < 10:
            valid_controls.append((idx, sub_id, "CTRL"))
        elif diagnosis_code == 1 and len(valid_patients) < 10:
            valid_patients.append((idx, sub_id, "ADHD"))
            
    if len(valid_controls) == 10 and len(valid_patients) == 10:
        break

cohort_list = valid_controls + valid_patients
print(f"Successfully selected {len(valid_controls)} Controls and {len(valid_patients)} ADHD subjects.")

# ==========================================
# STEP 3: Fetch Atlas and Build Mask
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
# STEP 4: Loop Through Cohort & Process
# ==========================================
n_trs_detected = 0 

for file_idx, sub_id, diagnosis in cohort_list:
    file_prefix = f"sub-{sub_id}_{diagnosis}"
    print(f"\nProcessing {file_prefix}...")
    
    fmri_img = dataset.func[file_idx]        
    confounds_file = dataset.confounds[file_idx] 
    
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
# STEP 5: Trigger stateMDS Bash Script
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