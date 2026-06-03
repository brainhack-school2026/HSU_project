import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind

# ==========================================
# CONFIGURATION
# ==========================================
DIR = "output_adhd"
INDICES_FILE = os.path.join(DIR, "Brain_Indices_Summary.csv")
VELOCITY_FILE = os.path.join(DIR, "Master_Velocity_Summary.csv")

# ==========================================
# STEP 1: Load and Merge Data
# ==========================================
print("Loading stateMDS results...")
df_idx = pd.read_csv(INDICES_FILE)
df_vel = pd.read_csv(VELOCITY_FILE)

# Merge the two CSVs based on the Subject column
df = pd.merge(df_idx, df_vel, on="Subject")

# Extract the group (CTRL vs ADHD) from the Subject ID string
# e.g., "sub-0010042_ADHD" -> "ADHD"
df['Group'] = df['Subject'].apply(lambda x: str(x).split('_')[-1])

# Clean up column names just in case they have leading/trailing spaces
df.columns = df.columns.str.strip()

# ==========================================
# STEP 2: Run Independent t-tests
# ==========================================
# THE FIX: Updated mapping to perfectly match your R script outputs
metrics = {
    'Velocity': 'Velocity_Mean', 
    'Convex Hull Area (CHA)': 'CHA_Norm',
    'Grid Entropy (GE)': 'GE_Norm',
    'Laminarity (LAM)': 'LAM_Norm'
}

print("\n" + "="*45)
print(" 📊 GROUP COMPARISONS (ADHD vs CTRL)")
print("="*45)

for label, col in metrics.items():
    if col in df.columns:
        adhd_vals = df[df['Group'] == 'ADHD'][col]
        ctrl_vals = df[df['Group'] == 'CTRL'][col]
        
        t_stat, p_val = ttest_ind(adhd_vals, ctrl_vals, equal_var=False) # Welch's t-test
        print(f"{label}:")
        print(f"  -> t = {t_stat:.2f}, p = {p_val:.4f}")
    else:
        print(f"⚠️ Column '{col}' not found in CSV.")

# ==========================================
# STEP 3: Generate Presentation Plots
# ==========================================
print("\n🎨 Generating 2x2 visualization grid...")

# Set the aesthetic style
sns.set_theme(style="whitegrid", context="talk")
fig, axes = plt.subplots(2, 2, figsize=(14, 12))
axes = axes.flatten()

# Custom colors for your slides (e.g., Blue for CTRL, Red for ADHD)
palette = {"CTRL": "#4C72B0", "ADHD": "#C44E52"}

for i, (label, col) in enumerate(metrics.items()):
    if col in df.columns:
        ax = axes[i]
        
        # 1. Draw the boxplot
        sns.boxplot(
            data=df, x='Group', y=col, ax=ax, 
            palette=palette, width=0.4, boxprops=dict(alpha=0.3), showfliers=False
        )
        
        # 2. Draw the individual dots (Swarmplot)
        sns.swarmplot(
            data=df, x='Group', y=col, ax=ax, 
            color='black', alpha=0.7, size=8
        )
        
        ax.set_title(label, fontweight='bold', pad=15)
        ax.set_xlabel("")
        ax.set_ylabel("Value")

plt.tight_layout()
output_plot = os.path.join(DIR, "Group_Comparisons.png")
plt.savefig(output_plot, dpi=300, bbox_inches='tight')
print(f"✅ Plot saved successfully to: {output_plot}")
plt.show()