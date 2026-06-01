import numpy as np
from nilearn import datasets
from nilearn.maskers import NiftiMasker
from sklearn.manifold import MDS
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# STEP 1: Download Open Data
# Fetching a single subject from the 'development_fmri' dataset.
# This data is already fMRIPrep-processed and in BIDS format!
# ---------------------------------------------------------
print("Fetching dataset...")
dataset = datasets.fetch_development_fmri(n_subjects=1)

fmri_img = dataset.func[0]        # The 4D resting-state NIfTI file
confounds_file = dataset.confounds[0] # The TSV file containing motion (FD) and tissue noise (aCompCor)

# ---------------------------------------------------------
# STEP 2: Denoise, Bandpass, and Mask (The Nilearn Way)
# This single object replaces your entire FSL/AFNI/SPM block.
# We are setting a standard gray matter mask and filtering.
# ---------------------------------------------------------
print("Building the NiftiMasker...")
masker = NiftiMasker(
    mask_strategy='epi',       # Automatically computes a whole-brain/GM mask
    standardize=True,          # Z-scores the time series
    detrend=True,              # Removes linear drift
    high_pass=0.01,            # Matches your 0.009 Hz requirement closely
    low_pass=0.08,             # Matches your 0.08 Hz requirement
    t_r=2.0,                   # The Repetition Time
    memory='nilearn_cache',    # Caches results so rerunning is instant
    verbose=1
)

# ---------------------------------------------------------
# STEP 3: Extract Voxel Values
# This step applies the mask, regresses out the confounds, 
# applies the bandpass filter, and extracts the 2D matrix.
# ---------------------------------------------------------
print("Extracting and cleaning time series...")
# The output is a NumPy array: Shape = (n_volumes, n_voxels)
time_series = masker.fit_transform(fmri_img, confounds=confounds_file)

print(f"Extracted shape: {time_series.shape[0]} volumes by {time_series.shape[1]} voxels.")

# ---------------------------------------------------------
# STEP 4: Multidimensional Scaling (stateMDS framework)
# Reduce the massive voxel dimension into a 2D state trajectory
# ---------------------------------------------------------
print("Running Multidimensional Scaling...")
# We use Euclidean distance to find the relationships between brain states at each TR
mds = MDS(n_components=2, dissimilarity='euclidean', random_state=42)

# Shape will become (n_volumes, 2)
state_trajectory = mds.fit_transform(time_series)

# ---------------------------------------------------------
# STEP 5: Visualize the Trajectory
# ---------------------------------------------------------
plt.figure(figsize=(8, 6))
plt.plot(state_trajectory[:, 0], state_trajectory[:, 1], marker='o', linestyle='-', alpha=0.6)
plt.title('Brain Network State Trajectory (MDS)')
plt.xlabel('MDS Dimension 1')
plt.ylabel('MDS Dimension 2')
plt.grid(True)
plt.show()